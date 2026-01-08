from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.chat import ChatGroup, GroupMember, Message
from app.models.user import User
from app.utils.responses import success_response, error_response
from sqlalchemy import or_, and_

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """Get list of recent conversations (Users and Groups) with unread counts"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user_id_int = int(current_user_id)
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        # Verify user exists
        user = User.query.get(user_id_int)
        if not user:
            return error_response('User not found', None, 404)
        
        from sqlalchemy import func
        
        # 1. Get Groups user belongs to
        group_memberships = GroupMember.query.filter_by(user_id=user_id_int).all()
        group_ids = [m.group_id for m in group_memberships]
        groups = ChatGroup.query.filter(ChatGroup.id.in_(group_ids)).all()
        
        groups_data = []
        for g in groups:
            g_dict = g.to_dict()
            member = next((m for m in group_memberships if m.group_id == g.id), None)
            last_read = member.last_read_at if member else None
            
            # Group unread count (User specific)
            if last_read:
                unread_count = Message.query.filter(
                    Message.group_id == g.id,
                    Message.created_at > last_read
                ).count()
            else:
                unread_count = Message.query.filter_by(group_id=g.id).count()
            
            g_dict['unread_count'] = unread_count
            groups_data.append(g_dict)

        # 2. Get Users - OPTIMIZED w/ Aggregation
        # Fetch ALL active users so nobody is hidden (scoped to same company)
        if user.company_id:
            users = User.query.filter(
                User.id != user_id_int, 
                User.is_active == True,
                User.company_id == user.company_id
            ).all()
        else:
            # If user has no company, return empty list
            users = []
        
        # Aggregate Unread DMs in one query: SELECT sender_id, COUNT(*) FROM message ... GROUP BY sender_id
        unread_counts = db.session.query(
            Message.sender_id, func.count(Message.id)
        ).filter(
            Message.recipient_id == user_id_int,
            Message.is_read == False
        ).group_by(Message.sender_id).all()
        
        # Convert to dict for O(1) lookup
        unread_map = {uid: count for uid, count in unread_counts}

        users_data = []
        for u in users:
            u_dict = u.to_dict()
            # O(1) lookup instead of O(N) query inside loop
            u_dict['unread_count'] = unread_map.get(u.id, 0)
            users_data.append(u_dict)
        
        return success_response('Conversations retrieved', {
            'groups': groups_data,
            'users': users_data
        })
    except Exception as e:
        return error_response(f'Failed to get conversations: {str(e)}', None, 500)

@chat_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    """
    Get messages for a specific conversation.
    Query Params:
    - user_id: ID of the other user (for DM)
    - group_id: ID of the group
    """
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user_id_int = int(current_user_id)
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        # Verify user exists
        user = User.query.get(user_id_int)
        if not user:
            return error_response('User not found', None, 404)
        
        other_user_id = request.args.get('user_id', type=int)
        group_id = request.args.get('group_id', type=int)
        
        if not other_user_id and not group_id:
            return error_response('Target (user_id or group_id) required', None, 400)
        
        filtered_messages = []
        
        if group_id:
            # Verify membership
            member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id_int).first()
            if not member:
                return error_response('Not a member of this group', None, 403)
            
            # Eager load sender to prevent N+1 queries
            from sqlalchemy.orm import joinedload
            messages = Message.query.options(joinedload(Message.sender))\
                .filter_by(group_id=group_id)\
                .order_by(Message.created_at.desc())\
                .limit(200)\
                .all()
            
            # Reverse in python
            messages.reverse()
            
            # Filter deleted for me
            c_uid = str(user_id_int) # Comparison needs str
            for m in messages:
                 deleted_list = m.deleted_by.split(',') if m.deleted_by else []
                 if c_uid not in deleted_list:
                     if m.is_deleted_globally:
                         m.content = "🚫 This message was deleted"
                         m.message_type = 'text' # Force text
                         m.attachment_url = None
                     filtered_messages.append(m)
            
            # Update Group Read Status
            from datetime import datetime
            member.last_read_at = datetime.utcnow()
            db.session.commit()
            
        else:
            # DM: (sender=Me AND recipient=Other) OR (sender=Other AND recipient=Me)
            from sqlalchemy.orm import joinedload
            # Fetch latest 200 messages
            messages = Message.query.options(joinedload(Message.sender))\
                .filter(
                and_(
                    Message.group_id.is_(None),  # Ensure not a group message
                    or_(
                        and_(Message.sender_id == user_id_int, Message.recipient_id == other_user_id),
                        and_(Message.sender_id == other_user_id, Message.recipient_id == user_id_int)
                    )
                )
            ).order_by(Message.created_at.desc())\
            .limit(200)\
            .all()
            
            # Reverse in python to show oldest first (chronological)
            messages.reverse()
            
            # Filter deleted for me
            for m in messages:
                 deleted_list = m.deleted_by.split(',') if m.deleted_by else []
                 if str(user_id_int) not in deleted_list:
                     if m.is_deleted_globally:
                         m.content = "🚫 This message was deleted"
                         m.message_type = 'text'
                         m.attachment_url = None
                     filtered_messages.append(m)

            # Update DM Read Status
            unread_updates = Message.query.filter(
                Message.sender_id == other_user_id,
                Message.recipient_id == user_id_int,
                Message.is_read == False
            ).update({'is_read': True})
            
            if unread_updates > 0:
                db.session.commit()
                  
        return success_response('Messages retrieved', [m.to_dict() for m in filtered_messages])
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(f'Failed to get messages: {str(e)}', None, 500)

@chat_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    """
    Send a message
    Body:
    - recipient_id (optional, for DM)
    - group_id (optional, for Group)
    - content
    """
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user_id_int = int(current_user_id)
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        # Verify user exists
        user = User.query.get(user_id_int)
        if not user:
            return error_response('User not found', None, 404)
        
        data = request.get_json()
        
        content = data.get('content')
        if not content or not content.strip():
            return error_response('Content required', None, 400)
            
        recipient_id = data.get('recipient_id')
        group_id = data.get('group_id')
        
        if not recipient_id and not group_id:
            return error_response('Recipient or Group required', None, 400)
            
        # Enforce mutual exclusivity
        if group_id:
            recipient_id = None
        
        message = Message(
            sender_id=user_id_int,
            content=content.strip(),
            recipient_id=recipient_id,
            group_id=group_id,
            attachment_url=data.get('attachment_url'),
            message_type=data.get('message_type', 'text')
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Check for AI Bot Interaction
        if recipient_id:
            recipient = User.query.get(recipient_id)
            if recipient and recipient.is_bot:
                # Generate AI Response
                from app.services.ai_service import AIService
                ai_response_content = AIService.process_message(user_id_int, content)
                
                # Send AI Reply
                ai_message = Message(
                    sender_id=recipient_id, # The Bot
                    recipient_id=user_id_int,
                    content=ai_response_content,
                    message_type='text',
                    is_read=False
                )
                db.session.add(ai_message)
                db.session.commit()
        
        return success_response('Message sent', message.to_dict(), 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to send message: {str(e)}', None, 500)

@chat_bp.route('/groups', methods=['POST'])
@jwt_required()
def create_group():
    """
    Create a new group
    Body:
    - name
    - member_ids (list of user IDs to add)
    """
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user_id_int = int(current_user_id)
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        # Verify user exists
        user = User.query.get(user_id_int)
        if not user:
            return error_response('User not found', None, 404)
        
        # Check if user has a company (for scoping members)
        if not user.company_id:
            return error_response('User is not associated with a company', None, 403)
        
        data = request.get_json()
        
        name = data.get('name')
        if not name or not name.strip():
            return error_response('Group name required', None, 400)
            
        member_ids = data.get('member_ids', [])
        
        # Create Group
        group = ChatGroup(name=name, created_by=user_id_int)
        db.session.add(group)
        db.session.flush() # Get ID
        
        # Add Creator
        db.session.add(GroupMember(group_id=group.id, user_id=user_id_int))
        
        # Add Members (only from same company)
        for uid in member_ids:
            if uid != user_id_int: # Avoid dupe
                 # Verify user exists and is in same company
                 member_user = User.query.get(uid)
                 if member_user and member_user.company_id == user.company_id:
                     db.session.add(GroupMember(group_id=group.id, user_id=uid))
        
        db.session.commit()
        return success_response('Group created', group.to_dict(), 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create group: {str(e)}', None, 500)

@chat_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    """
    Delete a message
    Query: ?mode=me (default) or ?mode=everyone
    """
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user_id_int = int(current_user_id)
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        mode = request.args.get('mode', 'me')
        
        message = Message.query.get_or_404(message_id)
        
        if mode == 'everyone':
            # Only sender can delete for everyone
            if message.sender_id != user_id_int:
                return error_response('Only sender can delete for everyone', None, 403)
            message.is_deleted_globally = True
            
        else:
            # Delete for me: Append ID to deleted_by string
            current_deleted = message.deleted_by.split(',') if message.deleted_by else []
            if str(user_id_int) not in current_deleted:
                current_deleted.append(str(user_id_int))
                message.deleted_by = ','.join(current_deleted)
        
        db.session.commit()
        return success_response('Message deleted')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete message: {str(e)}', None, 500)

@chat_bp.route('/conversations/clear', methods=['POST'])
@jwt_required()
def clear_chat():
    """Clear chat history for current user"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user_id_int = int(current_user_id)
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        data = request.get_json()
        target_user_id = data.get('user_id')
        group_id = data.get('group_id')
        
        if not target_user_id and not group_id:
            return error_response('Target required', None, 400)
            
        if group_id:
            messages = Message.query.filter_by(group_id=group_id).all()
        else:
            messages = Message.query.filter(
                or_(
                    and_(Message.sender_id == user_id_int, Message.recipient_id == target_user_id),
                    and_(Message.sender_id == target_user_id, Message.recipient_id == user_id_int)
                )
            ).all()
            
        count = 0
        for m in messages:
            current_deleted = m.deleted_by.split(',') if m.deleted_by else []
            if str(user_id_int) not in current_deleted:
                current_deleted.append(str(user_id_int))
                m.deleted_by = ','.join(current_deleted)
                count += 1
                
        db.session.commit()
        return success_response(f'Chat cleared ({count} messages)')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to clear chat: {str(e)}', None, 500)

@chat_bp.route('/messages/forward', methods=['POST'])
@jwt_required()
def forward_message():
    """Forward a message to multiple recipients"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user_id_int = int(current_user_id)
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        # Verify user exists
        user = User.query.get(user_id_int)
        if not user:
            return error_response('User not found', None, 404)
        
        data = request.get_json()
        
        original_msg_id = data.get('message_id')
        recipient_ids = data.get('recipient_ids', []) # List of user IDs
        group_ids = data.get('group_ids', []) # List of group IDs
        
        original = Message.query.get_or_404(original_msg_id)
        
        # Clone content
        content = original.content
        attachment = original.attachment_url
        msg_type = original.message_type
        
        # Don't forward deleted content
        if original.is_deleted_globally:
            return error_response('Cannot forward deleted message', None, 400)
            
        forwarded_count = 0
        
        # Forward to users (only same company)
        for uid in recipient_ids:
            recipient = User.query.get(uid)
            if recipient and recipient.company_id == user.company_id:
                msg = Message(
                    sender_id=user_id_int,
                    recipient_id=uid,
                    content=content,
                    attachment_url=attachment,
                    message_type=msg_type
                )
                db.session.add(msg)
                forwarded_count += 1
            
        # Forward to groups
        for gid in group_ids:
            msg = Message(
                sender_id=user_id_int,
                group_id=gid,
                content=content,
                attachment_url=attachment,
                message_type=msg_type
            )
            db.session.add(msg)
            forwarded_count += 1
        
        db.session.commit()
        return success_response(f'Forwarded to {forwarded_count} chats')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to forward: {str(e)}', None, 500)

@chat_bp.route('/groups/<int:group_id>', methods=['PUT'])
@jwt_required()
def rename_group(group_id):
    """Rename a group"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user_id_int = int(current_user_id)
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        data = request.get_json()
        new_name = data.get('name')
        
        if not new_name or not new_name.strip():
            return error_response('Group name required', None, 400)
            
        group = ChatGroup.query.get_or_404(group_id)
        
        # Check membership
        member = GroupMember.query.filter_by(group_id=group.id, user_id=user_id_int).first()
        if not member:
            return error_response('Not a member of this group', None, 403)
            
        group.name = new_name.strip()
        db.session.commit()
        
        return success_response('Group renamed', group.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to rename group: {str(e)}', None, 500)

@chat_bp.route('/groups/<int:group_id>/members', methods=['DELETE'])
@jwt_required()
def leave_group(group_id):
    """Leave a group"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user_id_int = int(current_user_id)
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        group = ChatGroup.query.get_or_404(group_id)
        
        # Check membership
        member = GroupMember.query.filter_by(group_id=group.id, user_id=user_id_int).first()
        if not member:
            return error_response('Not a member of this group', None, 400)
            
        db.session.delete(member)
        db.session.commit()
        
        return success_response('Left group successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to leave group: {str(e)}', None, 500)

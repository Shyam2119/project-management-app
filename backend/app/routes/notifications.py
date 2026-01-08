from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import Notification, User
from app.models.notification import NotificationType
from app.utils.responses import success_response, error_response, pagination_response

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """
    Get notifications for current user
    Query params:
    - page, per_page
    - is_read: Filter by read status (true/false)
    - type: Filter by notification type
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        is_read_filter = request.args.get('is_read')
        type_filter = request.args.get('type')
        
        # Build query
        query = Notification.query.filter_by(user_id=int(current_user_id))
        
        # Apply filters
        if is_read_filter is not None:
            is_read = is_read_filter.lower() == 'true'
            query = query.filter_by(is_read=is_read)
        
        if type_filter:
            try:
                notif_type = NotificationType[type_filter.upper()]
                query = query.filter_by(type=notif_type)
            except KeyError:
                return error_response('Invalid notification type', None, 400)
        
        # Order by most recent
        query = query.order_by(Notification.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        notifications = [notif.to_dict() for notif in pagination.items]
        
        # Get unread count
        unread_count = Notification.query.filter_by(
            user_id=user_id_int,
            is_read=False
        ).count()
        
        return pagination_response(
            notifications,
            page,
            per_page,
            pagination.total,
            f'Notifications retrieved successfully (Unread: {unread_count})'
        )
    
    except Exception as e:
        return error_response(f'Failed to get notifications: {str(e)}', None, 500)


@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(notification_id):
    """Mark notification as read"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user_id_int = int(current_user_id)
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return error_response('Notification not found', None, 404)
        
        # Check ownership
        if notification.user_id != user_id_int:
            return error_response('You do not have permission', None, 403)
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()
        
        return success_response('Notification marked as read', None, 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to mark notification: {str(e)}', None, 500)


@notifications_bp.route('/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_as_read():
    """Mark all notifications as read"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user_id_int = int(current_user_id)
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        updated_count = Notification.query.filter_by(
            user_id=user_id_int,
            is_read=False
        ).update({
            'is_read': True,
            'read_at': datetime.utcnow()
        })
        
        db.session.commit()
        
        return success_response(
            f'Marked {updated_count} notifications as read',
            {'updated': updated_count},
            200
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to mark notifications: {str(e)}', None, 500)


@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """Delete a notification"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user_id_int = int(current_user_id)
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return error_response('Notification not found', None, 404)
        
        # Check ownership
        if notification.user_id != user_id_int:
            return error_response('You do not have permission', None, 403)
        
        db.session.delete(notification)
        db.session.commit()
        
        return success_response('Notification deleted', None, 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete notification: {str(e)}', None, 500)


@notifications_bp.route('/clear-all', methods=['DELETE'])
@jwt_required()
def clear_all_notifications():
    """Clear all read notifications"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user_id_int = int(current_user_id)
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        deleted_count = Notification.query.filter_by(
            user_id=user_id_int
        ).delete()
        
        db.session.commit()
        
        return success_response(
            f'Cleared {deleted_count} notifications',
            {'deleted': deleted_count},
            200
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to clear notifications: {str(e)}', None, 500)


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get count of unread notifications"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user_id_int = int(current_user_id)
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        unread_count = Notification.query.filter_by(
            user_id=user_id_int,
            is_read=False
        ).count()
        
        return success_response(
            'Unread count retrieved',
            {'unread_count': unread_count},
            200
        )
    
    except Exception as e:
        return error_response(f'Failed to get count: {str(e)}', None, 500)
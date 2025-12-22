from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models import User
from app.models.user import UserRole
from app.utils.decorators import role_required
from app.utils.responses import success_response, error_response, pagination_response
from app.utils.validators import validate_required_fields, validate_email
from app.models.assignment import Assignment
from app.models.activity_log import ActivityLog, ActivityType

users_bp = Blueprint('users', __name__)


@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users with pagination and filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        role = request.args.get('role')
        search = request.args.get('search', '').strip()
        
        print(f"DEBUG: get_users called. Page={page}, Role={role}")

        query = User.query.filter_by(is_bot=False)
        
        if role:
            query = query.filter_by(role=UserRole(role))
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                db.or_(
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.email.ilike(search_pattern)
                )
            )
        
        # Check raw count before pagination
        total_raw = query.count()
        print(f"DEBUG: User query total raw count: {total_raw}")

        query = query.order_by(User.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        users = [user.to_dict() for user in pagination.items]
        print(f"DEBUG: Returning {len(users)} users")
        
        return pagination_response(users, page, per_page, pagination.total)
    
    except Exception as e:
        print(f"DEBUG: Error in get_users: {str(e)}")
        return error_response(f'Failed to get users: {str(e)}', None, 500)


@users_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    """Create new user (Admin creates managers/employees, Manager creates employees)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return error_response('Current user not found', None, 404)
        
        data = request.get_json()
        
        # Debug logging
        print(f"Create user request from: {current_user.email} ({current_user.role})")
        print(f"Request data: {data}")
        
        # Validate required fields
        required = ['email', 'first_name', 'last_name', 'role']
        error = validate_required_fields(data, required)
        if error:
            return error_response(error, None, 400)
        
        email = data.get('email').lower().strip()
        role = data.get('role')
        
        # Check permissions: Manager can only create employees
        if current_user.role == UserRole.TEAM_LEADER and role != 'employee':
            return error_response('Team leaders can only create employee accounts', None, 403)
        
        # Validate email
        if not validate_email(email):
            return error_response('Invalid email format', None, 400)
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return error_response('Email already registered', None, 400)
        
        # Create user with temporary password
        temp_password = data.get('temp_password', 'Welcome@123')
        
        user = User(
            email=email,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            role=UserRole(role),
            skills=data.get('skills'),
            weekly_capacity=data.get('weekly_capacity', 40),
            is_active=True,
            is_verified=False  # User must set password on first login
        )
        user.set_password(temp_password)
        
        db.session.add(user)
        
        # Log activity
        ActivityLog.log_activity(
            user_id=current_user.id,
            activity_type=ActivityType.USER_CREATED,
            description=f"Created user {user.email} ({user.role})",
            request=request
        )
        
        db.session.commit()
        
        print(f"✅ User created: {user.email}")
        
        return success_response(
            'User created successfully',
            {
                'user': user.to_dict(),
                'temp_password': temp_password
            },
            201
        )
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating user: {str(e)}")
        return error_response(f'Failed to create user: {str(e)}', None, 500)


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user by ID"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', None, 404)
        
        return success_response('User retrieved', user.to_dict())
    
    except Exception as e:
        return error_response(f'Failed to get user: {str(e)}', None, 500)


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user (Admin or Self)"""
    try:
        current_user_id = get_jwt_identity()
        current_user_role = get_jwt()['role'] # Assuming role is in JWT, otherwise query user
        
        # Check permissions: Admin can update anyone, User can update self
        if str(current_user_id) != str(user_id):
             # If not self, must be admin
             # We need to verify admin role. 
             # Since we don't have the user object readily available from get_jwt_identity() only returning ID usually
             # We query the current user or trust a claim. Safest is to query.
             curr_user = User.query.get(current_user_id)
             if curr_user.role != UserRole.ADMIN:
                 return error_response('Permission denied', None, 403)

        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', None, 404)
        
        data = request.get_json()
        
        # Prevent non-admins from changing sensitive fields like role or is_active
        is_admin = (User.query.get(current_user_id).role == UserRole.ADMIN)

        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        
        # Admin-only fields
        if is_admin:
            if 'role' in data:
                user.role = UserRole(data['role'])
            if 'weekly_capacity' in data:
                user.weekly_capacity = data['weekly_capacity']
            if 'is_active' in data:
                user.is_active = data['is_active']
        
        if 'skills' in data:
            user.skills = data['skills']
        
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture']

        if 'email_notifications' in data:
            user.email_notifications = data['email_notifications']
            
        if 'push_notifications' in data:
            user.push_notifications = data['push_notifications']
        
        # Log activity
        ActivityLog.log_activity(
            user_id=get_jwt_identity(),
            activity_type=ActivityType.USER_UPDATED,
            description=f"Updated user {user.email}",
            request=request
        )
        
        db.session.commit()
        
        return success_response('User updated', user.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update user: {str(e)}', None, 500)


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        if user_id == current_user_id:
            return error_response('Cannot delete your own account', None, 400)
        
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', None, 404)
        
        # Log activity
        ActivityLog.log_activity(
            user_id=current_user_id,
            activity_type=ActivityType.USER_DELETED,
            description=f"Deleted user {user.email}",
            request=request
        )
        
        db.session.delete(user)
        db.session.commit()
        
        return success_response('User deleted', None)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete user: {str(e)}', None, 500)


@users_bp.route('/<int:user_id>/workload', methods=['GET'])
@jwt_required()
def get_user_workload(user_id):
    """Get user's current workload"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', None, 404)
        
        workload = Assignment.get_user_workload(user_id)
        available = user.weekly_capacity - workload
        utilization = (workload / user.weekly_capacity * 100) if user.weekly_capacity > 0 else 0
        
        return success_response('Workload retrieved', {
            'user_id': user_id,
            'weekly_capacity': user.weekly_capacity,
            'current_workload': workload,
            'available_hours': available,
            'utilization_percentage': round(utilization, 1),
            'is_overloaded': workload > user.weekly_capacity
        })
    
    except Exception as e:
        return error_response(f'Failed to get workload: {str(e)}', None, 500)


@users_bp.route('/requests', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_user_requests():
    """Get all pending user requests (is_active=False)"""
    try:
        # Filter for is_active=False. 
        # Note: Might need to distinguish between manually deactivated and pending requests.
        # But for now, we assume is_active=False implies pending or deactivated, and Admin can see all.
        users = User.query.filter_by(is_active=False).order_by(User.created_at.desc()).all()
        return success_response('Pending requests retrieved', [user.to_dict() for user in users])
    except Exception as e:
        return error_response(f'Failed to get requests: {str(e)}', None, 500)


@users_bp.route('/requests/<int:user_id>/approve', methods=['POST'])
@jwt_required()
@role_required('admin')
def approve_request(user_id):
    """Approve user request (Set is_active=True, is_verified=True)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', None, 404)
        
        user.is_active = True
        user.is_verified = True
        
        ActivityLog.log_activity(
            user_id=get_jwt_identity(),
            activity_type=ActivityType.USER_UPDATED,
            description=f"Approved user request for {user.email}",
            request=request
        )
        
        db.session.commit()
        return success_response('User approved successfully', user.to_dict())
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to approve user: {str(e)}', None, 500)


@users_bp.route('/requests/<int:user_id>/reject', methods=['POST'])
@jwt_required()
@role_required('admin')
def reject_request(user_id):
    """Reject user request (Delete user)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', None, 404)
            
        ActivityLog.log_activity(
            user_id=get_jwt_identity(),
            activity_type=ActivityType.USER_DELETED,
            description=f"Rejected user request for {user.email}",
            request=request
        )
        
        db.session.delete(user)
        db.session.commit()
        return success_response('User request rejected', None)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to reject user: {str(e)}', None, 500)
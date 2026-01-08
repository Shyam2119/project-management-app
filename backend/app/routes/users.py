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

def get_current_user_obj():
    uid = get_jwt_identity()
    # Convert to int since JWT identity is stored as string but user ID is integer
    return User.query.get(int(uid)) if uid else None

@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users with pagination and filters (Scoped to Company)"""
    try:
        current_user = get_current_user_obj()
        if not current_user:
            return error_response('User not found', None, 404)
        
        # Check if user has a company
        if not current_user.company_id:
            return error_response('User is not associated with a company', None, 403)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        role = request.args.get('role')
        search = request.args.get('search', '').strip()

        query = User.query.filter_by(is_bot=False, company_id=current_user.company_id)
        
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

        query = query.order_by(User.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        users = [user.to_dict() for user in pagination.items]
        
        return pagination_response(users, page, per_page, pagination.total)
    
    except Exception as e:
        return error_response(f'Failed to get users: {str(e)}', None, 500)


@users_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    """Create new user (Admin creates managers/employees, Manager creates employees)"""
    try:
        current_user = get_current_user_obj()
        
        if not current_user:
            return error_response('Current user not found', None, 404)
        
        # Check if user has a company
        if not current_user.company_id:
            return error_response('User is not associated with a company', None, 403)
        
        data = request.get_json()
        
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
        
        if current_user.role == UserRole.EMPLOYEE:
             return error_response('Employees cannot create accounts', None, 403)

        # Validate email
        if not validate_email(email):
            return error_response('Invalid email format', None, 400)
        
        # Check if user exists (Global check? Or Company check? Usually Emails are unique globally)
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
            is_verified=False,  # User must set password on first login
            company_id=current_user.company_id # Assign to same company
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
        return error_response(f'Failed to create user: {str(e)}', None, 500)


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user by ID (Scoped)"""
    try:
        current_user = get_current_user_obj()
        # Find user ensuring they are in the same company
        user = User.query.filter_by(id=user_id, company_id=current_user.company_id).first()
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
        current_user = get_current_user_obj()
        
        # Check if user exists in company
        user = User.query.filter_by(id=user_id, company_id=current_user.company_id).first()
        if not user:
            return error_response('User not found', None, 404)
            
        # Check permissions: Admin can update anyone in company, User can update self
        if current_user.id != user.id:
             if current_user.role != UserRole.ADMIN:
                 return error_response('Permission denied', None, 403)

        data = request.get_json()
        
        # Prevent non-admins from changing sensitive fields like role or is_active
        is_admin = (current_user.role == UserRole.ADMIN)

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
            user_id=current_user.id,
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
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        current_user = get_current_user_obj()
        
        if current_user.role != UserRole.ADMIN:
            return error_response('Permission denied', None, 403)
        
        if user_id == current_user.id:
            return error_response('Cannot delete your own account', None, 400)
        
        user = User.query.filter_by(id=user_id, company_id=current_user.company_id).first()
        if not user:
            return error_response('User not found', None, 404)
        
        # Log activity
        ActivityLog.log_activity(
            user_id=current_user.id,
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
        current_user = get_current_user_obj()
        user = User.query.filter_by(id=user_id, company_id=current_user.company_id).first()
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
def get_user_requests():
    """Get all pending user requests (is_active=False) - Scoped to Company"""
    try:
        current_user = get_current_user_obj()
        if current_user.role != UserRole.ADMIN:
             return error_response('Permission denied', None, 403)

        users = User.query.filter_by(is_active=False, company_id=current_user.company_id).order_by(User.created_at.desc()).all()
        return success_response('Pending requests retrieved', [user.to_dict() for user in users])
    except Exception as e:
        return error_response(f'Failed to get requests: {str(e)}', None, 500)


@users_bp.route('/requests/<int:user_id>/approve', methods=['POST'])
@jwt_required()
def approve_request(user_id):
    """Approve user request"""
    try:
        current_user = get_current_user_obj()
        if current_user.role != UserRole.ADMIN:
             return error_response('Permission denied', None, 403)

        user = User.query.filter_by(id=user_id, company_id=current_user.company_id).first()
        if not user:
            return error_response('User not found', None, 404)
        
        user.is_active = True
        user.is_verified = True
        
        ActivityLog.log_activity(
            user_id=current_user.id,
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
def reject_request(user_id):
    """Reject user request"""
    try:
        current_user = get_current_user_obj()
        if current_user.role != UserRole.ADMIN:
             return error_response('Permission denied', None, 403)
             
        user = User.query.filter_by(id=user_id, company_id=current_user.company_id).first()
        if not user:
            return error_response('User not found', None, 404)
            
        ActivityLog.log_activity(
            user_id=current_user.id,
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
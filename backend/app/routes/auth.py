from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User, UserRole
from app.models.activity_log import ActivityLog, ActivityType
from app.utils.responses import success_response, error_response
from app.utils.validators import validate_required_fields, validate_email, validate_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user (Request Credentials)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['email', 'password', 'first_name', 'last_name']
        error = validate_required_fields(data, required)
        if error:
            return error_response(error, None, 400)
        
        email = data.get('email').lower().strip()
        
        # Validate email
        if not validate_email(email):
            return error_response('Invalid email format', None, 400)
            
        # Check if user exists
        if User.query.filter_by(email=email).first():
            return error_response('Email already registered', None, 400)
            
        # Validate password
        password = data.get('password')
        password_error = validate_password(password)
        if password_error:
            return error_response(password_error, None, 400)

        # Create user (Pending Approval)
        user = User(
            email=email,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            role=UserRole.EMPLOYEE, # Default to Employee
            is_active=False,      # Pending Approval
            is_verified=False
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return success_response(
            'Registration successful. Please wait for administrator approval.',
            {'user': user.to_dict()},
            201
        )

    except Exception as e:
        db.session.rollback()
        return error_response(f'Registration failed: {str(e)}', None, 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['email', 'password']
        error = validate_required_fields(data, required)
        if error:
            return error_response(error, None, 400)
        
        email = data.get('email').lower().strip()
        password = data.get('password')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return error_response('Invalid email or password', None, 401)
        
        if not user.is_active:
            return error_response('Account is pending approval or deactivated', None, 403)
        
        # Generate JWT token with string identity
        access_token = create_access_token(identity=str(user.id))
        
        # Log login activity
        try:
            ActivityLog.log_activity(
                user_id=user.id,
                activity_type=ActivityType.USER_LOGIN,
                description=f"User {user.email} logged in",
                request=request
            )
            db.session.commit()
        except Exception as log_error:
            # In a read-only environment (like Vercel with SQLite), commits will fail.
            # We explicitly ignore this error to allow the login to proceed.
            print(f"Warning: Failed to answer activity log (likely read-only DB): {log_error}")
            db.session.rollback()
        
        return success_response(
            'Login successful',
            {
                'access_token': access_token,
                'user': user.to_dict()
            }
        )
    
    except Exception as e:
        return error_response(f'Login failed: {str(e)}', None, 500)


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return error_response('User not found', None, 404)
        
        return success_response('User retrieved', user.to_dict())
    
    except Exception as e:
        return error_response(f'Failed to get user: {str(e)}', None, 500)


@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return error_response('User not found', None, 404)
        
        data = request.get_json()
        
        # Validate required fields
        required = ['old_password', 'new_password']
        error = validate_required_fields(data, required)
        if error:
            return error_response(error, None, 400)
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        # Verify old password
        if not user.check_password(old_password):
            return error_response('Current password is incorrect', None, 400)
        
        # Validate new password
        password_error = validate_password(new_password)
        if password_error:
            return error_response(password_error, None, 400)
        
        # Update password
        user.set_password(new_password)
        
        # Mark user as verified (important for first-time password setup)
        user.is_verified = True
        
        # Log password change
        ActivityLog.log_activity(
            user_id=user.id,
            activity_type=ActivityType.PASSWORD_CHANGED,
            description="User changed password",
            request=request
        )
        
        db.session.commit()
        
        return success_response(
            'Password changed successfully',
            {'user': user.to_dict()}
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to change password: {str(e)}', None, 500)


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_token():
    """Refresh JWT token"""
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=str(current_user_id))
        
        return success_response(
            'Token refreshed',
            {'access_token': access_token}
        )
    
    except Exception as e:
        return error_response(f'Failed to refresh token: {str(e)}', None, 500)
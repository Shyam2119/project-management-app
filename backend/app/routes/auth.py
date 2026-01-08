from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User, UserRole
from app.models.company import Company
from app.models.activity_log import ActivityLog, ActivityType
from app.utils.responses import success_response, error_response
from app.utils.validators import validate_required_fields, validate_email, validate_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user - can create company or join existing one"""
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

        company_id = None
        company_name = data.get('company_name', '').strip() if data.get('company_name') else None
        existing_company = None
        company_created = False
        
        # Handle company creation or joining
        if company_name:
            # Check if company exists
            existing_company = Company.query.filter_by(name=company_name).first()
            
            if existing_company:
                # Join existing company (pending approval)
                company_id = existing_company.id
                is_active = False  # Requires admin approval
                is_verified = False
            else:
                # Create new company
                company = Company(name=company_name)
                db.session.add(company)
                db.session.flush()
                company_id = company.id
                company_created = True
                is_active = True  # Auto-active for new company creator
                is_verified = True
        else:
            # No company specified - user will be assigned later by admin
            is_active = False  # Requires admin approval
            is_verified = False

        # Create User
        user = User(
            email=email,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            role=UserRole.EMPLOYEE,  # Default to employee
            skills=data.get('skills'),
            weekly_capacity=data.get('weekly_capacity', 40),
            is_active=is_active,
            is_verified=is_verified,
            company_id=company_id
        )
        user.set_password(password)
        
        db.session.add(user)
        
        # Log activity if user is active
        if is_active:
            try:
                ActivityLog.log_activity(
                    user_id=user.id,
                    activity_type=ActivityType.USER_CREATED,
                    description=f"User {user.email} registered and created company",
                    request=request
                )
            except Exception:
                pass  # Ignore logging errors
        
        db.session.commit()
        
        message = 'Registration successful'
        if not is_active:
            if company_id:
                message = 'Registration successful. Your account is pending admin approval to join the company.'
            else:
                message = 'Registration successful. Your account is pending admin approval and company assignment.'
        elif company_created:
            message = 'Registration successful. Your company has been created and you can now login.'
        
        return success_response(
            message,
            {
                'user': user.to_dict(),
                'requires_approval': not is_active,
                'company_id': company_id
            },
            201
        )

    except Exception as e:
        db.session.rollback()
        return error_response(f'Registration failed: {str(e)}', None, 500)

@auth_bp.route('/register-company', methods=['POST'])
def register_company():
    """Register a new company and admin user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['company_name', 'email', 'password', 'first_name', 'last_name']
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

        # Create Company
        company = Company(name=data.get('company_name').strip())
        
        # Optionally set company credentials
        company_email = data.get('company_email', '').lower().strip() if data.get('company_email') else None
        company_password = data.get('company_password')
        
        if company_email:
            if not validate_email(company_email):
                return error_response('Invalid company email format', None, 400)
            # Check if company email is already taken
            if Company.find_by_company_email(company_email):
                return error_response('Company email already in use', None, 400)
            company.company_email = company_email
            if company_password:
                password_error = validate_password(company_password)
                if password_error:
                    return error_response(f'Company password: {password_error}', None, 400)
                company.set_company_password(company_password)
                company.company_login_enabled = True
        
        db.session.add(company)
        db.session.flush() # Flush to get company ID

        # Create Admin User linked to Company
        user = User(
            email=email,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            role=UserRole.ADMIN,  # Explicitly ADMIN
            is_active=True,       # Auto-active
            is_verified=True,     # Auto-verified
            company_id=company.id # Link to company
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        company_data = company.to_dict()
        company_data.pop('company_password_hash', None)
        
        return success_response(
            'Company registration successful. You can now login.',
            {
                'user': user.to_dict(),
                'company': company_data
            },
            201
        )

    except Exception as e:
        db.session.rollback()
        return error_response(f'Registration failed: {str(e)}', None, 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token - supports both individual and company-wide login"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['email', 'password']
        error = validate_required_fields(data, required)
        if error:
            return error_response(error, None, 400)
        
        email = data.get('email').lower().strip()
        password = data.get('password')
        user_id = data.get('user_id')  # Optional: for company login to select specific user
        
        # First, try company-wide login
        company = Company.find_by_company_email(email)
        if company and company.company_login_enabled and company.check_company_password(password):
            # Company login successful - get users for this company
            users = User.query.filter_by(
                company_id=company.id,
                is_active=True
            ).all()
            
            if not users:
                return error_response('No active users found for this company', None, 404)
            
            # If user_id is provided, use that user
            if user_id:
                user = User.query.filter_by(id=user_id, company_id=company.id, is_active=True).first()
                if not user:
                    return error_response('Invalid user selected', None, 400)
            else:
                # If only one user, auto-select; otherwise return list for selection
                if len(users) == 1:
                    user = users[0]
                else:
                    # Return list of users for selection
                    return success_response(
                        'Company login successful - select user',
                        {
                            'requires_user_selection': True,
                            'users': [u.to_dict() for u in users],
                            'company': company.to_dict()
                        },
                        200
                    )
            
            # Generate JWT token
            access_token = create_access_token(identity=str(user.id))
            
            # Log login activity
            try:
                ActivityLog.log_activity(
                    user_id=user.id,
                    activity_type=ActivityType.USER_LOGIN,
                    description=f"User {user.email} logged in via company credentials",
                    request=request
                )
                db.session.commit()
            except Exception as log_error:
                print(f"Warning: Failed to log activity: {log_error}")
                db.session.rollback()
            
            return success_response(
                'Login successful',
                {
                    'access_token': access_token,
                    'user': user.to_dict(),
                    'login_type': 'company'
                }
            )
        
        # Fallback to individual user login
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
            print(f"Warning: Failed to answer activity log: {log_error}")
            db.session.rollback()
        
        return success_response(
            'Login successful',
            {
                'access_token': access_token,
                'user': user.to_dict(),
                'login_type': 'individual'
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
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        # Convert to int since JWT identity is stored as string but user ID is integer
        try:
            user = User.query.get(int(current_user_id))
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        if not user:
            return error_response('User not found', None, 404)
        
        # Include company info
        user_data = user.to_dict()
        if user.company:
            user_data['company'] = {'id': user.company.id, 'name': user.company.name}
        elif user.company_id:
            # Company exists but relationship not loaded
            company = Company.query.get(user.company_id)
            if company:
                user_data['company'] = {'id': company.id, 'name': company.name}
            
        return success_response('User retrieved', user_data)
    
    except Exception as e:
        return error_response(f'Failed to get user: {str(e)}', None, 500)

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        # Convert to int since JWT identity is stored as string but user ID is integer
        user = User.query.get(int(current_user_id)) if current_user_id else None
        
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

@auth_bp.route('/company-settings', methods=['GET'])
@jwt_required()
def get_company_settings():
    """Get company settings (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user = User.query.get(int(current_user_id))
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        if not user:
            return error_response('User not found', None, 404)
        
        if user.role != UserRole.ADMIN:
            return error_response('Permission denied', None, 403)
        
        if not user.company_id:
            return error_response('User is not associated with a company', None, 404)
        
        # Get company - try relationship first, then direct query
        company = user.company if user.company else Company.query.get(user.company_id)
        if not company:
            return error_response('Company not found', None, 404)
        
        company_data = company.to_dict()
        # Don't expose password hash
        company_data.pop('company_password_hash', None)
        
        return success_response('Company settings retrieved', company_data)
    
    except Exception as e:
        return error_response(f'Failed to get company settings: {str(e)}', None, 500)

@auth_bp.route('/company-settings', methods=['PUT'])
@jwt_required()
def update_company_settings():
    """Update company settings (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        try:
            user = User.query.get(int(current_user_id))
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        if not user:
            return error_response('User not found', None, 404)
        
        if user.role != UserRole.ADMIN:
            return error_response('Permission denied', None, 403)
        
        if not user.company_id:
            return error_response('User is not associated with a company', None, 404)
        
        # Get company - try relationship first, then direct query
        company = user.company if user.company else Company.query.get(user.company_id)
        if not company:
            return error_response('Company not found', None, 404)
        
        data = request.get_json()
        
        # Update company email
        if 'company_email' in data:
            new_email = data.get('company_email', '').lower().strip() if data.get('company_email') else None
            if new_email:
                # Check if email is already taken by another company
                existing = Company.query.filter(
                    Company.company_email == new_email,
                    Company.id != company.id
                ).first()
                if existing:
                    return error_response('Company email already in use', None, 400)
                if not validate_email(new_email):
                    return error_response('Invalid email format', None, 400)
            company.company_email = new_email
        
        # Update company password
        if 'company_password' in data:
            new_password = data.get('company_password')
            if new_password:
                password_error = validate_password(new_password)
                if password_error:
                    return error_response(password_error, None, 400)
                company.set_company_password(new_password)
            else:
                company.set_company_password(None)
        
        # Update company login enabled status
        if 'company_login_enabled' in data:
            company.company_login_enabled = bool(data.get('company_login_enabled'))
        
        # Log activity
        ActivityLog.log_activity(
            user_id=user.id,
            activity_type=ActivityType.USER_UPDATED,
            description="Updated company settings",
            request=request
        )
        
        db.session.commit()
        
        company_data = company.to_dict()
        company_data.pop('company_password_hash', None)
        
        return success_response('Company settings updated', company_data)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update company settings: {str(e)}', None, 500)
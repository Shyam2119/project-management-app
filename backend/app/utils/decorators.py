from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User, UserRole


def role_required(*roles):
    """Decorator to check if user has required role"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            # Convert to int since JWT identity is stored as string but user ID is integer
            user = User.query.get(int(current_user_id)) if current_user_id else None
            
            if not user:
                return jsonify({
                    'status': 'error',
                    'message': 'User not found'
                }), 404
            
            # Convert role to string for comparison
            user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
            
            if user_role not in roles:
                return jsonify({
                    'status': 'error',
                    'message': 'Insufficient permissions'
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator
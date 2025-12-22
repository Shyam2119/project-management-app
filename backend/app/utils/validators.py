import re

def validate_required_fields(data, required_fields):
    """Validate that all required fields are present and not empty"""
    if not data:
        return 'Request body is required'
    
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        return f'Missing required fields: {", ".join(missing_fields)}'
    
    return None

def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if not password:
        return 'Password is required'
    
    if len(password) < 6:
        return 'Password must be at least 6 characters long'
    
    return None

def validate_phone(phone):
    """Validate phone number format (optional)"""
    if not phone:
        return True
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it's all digits and reasonable length
    if not cleaned.isdigit() or len(cleaned) < 10 or len(cleaned) > 15:
        return False
    
    return True
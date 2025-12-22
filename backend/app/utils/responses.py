from flask import jsonify

def success_response(message, data=None, status_code=200):
    """Generate a success response"""
    response = {
        'status': 'success',
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code


def error_response(message, errors=None, status_code=400):
    """Generate an error response"""
    response = {
        'status': 'error',
        'message': message
    }
    
    if errors is not None:
        response['errors'] = errors
    
    return jsonify(response), status_code


def pagination_response(items, page, per_page, total, message="Success"):
    """Generate a paginated response"""
    return jsonify({
        'status': 'success',
        'message': message,
        'data': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    }), 200
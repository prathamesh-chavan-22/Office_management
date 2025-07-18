from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin']:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def hr_required(f):
    """Decorator to require HR or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'HR access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_json_data(required_fields):
    """Decorator to validate JSON data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'JSON data is required'}), 400
            
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'error': f'{field} is required'}), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def paginate_query(query, page, per_page):
    """Helper function to paginate query results"""
    try:
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 10
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    except ValueError:
        return None

def hr_or_admin_required(f):
    """Decorator to require HR or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['hr', 'admin']:
            return jsonify({'error': 'HR or admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def allowed_file(filename, allowed_extensions):
    """Check if a file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

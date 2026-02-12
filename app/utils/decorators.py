from functools import wraps
from flask import request, current_app, g
from app.utils.response import error_response
from app.models.user import User, UserRole
from flask_jwt_extended import jwt_required as jwt_required_flask_jwt, get_jwt_identity, get_jwt

def jwt_required(f):
    @wraps(f)
    @jwt_required_flask_jwt() # Use the decorator from flask_jwt_extended
    def decorated_function(*args, **kwargs):
        # Get the identity of the current user, which is the user_id
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            # This should ideally not happen if the token is valid and user exists
            return error_response("User not found or token invalid.", 401)
        
        g.current_user = user # Store the user object in Flask's global context
        # You might not need to pass it as kwargs['current_user'] anymore if routes access g.current_user
        # kwargs['current_user'] = user 
        
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        @jwt_required_flask_jwt() # Ensure JWT is present and valid
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            user_id = get_jwt_identity() # Get user_id to fetch user object
            
            user = User.query.get(user_id)
            if not user or user_role not in roles:
                return error_response("User does not have the required permissions.", 403)
            
            g.current_user = user # Ensure user object is available
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    @jwt_required_flask_jwt() # Ensure JWT is present and valid
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        user_role = claims.get('role')
        user_id = get_jwt_identity() # Get user_id to fetch user object

        user = User.query.get(user_id)
        if not user or user_role != UserRole.ADMIN.value:
            return error_response("Administrator access required.", 403)
        
        g.current_user = user # Ensure user object is available
        return f(*args, **kwargs)
    return decorated_function
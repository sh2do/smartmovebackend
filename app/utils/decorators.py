import jwt
from functools import wraps
from flask import request, current_app, g
from app.utils.response import error_response
from app.models.user import User, UserRole
import os # Import os

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return error_response("Authentication Token is missing!", 401)

        try:
            current_app.logger.debug(f"SECRET_KEY used for decode: {current_app.config.get('SECRET_KEY')}")
            payload = jwt.decode(token, os.environ.get('SECRET_KEY').encode('utf-8'), algorithms=["HS256"]) # Use os.environ directly for SECRET_KEY
            user_id = payload['sub'] # CORRECTED: Use 'sub' instead of 'user_id'
            user = User.query.get(user_id)
            if not user:
                return error_response("User not found!", 401)
            g.current_user = user # Store the whole user object in g
        except jwt.ExpiredSignatureError:
            return error_response("Token is expired!", 401)
        except jwt.InvalidTokenError:
            return error_response("Token is invalid!", 401)
        except KeyError:
            # If 'sub' is missing, it's also an invalid token
            return error_response("Token is missing user ID!", 401)

        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This decorator should be stacked AFTER @jwt_required
            if not hasattr(g, 'current_user'):
                return error_response("Authentication required.", 401)
            
            user = g.current_user
            # .value gets the string representation of the enum, e.g., 'customer'
            if user.role.value not in roles:
                return error_response("User does not have the required permissions.", 403)

            # Pass the user object to the decorated function
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This decorator should be stacked AFTER @jwt_required
        if not hasattr(g, 'current_user'):
            return error_response("Authentication required. Use @jwt_required before @admin_required.", 401)
        
        user = g.current_user
        if user.role != UserRole.ADMIN:
            return error_response("Administrator access required.", 403)
        
        # Pass the user object to the decorated function
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    return decorated_function
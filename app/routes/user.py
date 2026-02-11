from flask import Blueprint, request, current_app
from app.models.user import User # Import User model for validation
from app.utils.response import success, error_response
from app.utils.decorators import jwt_required

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/profile', methods=['GET'])
@jwt_required
def get_profile(current_user):
    return success(current_user.to_dict())

@user_bp.route('/profile', methods=['PUT'])
@jwt_required
def update_profile(current_user):
    data = request.get_json()    
    try:
        # Whitelist allowed fields for update.
        # Based on app/models/user.py, 'email' is the only non-system, non-password, non-role field.
        # Add other fields like 'first_name', 'last_name', 'phone_number' if they exist in User model.
        allowed_fields = ['email'] 
        
        for key, value in data.items():
            if key in allowed_fields:
                # Specific validation for 'email' to handle uniqueness and format
                if key == 'email':
                    if User.query.filter_by(email=value).first() and current_user.email != value:
                        raise ValueError("Email address already in use.")
                    # Basic email format check
                    if not '@' in value or not '.' in value:
                         raise ValueError("Invalid email format.")
                setattr(current_user, key, value)
            else:
                current_app.logger.warning(f"Attempted to update disallowed field: {key}") # Log attempts to update disallowed fields

        current_user.save()
        return success(current_user.to_dict())
    except ValueError as e: # Catch specific validation errors
        return error_response(str(e), 400)
    except Exception as e: # General error, allow to propagate to global handler for 500
        current_app.logger.error(f"Error updating user profile: {e}")
        raise # Re-raise to be caught by global 500 handler

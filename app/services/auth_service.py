from app.models.user import User, UserRole
from app.extensions import db
from flask import current_app
from flask_jwt_extended import create_access_token

class AuthService:
    @staticmethod
    def register_user(data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')
        role_str = data.get('role', 'customer')
        
        # Safely convert role string to UserRole enum
        try:
            role = UserRole(role_str)
        except ValueError:
            # Default to CUSTOMER if an invalid role is provided
            role = UserRole.CUSTOMER

        if User.query.filter_by(email=email).first():
            raise ValueError("User with this email already exists.") # Changed Exception to ValueError

        new_user = User(first_name=first_name, last_name=last_name, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Create the tokens we will be sending back to the user
            additional_claims = {"role": user.role.value}
            access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
            return {'token': access_token, 'user': user.to_dict()}
        raise ValueError("Invalid email or password.")

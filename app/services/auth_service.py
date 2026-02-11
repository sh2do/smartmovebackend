from app.models.user import User, UserRole
from app.extensions import db
from flask import current_app
import jwt
import datetime
import os # Add import os

class AuthService:
    @staticmethod
    def register_user(data):
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
            raise Exception("User with this email already exists.")

        new_user = User(email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
                'sub': user.id,
                'role': user.role.value
            }
            current_app.logger.debug(f"SECRET_KEY used for encoding: {current_app.config.get('SECRET_KEY')}")
            token = jwt.encode(
                payload,
                os.environ.get('SECRET_KEY').encode('utf-8'), # Use os.environ directly for SECRET_KEY
                algorithm='HS256'
            )
            return token
        raise Exception("Invalid email or password.")

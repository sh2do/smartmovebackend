from flask import Blueprint, request
from app.services.auth_service import AuthService
from app.utils.response import success, error_response
from app.utils.validators import validate_request

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
@validate_request('email', 'password')
def register():
    data = request.get_json()
    try:
        user = AuthService.register_user(data)
        return success(user.to_dict(), 201)
    except Exception as e:
        return error_response(str(e))

@auth_bp.route('/login', methods=['POST'])
@validate_request('email', 'password')
def login():
    data = request.get_json()
    try:
        token = AuthService.login_user(data['email'], data['password'])
        return success({'token': token})
    except Exception as e:
        return error_response(str(e), 401)

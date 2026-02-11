from app.services.auth_service import AuthService
from faker import Faker
from app.models.user import User, UserRole # Added missing import for UserRole

fake = Faker()


def test_auth_service_registration(test_app, init_database):
    with test_app.app_context():
        email = fake.email()
        password = fake.password()

        user_data = {"email": email, "password": password, "password_confirmation": password, "role": "customer"}
        user_obj = AuthService.register_user(user_data)

        assert user_obj is not None
        assert isinstance(user_obj, User)
        assert user_obj.email == email
        assert user_obj.role == UserRole.CUSTOMER

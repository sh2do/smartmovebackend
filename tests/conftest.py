import pytest
from app import create_app
from app.extensions import db
from app.models.user import User, UserRole # Import User and UserRole
import os

@pytest.fixture(scope='session')
def test_app():
    """
    Fixture to create and configure a Flask application for testing.
    Uses an in-memory SQLite database.
    """
    # Use a different configuration for testing
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'test_secret_key' # Needed for JWT/Bcrypt
        # Dummy M-Pesa configuration for testing
        MPESA_BASE_URL = 'http://test.mpesa.url'
        MPESA_CONSUMER_KEY = 'test_key'
        MPESA_CONSUMER_SECRET = 'test_secret'
        MPESA_SHORTCODE = '600000'
        MPESA_PASSKEY = 'test_passkey'
        CALLBACK_URL = 'http://test.callback.url' # Changed key name
        MPESA_CALLBACK_URL = 'http://test.callback.url'

    app = create_app(TestConfig)

    with app.app_context():
        # Create all tables
        db.create_all()
        yield app
        # Drop all tables after tests
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(test_app):
    """
    Fixture for a test client.
    """
    return test_app.test_client()

@pytest.fixture(scope='function')
def init_database(test_app):
    """
    Fixture to clear and re-create database tables for each test function.
    Ensures a clean state for each test.
    """
    with test_app.app_context():
        db.drop_all()
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def sample_user(init_database):
    """
    Fixture to create and return a sample user.
    """
    user = User(email='test@example.com', role=UserRole.CUSTOMER)
    user.set_password('password123')
    init_database.add(user) # Use session directly
    init_database.commit()  # Use session directly
    # Explicitly fetch the user again to ensure it's loaded into the session
    # that subsequent queries will use.
    reloaded_user = User.query.filter_by(email='test@example.com').first()
    return reloaded_user

@pytest.fixture(scope='session')
def app(test_app):
    yield test_app

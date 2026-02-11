import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


def get_database_uri():
    """Get database URI with postgres:// to postgresql:// conversion for SQLAlchemy 1.4+."""
    database_url = os.environ.get('DATABASE_URL')
    if database_url is None:
        # Default to SQLite for local development
        return 'sqlite:///' + os.path.join(basedir, '..', 'app.db')
    if database_url.startswith('postgres://'):
        # Render, Heroku, Railway use postgres:// but SQLAlchemy requires postgresql://
        return database_url.replace('postgres://', 'postgresql://', 1)
    return database_url


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if SECRET_KEY is None:
        raise ValueError("SECRET_KEY environment variable not set. Please set it for production readiness.")

    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis/Celery configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or REDIS_URL
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or REDIS_URL

    # MPESA Configuration
    MPESA_BASE_URL = os.environ.get('MPESA_BASE_URL')
    MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY')
    MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET')
    MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE')
    MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY')
    CALLBACK_URL = os.environ.get('CALLBACK_URL')

    # Google Maps Configuration
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

    # Validate critical MPESA configurations
    if any(v is None for v in [MPESA_BASE_URL, MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, MPESA_SHORTCODE, MPESA_PASSKEY, CALLBACK_URL, GOOGLE_MAPS_API_KEY]):
        raise ValueError("One or more critical API environment variables are not set. Please check MPESA and GOOGLE_MAPS configurations.")


"""
Tests for cache headers on static file responses.

Feature: backend-frontend-merge
Validates: Requirements 1.4
"""
import pytest
import os
import tempfile
from app import create_app
from app.extensions import db


@pytest.fixture
def app_with_static_files():
    """
    Create a test app with a temporary static folder containing test files.
    """
    # Create temporary directory for static files
    temp_dir = tempfile.mkdtemp()
    
    # Create test static files
    index_html = os.path.join(temp_dir, 'index.html')
    with open(index_html, 'w') as f:
        f.write('<html><body>Test</body></html>')
    
    # Create hashed asset (simulating Vite build output)
    hashed_js = os.path.join(temp_dir, 'assets')
    os.makedirs(hashed_js, exist_ok=True)
    with open(os.path.join(hashed_js, 'index-DxN8sj2K.js'), 'w') as f:
        f.write('console.log("test");')
    
    # Create non-hashed asset
    with open(os.path.join(hashed_js, 'logo.png'), 'w') as f:
        f.write('fake image data')
    
    # Configure test app with custom static folder
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'test_secret_key'
    
    # Create app with custom static folder
    app = create_app(TestConfig)
    app.static_folder = temp_dir
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    # Cleanup temp directory
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_index_html_no_cache(app_with_static_files):
    """
    Test that index.html has no-cache headers.
    """
    client = app_with_static_files.test_client()
    
    # Request index.html directly
    response = client.get('/index.html')
    
    assert response.status_code == 200
    assert 'Cache-Control' in response.headers
    cache_control = response.headers['Cache-Control']
    assert 'no-cache' in cache_control
    assert 'no-store' in cache_control
    assert 'must-revalidate' in cache_control


def test_hashed_asset_long_cache(app_with_static_files):
    """
    Test that hashed assets (e.g., index-DxN8sj2K.js) have long cache duration.
    """
    client = app_with_static_files.test_client()
    
    # Request hashed JS file
    response = client.get('/assets/index-DxN8sj2K.js')
    
    assert response.status_code == 200
    assert 'Cache-Control' in response.headers
    assert 'max-age=31536000' in response.headers['Cache-Control']
    assert 'immutable' in response.headers['Cache-Control']


def test_non_hashed_asset_short_cache(app_with_static_files):
    """
    Test that non-hashed assets have short cache duration.
    """
    client = app_with_static_files.test_client()
    
    # Request non-hashed asset
    response = client.get('/assets/logo.png')
    
    assert response.status_code == 200
    assert 'Cache-Control' in response.headers
    assert 'max-age=3600' in response.headers['Cache-Control']


def test_root_path_no_cache(app_with_static_files):
    """
    Test that root path (/) serving index.html has no-cache headers.
    """
    client = app_with_static_files.test_client()
    
    # Request root path
    response = client.get('/')
    
    assert response.status_code == 200
    assert 'Cache-Control' in response.headers
    assert 'no-cache' in response.headers['Cache-Control']


def test_api_routes_no_cache_headers(app_with_static_files):
    """
    Test that API routes don't get cache headers (only static files).
    """
    client = app_with_static_files.test_client()
    
    # Request API endpoint
    response = client.get('/api/auth/login')
    
    # API routes should not have cache headers for static files
    # (they may have other cache headers, but not the ones we set for static files)
    if 'Cache-Control' in response.headers:
        # If present, it shouldn't be the long cache we set for hashed assets
        assert 'max-age=31536000' not in response.headers.get('Cache-Control', '')


def test_health_check_no_cache_headers(app_with_static_files):
    """
    Test that health check endpoints don't get static file cache headers.
    """
    client = app_with_static_files.test_client()
    
    # Request health check
    response = client.get('/health')
    
    assert response.status_code == 200
    # Health checks should not have long cache headers
    if 'Cache-Control' in response.headers:
        assert 'max-age=31536000' not in response.headers.get('Cache-Control', '')

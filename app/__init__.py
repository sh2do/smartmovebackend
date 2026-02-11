import os
from flask import Flask, jsonify
from app.config import Config
from app.extensions import db, migrate, cors, bcrypt
from app.utils.errors import register_error_handlers

# Import models to ensure they are registered with SQLAlchemy MetaData
from app.models.user import User
from app.models.address import Address
from app.models.booking import Booking
from app.models.mover import Mover
from app.models.notification import Notification
from app.models.quote import Quote
from app.models.review import Review
from app.models.inventory import Inventory
from app.models.chat import Message


def create_app(config_class=Config):
    # Configure static folder for serving built React frontend
    # Path resolution: find build directory relative to app root
    app_root = os.path.dirname(os.path.abspath(__file__))
    static_folder = os.path.join(app_root, '..', 'build')
    static_url_path = '/static'
    
    app = Flask(__name__,
                static_folder=static_folder,
                static_url_path=static_url_path)
    app.config.from_object(config_class)
    
    # Log warning if static folder doesn't exist
    if not os.path.exists(app.static_folder):
        app.logger.warning(
            f"Static folder not found: {app.static_folder}. "
            "Run 'bash scripts/build_frontend.sh' to build the frontend."
        )

    import logging
    app.logger.setLevel(logging.DEBUG)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configure CORS based on environment
    flask_env = os.environ.get('FLASK_ENV', 'production')
    if flask_env == 'development':
        # Development: Allow requests from Vite dev server
        cors.init_app(app, resources={
            r"/api/*": {
                "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True
            }
        })
        app.logger.info("CORS configured for development mode with origins: localhost:5173, localhost:5174, 127.0.0.1:5173, 127.0.0.1:5174")
    else:
        # Production: Allow same-origin or specific production origins
        # In production with merged deployment, CORS is not strictly needed (same-origin)
        # but we configure it to allow flexibility for future CDN or subdomain usage
        # Production: Use explicit origins from env var, fallback to safe default or disable
        production_origins_str = os.environ.get('CORS_ORIGINS')
        production_origins = production_origins_str.split(',') if production_origins_str else [] # If not set, default to empty list (no origins)
        
        # NOTE: If your frontend is served from the same domain as the backend,
        # CORS might not be strictly needed for API calls. If different domains,
        # ensure CORS_ORIGINS environment variable is set to a comma-separated list of trusted frontend URLs.
        if production_origins:
            cors.init_app(app, resources={
                r"/api/*": {
                    "origins": production_origins,
                    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                    "allow_headers": ["Content-Type", "Authorization"],
                    "supports_credentials": False
                }
            })
            app.logger.info(f"CORS configured for production mode with origins: {production_origins}")
        else:
            app.logger.info("CORS not explicitly configured for production mode (no CORS_ORIGINS env var found), relying on same-origin policy or default browser behavior.")
            # Optionally, you could still initialize CORS with specific non-wildcard settings here
            # or raise an error if CORS_ORIGINS is critical for this setup.
    
    bcrypt.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.booking import booking_bp
    from app.routes.mover import mover_bp
    from app.routes.review import review_bp
    from app.routes.admin import admin_bp
    from app.routes.chat import chat_bp
    from app.routes.inventory import inventory_bp
    from app.routes.maps import maps_bp
    from app.routes.notification import notification_bp
    from app.routes.payments import payment_bp # Import payment_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(booking_bp, url_prefix='/api/bookings')
    app.register_blueprint(mover_bp, url_prefix='/api/movers')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(chat_bp, url_prefix='/api/chats')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(maps_bp, url_prefix='/api/maps')
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')

    # Register error handlers
    register_error_handlers(app)

    # Health check endpoint for Render/load balancers
    @app.route('/health', methods=['GET'])
    def health_check():
        """Basic health check - returns 200 if app is running."""
        return jsonify({"status": "ok"}), 200

    @app.route('/health/ready', methods=['GET'])
    def readiness_check():
        """Readiness check - verifies database connectivity."""
        try:
            db.session.execute(db.text('SELECT 1'))
            return jsonify({"status": "ready", "database": "connected"}), 200
        except Exception as e:
            return jsonify({"status": "not ready", "database": "disconnected", "error": str(e)}), 503

    # Add cache headers for static files
    @app.after_request
    def add_cache_headers(response):
        """
        Add cache-control headers to static file responses.
        
        Cache strategy:
        - Hashed assets (JS, CSS with hash in filename): 1 year cache
        - index.html: no-cache (always revalidate)
        - Other static files: short cache (1 hour)
        
        This ensures optimal performance while allowing immediate updates
        when new versions are deployed.
        """
        from flask import request
        import re
        
        # Only add cache headers for successful responses
        if response.status_code != 200:
            return response
        
        path = request.path
        
        # Check if this is a static file request
        is_static = (
            path.startswith('/static/') or 
            path.endswith('.js') or 
            path.endswith('.css') or 
            path.endswith('.html') or
            path.endswith('.png') or 
            path.endswith('.jpg') or 
            path.endswith('.jpeg') or 
            path.endswith('.gif') or 
            path.endswith('.svg') or 
            path.endswith('.ico') or
            path.endswith('.woff') or
            path.endswith('.woff2') or
            path.endswith('.ttf') or
            path.endswith('.eot')
        )
        
        if is_static:
            # Check if this is index.html or root path
            if 'index.html' in path or path == '/' or (path and not '.' in path.split('/')[-1]):
                # No cache for index.html and SPA routes
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            else:
                # Check if filename contains a hash (e.g., main.abc123.js)
                # Vite typically generates files like: index-DxN8sj2K.js
                filename = path.split('/')[-1]
                has_hash = re.search(r'[.-][a-f0-9]{8,}[.-]', filename) or re.search(r'-[A-Za-z0-9_-]{8,}\.(js|css)', filename)
                
                if has_hash:
                    # Long cache for hashed assets (1 year)
                    response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
                else:
                    # Short cache for other static files (1 hour)
                    response.headers['Cache-Control'] = 'public, max-age=3600'
        
        return response

    # SPA fallback route - must be registered last to avoid overriding other routes
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_spa(path):
        """
        Serve the React SPA for all non-API routes.
        
        This catch-all route handles:
        - Root path (/)
        - All SPA routes (e.g., /dashboard, /bookings/123)
        - Returns index.html for React Router to handle
        
        Route priority:
        1. Health check routes (/health, /health/ready)
        2. API routes (/api/*)
        3. Static files (/static/*)
        4. SPA fallback (everything else)
        
        Args:
            path: The requested path
            
        Returns:
            The index.html file or 404 if static folder doesn't exist
        """
        # Skip API routes - let them 404 naturally if not found
        if path.startswith('api/'):
            return jsonify({"error": "API endpoint not found"}), 404
        
        # Check if the path corresponds to a static file
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return app.send_static_file(path)
        
        # Check if static folder exists
        if not os.path.exists(app.static_folder):
            return jsonify({
                "error": "Frontend not built",
                "message": "Run 'bash scripts/build_frontend.sh' to build the frontend."
            }), 500
        
        # Check if index.html exists
        index_path = os.path.join(app.static_folder, 'index.html')
        if not os.path.exists(index_path):
            return jsonify({
                "error": "index.html not found",
                "message": "Frontend build may be incomplete."
            }), 500
        
        # Serve index.html for SPA routing
        return app.send_static_file('index.html')

    return app

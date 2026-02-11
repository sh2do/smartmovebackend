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
    app = Flask(__name__)
    app.config.from_object(config_class)

    import logging
    app.logger.setLevel(logging.DEBUG)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
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

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(mover_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(maps_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(payment_bp) # Register payment_bp

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

    return app

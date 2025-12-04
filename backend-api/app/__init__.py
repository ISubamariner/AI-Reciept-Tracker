# app/__init__.py (Updated with Blueprint Registration)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS # <-- New Import
from config import Config

# Initialize extensions outside of the app factory
db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    
    
    
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}}) # <-- Allow all origins for API endpoints
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    
    # Add error handlers
    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        app.logger.error(f"Unhandled exception: {e}")
        app.logger.error(traceback.format_exc())
        return {'error': 'Internal server error', 'message': str(e)}, 500
    
    # Import models so they are recognized by the ORM
    from app import models 
    
    # --- Register Blueprints ---
    from app.auth.routes import bp as auth_bp
    # All routes in auth_bp will be prefixed with /api/auth
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.receipts.routes import bp as receipts_bp
    app.register_blueprint(receipts_bp, url_prefix='/api/receipts')
    # -------------------------

    return app
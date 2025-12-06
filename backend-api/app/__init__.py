# app/__init__.py (Updated with Blueprint Registration)

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS # <-- New Import
from flask_swagger_ui import get_swaggerui_blueprint
from config import Config
from datetime import datetime
import os

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
    
    # Initialize MongoDB
    from app.mongo_connector import init_mongo_app
    init_mongo_app(app)
    
    # Initialize currency system and scheduler (only if tables exist)
    with app.app_context():
        try:
            # Check if currency tables exist before initializing
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'currencies' in tables and 'exchange_rates' in tables:
                # Initialize currencies on first run
                try:
                    from app.services.currency_service import CurrencyService
                    CurrencyService.initialize_currencies()
                    app.logger.info("Currency system initialized successfully")
                except Exception as e:
                    app.logger.warning(f"Currency initialization warning: {e}")
                
                # Initialize scheduler for exchange rate updates
                try:
                    from app.services.scheduler_service import SchedulerService
                    SchedulerService.initialize(app)
                    app.logger.info("Scheduler initialized successfully")
                except ImportError as e:
                    app.logger.warning(f"Scheduler not available (APScheduler not installed): {e}")
                except Exception as e:
                    app.logger.warning(f"Scheduler initialization failed: {e}")
            else:
                app.logger.info("Currency tables not found. Run migration script to enable currency features.")
        except Exception as e:
            app.logger.warning(f"Currency system check failed: {e}")
    
    # --- Register Blueprints ---
    from app.auth.routes import bp as auth_bp
    # All routes in auth_bp will be prefixed with /api/auth
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.receipts.routes import bp as receipts_bp
    app.register_blueprint(receipts_bp, url_prefix='/api/receipts')
    
    from app.users.routes import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/api')
    
    from app.audit.routes import bp as audit_bp
    app.register_blueprint(audit_bp, url_prefix='/api')
    
    # Register currency blueprint (only if dependencies are available)
    try:
        from app.currency import currency_bp
        app.register_blueprint(currency_bp, url_prefix='/api/currency')
        app.logger.info("Currency endpoints registered successfully")
    except ImportError as e:
        app.logger.warning(f"Currency endpoints not available: {e}")
    except Exception as e:
        app.logger.error(f"Failed to register currency endpoints: {e}")
    # -------------------------
    
    # --- Swagger UI Configuration ---
    SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI
    API_URL = '/swagger.json'  # URL for OpenAPI spec
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "AI Receipt Tracker API",
            'docExpansion': 'list',
            'defaultModelsExpandDepth': 3
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Serve the swagger.json file
    @app.route('/swagger.json')
    def swagger_spec():
        import json
        swagger_path = os.path.join(app.root_path, '..', 'swagger.json')
        with open(swagger_path, 'r') as f:
            spec = json.load(f)
        return jsonify(spec)
    # --------------------------------
    
    # --- Health Check Endpoint ---
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint to verify API is running"""
        from app.mongo_connector import MongoDBConnector
        
        # Check MongoDB status
        mongodb_status = 'disconnected'
        try:
            mongo_db = MongoDBConnector.get_db()
            if mongo_db is not None:
                # Try a simple ping
                mongo_db.client.admin.command('ping')
                mongodb_status = 'connected'
        except Exception as e:
            app.logger.warning(f"MongoDB health check failed: {e}")
            mongodb_status = 'disconnected'
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0',
            'services': {
                'database': 'connected' if db.engine else 'disconnected',
                'mongodb': mongodb_status,
                'gemini_api': 'configured' if Config.GEMINI_API_KEY else 'not configured'
            }
        }), 200
    # -----------------------------

    return app
# app/__init__.py (Updated with Receipts Blueprint Registration)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    
    from app import models 
    
    # --- Register Blueprints ---
    from app.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # NEW: Register the Receipts Blueprint
    from app.receipts.routes import bp as receipts_bp
    app.register_blueprint(receipts_bp, url_prefix='/api/receipts')
    # -------------------------

    return app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    """
    Initializes Flask app, configures it, registers blueprints,
    and creates DB tables.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    from .routes import auth_bp
    app.register_blueprint(auth_bp)

    # Import models so tables are created
    from . import models

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app   # ✅ sirf ye line

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    """
    The `create_app` function initializes a Flask application, configures it, registers blueprints,
    initializes the database, creates database tables, and returns the application instance.
    :return: The function `create_app()` is returning an instance of the Flask application after
    initializing the app with configurations, registering blueprints, initializing the database,
    creating database tables, and setting up the application context.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    
    from .routes import auth_bp
    app.register_blueprint(auth_bp)

   
    from . import models

    with app.app_context():
        db.create_all()

    return app

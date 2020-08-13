import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from flask_cors import CORS

from config import config, s3_bucket, ACCESS_KEY, SECRET_KEY

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('CONFIG', 'development')
    
    app = Flask(__name__)
    app.config['CORS_HEADERS'] = 'Content-Type'
    # CORS(app, resources={r"*": {"origins": "http://localhost:3000"}})
    CORS(app)
    app.config.from_object(config[config_name])

    db.init_app(app)
    from .models import User, Trip, Location, Photo
    migrate.init_app(app, db)
    
    from app.api.v1 import auth_bp, trip_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(trip_bp)

    return app

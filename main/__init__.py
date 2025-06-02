from flask import Flask
from .database import db
from .routes import blueprint_main

def create_app(uri="sqlite:///analysis_data.db"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.register_blueprint(blueprint_main)
    
    return app

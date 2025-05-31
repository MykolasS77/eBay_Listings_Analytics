from flask import Flask
from flask_login import LoginManager
from .database import db
from .routes import blueprint_main

def create_app(uri="sqlite:///analysis_data.db"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config['SECRET_KEY'] = 'your_secret_key'
    # login_manager = LoginManager()
    # login_manager.init_app(app)
    # @login_manager.user_loader
    

    # def load_user(user_id):
    #     return ClientAccount.query.get(int(user_id))
    app.register_blueprint(blueprint_main)
    
    return app

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main application file
"""

import os
import sys
from flask import Flask, render_template
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

# Import blueprints and extensions
from database import db
from app.auth import login_manager
from app.admin import admin_bp
from app.api import api_bp
from app.auth import auth_bp
from app.chat import chat_bp
from models.user import User

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, instance_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance'))

    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY') or 'dev_secret_key',
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(app.instance_path, 'hsa_chatbot.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)

    # A simple route for the index page
    @app.route('/')
    def index():
        return render_template('index.html')

    with app.app_context():
        db.create_all()
        create_admin_user()

    return app

def create_admin_user():
    """Create admin user if not exists"""
    from models.user import User
    from database import db
    
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin')
    
    if not User.query.filter_by(username=admin_username).first():
        admin_user = User(
            username=admin_username,
            email='admin@example.com',
            full_name='Admin User',
            role='admin',
            is_active=True
        )
        admin_user.set_password(admin_password)
        db.session.add(admin_user)
        db.session.commit()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HSA Chatbot - Flask Application
Chatbot hỗ trợ thí sinh tham dự kỳ thi HSA của Đại học Quốc gia Hà Nội
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'hsa-chatbot-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///hsa_chatbot.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize extensions
from database import db
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models
from models.user import User
from models.document import Document
from models.chat import ChatSession, ChatMessage

# Import blueprints
from app.auth import auth_bp
from app.admin import admin_bp
from app.chat import chat_bp
from app.api import api_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(api_bp, url_prefix='/api')

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    """Trang chủ - chuyển hướng đến chatbot hoặc đăng nhập"""
    if current_user.is_authenticated:
        return redirect(url_for('chat.chatbot'))
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'app_name': os.getenv('APP_NAME', 'HSA Chatbot')
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

def create_admin_user():
    """Tạo tài khoản admin mặc định"""
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'hsa_admin_2024')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@hsa.edu.vn')
    
    admin = User.query.filter_by(username=admin_username).first()
    if not admin:
        admin = User(
            username=admin_username,
            email=admin_email,
            full_name='Administrator',
            role='admin',
            is_active=True
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        logger.info(f"Created admin user: {admin_username}")

def init_database():
    """Khởi tạo database"""
    with app.app_context():
        db.create_all()
        create_admin_user()
        logger.info("Database initialized successfully")

if __name__ == '__main__':
    init_database()
    
    # Run the app
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting HSA Chatbot on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


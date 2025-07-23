#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Model - Quản lý người dùng
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Import db from database
from database import db

class User(UserMixin, db.Model):
    """Model người dùng"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    
    # Thông tin thí sinh
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    school = db.Column(db.String(200), nullable=True)
    grade = db.Column(db.String(10), nullable=True)  # Lớp 12, 11, etc.
    
    # Phân quyền
    role = db.Column(db.String(20), default='student', nullable=False)  # admin, student
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    chat_sessions = db.relationship('ChatSession', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Mã hóa và lưu mật khẩu"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Kiểm tra mật khẩu"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Kiểm tra quyền admin"""
        return self.role == 'admin'
    
    def update_last_login(self):
        """Cập nhật thời gian đăng nhập cuối"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Chuyển đổi thành dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'student_id': self.student_id,
            'phone': self.phone,
            'school': self.school,
            'grade': self.grade,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


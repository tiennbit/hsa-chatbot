#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chat Model - Quản lý cuộc trò chuyện
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

# Import db from database
from database import db

class ChatSession(db.Model):
    """Model phiên trò chuyện"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    message_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def update_activity(self):
        """Cập nhật thời gian hoạt động cuối"""
        self.last_activity = datetime.utcnow()
        db.session.commit()
    
    def get_message_count(self):
        """Lấy số lượng tin nhắn trong phiên"""
        return len(self.messages)
    
    def get_last_message(self):
        """Lấy tin nhắn cuối cùng"""
        if self.messages:
            return max(self.messages, key=lambda m: m.created_at)
        return None
    
    def get_recent_messages(self, limit=10):
        """Lấy tin nhắn gần đây"""
        return sorted(self.messages, key=lambda m: m.created_at)[-limit:]
    
    def increment_message_count(self, count=1):
        """Tăng số lượng tin nhắn"""
        self.message_count += count
    
    def to_dict(self):
        """Chuyển đổi thành dictionary"""
        last_message = self.get_last_message()
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'title': self.title,
            'message_count': self.get_message_count(),
            'last_message': last_message.content[:100] + '...' if last_message and len(last_message.content) > 100 else last_message.content if last_message else None,
            'last_message_type': last_message.message_type if last_message else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }
    
    def __repr__(self):
        return f'<ChatSession {self.session_id}>'

class ChatMessage(db.Model):
    """Model tin nhắn trò chuyện"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(10), nullable=False)  # 'user' or 'bot'
    
    # Metadata
    tokens_used = db.Column(db.Integer, nullable=True)
    response_time = db.Column(db.Float, nullable=True)  # seconds
    model_used = db.Column(db.String(50), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def get_content_preview(self, max_length=100):
        """Lấy preview nội dung tin nhắn"""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + '...'
    
    def is_user_message(self):
        """Kiểm tra có phải tin nhắn của người dùng"""
        return self.message_type == 'user'
    
    def is_bot_message(self):
        """Kiểm tra có phải tin nhắn của bot"""
        return self.message_type == 'bot'
    
    def to_dict(self):
        """Chuyển đổi thành dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'content': self.content,
            'message_type': self.message_type,
            'tokens_used': self.tokens_used,
            'response_time': self.response_time,
            'model_used': self.model_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ChatMessage {self.message_type}: {self.get_content_preview(50)}>'

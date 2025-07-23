#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chat Models - Quản lý cuộc trò chuyện
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Import db from database
from database import db

class ChatSession(db.Model):
    """Model phiên trò chuyện"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=True)
    
    # User info
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for anonymous users
    user_ip = db.Column(db.String(45), nullable=True)  # IPv4/IPv6
    user_agent = db.Column(db.String(500), nullable=True)
    
    # Session metadata
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    message_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan', order_by='ChatMessage.created_at')
    
    def update_activity(self):
        """Cập nhật thời gian hoạt động cuối"""
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def increment_message_count(self):
        """Tăng số lượng tin nhắn"""
        self.message_count += 1
        self.update_activity()
    
    def get_recent_messages(self, limit=10):
        """Lấy tin nhắn gần đây"""
        return ChatMessage.query.filter_by(session_id=self.id)\
                               .order_by(ChatMessage.created_at.desc())\
                               .limit(limit).all()
    
    def to_dict(self, include_messages=False):
        """Chuyển đổi thành dictionary"""
        data = {
            'id': self.id,
            'session_id': self.session_id,
            'title': self.title,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else 'Anonymous',
            'is_active': self.is_active,
            'message_count': self.message_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_activity': self.last_activity.isoformat()
        }
        
        if include_messages:
            data['messages'] = [msg.to_dict() for msg in self.messages]
        
        return data
    
    def __repr__(self):
        return f'<ChatSession {self.session_id}>'

class ChatMessage(db.Model):
    """Model tin nhắn trò chuyện"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    
    # Message content
    message_type = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    
    # RAG metadata
    sources = db.Column(db.Text, nullable=True)  # JSON array of source documents
    relevance_score = db.Column(db.Float, nullable=True)
    processing_time = db.Column(db.Float, nullable=True)  # seconds
    
    # LLM metadata
    llm_provider = db.Column(db.String(20), nullable=True)  # openai, gemini, deepseek
    model_name = db.Column(db.String(50), nullable=True)
    tokens_used = db.Column(db.Integer, nullable=True)
    
    # User feedback
    rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    feedback = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def get_sources_list(self):
        """Lấy danh sách nguồn tài liệu"""
        if self.sources:
            try:
                return json.loads(self.sources)
            except:
                return []
        return []
    
    def set_sources_list(self, sources_list):
        """Thiết lập danh sách nguồn tài liệu"""
        if sources_list:
            self.sources = json.dumps(sources_list, ensure_ascii=False)
        else:
            self.sources = None
    
    def get_rating_display(self):
        """Hiển thị đánh giá bằng sao"""
        if self.rating:
            return '⭐' * self.rating + '☆' * (5 - self.rating)
        return 'Chưa đánh giá'
    
    def to_dict(self):
        """Chuyển đổi thành dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'message_type': self.message_type,
            'content': self.content,
            'sources': self.get_sources_list(),
            'relevance_score': self.relevance_score,
            'processing_time': self.processing_time,
            'llm_provider': self.llm_provider,
            'model_name': self.model_name,
            'tokens_used': self.tokens_used,
            'rating': self.rating,
            'rating_display': self.get_rating_display(),
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ChatMessage {self.id} ({self.message_type})>'


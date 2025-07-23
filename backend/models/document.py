#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Model - Quản lý tài liệu
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Import db from database
from database import db

class Document(db.Model):
    """Model tài liệu"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # bytes
    file_type = db.Column(db.String(10), nullable=False)  # pdf, docx, txt, etc.
    
    # Metadata
    title = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)  # hsa_info, exam_guide, faq, etc.
    tags = db.Column(db.String(500), nullable=True)  # comma-separated tags
    
    # Processing status
    status = db.Column(db.String(20), default='uploaded', nullable=False)  # uploaded, processing, processed, error
    processed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Vector database info
    vector_ids = db.Column(db.Text, nullable=True)  # JSON array of vector IDs
    chunk_count = db.Column(db.Integer, default=0)
    
    # Access control
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    uploader = db.relationship('User', backref='uploaded_documents')
    
    def get_file_size_mb(self):
        """Lấy kích thước file theo MB"""
        return round(self.file_size / (1024 * 1024), 2)
    
    def get_status_display(self):
        """Hiển thị trạng thái tiếng Việt"""
        status_map = {
            'uploaded': 'Đã tải lên',
            'processing': 'Đang xử lý',
            'processed': 'Đã xử lý',
            'error': 'Lỗi'
        }
        return status_map.get(self.status, self.status)
    
    def get_category_display(self):
        """Hiển thị danh mục tiếng Việt"""
        category_map = {
            'hsa_info': 'Thông tin HSA',
            'exam_guide': 'Hướng dẫn thi',
            'faq': 'Câu hỏi thường gặp',
            'study_material': 'Tài liệu học tập',
            'admission': 'Tuyển sinh',
            'other': 'Khác'
        }
        return category_map.get(self.category, self.category or 'Chưa phân loại')
    
    def get_tags_list(self):
        """Lấy danh sách tags"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags_list(self, tags_list):
        """Thiết lập danh sách tags"""
        if tags_list:
            self.tags = ', '.join([tag.strip() for tag in tags_list if tag.strip()])
        else:
            self.tags = None
    
    def delete_file(self):
        """Xóa file vật lý"""
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
                return True
        except Exception as e:
            print(f"Error deleting file {self.file_path}: {e}")
        return False
    
    def to_dict(self):
        """Chuyển đổi thành dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_size_mb': self.get_file_size_mb(),
            'file_type': self.file_type,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'category_display': self.get_category_display(),
            'tags': self.get_tags_list(),
            'status': self.status,
            'status_display': self.get_status_display(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'chunk_count': self.chunk_count,
            'is_public': self.is_public,
            'uploaded_by': self.uploaded_by,
            'uploader_name': self.uploader.full_name if self.uploader else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Document {self.original_filename}>'


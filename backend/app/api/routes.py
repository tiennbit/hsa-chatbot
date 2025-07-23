#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Routes
"""

from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from . import api_bp
from models.document import Document
from models.chat import ChatSession, ChatMessage

@api_bp.route('/documents')
@login_required
def get_documents():
    """Lấy danh sách tài liệu"""
    try:
        documents = Document.query.all()
        docs = []
        for doc in documents:
            docs.append({
                'id': doc.id,
                'title': doc.title,
                'filename': doc.filename,
                'upload_date': doc.upload_date.isoformat(),
                'file_size': doc.file_size
            })
        return jsonify({'documents': docs})
    except Exception as e:
        current_app.logger.error(f"Error getting documents: {str(e)}")
        return jsonify({'error': 'Có lỗi xảy ra khi lấy danh sách tài liệu'}), 500

@api_bp.route('/chat/sessions')
@login_required
def get_chat_sessions():
    """Lấy danh sách session chat"""
    try:
        sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).all()
        session_list = []
        for session in sessions:
            session_list.append({
                'id': session.id,
                'created_at': session.created_at.isoformat(),
                'is_active': session.is_active
            })
        return jsonify({'sessions': session_list})
    except Exception as e:
        current_app.logger.error(f"Error getting chat sessions: {str(e)}")
        return jsonify({'error': 'Có lỗi xảy ra khi lấy danh sách session chat'}), 500 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chat Routes
"""

from flask import render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from . import chat_bp
from models.chat import ChatSession, ChatMessage
from models.document import Document
from utils.rag_processor import RAGProcessor
import json

@chat_bp.route('/chatbot')
@login_required
def chatbot():
    """Trang chatbot chính"""
    return render_template('chat/chatbot.html')

@chat_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """API endpoint cho chat"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Tin nhắn không được để trống'}), 400
        
        # Tạo session chat mới nếu chưa có
        session = ChatSession.query.filter_by(user_id=current_user.id, is_active=True).first()
        if not session:
            import uuid
            session = ChatSession(
                user_id=current_user.id,
                session_id=str(uuid.uuid4())
            )
            from database import db
            db.session.add(session)
            db.session.commit()
        
        # Lưu tin nhắn của user
        user_message = ChatMessage(
            session_id=session.id,
            content=message,
            message_type='user'
        )
        from database import db
        db.session.add(user_message)
        
        # Xử lý tin nhắn với RAG
        rag_processor = RAGProcessor()
        response = rag_processor.process_query(message)
        
        # Lưu phản hồi của bot
        bot_message = ChatMessage(
            session_id=session.id,
            content=response,
            message_type='assistant'
        )
        db.session.add(bot_message)
        db.session.commit()
        
        return jsonify({
            'response': response,
            'session_id': session.id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in chat: {str(e)}")
        return jsonify({'error': 'Có lỗi xảy ra khi xử lý tin nhắn'}), 500

@chat_bp.route('/api/chat/history')
@login_required
def chat_history():
    """Lấy lịch sử chat"""
    try:
        session = ChatSession.query.filter_by(user_id=current_user.id, is_active=True).first()
        if not session:
            return jsonify({'messages': []})
        
        messages = ChatMessage.query.filter_by(session_id=session.id).order_by(ChatMessage.created_at).all()
        history = []
        for msg in messages:
            history.append({
                'content': msg.content,
                'sender': 'user' if msg.message_type == 'user' else 'bot',
                'timestamp': msg.created_at.isoformat()
            })
        
        return jsonify({'messages': history})
        
    except Exception as e:
        current_app.logger.error(f"Error getting chat history: {str(e)}")
        return jsonify({'error': 'Có lỗi xảy ra khi lấy lịch sử chat'}), 500 
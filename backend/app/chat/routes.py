#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chat Routes
"""

from flask import render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from . import chat_bp
from models.chat import ChatSession, ChatMessage
from models.unanswered import UnansweredQuestion
from database import db
from utils.rag_processor import RAGProcessor
import uuid

@chat_bp.route('/chatbot')
@login_required
def chatbot():
    """Render the main chatbot page"""
    return render_template('chat/chatbot.html')

@chat_bp.route('/api/chat/sessions', methods=['GET'])
@login_required
def get_sessions():
    """Get all chat sessions for the current user"""
    try:
        sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.last_activity.desc()).all()
        return jsonify({'sessions': [s.to_dict() for s in sessions]})
    except Exception as e:
        current_app.logger.error(f"Error getting sessions: {str(e)}")
        return jsonify({'error': 'Could not retrieve sessions'}), 500

@chat_bp.route('/api/chat/session', methods=['POST'])
@login_required
def create_session():
    """Create a new chat session"""
    try:
        new_session = ChatSession(
            user_id=current_user.id,
            session_id=str(uuid.uuid4()),
            title=None  # Set title to NULL initially
        )
        db.session.add(new_session)
        db.session.commit()
        return jsonify(new_session.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating session: {str(e)}")
        return jsonify({'error': 'Could not create new session'}), 500

@chat_bp.route('/api/chat/history/<session_id>', methods=['GET'])
@login_required
def get_session_history(session_id):
    """Get the message history for a specific session"""
    try:
        session = ChatSession.query.filter_by(session_id=session_id, user_id=current_user.id).first_or_404()
        messages = ChatMessage.query.filter_by(session_id=session.id).order_by(ChatMessage.created_at.asc()).all()
        return jsonify({'messages': [m.to_dict() for m in messages]})
    except Exception as e:
        current_app.logger.error(f"Error getting session history: {str(e)}")
        return jsonify({'error': 'Could not retrieve message history'}), 500

@chat_bp.route('/api/chat/<session_id>', methods=['POST'])
@login_required
def post_message(session_id):
    """Post a new message to a specific chat session"""
    try:
        session = ChatSession.query.filter_by(session_id=session_id, user_id=current_user.id).first_or_404()
        data = request.get_json()
        message_content = data.get('message', '').strip()

        if not message_content:
            return jsonify({'error': 'Message cannot be empty'}), 400

        # Save user message
        user_message = ChatMessage(session_id=session.id, content=message_content, message_type='user')
        db.session.add(user_message)

        # Process with RAG
        rag_processor = RAGProcessor()

        # If the session has no title, set it from the first user message.
        if session.title is None and message_content:
            session.title = message_content[:80]
        
        # Prepare chat history for RAG processor
        recent_messages = session.get_recent_messages()
        chat_history_for_rag = [msg.to_dict() for msg in recent_messages]
        
        response_content, found_context = rag_processor.process_query(
            query=message_content,
            chat_history=chat_history_for_rag
        )

        # If no context was found, save the question as unanswered
        if not found_context:
            existing_question = UnansweredQuestion.query.filter_by(
                question_text=message_content,
                status='pending'
            ).first()
            if not existing_question:
                unanswered = UnansweredQuestion(
                    question_text=message_content,
                    session_id=session.id,
                    user_id=current_user.id
                )
                db.session.add(unanswered)
        
        # Save bot response
        bot_message = ChatMessage(session_id=session.id, content=response_content, message_type='bot')
        db.session.add(bot_message)
        
        # Update session metadata
        session.update_activity()
        session.increment_message_count(count=2)

        db.session.commit()

        return jsonify({'response': response_content})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in chat session {session_id}: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your message'}), 500

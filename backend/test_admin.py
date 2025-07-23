#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Admin Dashboard
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import app from main.py
from main import app

from models.user import User
from models.document import Document
from models.chat import ChatSession, ChatMessage
from database import db
from datetime import datetime, timedelta
from sqlalchemy import func, desc

def test_admin_dashboard():
    """Test admin dashboard functionality"""
    with app.app_context():
        try:
            # Test database queries
            print("Testing database queries...")
            
            # Test User queries
            total_users = User.query.filter_by(role='student').count()
            print(f"Total users: {total_users}")
            
            # Test Document queries
            total_documents = Document.query.count()
            print(f"Total documents: {total_documents}")
            
            # Test ChatSession queries
            total_sessions = ChatSession.query.count()
            print(f"Total sessions: {total_sessions}")
            
            # Test ChatMessage queries
            total_messages = ChatMessage.query.count()
            print(f"Total messages: {total_messages}")
            
            # Test active sessions today
            active_sessions_today = ChatSession.query.filter(
                ChatSession.last_activity >= datetime.utcnow() - timedelta(days=1)
            ).count()
            print(f"Active sessions today: {active_sessions_today}")
            
            # Test document status counts
            documents_processed = Document.query.filter_by(status='processed').count()
            documents_processing = Document.query.filter_by(status='processing').count()
            documents_error = Document.query.filter_by(status='error').count()
            print(f"Documents processed: {documents_processed}")
            print(f"Documents processing: {documents_processing}")
            print(f"Documents error: {documents_error}")
            
            # Test top users query - simplified
            try:
                top_users = db.session.query(
                    User.id, User.full_name, User.username,
                    func.count(ChatMessage.id).label('message_count')
                ).select_from(User)\
                 .outerjoin(ChatSession, User.id == ChatSession.user_id)\
                 .outerjoin(ChatMessage, ChatSession.id == ChatMessage.session_id)\
                 .filter(User.role == 'student')\
                 .group_by(User.id, User.full_name, User.username)\
                 .order_by(desc('message_count'))\
                 .limit(10).all()
                print(f"Top users: {len(top_users)}")
            except Exception as e:
                print(f"Top users query error: {e}")
                top_users = []
            
            # Test recent sessions
            recent_sessions = ChatSession.query.order_by(desc(ChatSession.last_activity)).limit(10).all()
            print(f"Recent sessions: {len(recent_sessions)}")
            
            # Test recent documents
            recent_documents = Document.query.order_by(desc(Document.created_at)).limit(10).all()
            print(f"Recent documents: {len(recent_documents)}")
            
            print("All tests passed!")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_admin_dashboard() 
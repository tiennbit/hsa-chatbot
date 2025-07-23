#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Explorer for HSA Chatbot
"""

import sqlite3
import os
from datetime import datetime

def explore_database():
    """Khám phá database"""
    db_path = "instance/hsa_chatbot.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database không tồn tại: {db_path}")
        return
    
    print(f"📊 Khám phá database: {db_path}")
    print("=" * 50)
    
    # Kết nối database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Lấy danh sách tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"📋 Có {len(tables)} tables:")
    for table in tables:
        table_name = table[0]
        print(f"  - {table_name}")
        
        # Đếm số records
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"    Records: {count}")
        
        # Hiển thị schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"    Columns:")
        for col in columns:
            print(f"      {col[1]} ({col[2]})")
        print()
    
    # Hiển thị dữ liệu từ các tables chính
    print("📄 Dữ liệu chi tiết:")
    print("=" * 50)
    
    # Users table
    print("\n👥 USERS TABLE:")
    cursor.execute("SELECT id, username, email, full_name, role, created_at FROM users LIMIT 5")
    users = cursor.fetchall()
    for user in users:
        print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Role: {user[4]}")
    
    # Documents table
    print("\n📚 DOCUMENTS TABLE:")
    cursor.execute("SELECT id, title, filename, file_type, status, created_at FROM documents LIMIT 5")
    documents = cursor.fetchall()
    for doc in documents:
        print(f"  ID: {doc[0]}, Title: {doc[1]}, File: {doc[2]}, Status: {doc[4]}")
    
    # Chat Sessions table
    print("\n💬 CHAT SESSIONS TABLE:")
    cursor.execute("SELECT id, user_id, session_id, is_active, created_at FROM chat_sessions LIMIT 5")
    sessions = cursor.fetchall()
    for session in sessions:
        print(f"  ID: {session[0]}, User: {session[1]}, Session: {session[2]}, Active: {session[3]}")
    
    # Chat Messages table
    print("\n💭 CHAT MESSAGES TABLE:")
    cursor.execute("SELECT id, session_id, content, message_type, created_at FROM chat_messages LIMIT 5")
    messages = cursor.fetchall()
    for msg in messages:
        content_preview = msg[2][:50] + "..." if len(msg[2]) > 50 else msg[2]
        print(f"  ID: {msg[0]}, Session: {msg[1]}, Type: {msg[3]}, Content: {content_preview}")
    
    conn.close()
    print("\n✅ Hoàn thành khám phá database!")

def run_sql_query(query):
    """Chạy SQL query tùy chỉnh"""
    db_path = "instance/hsa_chatbot.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database không tồn tại: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Lấy tên columns
        columns = [description[0] for description in cursor.description]
        
        print(f"📊 Kết quả query: {query}")
        print("=" * 50)
        
        # Hiển thị headers
        if columns:
            print(" | ".join(columns))
            print("-" * 50)
        
        # Hiển thị results
        for row in results:
            print(" | ".join(str(cell) for cell in row))
        
        print(f"\n📈 Tổng số records: {len(results)}")
        
    except Exception as e:
        print(f"❌ Lỗi khi chạy query: {e}")
    
    conn.close()

if __name__ == "__main__":
    print("🔍 HSA Chatbot Database Explorer")
    print("=" * 50)
    
    # Khám phá database
    explore_database()
    
    # Một số queries mẫu
    print("\n🔍 Một số queries mẫu:")
    print("1. SELECT * FROM users WHERE role='admin';")
    print("2. SELECT COUNT(*) as total_messages FROM chat_messages;")
    print("3. SELECT * FROM documents WHERE status='processed';")
    print("4. SELECT users.username, COUNT(chat_messages.id) as message_count FROM users LEFT JOIN chat_sessions ON users.id = chat_sessions.user_id LEFT JOIN chat_messages ON chat_sessions.id = chat_messages.session_id GROUP BY users.id;")
    
    # Chạy query mẫu
    print("\n📊 Thống kê tổng quan:")
    run_sql_query("SELECT 'Users' as table_name, COUNT(*) as count FROM users UNION ALL SELECT 'Documents', COUNT(*) FROM documents UNION ALL SELECT 'Chat Sessions', COUNT(*) FROM chat_sessions UNION ALL SELECT 'Chat Messages', COUNT(*) FROM chat_messages;") 
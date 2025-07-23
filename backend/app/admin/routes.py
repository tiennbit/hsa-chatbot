#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin Panel Routes
"""

from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from functools import wraps
from . import admin_bp
from models.user import User
from database import db
from models.document import Document
from models.chat import ChatSession, ChatMessage
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import os

def admin_required(f):
    """Decorator yêu cầu quyền admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Bạn không có quyền truy cập trang này', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Dashboard admin"""
    # Thống kê tổng quan
    stats = {
        'total_users': User.query.filter_by(role='student').count(),
        'total_documents': Document.query.count(),
        'total_sessions': ChatSession.query.count(),
        'total_messages': ChatMessage.query.count(),
        'active_sessions_today': ChatSession.query.filter(
            ChatSession.last_activity >= datetime.utcnow() - timedelta(days=1)
        ).count(),
        'documents_processed': Document.query.filter_by(status='processed').count(),
        'documents_processing': Document.query.filter_by(status='processing').count(),
        'documents_error': Document.query.filter_by(status='error').count()
    }
    
    # Thống kê theo thời gian (7 ngày gần đây)
    daily_stats = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        
        daily_data = {
            'date': date_start.strftime('%Y-%m-%d'),
            'new_users': User.query.filter(
                User.created_at >= date_start,
                User.created_at < date_end,
                User.role == 'student'
            ).count(),
            'new_sessions': ChatSession.query.filter(
                ChatSession.created_at >= date_start,
                ChatSession.created_at < date_end
            ).count(),
            'messages': ChatMessage.query.filter(
                ChatMessage.created_at >= date_start,
                ChatMessage.created_at < date_end
            ).count()
        }
        daily_stats.append(daily_data)
    
    # Top users theo số tin nhắn
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
    
    # Recent activities
    recent_sessions = ChatSession.query.order_by(desc(ChatSession.last_activity)).limit(10).all()
    recent_documents = Document.query.order_by(desc(Document.created_at)).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         daily_stats=daily_stats,
                         top_users=top_users,
                         recent_sessions=recent_sessions,
                         recent_documents=recent_documents)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Quản lý người dùng"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.full_name.contains(search)) |
            (User.email.contains(search)) |
            (User.student_id.contains(search))
        )
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    users = query.order_by(desc(User.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users, search=search, role_filter=role_filter)

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """Chi tiết người dùng"""
    user = User.query.get_or_404(user_id)
    
    # Thống kê hoạt động của user
    user_stats = {
        'total_sessions': ChatSession.query.filter_by(user_id=user_id).count(),
        'total_messages': db.session.query(func.count(ChatMessage.id))\
                                   .join(ChatSession)\
                                   .filter(ChatSession.user_id == user_id).scalar(),
        'last_activity': ChatSession.query.filter_by(user_id=user_id)\
                                          .order_by(desc(ChatSession.last_activity))\
                                          .first()
    }
    
    # Recent sessions
    recent_sessions = ChatSession.query.filter_by(user_id=user_id)\
                                       .order_by(desc(ChatSession.last_activity))\
                                       .limit(10).all()
    
    return render_template('admin/user_detail.html',
                         user=user,
                         user_stats=user_stats,
                         recent_sessions=recent_sessions)

@admin_bp.route('/users/<int:user_id>/toggle_status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Kích hoạt/vô hiệu hóa người dùng"""
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin':
        return jsonify({'error': 'Không thể thay đổi trạng thái admin'}), 400
    
    user.is_active = not user.is_active
    user.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        status = 'kích hoạt' if user.is_active else 'vô hiệu hóa'
        return jsonify({
            'success': True,
            'message': f'Đã {status} người dùng {user.username}',
            'is_active': user.is_active
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Có lỗi xảy ra khi cập nhật trạng thái'}), 500

@admin_bp.route('/documents')
@login_required
@admin_required
def documents():
    """Quản lý tài liệu"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    
    query = Document.query
    
    if search:
        query = query.filter(
            (Document.original_filename.contains(search)) |
            (Document.title.contains(search)) |
            (Document.description.contains(search))
        )
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    documents = query.order_by(desc(Document.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Categories for filter
    categories = db.session.query(Document.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('admin/documents.html',
                         documents=documents,
                         search=search,
                         status_filter=status_filter,
                         category_filter=category_filter,
                         categories=categories)

@admin_bp.route('/documents/<int:doc_id>')
@login_required
@admin_required
def document_detail(doc_id):
    """Chi tiết tài liệu"""
    document = Document.query.get_or_404(doc_id)
    return render_template('admin/document_detail.html', document=document)

@admin_bp.route('/documents/<int:doc_id>/download')
@login_required
@admin_required
def download_document(doc_id):
    """Tải xuống tài liệu"""
    document = Document.query.get_or_404(doc_id)
    
    if not os.path.exists(document.file_path):
        flash('File không tồn tại', 'error')
        return redirect(url_for('admin.documents'))
    
    return send_file(document.file_path,
                     as_attachment=True,
                     download_name=document.original_filename)

@admin_bp.route('/documents/<int:doc_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_document(doc_id):
    """Xóa tài liệu"""
    document = Document.query.get_or_404(doc_id)
    
    try:
        # Delete physical file
        document.delete_file()
        
        # Delete from database
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Đã xóa tài liệu {document.original_filename}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Có lỗi xảy ra khi xóa tài liệu'}), 500

@admin_bp.route('/chats')
@login_required
@admin_required
def chats():
    """Quản lý cuộc trò chuyện"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    query = ChatSession.query.join(User, ChatSession.user_id == User.id, isouter=True)
    
    if search:
        query = query.filter(
            (ChatSession.title.contains(search)) |
            (User.username.contains(search)) |
            (User.full_name.contains(search))
        )
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(ChatSession.created_at >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(ChatSession.created_at < date_to_obj)
        except ValueError:
            pass
    
    sessions = query.order_by(desc(ChatSession.last_activity)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/chats.html',
                         sessions=sessions,
                         search=search,
                         date_from=date_from,
                         date_to=date_to)

@admin_bp.route('/chats/<int:session_id>')
@login_required
@admin_required
def chat_detail(session_id):
    """Chi tiết cuộc trò chuyện"""
    session = ChatSession.query.get_or_404(session_id)
    messages = ChatMessage.query.filter_by(session_id=session_id)\
                                .order_by(ChatMessage.created_at).all()
    
    return render_template('admin/chat_detail.html',
                         session=session,
                         messages=messages)

@admin_bp.route('/api/session/<int:session_id>')
@login_required
@admin_required
def get_session_details(session_id):
    """API để lấy chi tiết session"""
    try:
        session = ChatSession.query.get_or_404(session_id)
        messages = ChatMessage.query.filter_by(session_id=session_id)\
                                    .order_by(ChatMessage.created_at).all()
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'content': msg.content,
                'message_type': msg.message_type,
                'created_at': msg.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'session': {
                'id': session.id,
                'session_id': session.session_id,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            },
            'messages': messages_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@admin_bp.route('/api/session/<int:session_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_session(session_id):
    """API để xóa session"""
    try:
        session = ChatSession.query.get_or_404(session_id)
        
        # Xóa tất cả messages của session
        ChatMessage.query.filter_by(session_id=session_id).delete()
        
        # Xóa session
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Session deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Phân tích và báo cáo"""
    # Thống kê theo tháng (12 tháng gần đây)
    monthly_stats = []
    for i in range(12):
        date = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if date.month == 12:
            month_end = date.replace(year=date.year+1, month=1, day=1)
        else:
            month_end = date.replace(month=date.month+1, day=1)
        
        monthly_data = {
            'month': month_start.strftime('%Y-%m'),
            'new_users': User.query.filter(
                User.created_at >= month_start,
                User.created_at < month_end,
                User.role == 'student'
            ).count(),
            'sessions': ChatSession.query.filter(
                ChatSession.created_at >= month_start,
                ChatSession.created_at < month_end
            ).count(),
            'messages': ChatMessage.query.filter(
                ChatMessage.created_at >= month_start,
                ChatMessage.created_at < month_end
            ).count()
        }
        monthly_stats.append(monthly_data)
    
    monthly_stats.reverse()
    
    # Top questions/topics
    popular_messages = ChatMessage.query.filter_by(message_type='user')\
                                        .order_by(desc(ChatMessage.created_at))\
                                        .limit(100).all()
    
    # User engagement
    user_engagement = db.session.query(
        User.grade,
        func.count(User.id).label('user_count'),
        func.avg(func.count(ChatMessage.id)).label('avg_messages')
    ).join(ChatSession).join(ChatMessage)\
     .filter(User.role == 'student')\
     .group_by(User.grade).all()
    
    return render_template('admin/analytics.html',
                         monthly_stats=monthly_stats,
                         popular_messages=popular_messages,
                         user_engagement=user_engagement)

@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Cài đặt hệ thống"""
    # Load current configuration
    config = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY', ''),
        'EMBEDDING_MODEL': os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
        'DEFAULT_LLM_PROVIDER': os.getenv('DEFAULT_LLM_PROVIDER', 'gemini'),
        'RESPONSE_MAX_TOKENS': int(os.getenv('RESPONSE_MAX_TOKENS', 1000)),
        'TEMPERATURE': float(os.getenv('TEMPERATURE', 0.7)),
        'MAX_CONTENT_LENGTH': int(os.getenv('MAX_CONTENT_LENGTH', 52428800))
    }
    
    return render_template('admin/settings.html', config=config)

@admin_bp.route('/update_settings', methods=['POST'])
@login_required
@admin_required
def update_settings():
    """Cập nhật cấu hình API"""
    try:
        # Update .env file
        env_file = os.path.join(os.getcwd(), '.env')
        env_content = []
        
        # Read existing .env file
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                env_content = f.readlines()
        
        # Update or add API keys
        api_keys = {
            'OPENAI_API_KEY': request.form.get('openai_api_key', ''),
            'GEMINI_API_KEY': request.form.get('gemini_api_key', ''),
            'DEEPSEEK_API_KEY': request.form.get('deepseek_api_key', '')
        }
        
        # Update existing keys or add new ones
        for key, value in api_keys.items():
            if value.strip():  # Only update if value is not empty
                found = False
                for i, line in enumerate(env_content):
                    if line.startswith(f'{key}='):
                        env_content[i] = f'{key}={value}\n'
                        found = True
                        break
                if not found:
                    env_content.append(f'{key}={value}\n')
        
        # Write back to .env file
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(env_content)
        
        flash('Cấu hình API đã được cập nhật thành công', 'success')
        return redirect(url_for('admin.settings'))
        
    except Exception as e:
        flash(f'Có lỗi xảy ra khi cập nhật cấu hình: {str(e)}', 'error')
        return redirect(url_for('admin.settings'))

@admin_bp.route('/update_system_settings', methods=['POST'])
@login_required
@admin_required
def update_system_settings():
    """Cập nhật cài đặt hệ thống"""
    try:
        # Update .env file
        env_file = os.path.join(os.getcwd(), '.env')
        env_content = []
        
        # Read existing .env file
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                env_content = f.readlines()
        
        # Update system settings
        settings = {
            'DEFAULT_LLM_PROVIDER': request.form.get('default_llm_provider', 'gemini'),
            'EMBEDDING_MODEL': request.form.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2'),
            'RESPONSE_MAX_TOKENS': request.form.get('response_max_tokens', '1000'),
            'TEMPERATURE': request.form.get('temperature', '0.7'),
            'MAX_CONTENT_LENGTH': str(int(request.form.get('max_file_size', '50')) * 1024 * 1024)
        }
        
        # Update existing settings or add new ones
        for key, value in settings.items():
            found = False
            for i, line in enumerate(env_content):
                if line.startswith(f'{key}='):
                    env_content[i] = f'{key}={value}\n'
                    found = True
                    break
            if not found:
                env_content.append(f'{key}={value}\n')
        
        # Write back to .env file
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(env_content)
        
        flash('Cài đặt hệ thống đã được cập nhật thành công', 'success')
        return redirect(url_for('admin.settings'))
        
    except Exception as e:
        flash(f'Có lỗi xảy ra khi cập nhật cài đặt: {str(e)}', 'error')
        return redirect(url_for('admin.settings'))

@admin_bp.route('/test_rag', methods=['POST'])
@login_required
@admin_required
def test_rag():
    """Test RAG system"""
    try:
        from utils.rag_processor import RAGProcessor
        rag = RAGProcessor()
        response = rag.process_query("HSA là gì?")
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/rebuild_index', methods=['POST'])
@login_required
@admin_required
def rebuild_index():
    """Rebuild vector index"""
    try:
        from utils.rag_processor import RAGProcessor
        rag = RAGProcessor()
        
        # Get all documents
        documents = Document.query.filter_by(status='processed').all()
        
        for doc in documents:
            if os.path.exists(doc.file_path):
                rag.process_document(
                    document_id=doc.id,
                    file_path=doc.file_path,
                    file_type=doc.file_type,
                    title=doc.title,
                    category=doc.category
                )
        
        return jsonify({'success': True, 'message': f'Đã rebuild {len(documents)} documents'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/export_data')
@login_required
@admin_required
def export_data():
    """Export system data"""
    try:
        import json
        from datetime import datetime
        
        data = {
            'export_date': datetime.utcnow().isoformat(),
            'users': [],
            'documents': [],
            'chat_sessions': []
        }
        
        # Export users
        users = User.query.all()
        for user in users:
            data['users'].append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        # Export documents
        documents = Document.query.all()
        for doc in documents:
            data['documents'].append({
                'id': doc.id,
                'title': doc.title,
                'filename': doc.filename,
                'category': doc.category,
                'status': doc.status,
                'created_at': doc.created_at.isoformat() if doc.created_at else None
            })
        
        # Export chat sessions
        sessions = ChatSession.query.all()
        for session in sessions:
            data['chat_sessions'].append({
                'id': session.id,
                'user_id': session.user_id,
                'message_count': ChatMessage.query.filter_by(session_id=session.id).count(),
                'created_at': session.created_at.isoformat() if session.created_at else None
            })
        
        # Create response
        from flask import Response
        response = Response(
            json.dumps(data, indent=2, ensure_ascii=False),
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename=hsa_chatbot_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'}
        )
        return response
        
    except Exception as e:
        flash(f'Có lỗi xảy ra khi export data: {str(e)}', 'error')
        return redirect(url_for('admin.settings'))

@admin_bp.route('/clear_cache', methods=['POST'])
@login_required
@admin_required
def clear_cache():
    """Clear system cache"""
    try:
        # Clear ChromaDB cache
        import shutil
        chroma_dir = os.path.join(os.getcwd(), 'chroma_db')
        if os.path.exists(chroma_dir):
            shutil.rmtree(chroma_dir)
            os.makedirs(chroma_dir, exist_ok=True)
        
        return jsonify({'success': True, 'message': 'Cache đã được xóa thành công'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/upload_document', methods=['POST'])
@login_required
@admin_required
def upload_document():
    """Tải lên tài liệu"""
    try:
        if 'file' not in request.files:
            flash('Không có file được chọn', 'error')
            return redirect(url_for('admin.documents'))
        
        file = request.files['file']
        if file.filename == '':
            flash('Không có file được chọn', 'error')
            return redirect(url_for('admin.documents'))
        
        # Kiểm tra định dạng file
        allowed_extensions = {'pdf', 'docx', 'pptx', 'txt', 'xlsx'}
        if not file.filename.lower().endswith(tuple('.' + ext for ext in allowed_extensions)):
            flash('Định dạng file không được hỗ trợ', 'error')
            return redirect(url_for('admin.documents'))
        
        # Lưu file
        import os
        from werkzeug.utils import secure_filename
        
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{timestamp}_{filename}"
        
        upload_dir = os.path.join(os.getcwd(), '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, new_filename)
        
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Tạo record trong database
        document = Document(
            filename=new_filename,
            original_filename=filename,
            file_path=file_path,
            file_size=file_size,
            file_type=filename.split('.')[-1].lower(),
            title=request.form.get('title', ''),
            description=request.form.get('description', ''),
            category=request.form.get('category', 'other'),
            tags=request.form.get('tags', ''),
            is_public=request.form.get('is_public') == 'on',
            uploaded_by=current_user.id,
            status='uploaded'
        )
        
        db.session.add(document)
        db.session.commit()
        
        # Xử lý tài liệu với RAG (background task)
        try:
            from utils.rag_processor import RAGProcessor
            rag_processor = RAGProcessor()
            rag_processor.process_document(
                document_id=document.id,
                file_path=file_path,
                file_type=document.file_type,
                title=document.title,
                category=document.category
            )
            document.status = 'processed'
            document.processed_at = datetime.utcnow()
            db.session.commit()
            flash('Tài liệu đã được tải lên và xử lý thành công', 'success')
        except Exception as e:
            document.status = 'error'
            document.error_message = str(e)
            db.session.commit()
            flash(f'Tài liệu đã được tải lên nhưng có lỗi khi xử lý: {str(e)}', 'warning')
        
        return redirect(url_for('admin.documents'))
        
    except Exception as e:
        flash(f'Có lỗi xảy ra khi tải lên tài liệu: {str(e)}', 'error')
        return redirect(url_for('admin.documents'))


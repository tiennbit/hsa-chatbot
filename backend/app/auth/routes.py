#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication Routes
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from models.user import User
from database import db
from datetime import datetime

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Đăng nhập"""
    if current_user.is_authenticated:
        return redirect(url_for('chat.chatbot'))
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
        
        if not username or not password:
            if request.is_json:
                return jsonify({'error': 'Vui lòng nhập tên đăng nhập và mật khẩu'}), 400
            flash('Vui lòng nhập tên đăng nhập và mật khẩu', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=True)
            user.update_last_login()
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Đăng nhập thành công',
                    'user': user.to_dict(),
                    'redirect_url': url_for('admin.dashboard') if user.is_admin() else url_for('chat.chatbot')
                })
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('chat.chatbot'))
        else:
            error_msg = 'Tên đăng nhập hoặc mật khẩu không đúng'
            if request.is_json:
                return jsonify({'error': error_msg}), 401
            flash(error_msg, 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Đăng ký tài khoản thí sinh"""
    if current_user.is_authenticated:
        return redirect(url_for('chat.chatbot'))
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                error_msg = f'Vui lòng nhập {field}'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('auth/register.html')
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            error_msg = 'Tên đăng nhập hoặc email đã tồn tại'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            student_id=data.get('student_id'),
            phone=data.get('phone'),
            school=data.get('school'),
            grade=data.get('grade'),
            role='student',
            is_active=True
        )
        user.set_password(data['password'])
        
        try:
            db.session.add(user)
            db.session.commit()
            
            success_msg = 'Đăng ký thành công! Vui lòng đăng nhập.'
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': success_msg,
                    'redirect_url': url_for('auth.login')
                })
            flash(success_msg, 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            error_msg = 'Có lỗi xảy ra khi đăng ký. Vui lòng thử lại.'
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(error_msg, 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Đăng xuất"""
    logout_user()
    flash('Đã đăng xuất thành công', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Trang thông tin cá nhân"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Cập nhật thông tin cá nhân"""
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    # Update allowed fields
    allowed_fields = ['full_name', 'email', 'phone', 'school', 'grade', 'student_id']
    for field in allowed_fields:
        if field in data and data[field] is not None:
            setattr(current_user, field, data[field])
    
    # Update password if provided
    if data.get('new_password'):
        if not data.get('current_password'):
            error_msg = 'Vui lòng nhập mật khẩu hiện tại'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('auth.profile'))
        
        if not current_user.check_password(data['current_password']):
            error_msg = 'Mật khẩu hiện tại không đúng'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('auth.profile'))
        
        current_user.set_password(data['new_password'])
    
    try:
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        success_msg = 'Cập nhật thông tin thành công'
        if request.is_json:
            return jsonify({
                'success': True,
                'message': success_msg,
                'user': current_user.to_dict()
            })
        flash(success_msg, 'success')
        
    except Exception as e:
        db.session.rollback()
        error_msg = 'Có lỗi xảy ra khi cập nhật thông tin'
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
    
    return redirect(url_for('auth.profile'))


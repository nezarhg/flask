from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from datetime import datetime
from .models import db, User, Permission, ActivityLog

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """تسجيل الدخول وإنشاء رمز الوصول"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'يجب توفير اسم المستخدم وكلمة المرور'}), 400
    
    user = User.query.filter_by(username=data.get('username')).first()
    
    if not user or not user.check_password(data.get('password')):
        return jsonify({'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'}), 401
    
    # تحديث وقت آخر تسجيل دخول
    user.last_login = datetime.utcnow()
    
    # تسجيل نشاط تسجيل الدخول
    activity = ActivityLog(
        user_id=user.id,
        action='تسجيل الدخول',
        entity_type='user',
        entity_id=user.id,
        details='تم تسجيل الدخول بنجاح',
        ip_address=request.remote_addr
    )
    
    db.session.add(activity)
    db.session.commit()
    
    # إنشاء رموز الوصول والتحديث
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'تم تسجيل الدخول بنجاح',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """تحديث رمز الوصول باستخدام رمز التحديث"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'access_token': access_token
    }), 200

@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    """تسجيل مستخدم جديد (يتطلب صلاحيات المسؤول)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # التحقق من صلاحيات المستخدم
    if current_user.role != 'admin' and not any(p.name == 'user_create' for p in current_user.permissions):
        return jsonify({'message': 'ليس لديك صلاحية لإنشاء مستخدمين جدد'}), 403
    
    data = request.get_json()
    
    # التحقق من البيانات المطلوبة
    required_fields = ['username', 'password', 'email', 'full_name', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'الحقل {field} مطلوب'}), 400
    
    # التحقق من عدم وجود مستخدم بنفس اسم المستخدم أو البريد الإلكتروني
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'اسم المستخدم موجود بالفعل'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'البريد الإلكتروني موجود بالفعل'}), 400
    
    # إنشاء المستخدم الجديد
    new_user = User(
        username=data['username'],
        email=data['email'],
        full_name=data['full_name'],
        role=data['role']
    )
    new_user.set_password(data['password'])
    
    # إضافة الصلاحيات إذا تم توفيرها
    if 'permissions' in data and isinstance(data['permissions'], list):
        for permission_name in data['permissions']:
            permission = Permission.query.filter_by(name=permission_name).first()
            if permission:
                new_user.permissions.append(permission)
    
    db.session.add(new_user)
    
    # تسجيل نشاط إنشاء المستخدم
    activity = ActivityLog(
        user_id=current_user_id,
        action='إنشاء مستخدم',
        entity_type='user',
        entity_id=new_user.id,
        details=f'تم إنشاء مستخدم جديد: {new_user.username}',
        ip_address=request.remote_addr
    )
    
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم إنشاء المستخدم بنجاح',
        'user': new_user.to_dict()
    }), 201

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """الحصول على قائمة المستخدمين (يتطلب صلاحيات المسؤول)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # التحقق من صلاحيات المستخدم
    if current_user.role != 'admin' and not any(p.name == 'user_read' for p in current_user.permissions):
        return jsonify({'message': 'ليس لديك صلاحية لعرض المستخدمين'}), 403
    
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """الحصول على بيانات مستخدم محدد (يتطلب صلاحيات المسؤول أو المستخدم نفسه)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # السماح للمستخدم بعرض بياناته الخاصة أو للمسؤول بعرض بيانات أي مستخدم
    if current_user_id != user_id and current_user.role != 'admin' and not any(p.name == 'user_read' for p in current_user.permissions):
        return jsonify({'message': 'ليس لديك صلاحية لعرض بيانات هذا المستخدم'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'المستخدم غير موجود'}), 404
    
    return jsonify({
        'user': user.to_dict()
    }), 200

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """تحديث بيانات مستخدم (يتطلب صلاحيات المسؤول أو المستخدم نفسه)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # السماح للمستخدم بتحديث بياناته الخاصة أو للمسؤول بتحديث بيانات أي مستخدم
    if current_user_id != user_id and current_user.role != 'admin' and not any(p.name == 'user_update' for p in current_user.permissions):
        return jsonify({'message': 'ليس لديك صلاحية لتحديث بيانات هذا المستخدم'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'المستخدم غير موجود'}), 404
    
    data = request.get_json()
    
    # تحديث البيانات المسموح بها
    if 'email' in data:
        # التحقق من عدم وجود مستخدم آخر بنفس البريد الإلكتروني
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'message': 'البريد الإلكتروني موجود بالفعل'}), 400
        user.email = data['email']
    
    if 'full_name' in data:
        user.full_name = data['full_name']
    
    # تحديث كلمة المرور (إذا تم توفيرها)
    if 'password' in data:
        user.set_password(data['password'])
    
    # تحديث الدور (للمسؤول فقط)
    if 'role' in data and current_user.role == 'admin':
        user.role = data['role']
    
    # تحديث الصلاحيات (للمسؤول فقط)
    if 'permissions' in data and isinstance(data['permissions'], list) and current_user.role == 'admin':
        # إزالة جميع الصلاحيات الحالية
        user.permissions = []
        
        # إضافة الصلاحيات الجديدة
        for permission_name in data['permissions']:
            permission = Permission.query.filter_by(name=permission_name).first()
            if permission:
                user.permissions.append(permission)
    
    # تسجيل نشاط تحديث المستخدم
    activity = ActivityLog(
        user_id=current_user_id,
        action='تحديث مستخدم',
        entity_type='user',
        entity_id=user.id,
        details=f'تم تحديث بيانات المستخدم: {user.username}',
        ip_address=request.remote_addr
    )
    
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم تحديث بيانات المستخدم بنجاح',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """حذف مستخدم (يتطلب صلاحيات المسؤول)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # التحقق من صلاحيات المستخدم
    if current_user.role != 'admin' and not any(p.name == 'user_delete' for p in current_user.permissions):
        return jsonify({'message': 'ليس لديك صلاحية لحذف المستخدمين'}), 403
    
    # منع حذف المستخدم الحالي
    if current_user_id == user_id:
        return jsonify({'message': 'لا يمكنك حذف حسابك الخاص'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'المستخدم غير موجود'}), 404
    
    # تسجيل نشاط حذف المستخدم
    activity = ActivityLog(
        user_id=current_user_id,
        action='حذف مستخدم',
        entity_type='user',
        entity_id=user.id,
        details=f'تم حذف المستخدم: {user.username}',
        ip_address=request.remote_addr
    )
    
    db.session.add(activity)
    
    # حذف المستخدم
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'message': 'تم حذف المستخدم بنجاح'
    }), 200

@auth_bp.route('/permissions', methods=['GET'])
@jwt_required()
def get_permissions():
    """الحصول على قائمة الصلاحيات المتاحة"""
    permissions = Permission.query.all()
    return jsonify({
        'permissions': [permission.to_dict() for permission in permissions]
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """الحصول على الملف الشخصي للمستخدم الحالي"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'المستخدم غير موجود'}), 404
    
    return jsonify({
        'user': user.to_dict()
    }), 200

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Establishment, Region, City, EstablishmentType, User, ActivityLog
from ..marketing.models import MarketingCampaign, MarketingMessage, MarketingDelivery
import datetime
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import os

statistics_bp = Blueprint('statistics', __name__)

# إحصائيات عامة
@statistics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_statistics():
    """الحصول على إحصائيات لوحة التحكم الرئيسية"""
    
    # إحصائيات المنشآت
    total_establishments = Establishment.query.count()
    
    # إحصائيات المناطق
    regions = Region.query.all()
    region_stats = []
    
    for region in regions:
        count = Establishment.query.filter_by(region_id=region.id).count()
        if count > 0:
            region_stats.append({
                'region': region.name,
                'count': count,
                'percentage': round((count / total_establishments) * 100, 1) if total_establishments > 0 else 0
            })
    
    # ترتيب المناطق حسب العدد تنازليًا
    region_stats = sorted(region_stats, key=lambda x: x['count'], reverse=True)
    
    # إحصائيات أنواع المنشآت
    establishment_types = EstablishmentType.query.all()
    type_stats = []
    
    for type_item in establishment_types:
        count = Establishment.query.filter_by(establishment_type_id=type_item.id).count()
        if count > 0:
            type_stats.append({
                'type': type_item.name,
                'count': count,
                'percentage': round((count / total_establishments) * 100, 1) if total_establishments > 0 else 0
            })
    
    # ترتيب أنواع المنشآت حسب العدد تنازليًا
    type_stats = sorted(type_stats, key=lambda x: x['count'], reverse=True)
    
    # إحصائيات المستخدمين
    total_users = User.query.count()
    admin_users = User.query.filter_by(role='admin').count()
    manager_users = User.query.filter_by(role='manager').count()
    normal_users = User.query.filter_by(role='user').count()
    
    # إحصائيات الحملات التسويقية
    total_campaigns = MarketingCampaign.query.count()
    active_campaigns = MarketingCampaign.query.filter_by(status='نشطة').count()
    completed_campaigns = MarketingCampaign.query.filter_by(status='مكتملة').count()
    
    # إحصائيات الرسائل التسويقية
    total_messages = MarketingMessage.query.count()
    email_messages = MarketingMessage.query.filter_by(type='email').count()
    whatsapp_messages = MarketingMessage.query.filter_by(type='whatsapp').count()
    social_messages = MarketingMessage.query.filter_by(type='social').count()
    
    # إحصائيات النشاطات
    recent_activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    
    return jsonify({
        'establishments': {
            'total': total_establishments,
            'by_region': region_stats,
            'by_type': type_stats
        },
        'users': {
            'total': total_users,
            'admin': admin_users,
            'manager': manager_users,
            'normal': normal_users
        },
        'marketing': {
            'campaigns': {
                'total': total_campaigns,
                'active': active_campaigns,
                'completed': completed_campaigns
            },
            'messages': {
                'total': total_messages,
                'email': email_messages,
                'whatsapp': whatsapp_messages,
                'social': social_messages
            }
        },
        'recent_activities': [activity.to_dict() for activity in recent_activities]
    }), 200

# إحصائيات المنشآت
@statistics_bp.route('/establishments', methods=['GET'])
@jwt_required()
def get_establishment_statistics():
    """الحصول على إحصائيات المنشآت"""
    
    # إحصائيات حسب المنطقة
    region_query = db.session.query(
        Region.name,
        db.func.count(Establishment.id).label('count')
    ).outerjoin(
        Establishment, Region.id == Establishment.region_id
    ).group_by(Region.name).all()
    
    region_stats = [{'region': r.name, 'count': r.count} for r in region_query]
    
    # إحصائيات حسب المدينة (أعلى 10 مدن)
    city_query = db.session.query(
        City.name,
        Region.name.label('region_name'),
        db.func.count(Establishment.id).label('count')
    ).outerjoin(
        Establishment, City.id == Establishment.city_id
    ).outerjoin(
        Region, City.region_id == Region.id
    ).group_by(City.name, Region.name).order_by(db.func.count(Establishment.id).desc()).limit(10).all()
    
    city_stats = [{'city': c.name, 'region': c.region_name, 'count': c.count} for c in city_query]
    
    # إحصائيات حسب نوع المنشأة
    type_query = db.session.query(
        EstablishmentType.name,
        db.func.count(Establishment.id).label('count')
    ).outerjoin(
        Establishment, EstablishmentType.id == Establishment.establishment_type_id
    ).group_by(EstablishmentType.name).all()
    
    type_stats = [{'type': t.name, 'count': t.count} for t in type_query]
    
    # إحصائيات حسب وجود البريد الإلكتروني والواتساب
    with_email = Establishment.query.filter(Establishment.email.isnot(None)).count()
    without_email = Establishment.query.filter(Establishment.email.is_(None)).count()
    with_whatsapp = Establishment.query.filter(Establishment.whatsapp.isnot(None)).count()
    without_whatsapp = Establishment.query.filter(Establishment.whatsapp.is_(None)).count()
    
    # إحصائيات حسب نوع الرخصة
    with_brokerage = Establishment.query.filter(Establishment.brokerage_license.isnot(None)).count()
    with_property_management = Establishment.query.filter(Establishment.property_management_license.isnot(None)).count()
    with_facility_management = Establishment.query.filter(Establishment.facility_management_license.isnot(None)).count()
    with_auction = Establishment.query.filter(Establishment.auction_license.isnot(None)).count()
    
    # إنشاء رسم بياني للمنشآت حسب المنطقة
    chart_data = {
        'region_chart': generate_region_chart(region_stats),
        'type_chart': generate_type_chart(type_stats)
    }
    
    return jsonify({
        'by_region': region_stats,
        'by_city': city_stats,
        'by_type': type_stats,
        'contact_info': {
            'with_email': with_email,
            'without_email': without_email,
            'with_whatsapp': with_whatsapp,
            'without_whatsapp': without_whatsapp
        },
        'licenses': {
            'brokerage': with_brokerage,
            'property_management': with_property_management,
            'facility_management': with_facility_management,
            'auction': with_auction
        },
        'charts': chart_data
    }), 200

# إحصائيات التسويق
@statistics_bp.route('/marketing', methods=['GET'])
@jwt_required()
def get_marketing_statistics():
    """الحصول على إحصائيات التسويق"""
    
    # إحصائيات الحملات حسب النوع
    campaign_type_query = db.session.query(
        MarketingCampaign.type,
        db.func.count(MarketingCampaign.id).label('count')
    ).group_by(MarketingCampaign.type).all()
    
    campaign_type_stats = [{'type': c.type, 'count': c.count} for c in campaign_type_query]
    
    # إحصائيات الحملات حسب الحالة
    campaign_status_query = db.session.query(
        MarketingCampaign.status,
        db.func.count(MarketingCampaign.id).label('count')
    ).group_by(MarketingCampaign.status).all()
    
    campaign_status_stats = [{'status': c.status, 'count': c.count} for c in campaign_status_query]
    
    # إحصائيات الرسائل حسب النوع
    message_type_query = db.session.query(
        MarketingMessage.type,
        db.func.count(MarketingMessage.id).label('count')
    ).group_by(MarketingMessage.type).all()
    
    message_type_stats = [{'type': m.type, 'count': m.count} for m in message_type_query]
    
    # إحصائيات التسليم حسب الحالة
    delivery_status_query = db.session.query(
        MarketingDelivery.status,
        db.func.count(MarketingDelivery.id).label('count')
    ).group_by(MarketingDelivery.status).all()
    
    delivery_status_stats = [{'status': d.status, 'count': d.count} for d in delivery_status_query]
    
    # إحصائيات الحملات الأخيرة
    recent_campaigns = MarketingCampaign.query.order_by(MarketingCampaign.created_at.desc()).limit(5).all()
    
    # إنشاء رسم بياني للحملات حسب النوع
    chart_data = {
        'campaign_type_chart': generate_campaign_type_chart(campaign_type_stats),
        'message_type_chart': generate_message_type_chart(message_type_stats)
    }
    
    return jsonify({
        'campaigns': {
            'by_type': campaign_type_stats,
            'by_status': campaign_status_stats,
            'recent': [campaign.to_dict() for campaign in recent_campaigns]
        },
        'messages': {
            'by_type': message_type_stats
        },
        'deliveries': {
            'by_status': delivery_status_stats
        },
        'charts': chart_data
    }), 200

# إحصائيات المستخدمين والنشاطات
@statistics_bp.route('/users-activities', methods=['GET'])
@jwt_required()
def get_users_activities_statistics():
    """الحصول على إحصائيات المستخدمين والنشاطات"""
    
    # إحصائيات المستخدمين حسب الدور
    user_role_query = db.session.query(
        User.role,
        db.func.count(User.id).label('count')
    ).group_by(User.role).all()
    
    user_role_stats = [{'role': u.role, 'count': u.count} for u in user_role_query]
    
    # إحصائيات النشاطات حسب النوع
    activity_type_query = db.session.query(
        ActivityLog.action,
        db.func.count(ActivityLog.id).label('count')
    ).group_by(ActivityLog.action).all()
    
    activity_type_stats = [{'action': a.action, 'count': a.count} for a in activity_type_query]
    
    # إحصائيات النشاطات حسب المستخدم (أعلى 10 مستخدمين نشاطًا)
    user_activity_query = db.session.query(
        User.username,
        User.role,
        db.func.count(ActivityLog.id).label('count')
    ).join(
        ActivityLog, User.id == ActivityLog.user_id
    ).group_by(User.username, User.role).order_by(db.func.count(ActivityLog.id).desc()).limit(10).all()
    
    user_activity_stats = [{'username': u.username, 'role': u.role, 'count': u.count} for u in user_activity_query]
    
    # إحصائيات النشاطات حسب اليوم (آخر 7 أيام)
    seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    
    daily_activity_query = db.session.query(
        db.func.date(ActivityLog.created_at).label('date'),
        db.func.count(ActivityLog.id).label('count')
    ).filter(
        ActivityLog.created_at >= seven_days_ago
    ).group_by(
        db.func.date(ActivityLog.created_at)
    ).order_by(
        db.func.date(ActivityLog.created_at)
    ).all()
    
    daily_activity_stats = [{'date': str(d.date), 'count': d.count} for d in daily_activity_query]
    
    # إنشاء رسم بياني للمستخدمين حسب الدور
    chart_data = {
        'user_role_chart': generate_user_role_chart(user_role_stats),
        'activity_type_chart': generate_activity_type_chart(activity_type_stats)
    }
    
    return jsonify({
        'users': {
            'by_role': user_role_stats,
            'most_active': user_activity_stats
        },
        'activities': {
            'by_type': activity_type_stats,
            'daily': daily_activity_stats
        },
        'charts': chart_data
    }), 200

# تقارير مخصصة
@statistics_bp.route('/custom-report', methods=['POST'])
@jwt_required()
def generate_custom_report():
    """إنشاء تقرير مخصص بناءً على معايير محددة"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'entity_type' not in data or 'criteria' not in data:
        return jsonify({'message': 'نوع الكيان ومعايير التقرير مطلوبة'}), 400
    
    entity_type = data['entity_type']
    criteria = data['criteria']
    
    # إنشاء التقرير حسب نوع الكيان
    if entity_type == 'establishments':
        return generate_establishments_report(criteria, current_user_id)
    elif entity_type == 'marketing':
        return generate_marketing_report(criteria, current_user_id)
    elif entity_type == 'users':
        return generate_users_report(criteria, current_user_id)
    else:
        return jsonify({'message': 'نوع الكيان غير مدعوم'}), 400

# تصدير البيانات
@statistics_bp.route('/export', methods=['POST'])
@jwt_required()
def export_data():
    """تصدير البيانات بتنسيق محدد"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'entity_type' not in data or 'format' not in data:
        return jsonify({'message': 'نوع الكيان وتنسيق التصدير مطلوبان'}), 400
    
    entity_type = data['entity_type']
    export_format = data['format']
    criteria = data.get('criteria', {})
    
    # تحديد مسار الملف المصدر
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    export_dir = '/home/ubuntu/crm_project/exports'
    os.makedirs(export_dir, exist_ok=True)
    
    # تصدير البيانات حسب نوع الكيان
    if entity_type == 'establishments':
        return export_establishments_data(export_format, criteria, export_dir, timestamp, current_user_id)
    elif entity_type == 'marketing':
        return export_marketing_data(export_format, criteria, export_dir, timestamp, current_user_id)
    elif entity_type == 'users':
        return export_users_data(export_format, criteria, export_dir, timestamp, current_user_id)
    else:
        return jsonify({'message': 'نوع الكيان غير مدعوم'}), 400

# دوال مساعدة لإنشاء الرسوم البيانية
def generate_region_chart(region_stats):
    """إنشاء رسم بياني للمنشآت حسب المنطقة"""
    plt.figure(figsize=(10, 6))
    
    # استخراج البيانات
    regions = [stat['region'] for stat in region_stats]
    counts = [stat['count'] for stat in region_stats]
    
    # إنشاء الرسم البياني
    plt.bar(regions, counts)
    plt.xlabel('المنطقة')
    plt.ylabel('عدد المنشآت')
    plt.title('توزيع المنشآت حسب المنطقة')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # تحويل الرسم البياني إلى صورة
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # تحويل الصورة إلى سلسلة Base64
    graphic = base64.b64encode(image_png).decode('utf-8')
    
    return graphic

def generate_type_chart(type_stats):
    """إنشاء رسم بياني للمنشآت حسب النوع"""
    plt.figure(figsize=(10, 6))
    
    # استخراج البيانات
    types = [stat['type'] for stat in type_stats]
    counts = [stat['count'] for stat in type_stats]
    
    # إنشاء الرسم البياني
    plt.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('توزيع المنشآت حسب النوع')
    plt.tight_layout()
    
    # تحويل الرسم البياني إلى صورة
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # تحويل الصورة إلى سلسلة Base64
    graphic = base64.b64encode(image_png).decode('utf-8')
    
    return graphic

def generate_campaign_type_chart(campaign_type_stats):
    """إنشاء رسم بياني للحملات حسب النوع"""
    plt.figure(figsize=(10, 6))
    
    # استخراج البيانات
    types = [stat['type'] for stat in campaign_type_stats]
    counts = [stat['count'] for stat in campaign_type_stats]
    
    # إنشاء الرسم البياني
    plt.bar(types, counts)
    plt.xlabel('نوع الحملة')
    plt.ylabel('العدد')
    plt.title('توزيع الحملات حسب النوع')
    plt.tight_layout()
    
    # تحويل الرسم البياني إلى صورة
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # تحويل الصورة إلى سلسلة Base64
    graphic = base64.b64encode(image_png).decode('utf-8')
    
    return graphic

def generate_message_type_chart(message_type_stats):
    """إنشاء رسم بياني للرسائل حسب النوع"""
    plt.figure(figsize=(10, 6))
    
    # استخراج البيانات
    types = [stat['type'] for stat in message_type_stats]
    counts = [stat['count'] for stat in message_type_stats]
    
    # إنشاء الرسم البياني
    plt.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('توزيع الرسائل حسب النوع')
    plt.tight_layout()
    
    # تحويل الرسم البياني إلى صورة
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # تحويل الصورة إلى سلسلة Base64
    graphic = base64.b64encode(image_png).decode('utf-8')
    
    return graphic

def generate_user_role_chart(user_role_stats):
    """إنشاء رسم بياني للمستخدمين حسب الدور"""
    plt.figure(figsize=(10, 6))
    
    # استخراج البيانات
    roles = [stat['role'] for stat in user_role_stats]
    counts = [stat['count'] for stat in user_role_stats]
    
    # إنشاء الرسم البياني
    plt.bar(roles, counts)
    plt.xlabel('الدور')
    plt.ylabel('العدد')
    plt.title('توزيع المستخدمين حسب الدور')
    plt.tight_layout()
    
    # تحويل الرسم البياني إلى صورة
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # تحويل الصورة إلى سلسلة Base64
    graphic = base64.b64encode(image_png).decode('utf-8')
    
    return graphic

def generate_activity_type_chart(activity_type_stats):
    """إنشاء رسم بياني للنشاطات حسب النوع"""
    plt.figure(figsize=(12, 6))
    
    # استخراج البيانات
    actions = [stat['action'] for stat in activity_type_stats]
    counts = [stat['count'] for stat in activity_type_stats]
    
    # إنشاء الرسم البياني
    plt.barh(actions, counts)
    plt.xlabel('العدد')
    plt.ylabel('نوع النشاط')
    plt.title('توزيع النشاطات حسب النوع')
    plt.tight_layout()
    
    # تحويل الرسم البياني إلى صورة
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # تحويل الصورة إلى سلسلة Base64
    graphic = base64.b64encode(image_png).decode('utf-8')
    
    return graphic

# دوال مساعدة لإنشاء التقارير المخصصة
def generate_establishments_report(criteria, user_id):
    """إنشاء تقرير مخصص للمنشآت"""
    # بناء استعلام للبحث عن المنشآت
    query = Establishment.query
    
    if 'region_id' in criteria and criteria['region_id']:
        query = query.filter_by(region_id=criteria['region_id'])
    
    if 'city_id' in criteria and criteria['city_id']:
        query = query.filter_by(city_id=criteria['city_id'])
    
    if 'establishment_type_id' in criteria and criteria['establishment_type_id']:
        query = query.filter_by(establishment_type_id=criteria['establishment_type_id'])
    
    if 'has_email' in criteria and criteria['has_email']:
        query = query.filter(Establishment.email.isnot(None))
    
    if 'has_whatsapp' in criteria and criteria['has_whatsapp']:
        query = query.filter(Establishment.whatsapp.isnot(None))
    
    # تنفيذ الاستعلام
    establishments = query.all()
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=user_id,
        action='إنشاء تقرير',
        entity_type='establishment',
        details=f'تم إنشاء تقرير مخصص للمنشآت يحتوي على {len(establishments)} منشأة',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم إنشاء التقرير بنجاح',
        'total': len(establishments),
        'establishments': [establishment.to_dict() for establishment in establishments]
    }), 200

def generate_marketing_report(criteria, user_id):
    """إنشاء تقرير مخصص للتسويق"""
    # بناء استعلام للبحث عن الحملات التسويقية
    query = MarketingCampaign.query
    
    if 'type' in criteria and criteria['type']:
        query = query.filter_by(type=criteria['type'])
    
    if 'status' in criteria and criteria['status']:
        query = query.filter_by(status=criteria['status'])
    
    if 'start_date' in criteria and criteria['start_date']:
        start_date = datetime.datetime.strptime(criteria['start_date'], '%Y-%m-%d')
        query = query.filter(MarketingCampaign.start_date >= start_date)
    
    if 'end_date' in criteria and criteria['end_date']:
        end_date = datetime.datetime.strptime(criteria['end_date'], '%Y-%m-%d')
        query = query.filter(MarketingCampaign.end_date <= end_date)
    
    # تنفيذ الاستعلام
    campaigns = query.all()
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=user_id,
        action='إنشاء تقرير',
        entity_type='marketing',
        details=f'تم إنشاء تقرير مخصص للتسويق يحتوي على {len(campaigns)} حملة',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم إنشاء التقرير بنجاح',
        'total': len(campaigns),
        'campaigns': [campaign.to_dict() for campaign in campaigns]
    }), 200

def generate_users_report(criteria, user_id):
    """إنشاء تقرير مخصص للمستخدمين"""
    # بناء استعلام للبحث عن المستخدمين
    query = User.query
    
    if 'role' in criteria and criteria['role']:
        query = query.filter_by(role=criteria['role'])
    
    if 'permission' in criteria and criteria['permission']:
        query = query.join(User.permissions).filter(Permission.name == criteria['permission'])
    
    # تنفيذ الاستعلام
    users = query.all()
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=user_id,
        action='إنشاء تقرير',
        entity_type='user',
        details=f'تم إنشاء تقرير مخصص للمستخدمين يحتوي على {len(users)} مستخدم',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم إنشاء التقرير بنجاح',
        'total': len(users),
        'users': [user.to_dict() for user in users]
    }), 200

# دوال مساعدة لتصدير البيانات
def export_establishments_data(export_format, criteria, export_dir, timestamp, user_id):
    """تصدير بيانات المنشآت"""
    # بناء استعلام للبحث عن المنشآت
    query = Establishment.query
    
    if 'region_id' in criteria and criteria['region_id']:
        query = query.filter_by(region_id=criteria['region_id'])
    
    if 'city_id' in criteria and criteria['city_id']:
        query = query.filter_by(city_id=criteria['city_id'])
    
    if 'establishment_type_id' in criteria and criteria['establishment_type_id']:
        query = query.filter_by(establishment_type_id=criteria['establishment_type_id'])
    
    # تنفيذ الاستعلام
    establishments = query.all()
    
    # تحويل البيانات إلى DataFrame
    data = []
    for establishment in establishments:
        data.append({
            'id': establishment.id,
            'name': establishment.name,
            'unified_number': establishment.unified_number,
            'mobile': establishment.mobile,
            'email': establishment.email,
            'region': establishment.region.name if establishment.region else None,
            'city': establishment.city.name if establishment.city else None,
            'district': establishment.district.name if establishment.district else None,
            'establishment_type': establishment.establishment_type.name if establishment.establishment_type else None,
            'brokerage_license': establishment.brokerage_license,
            'property_management_license': establishment.property_management_license,
            'facility_management_license': establishment.facility_management_license,
            'auction_license': establishment.auction_license,
            'real_estate_cooperation': establishment.real_estate_cooperation,
            'whatsapp': establishment.whatsapp,
            'campaign_type': establishment.campaign_type,
            'action_taken': establishment.action_taken,
            'created_at': establishment.created_at.strftime('%Y-%m-%d %H:%M:%S') if establishment.created_at else None
        })
    
    df = pd.DataFrame(data)
    
    # تصدير البيانات حسب التنسيق المطلوب
    if export_format == 'csv':
        file_path = f"{export_dir}/establishments_{timestamp}.csv"
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
    elif export_format == 'excel':
        file_path = f"{export_dir}/establishments_{timestamp}.xlsx"
        df.to_excel(file_path, index=False)
    elif export_format == 'json':
        file_path = f"{export_dir}/establishments_{timestamp}.json"
        df.to_json(file_path, orient='records', force_ascii=False)
    else:
        return jsonify({'message': 'تنسيق التصدير غير مدعوم'}), 400
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=user_id,
        action='تصدير بيانات',
        entity_type='establishment',
        details=f'تم تصدير بيانات {len(establishments)} منشأة بتنسيق {export_format}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم تصدير البيانات بنجاح',
        'file_path': file_path,
        'total_records': len(establishments)
    }), 200

def export_marketing_data(export_format, criteria, export_dir, timestamp, user_id):
    """تصدير بيانات التسويق"""
    # بناء استعلام للبحث عن الحملات التسويقية
    query = MarketingCampaign.query
    
    if 'type' in criteria and criteria['type']:
        query = query.filter_by(type=criteria['type'])
    
    if 'status' in criteria and criteria['status']:
        query = query.filter_by(status=criteria['status'])
    
    # تنفيذ الاستعلام
    campaigns = query.all()
    
    # تحويل البيانات إلى DataFrame
    data = []
    for campaign in campaigns:
        data.append({
            'id': campaign.id,
            'name': campaign.name,
            'type': campaign.type,
            'description': campaign.description,
            'status': campaign.status,
            'start_date': campaign.start_date.strftime('%Y-%m-%d') if campaign.start_date else None,
            'end_date': campaign.end_date.strftime('%Y-%m-%d') if campaign.end_date else None,
            'created_by': campaign.created_by,
            'created_at': campaign.created_at.strftime('%Y-%m-%d %H:%M:%S') if campaign.created_at else None
        })
    
    df = pd.DataFrame(data)
    
    # تصدير البيانات حسب التنسيق المطلوب
    if export_format == 'csv':
        file_path = f"{export_dir}/marketing_campaigns_{timestamp}.csv"
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
    elif export_format == 'excel':
        file_path = f"{export_dir}/marketing_campaigns_{timestamp}.xlsx"
        df.to_excel(file_path, index=False)
    elif export_format == 'json':
        file_path = f"{export_dir}/marketing_campaigns_{timestamp}.json"
        df.to_json(file_path, orient='records', force_ascii=False)
    else:
        return jsonify({'message': 'تنسيق التصدير غير مدعوم'}), 400
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=user_id,
        action='تصدير بيانات',
        entity_type='marketing',
        details=f'تم تصدير بيانات {len(campaigns)} حملة تسويقية بتنسيق {export_format}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم تصدير البيانات بنجاح',
        'file_path': file_path,
        'total_records': len(campaigns)
    }), 200

def export_users_data(export_format, criteria, export_dir, timestamp, user_id):
    """تصدير بيانات المستخدمين"""
    # بناء استعلام للبحث عن المستخدمين
    query = User.query
    
    if 'role' in criteria and criteria['role']:
        query = query.filter_by(role=criteria['role'])
    
    # تنفيذ الاستعلام
    users = query.all()
    
    # تحويل البيانات إلى DataFrame
    data = []
    for user in users:
        data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
            'permissions': ', '.join([p.name for p in user.permissions])
        })
    
    df = pd.DataFrame(data)
    
    # تصدير البيانات حسب التنسيق المطلوب
    if export_format == 'csv':
        file_path = f"{export_dir}/users_{timestamp}.csv"
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
    elif export_format == 'excel':
        file_path = f"{export_dir}/users_{timestamp}.xlsx"
        df.to_excel(file_path, index=False)
    elif export_format == 'json':
        file_path = f"{export_dir}/users_{timestamp}.json"
        df.to_json(file_path, orient='records', force_ascii=False)
    else:
        return jsonify({'message': 'تنسيق التصدير غير مدعوم'}), 400
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=user_id,
        action='تصدير بيانات',
        entity_type='user',
        details=f'تم تصدير بيانات {len(users)} مستخدم بتنسيق {export_format}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم تصدير البيانات بنجاح',
        'file_path': file_path,
        'total_records': len(users)
    }), 200

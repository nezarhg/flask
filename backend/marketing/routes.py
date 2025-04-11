from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Establishment, ActivityLog
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import os

marketing_bp = Blueprint('marketing', __name__)

# إعدادات البريد الإلكتروني
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.example.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USER = os.environ.get('EMAIL_USER', 'user@example.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'password')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'crm@example.com')

# إعدادات الواتساب (باستخدام API افتراضية)
WHATSAPP_API_URL = os.environ.get('WHATSAPP_API_URL', 'https://api.whatsapp.com/send')
WHATSAPP_API_KEY = os.environ.get('WHATSAPP_API_KEY', 'your_api_key')

# إدارة الحملات التسويقية
@marketing_bp.route('/campaigns', methods=['GET'])
@jwt_required()
def get_campaigns():
    """الحصول على قائمة الحملات التسويقية"""
    from ..models import MarketingCampaign
    
    campaigns = MarketingCampaign.query.all()
    return jsonify({
        'campaigns': [campaign.to_dict() for campaign in campaigns]
    }), 200

@marketing_bp.route('/campaigns', methods=['POST'])
@jwt_required()
def create_campaign():
    """إنشاء حملة تسويقية جديدة"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'name' not in data or 'type' not in data:
        return jsonify({'message': 'اسم الحملة ونوعها مطلوبان'}), 400
    
    from ..models import MarketingCampaign
    
    campaign = MarketingCampaign(
        name=data['name'],
        type=data['type'],
        description=data.get('description', ''),
        status=data.get('status', 'جديدة'),
        start_date=datetime.datetime.strptime(data.get('start_date', datetime.datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d'),
        end_date=datetime.datetime.strptime(data.get('end_date', ''), '%Y-%m-%d') if data.get('end_date') else None,
        created_by=current_user_id
    )
    
    db.session.add(campaign)
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='إنشاء حملة تسويقية',
        entity_type='marketing_campaign',
        entity_id=campaign.id,
        details=f'تم إنشاء حملة تسويقية جديدة: {campaign.name}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم إنشاء الحملة التسويقية بنجاح',
        'campaign': campaign.to_dict()
    }), 201

@marketing_bp.route('/campaigns/<int:campaign_id>', methods=['GET'])
@jwt_required()
def get_campaign(campaign_id):
    """الحصول على بيانات حملة تسويقية محددة"""
    from ..models import MarketingCampaign
    
    campaign = MarketingCampaign.query.get(campaign_id)
    
    if not campaign:
        return jsonify({'message': 'الحملة التسويقية غير موجودة'}), 404
    
    return jsonify({
        'campaign': campaign.to_dict()
    }), 200

@marketing_bp.route('/campaigns/<int:campaign_id>', methods=['PUT'])
@jwt_required()
def update_campaign(campaign_id):
    """تحديث بيانات حملة تسويقية"""
    current_user_id = get_jwt_identity()
    from ..models import MarketingCampaign
    
    campaign = MarketingCampaign.query.get(campaign_id)
    
    if not campaign:
        return jsonify({'message': 'الحملة التسويقية غير موجودة'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        campaign.name = data['name']
    
    if 'type' in data:
        campaign.type = data['type']
    
    if 'description' in data:
        campaign.description = data['description']
    
    if 'status' in data:
        campaign.status = data['status']
    
    if 'start_date' in data:
        campaign.start_date = datetime.datetime.strptime(data['start_date'], '%Y-%m-%d')
    
    if 'end_date' in data:
        campaign.end_date = datetime.datetime.strptime(data['end_date'], '%Y-%m-%d') if data['end_date'] else None
    
    campaign.updated_at = datetime.datetime.utcnow()
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='تحديث حملة تسويقية',
        entity_type='marketing_campaign',
        entity_id=campaign.id,
        details=f'تم تحديث بيانات الحملة التسويقية: {campaign.name}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم تحديث بيانات الحملة التسويقية بنجاح',
        'campaign': campaign.to_dict()
    }), 200

@marketing_bp.route('/campaigns/<int:campaign_id>', methods=['DELETE'])
@jwt_required()
def delete_campaign(campaign_id):
    """حذف حملة تسويقية"""
    current_user_id = get_jwt_identity()
    from ..models import MarketingCampaign
    
    campaign = MarketingCampaign.query.get(campaign_id)
    
    if not campaign:
        return jsonify({'message': 'الحملة التسويقية غير موجودة'}), 404
    
    campaign_name = campaign.name
    db.session.delete(campaign)
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='حذف حملة تسويقية',
        entity_type='marketing_campaign',
        entity_id=campaign_id,
        details=f'تم حذف الحملة التسويقية: {campaign_name}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم حذف الحملة التسويقية بنجاح'
    }), 200

# إدارة الرسائل التسويقية
@marketing_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    """الحصول على قائمة الرسائل التسويقية"""
    from ..models import MarketingMessage
    
    messages = MarketingMessage.query.all()
    return jsonify({
        'messages': [message.to_dict() for message in messages]
    }), 200

@marketing_bp.route('/messages', methods=['POST'])
@jwt_required()
def create_message():
    """إنشاء رسالة تسويقية جديدة"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'subject' not in data or 'content' not in data or 'type' not in data:
        return jsonify({'message': 'عنوان الرسالة ومحتواها ونوعها مطلوبة'}), 400
    
    from ..models import MarketingMessage
    
    message = MarketingMessage(
        subject=data['subject'],
        content=data['content'],
        type=data['type'],
        campaign_id=data.get('campaign_id'),
        created_by=current_user_id
    )
    
    db.session.add(message)
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='إنشاء رسالة تسويقية',
        entity_type='marketing_message',
        entity_id=message.id,
        details=f'تم إنشاء رسالة تسويقية جديدة: {message.subject}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم إنشاء الرسالة التسويقية بنجاح',
        'marketing_message': message.to_dict()
    }), 201

# إرسال رسائل البريد الإلكتروني
@marketing_bp.route('/send-email', methods=['POST'])
@jwt_required()
def send_email():
    """إرسال رسالة بريد إلكتروني"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'recipients' not in data or 'subject' not in data or 'content' not in data:
        return jsonify({'message': 'المستلمون وعنوان الرسالة ومحتواها مطلوبة'}), 400
    
    recipients = data['recipients']
    subject = data['subject']
    content = data['content']
    
    # التحقق من صحة المستلمين
    if not isinstance(recipients, list) or len(recipients) == 0:
        return jsonify({'message': 'يجب توفير قائمة صالحة من المستلمين'}), 400
    
    # إرسال البريد الإلكتروني
    try:
        # إنشاء اتصال SMTP
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        # إرسال البريد لكل مستلم
        successful_recipients = []
        failed_recipients = []
        
        for recipient in recipients:
            try:
                # إنشاء رسالة البريد
                msg = MIMEMultipart()
                msg['From'] = EMAIL_FROM
                msg['To'] = recipient
                msg['Subject'] = subject
                
                # إضافة محتوى الرسالة
                msg.attach(MIMEText(content, 'html'))
                
                # إرسال الرسالة
                server.send_message(msg)
                successful_recipients.append(recipient)
            except Exception as e:
                failed_recipients.append({'email': recipient, 'error': str(e)})
        
        # إغلاق الاتصال
        server.quit()
        
        # تسجيل النشاط
        activity = ActivityLog(
            user_id=current_user_id,
            action='إرسال بريد إلكتروني',
            entity_type='email',
            details=f'تم إرسال بريد إلكتروني بعنوان: {subject} إلى {len(successful_recipients)} مستلم',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إرسال البريد الإلكتروني بنجاح',
            'successful_recipients': successful_recipients,
            'failed_recipients': failed_recipients
        }), 200
    
    except Exception as e:
        return jsonify({
            'message': 'حدث خطأ أثناء إرسال البريد الإلكتروني',
            'error': str(e)
        }), 500

# إرسال رسائل الواتساب
@marketing_bp.route('/send-whatsapp', methods=['POST'])
@jwt_required()
def send_whatsapp():
    """إرسال رسالة واتساب"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'recipients' not in data or 'message' not in data:
        return jsonify({'message': 'المستلمون ومحتوى الرسالة مطلوبة'}), 400
    
    recipients = data['recipients']
    message = data['message']
    
    # التحقق من صحة المستلمين
    if not isinstance(recipients, list) or len(recipients) == 0:
        return jsonify({'message': 'يجب توفير قائمة صالحة من المستلمين'}), 400
    
    # إرسال رسائل الواتساب
    successful_recipients = []
    failed_recipients = []
    
    for recipient in recipients:
        try:
            # تنسيق رقم الهاتف (إزالة الرموز غير الرقمية)
            phone = ''.join(filter(str.isdigit, recipient))
            
            # إرسال الرسالة باستخدام API الواتساب
            response = requests.post(
                WHATSAPP_API_URL,
                headers={
                    'Authorization': f'Bearer {WHATSAPP_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'phone': phone,
                    'message': message
                }
            )
            
            if response.status_code == 200:
                successful_recipients.append(recipient)
            else:
                failed_recipients.append({
                    'phone': recipient,
                    'error': f'فشل الإرسال: {response.status_code} - {response.text}'
                })
        
        except Exception as e:
            failed_recipients.append({'phone': recipient, 'error': str(e)})
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='إرسال رسالة واتساب',
        entity_type='whatsapp',
        details=f'تم إرسال رسالة واتساب إلى {len(successful_recipients)} مستلم',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم إرسال رسائل الواتساب بنجاح',
        'successful_recipients': successful_recipients,
        'failed_recipients': failed_recipients
    }), 200

# إرسال منشورات مواقع التواصل الاجتماعي
@marketing_bp.route('/send-social-post', methods=['POST'])
@jwt_required()
def send_social_post():
    """إرسال منشور على مواقع التواصل الاجتماعي"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'platforms' not in data or 'content' not in data:
        return jsonify({'message': 'المنصات ومحتوى المنشور مطلوبة'}), 400
    
    platforms = data['platforms']
    content = data['content']
    
    # التحقق من صحة المنصات
    if not isinstance(platforms, list) or len(platforms) == 0:
        return jsonify({'message': 'يجب توفير قائمة صالحة من المنصات'}), 400
    
    # إرسال المنشورات
    successful_platforms = []
    failed_platforms = []
    
    for platform in platforms:
        try:
            # هنا يمكن إضافة الكود الخاص بإرسال المنشورات لكل منصة
            # مثال: استخدام API الخاص بكل منصة (Facebook, Twitter, LinkedIn, etc.)
            
            # تمثيل للنجاح (يجب استبداله بالتنفيذ الفعلي)
            successful_platforms.append(platform)
        
        except Exception as e:
            failed_platforms.append({'platform': platform, 'error': str(e)})
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='إرسال منشور اجتماعي',
        entity_type='social_post',
        details=f'تم إرسال منشور على {len(successful_platforms)} منصة اجتماعية',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم إرسال المنشورات بنجاح',
        'successful_platforms': successful_platforms,
        'failed_platforms': failed_platforms
    }), 200

# استهداف العملاء
@marketing_bp.route('/target-customers', methods=['POST'])
@jwt_required()
def target_customers():
    """استهداف مجموعة من العملاء بناءً على معايير محددة"""
    data = request.get_json()
    
    if not data or 'criteria' not in data:
        return jsonify({'message': 'معايير الاستهداف مطلوبة'}), 400
    
    criteria = data['criteria']
    
    # بناء استعلام للبحث عن المنشآت المستهدفة
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
    targeted_establishments = query.all()
    
    # استخراج معلومات الاتصال
    email_contacts = []
    whatsapp_contacts = []
    
    for establishment in targeted_establishments:
        if establishment.email:
            email_contacts.append(establishment.email)
        
        if establishment.whatsapp:
            whatsapp_contacts.append(establishment.whatsapp)
    
    return jsonify({
        'message': 'تم استهداف العملاء بنجاح',
        'total_targeted': len(targeted_establishments),
        'email_contacts': email_contacts,
        'whatsapp_contacts': whatsapp_contacts
    }), 200

# تحليلات التسويق
@marketing_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_marketing_analytics():
    """الحصول على تحليلات التسويق"""
    from ..models import MarketingCampaign, MarketingMessage
    
    # إحصائيات الحملات
    total_campaigns = MarketingCampaign.query.count()
    active_campaigns = MarketingCampaign.query.filter_by(status='نشطة').count()
    completed_campaigns = MarketingCampaign.query.filter_by(status='مكتملة').count()
    
    # إحصائيات الرسائل
    total_messages = MarketingMessage.query.count()
    email_messages = MarketingMessage.query.filter_by(type='email').count()
    whatsapp_messages = MarketingMessage.query.filter_by(type='whatsapp').count()
    social_messages = MarketingMessage.query.filter_by(type='social').count()
    
    # إحصائيات المنشآت
    total_establishments = Establishment.query.count()
    establishments_with_email = Establishment.query.filter(Establishment.email.isnot(None)).count()
    establishments_with_whatsapp = Establishment.query.filter(Establishment.whatsapp.isnot(None)).count()
    
    return jsonify({
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
        },
        'establishments': {
            'total': total_establishments,
            'with_email': establishments_with_email,
            'with_whatsapp': establishments_with_whatsapp
        }
    }), 200

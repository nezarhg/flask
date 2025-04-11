from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Establishment, User, ActivityLog, Region, City, District, EstablishmentType
from ..marketing.models import MarketingCampaign, MarketingMessage, MarketingDelivery
import datetime
import json
import uuid

api_bp = Blueprint('api', __name__)

# توثيق API
@api_bp.route('/docs', methods=['GET'])
def get_api_docs():
    """الحصول على توثيق واجهات برمجة التطبيقات"""
    
    docs = {
        "api_version": "1.0.0",
        "title": "CRM API للتكامل مع تطبيقات الأتمتة",
        "description": "واجهات برمجية للتكامل مع تطبيقات الأتمتة مثل n8n وZapier وMake",
        "base_url": "/api/v1",
        "authentication": {
            "type": "Bearer Token",
            "description": "يجب إرفاق رمز الوصول في ترويسة Authorization بتنسيق: Bearer {token}"
        },
        "endpoints": {
            "establishments": {
                "get_all": {
                    "method": "GET",
                    "path": "/establishments",
                    "description": "الحصول على قائمة المنشآت",
                    "parameters": {
                        "page": "رقم الصفحة (افتراضي: 1)",
                        "per_page": "عدد العناصر في الصفحة (افتراضي: 20)",
                        "search": "نص البحث",
                        "region_id": "معرف المنطقة",
                        "city_id": "معرف المدينة",
                        "establishment_type_id": "معرف نوع المنشأة"
                    }
                },
                "get_one": {
                    "method": "GET",
                    "path": "/establishments/{id}",
                    "description": "الحصول على بيانات منشأة محددة",
                    "parameters": {
                        "id": "معرف المنشأة"
                    }
                },
                "create": {
                    "method": "POST",
                    "path": "/establishments",
                    "description": "إنشاء منشأة جديدة",
                    "body": {
                        "name": "اسم المنشأة (مطلوب)",
                        "unified_number": "الرقم الموحد للمنشأة",
                        "mobile": "رقم الجوال",
                        "email": "البريد الإلكتروني",
                        "region_id": "معرف المنطقة",
                        "city_id": "معرف المدينة",
                        "district_id": "معرف الحي",
                        "establishment_type_id": "معرف نوع المنشأة",
                        "brokerage_license": "رخصة الوساطة والتسويق",
                        "property_management_license": "رخصة إدارة الأملاك",
                        "facility_management_license": "رخصة إدارة المرافق",
                        "auction_license": "رخصة المزادات",
                        "real_estate_cooperation": "التعاون العقاري",
                        "whatsapp": "رقم الواتساب",
                        "campaign_type": "نوع الحملة",
                        "action_taken": "الإجراء المتخذ"
                    }
                },
                "update": {
                    "method": "PUT",
                    "path": "/establishments/{id}",
                    "description": "تحديث بيانات منشأة",
                    "parameters": {
                        "id": "معرف المنشأة"
                    },
                    "body": "نفس حقول إنشاء المنشأة"
                },
                "delete": {
                    "method": "DELETE",
                    "path": "/establishments/{id}",
                    "description": "حذف منشأة",
                    "parameters": {
                        "id": "معرف المنشأة"
                    }
                }
            },
            "marketing": {
                "campaigns": {
                    "get_all": {
                        "method": "GET",
                        "path": "/marketing/campaigns",
                        "description": "الحصول على قائمة الحملات التسويقية",
                        "parameters": {
                            "page": "رقم الصفحة (افتراضي: 1)",
                            "per_page": "عدد العناصر في الصفحة (افتراضي: 20)",
                            "status": "حالة الحملة (جديدة، نشطة، متوقفة، مكتملة)",
                            "type": "نوع الحملة (email, whatsapp, social, mixed)"
                        }
                    },
                    "get_one": {
                        "method": "GET",
                        "path": "/marketing/campaigns/{id}",
                        "description": "الحصول على بيانات حملة تسويقية محددة",
                        "parameters": {
                            "id": "معرف الحملة"
                        }
                    },
                    "create": {
                        "method": "POST",
                        "path": "/marketing/campaigns",
                        "description": "إنشاء حملة تسويقية جديدة",
                        "body": {
                            "name": "اسم الحملة (مطلوب)",
                            "type": "نوع الحملة (مطلوب)",
                            "description": "وصف الحملة",
                            "status": "حالة الحملة",
                            "start_date": "تاريخ البدء (YYYY-MM-DD)",
                            "end_date": "تاريخ الانتهاء (YYYY-MM-DD)"
                        }
                    }
                },
                "messages": {
                    "get_all": {
                        "method": "GET",
                        "path": "/marketing/messages",
                        "description": "الحصول على قائمة الرسائل التسويقية",
                        "parameters": {
                            "page": "رقم الصفحة (افتراضي: 1)",
                            "per_page": "عدد العناصر في الصفحة (افتراضي: 20)",
                            "type": "نوع الرسالة (email, whatsapp, social)",
                            "campaign_id": "معرف الحملة"
                        }
                    },
                    "create": {
                        "method": "POST",
                        "path": "/marketing/messages",
                        "description": "إنشاء رسالة تسويقية جديدة",
                        "body": {
                            "subject": "عنوان الرسالة (مطلوب)",
                            "content": "محتوى الرسالة (مطلوب)",
                            "type": "نوع الرسالة (مطلوب)",
                            "campaign_id": "معرف الحملة"
                        }
                    },
                    "send_email": {
                        "method": "POST",
                        "path": "/marketing/send-email",
                        "description": "إرسال رسالة بريد إلكتروني",
                        "body": {
                            "recipients": "قائمة بعناوين البريد الإلكتروني (مطلوب)",
                            "subject": "عنوان الرسالة (مطلوب)",
                            "content": "محتوى الرسالة (مطلوب)"
                        }
                    },
                    "send_whatsapp": {
                        "method": "POST",
                        "path": "/marketing/send-whatsapp",
                        "description": "إرسال رسالة واتساب",
                        "body": {
                            "recipients": "قائمة بأرقام الهواتف (مطلوب)",
                            "message": "محتوى الرسالة (مطلوب)"
                        }
                    }
                }
            },
            "statistics": {
                "dashboard": {
                    "method": "GET",
                    "path": "/statistics/dashboard",
                    "description": "الحصول على إحصائيات لوحة التحكم الرئيسية"
                },
                "establishments": {
                    "method": "GET",
                    "path": "/statistics/establishments",
                    "description": "الحصول على إحصائيات المنشآت"
                },
                "marketing": {
                    "method": "GET",
                    "path": "/statistics/marketing",
                    "description": "الحصول على إحصائيات التسويق"
                },
                "users_activities": {
                    "method": "GET",
                    "path": "/statistics/users-activities",
                    "description": "الحصول على إحصائيات المستخدمين والنشاطات"
                },
                "custom_report": {
                    "method": "POST",
                    "path": "/statistics/custom-report",
                    "description": "إنشاء تقرير مخصص",
                    "body": {
                        "entity_type": "نوع الكيان (establishments, marketing, users)",
                        "criteria": "معايير التقرير"
                    }
                },
                "export": {
                    "method": "POST",
                    "path": "/statistics/export",
                    "description": "تصدير البيانات",
                    "body": {
                        "entity_type": "نوع الكيان (establishments, marketing, users)",
                        "format": "تنسيق التصدير (csv, excel, json)",
                        "criteria": "معايير التصدير"
                    }
                }
            },
            "webhooks": {
                "register": {
                    "method": "POST",
                    "path": "/webhooks/register",
                    "description": "تسجيل webhook جديد",
                    "body": {
                        "event_type": "نوع الحدث (مطلوب)",
                        "target_url": "عنوان URL المستهدف (مطلوب)",
                        "description": "وصف الـ webhook"
                    }
                },
                "list": {
                    "method": "GET",
                    "path": "/webhooks",
                    "description": "الحصول على قائمة الـ webhooks المسجلة"
                },
                "delete": {
                    "method": "DELETE",
                    "path": "/webhooks/{id}",
                    "description": "حذف webhook",
                    "parameters": {
                        "id": "معرف الـ webhook"
                    }
                }
            },
            "reference_data": {
                "regions": {
                    "method": "GET",
                    "path": "/reference/regions",
                    "description": "الحصول على قائمة المناطق"
                },
                "cities": {
                    "method": "GET",
                    "path": "/reference/cities",
                    "description": "الحصول على قائمة المدن",
                    "parameters": {
                        "region_id": "معرف المنطقة (اختياري)"
                    }
                },
                "districts": {
                    "method": "GET",
                    "path": "/reference/districts",
                    "description": "الحصول على قائمة الأحياء",
                    "parameters": {
                        "city_id": "معرف المدينة (اختياري)"
                    }
                },
                "establishment_types": {
                    "method": "GET",
                    "path": "/reference/establishment-types",
                    "description": "الحصول على قائمة أنواع المنشآت"
                }
            }
        }
    }
    
    return jsonify(docs), 200

# واجهات برمجة المنشآت
@api_bp.route('/establishments', methods=['GET'])
@jwt_required()
def get_establishments():
    """الحصول على قائمة المنشآت"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    region_id = request.args.get('region_id', type=int)
    city_id = request.args.get('city_id', type=int)
    establishment_type_id = request.args.get('establishment_type_id', type=int)
    
    # بناء الاستعلام
    query = Establishment.query
    
    if search:
        query = query.filter(Establishment.name.ilike(f'%{search}%'))
    
    if region_id:
        query = query.filter_by(region_id=region_id)
    
    if city_id:
        query = query.filter_by(city_id=city_id)
    
    if establishment_type_id:
        query = query.filter_by(establishment_type_id=establishment_type_id)
    
    # تنفيذ الاستعلام مع التصفح
    pagination = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'establishments': [establishment.to_dict() for establishment in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
        'per_page': per_page
    }), 200

@api_bp.route('/establishments/<int:id>', methods=['GET'])
@jwt_required()
def get_establishment(id):
    """الحصول على بيانات منشأة محددة"""
    establishment = Establishment.query.get(id)
    
    if not establishment:
        return jsonify({'message': 'المنشأة غير موجودة'}), 404
    
    return jsonify({
        'establishment': establishment.to_dict()
    }), 200

@api_bp.route('/establishments', methods=['POST'])
@jwt_required()
def create_establishment():
    """إنشاء منشأة جديدة"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'message': 'اسم المنشأة مطلوب'}), 400
    
    establishment = Establishment(
        name=data['name'],
        unified_number=data.get('unified_number'),
        mobile=data.get('mobile'),
        email=data.get('email'),
        region_id=data.get('region_id'),
        city_id=data.get('city_id'),
        district_id=data.get('district_id'),
        establishment_type_id=data.get('establishment_type_id'),
        brokerage_license=data.get('brokerage_license'),
        property_management_license=data.get('property_management_license'),
        facility_management_license=data.get('facility_management_license'),
        auction_license=data.get('auction_license'),
        real_estate_cooperation=data.get('real_estate_cooperation'),
        whatsapp=data.get('whatsapp'),
        campaign_type=data.get('campaign_type'),
        action_taken=data.get('action_taken')
    )
    
    db.session.add(establishment)
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='إنشاء منشأة',
        entity_type='establishment',
        entity_id=establishment.id,
        details=f'تم إنشاء منشأة جديدة: {establishment.name}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    # إرسال إشعار webhook
    trigger_webhook('establishment_created', establishment.to_dict())
    
    return jsonify({
        'message': 'تم إنشاء المنشأة بنجاح',
        'establishment': establishment.to_dict()
    }), 201

@api_bp.route('/establishments/<int:id>', methods=['PUT'])
@jwt_required()
def update_establishment(id):
    """تحديث بيانات منشأة"""
    current_user_id = get_jwt_identity()
    establishment = Establishment.query.get(id)
    
    if not establishment:
        return jsonify({'message': 'المنشأة غير موجودة'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        establishment.name = data['name']
    
    if 'unified_number' in data:
        establishment.unified_number = data['unified_number']
    
    if 'mobile' in data:
        establishment.mobile = data['mobile']
    
    if 'email' in data:
        establishment.email = data['email']
    
    if 'region_id' in data:
        establishment.region_id = data['region_id']
    
    if 'city_id' in data:
        establishment.city_id = data['city_id']
    
    if 'district_id' in data:
        establishment.district_id = data['district_id']
    
    if 'establishment_type_id' in data:
        establishment.establishment_type_id = data['establishment_type_id']
    
    if 'brokerage_license' in data:
        establishment.brokerage_license = data['brokerage_license']
    
    if 'property_management_license' in data:
        establishment.property_management_license = data['property_management_license']
    
    if 'facility_management_license' in data:
        establishment.facility_management_license = data['facility_management_license']
    
    if 'auction_license' in data:
        establishment.auction_license = data['auction_license']
    
    if 'real_estate_cooperation' in data:
        establishment.real_estate_cooperation = data['real_estate_cooperation']
    
    if 'whatsapp' in data:
        establishment.whatsapp = data['whatsapp']
    
    if 'campaign_type' in data:
        establishment.campaign_type = data['campaign_type']
    
    if 'action_taken' in data:
        establishment.action_taken = data['action_taken']
    
    establishment.updated_at = datetime.datetime.utcnow()
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='تحديث منشأة',
        entity_type='establishment',
        entity_id=establishment.id,
        details=f'تم تحديث بيانات المنشأة: {establishment.name}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    # إرسال إشعار webhook
    trigger_webhook('establishment_updated', establishment.to_dict())
    
    return jsonify({
        'message': 'تم تحديث بيانات المنشأة بنجاح',
        'establishment': establishment.to_dict()
    }), 200

@api_bp.route('/establishments/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_establishment(id):
    """حذف منشأة"""
    current_user_id = get_jwt_identity()
    establishment = Establishment.query.get(id)
    
    if not establishment:
        return jsonify({'message': 'المنشأة غير موجودة'}), 404
    
    establishment_name = establishment.name
    establishment_data = establishment.to_dict()
    
    db.session.delete(establishment)
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='حذف منشأة',
        entity_type='establishment',
        entity_id=id,
        details=f'تم حذف المنشأة: {establishment_name}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    # إرسال إشعار webhook
    trigger_webhook('establishment_deleted', establishment_data)
    
    return jsonify({
        'message': 'تم حذف المنشأة بنجاح'
    }), 200

# واجهات برمجة البيانات المرجعية
@api_bp.route('/reference/regions', methods=['GET'])
@jwt_required()
def get_regions():
    """الحصول على قائمة المناطق"""
    regions = Region.query.all()
    
    return jsonify({
        'regions': [region.to_dict() for region in regions]
    }), 200

@api_bp.route('/reference/cities', methods=['GET'])
@jwt_required()
def get_cities():
    """الحصول على قائمة المدن"""
    region_id = request.args.get('region_id', type=int)
    
    query = City.query
    
    if region_id:
        query = query.filter_by(region_id=region_id)
    
    cities = query.all()
    
    return jsonify({
        'cities': [city.to_dict() for city in cities]
    }), 200

@api_bp.route('/reference/districts', methods=['GET'])
@jwt_required()
def get_districts():
    """الحصول على قائمة الأحياء"""
    city_id = request.args.get('city_id', type=int)
    
    query = District.query
    
    if city_id:
        query = query.filter_by(city_id=city_id)
    
    districts = query.all()
    
    return jsonify({
        'districts': [district.to_dict() for district in districts]
    }), 200

@api_bp.route('/reference/establishment-types', methods=['GET'])
@jwt_required()
def get_establishment_types():
    """الحصول على قائمة أنواع المنشآت"""
    types = EstablishmentType.query.all()
    
    return jsonify({
        'types': [type_item.to_dict() for type_item in types]
    }), 200

# واجهات برمجة الـ Webhooks
@api_bp.route('/webhooks/register', methods=['POST'])
@jwt_required()
def register_webhook():
    """تسجيل webhook جديد"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'event_type' not in data or 'target_url' not in data:
        return jsonify({'message': 'نوع الحدث وعنوان URL المستهدف مطلوبان'}), 400
    
    from ..models import Webhook
    
    webhook = Webhook(
        id=str(uuid.uuid4()),
        event_type=data['event_type'],
        target_url=data['target_url'],
        description=data.get('description', ''),
        created_by=current_user_id
    )
    
    db.session.add(webhook)
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='تسجيل webhook',
        entity_type='webhook',
        entity_id=webhook.id,
        details=f'تم تسجيل webhook جديد لحدث: {webhook.event_type}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم تسجيل الـ webhook بنجاح',
        'webhook': webhook.to_dict()
    }), 201

@api_bp.route('/webhooks', methods=['GET'])
@jwt_required()
def get_webhooks():
    """الحصول على قائمة الـ webhooks المسجلة"""
    from ..models import Webhook
    
    webhooks = Webhook.query.all()
    
    return jsonify({
        'webhooks': [webhook.to_dict() for webhook in webhooks]
    }), 200

@api_bp.route('/webhooks/<string:id>', methods=['DELETE'])
@jwt_required()
def delete_webhook(id):
    """حذف webhook"""
    current_user_id = get_jwt_identity()
    from ..models import Webhook
    
    webhook = Webhook.query.get(id)
    
    if not webhook:
        return jsonify({'message': 'الـ webhook غير موجود'}), 404
    
    webhook_event_type = webhook.event_type
    
    db.session.delete(webhook)
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='حذف webhook',
        entity_type='webhook',
        entity_id=id,
        details=f'تم حذف webhook لحدث: {webhook_event_type}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم حذف الـ webhook بنجاح'
    }), 200

# دوال مساعدة
def trigger_webhook(event_type, data):
    """إرسال إشعار webhook"""
    from ..models import Webhook
    import requests
    
    webhooks = Webhook.query.filter_by(event_type=event_type).all()
    
    for webhook in webhooks:
        try:
            payload = {
                'event_type': event_type,
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'data': data
            }
            
            # إرسال الإشعار بشكل غير متزامن
            requests.post(
                webhook.target_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            # تحديث آخر استدعاء ناجح
            webhook.last_triggered = datetime.datetime.utcnow()
            webhook.status = 'active'
            db.session.commit()
            
        except Exception as e:
            # تسجيل الخطأ
            webhook.status = 'error'
            webhook.last_error = str(e)
            db.session.commit()

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, Establishment, Region, City, District, EstablishmentType, DataEntryProject, Statistic, ActivityLog
import datetime

admin_bp = Blueprint('admin', __name__)

# إدارة المناطق
@admin_bp.route('/regions', methods=['GET'])
@jwt_required()
def get_regions():
    """الحصول على قائمة المناطق"""
    regions = Region.query.all()
    return jsonify({
        'regions': [region.to_dict() for region in regions]
    }), 200

@admin_bp.route('/regions', methods=['POST'])
@jwt_required()
def create_region():
    """إنشاء منطقة جديدة"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'message': 'اسم المنطقة مطلوب'}), 400
    
    # التحقق من عدم وجود منطقة بنفس الاسم
    if Region.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'المنطقة موجودة بالفعل'}), 400
    
    region = Region(name=data['name'])
    db.session.add(region)
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='إنشاء منطقة',
        entity_type='region',
        entity_id=region.id,
        details=f'تم إنشاء منطقة جديدة: {region.name}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم إنشاء المنطقة بنجاح',
        'region': region.to_dict()
    }), 201

@admin_bp.route('/regions/<int:region_id>', methods=['PUT'])
@jwt_required()
def update_region(region_id):
    """تحديث منطقة"""
    current_user_id = get_jwt_identity()
    region = Region.query.get(region_id)
    
    if not region:
        return jsonify({'message': 'المنطقة غير موجودة'}), 404
    
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'message': 'اسم المنطقة مطلوب'}), 400
    
    # التحقق من عدم وجود منطقة أخرى بنفس الاسم
    existing_region = Region.query.filter_by(name=data['name']).first()
    if existing_region and existing_region.id != region_id:
        return jsonify({'message': 'يوجد منطقة أخرى بنفس الاسم'}), 400
    
    old_name = region.name
    region.name = data['name']
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='تحديث منطقة',
        entity_type='region',
        entity_id=region.id,
        details=f'تم تحديث المنطقة من: {old_name} إلى: {region.name}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم تحديث المنطقة بنجاح',
        'region': region.to_dict()
    }), 200

@admin_bp.route('/regions/<int:region_id>', methods=['DELETE'])
@jwt_required()
def delete_region(region_id):
    """حذف منطقة"""
    current_user_id = get_jwt_identity()
    region = Region.query.get(region_id)
    
    if not region:
        return jsonify({'message': 'المنطقة غير موجودة'}), 404
    
    # التحقق من عدم وجود مدن مرتبطة بالمنطقة
    if City.query.filter_by(region_id=region_id).first():
        return jsonify({'message': 'لا يمكن حذف المنطقة لأنها تحتوي على مدن'}), 400
    
    # التحقق من عدم وجود منشآت مرتبطة بالمنطقة
    if Establishment.query.filter_by(region_id=region_id).first():
        return jsonify({'message': 'لا يمكن حذف المنطقة لأنها تحتوي على منشآت'}), 400
    
    region_name = region.name
    db.session.delete(region)
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='حذف منطقة',
        entity_type='region',
        entity_id=region_id,
        details=f'تم حذف المنطقة: {region_name}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم حذف المنطقة بنجاح'
    }), 200

# إدارة المدن
@admin_bp.route('/cities', methods=['GET'])
@jwt_required()
def get_cities():
    """الحصول على قائمة المدن"""
    region_id = request.args.get('region_id', type=int)
    
    if region_id:
        cities = City.query.filter_by(region_id=region_id).all()
    else:
        cities = City.query.all()
    
    return jsonify({
        'cities': [city.to_dict() for city in cities]
    }), 200

@admin_bp.route('/cities', methods=['POST'])
@jwt_required()
def create_city():
    """إنشاء مدينة جديدة"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'name' not in data or 'region_id' not in data:
        return jsonify({'message': 'اسم المدينة والمنطقة مطلوبان'}), 400
    
    # التحقق من وجود المنطقة
    region = Region.query.get(data['region_id'])
    if not region:
        return jsonify({'message': 'المنطقة غير موجودة'}), 404
    
    # التحقق من عدم وجود مدينة بنفس الاسم في نفس المنطقة
    if City.query.filter_by(name=data['name'], region_id=data['region_id']).first():
        return jsonify({'message': 'المدينة موجودة بالفعل في هذه المنطقة'}), 400
    
    city = City(name=data['name'], region_id=data['region_id'])
    db.session.add(city)
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='إنشاء مدينة',
        entity_type='city',
        entity_id=city.id,
        details=f'تم إنشاء مدينة جديدة: {city.name} في منطقة: {region.name}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم إنشاء المدينة بنجاح',
        'city': city.to_dict()
    }), 201

# إدارة المنشآت
@admin_bp.route('/establishments', methods=['GET'])
@jwt_required()
def get_establishments():
    """الحصول على قائمة المنشآت مع دعم التصفية والبحث"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    region_id = request.args.get('region_id', type=int)
    city_id = request.args.get('city_id', type=int)
    district_id = request.args.get('district_id', type=int)
    establishment_type_id = request.args.get('establishment_type_id', type=int)
    search = request.args.get('search', '')
    
    # بناء الاستعلام مع التصفية
    query = Establishment.query
    
    if region_id:
        query = query.filter_by(region_id=region_id)
    
    if city_id:
        query = query.filter_by(city_id=city_id)
    
    if district_id:
        query = query.filter_by(district_id=district_id)
    
    if establishment_type_id:
        query = query.filter_by(establishment_type_id=establishment_type_id)
    
    if search:
        query = query.filter(Establishment.name.ilike(f'%{search}%'))
    
    # تنفيذ الاستعلام مع التقسيم إلى صفحات
    paginated_establishments = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'establishments': [establishment.to_dict() for establishment in paginated_establishments.items],
        'total': paginated_establishments.total,
        'pages': paginated_establishments.pages,
        'current_page': page
    }), 200

@admin_bp.route('/establishments/<int:establishment_id>', methods=['GET'])
@jwt_required()
def get_establishment(establishment_id):
    """الحصول على بيانات منشأة محددة"""
    establishment = Establishment.query.get(establishment_id)
    
    if not establishment:
        return jsonify({'message': 'المنشأة غير موجودة'}), 404
    
    return jsonify({
        'establishment': establishment.to_dict()
    }), 200

@admin_bp.route('/establishments', methods=['POST'])
@jwt_required()
def create_establishment():
    """إنشاء منشأة جديدة"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # التحقق من البيانات المطلوبة
    required_fields = ['name']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'الحقل {field} مطلوب'}), 400
    
    # التحقق من عدم وجود منشأة بنفس الرقم الموحد (إذا تم توفيره)
    if 'unified_number' in data and data['unified_number']:
        if Establishment.query.filter_by(unified_number=data['unified_number']).first():
            return jsonify({'message': 'يوجد منشأة أخرى بنفس الرقم الموحد'}), 400
    
    # إنشاء المنشأة الجديدة
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
        action_taken=data.get('action_taken'),
        created_by=current_user_id
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
    
    return jsonify({
        'message': 'تم إنشاء المنشأة بنجاح',
        'establishment': establishment.to_dict()
    }), 201

@admin_bp.route('/establishments/<int:establishment_id>', methods=['PUT'])
@jwt_required()
def update_establishment(establishment_id):
    """تحديث بيانات منشأة"""
    current_user_id = get_jwt_identity()
    establishment = Establishment.query.get(establishment_id)
    
    if not establishment:
        return jsonify({'message': 'المنشأة غير موجودة'}), 404
    
    data = request.get_json()
    
    # التحقق من عدم وجود منشأة أخرى بنفس الرقم الموحد (إذا تم تغييره)
    if 'unified_number' in data and data['unified_number'] and data['unified_number'] != establishment.unified_number:
        existing_establishment = Establishment.query.filter_by(unified_number=data['unified_number']).first()
        if existing_establishment and existing_establishment.id != establishment_id:
            return jsonify({'message': 'يوجد منشأة أخرى بنفس الرقم الموحد'}), 400
    
    # تحديث بيانات المنشأة
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
    
    return jsonify({
        'message': 'تم تحديث بيانات المنشأة بنجاح',
        'establishment': establishment.to_dict()
    }), 200

@admin_bp.route('/establishments/<int:establishment_id>', methods=['DELETE'])
@jwt_required()
def delete_establishment(establishment_id):
    """حذف منشأة"""
    current_user_id = get_jwt_identity()
    establishment = Establishment.query.get(establishment_id)
    
    if not establishment:
        return jsonify({'message': 'المنشأة غير موجودة'}), 404
    
    establishment_name = establishment.name
    db.session.delete(establishment)
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='حذف منشأة',
        entity_type='establishment',
        entity_id=establishment_id,
        details=f'تم حذف المنشأة: {establishment_name}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'تم حذف المنشأة بنجاح'
    }), 200

# إدارة مشاريع إدخال البيانات
@admin_bp.route('/data-entry-projects', methods=['GET'])
@jwt_required()
def get_data_entry_projects():
    """الحصول على قائمة مشاريع إدخال البيانات"""
    projects = DataEntryProject.query.all()
    return jsonify({
        'projects': [project.to_dict() for project in projects]
    }), 200

@admin_bp.route('/data-entry-projects/<int:project_id>', methods=['GET'])
@jwt_required()
def get_data_entry_project(project_id):
    """الحصول على بيانات مشروع إدخال بيانات محدد"""
    project = DataEntryProject.query.get(project_id)
    
    if not project:
        return jsonify({'message': 'المشروع غير موجود'}), 404
    
    return jsonify({
        'project': project.to_dict()
    }), 200

# إدارة الإحصائيات
@admin_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """الحصول على الإحصائيات العامة للنظام"""
    # إحصائيات المنشآت حسب المنطقة
    regions = Region.query.all()
    region_stats = []
    
    for region in regions:
        count = Establishment.query.filter_by(region_id=region.id).count()
        region_stats.append({
            'region': region.name,
            'count': count
        })
    
    # إحصائيات المنشآت حسب النوع
    types = EstablishmentType.query.all()
    type_stats = []
    
    for type_item in types:
        count = Establishment.query.filter_by(establishment_type_id=type_item.id).count()
        type_stats.append({
            'type': type_item.name,
            'count': count
        })
    
    # إحصائيات مشاريع إدخال البيانات
    projects_count = DataEntryProject.query.count()
    completed_projects_count = DataEntryProject.query.filter_by(status='منتهي').count()
    in_progress_projects_count = DataEntryProject.query.filter_by(status='جاري').count()
    not_started_projects_count = DataEntryProject.query.filter_by(status='لم يبدأ').count()
    
    # إحصائيات المستخدمين
    users_count = User.query.count()
    admin_users_count = User.query.filter_by(role='admin').count()
    manager_users_count = User.query.filter_by(role='manager').count()
    normal_users_count = User.query.filter_by(role='user').count()
    
    return jsonify({
        'establishments': {
            'total': Establishment.query.count(),
            'by_region': region_stats,
            'by_type': type_stats
        },
        'projects': {
            'total': projects_count,
            'completed': completed_projects_count,
            'in_progress': in_progress_projects_count,
            'not_started': not_started_projects_count
        },
        'users': {
            'total': users_count,
            'admin': admin_users_count,
            'manager': manager_users_count,
            'normal': normal_users_count
        }
    }), 200

# سجل النشاطات
@admin_bp.route('/activity-logs', methods=['GET'])
@jwt_required()
def get_activity_logs():
    """الحصول على سجل النشاطات"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    entity_type = request.args.get('entity_type')
    action = request.args.get('action')
    
    # بناء الاستعلام مع التصفية
    query = ActivityLog.query.order_by(ActivityLog.created_at.desc())
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if entity_type:
        query = query.filter_by(entity_type=entity_type)
    
    if action:
        query = query.filter_by(action=action)
    
    # تنفيذ الاستعلام مع التقسيم إلى صفحات
    paginated_logs = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'logs': [log.to_dict() for log in paginated_logs.items],
        'total': paginated_logs.total,
        'pages': paginated_logs.pages,
        'current_page': page
    }), 200

# مزامنة البيانات
@admin_bp.route('/sync-data', methods=['POST'])
@jwt_required()
def sync_data():
    """مزامنة البيانات من ملفات خارجية"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'source' not in data:
        return jsonify({'message': 'مصدر البيانات مطلوب'}), 400
    
    # تسجيل النشاط
    activity = ActivityLog(
        user_id=current_user_id,
        action='مزامنة البيانات',
        entity_type='system',
        details=f'تم بدء عملية مزامنة البيانات من المصدر: {data["source"]}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
    
    # هنا سيتم تنفيذ عملية المزامنة الفعلية (سيتم تنفيذها لاحقًا)
    
    return jsonify({
        'message': 'تم بدء عملية مزامنة البيانات بنجاح',
        'status': 'pending'
    }), 200

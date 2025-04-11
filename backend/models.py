from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from datetime import datetime
import bcrypt

db = SQLAlchemy()
jwt = JWTManager()

# جدول العلاقة بين المستخدمين والصلاحيات
user_permissions = db.Table('user_permissions',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, manager, user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # العلاقة مع جدول الصلاحيات
    permissions = db.relationship('Permission', secondary=user_permissions, lazy='subquery',
                                 backref=db.backref('users', lazy=True))
    
    # العلاقة مع جدول سجل النشاطات
    activities = db.relationship('ActivityLog', backref='user', lazy=True)
    
    # العلاقة مع جدول المنشآت
    establishments = db.relationship('Establishment', backref='creator', lazy=True)
    
    def set_password(self, password):
        """تشفير كلمة المرور"""
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    def to_dict(self):
        """تحويل بيانات المستخدم إلى قاموس"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'permissions': [p.name for p in self.permissions]
        }

class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    def to_dict(self):
        """تحويل بيانات الصلاحية إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class Region(db.Model):
    __tablename__ = 'regions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # العلاقات
    cities = db.relationship('City', backref='region', lazy=True)
    establishments = db.relationship('Establishment', backref='region', lazy=True)
    data_entry_projects = db.relationship('DataEntryProject', backref='region', lazy=True)
    statistics = db.relationship('Statistic', backref='region', lazy=True)
    
    def to_dict(self):
        """تحويل بيانات المنطقة إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name
        }

class City(db.Model):
    __tablename__ = 'cities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=True)
    
    # العلاقات
    districts = db.relationship('District', backref='city', lazy=True)
    establishments = db.relationship('Establishment', backref='city', lazy=True)
    data_entry_projects = db.relationship('DataEntryProject', backref='city', lazy=True)
    
    __table_args__ = (db.UniqueConstraint('name', 'region_id', name='_city_region_uc'),)
    
    def to_dict(self):
        """تحويل بيانات المدينة إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name,
            'region_id': self.region_id
        }

class District(db.Model):
    __tablename__ = 'districts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)
    
    # العلاقات
    establishments = db.relationship('Establishment', backref='district', lazy=True)
    
    __table_args__ = (db.UniqueConstraint('name', 'city_id', name='_district_city_uc'),)
    
    def to_dict(self):
        """تحويل بيانات الحي إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name,
            'city_id': self.city_id
        }

class EstablishmentType(db.Model):
    __tablename__ = 'establishment_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # العلاقات
    establishments = db.relationship('Establishment', backref='establishment_type', lazy=True)
    
    def to_dict(self):
        """تحويل بيانات نوع المنشأة إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name
        }

class Establishment(db.Model):
    __tablename__ = 'establishments'
    
    id = db.Column(db.Integer, primary_key=True)
    unified_number = db.Column(db.BigInteger, unique=True)
    name = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(100))
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'))
    establishment_type_id = db.Column(db.Integer, db.ForeignKey('establishment_types.id'))
    brokerage_license = db.Column(db.String(50))
    property_management_license = db.Column(db.String(50))
    facility_management_license = db.Column(db.String(50))
    auction_license = db.Column(db.String(50))
    real_estate_cooperation = db.Column(db.String(100))
    whatsapp = db.Column(db.String(20))
    campaign_type = db.Column(db.String(100))
    action_taken = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        """تحويل بيانات المنشأة إلى قاموس"""
        return {
            'id': self.id,
            'unified_number': self.unified_number,
            'name': self.name,
            'mobile': self.mobile,
            'email': self.email,
            'region_id': self.region_id,
            'city_id': self.city_id,
            'district_id': self.district_id,
            'establishment_type_id': self.establishment_type_id,
            'brokerage_license': self.brokerage_license,
            'property_management_license': self.property_management_license,
            'facility_management_license': self.facility_management_license,
            'auction_license': self.auction_license,
            'real_estate_cooperation': self.real_estate_cooperation,
            'whatsapp': self.whatsapp,
            'campaign_type': self.campaign_type,
            'action_taken': self.action_taken,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }

class DataEntryProject(db.Model):
    __tablename__ = 'data_entry_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String(100), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False)  # منتهي، جاري، لم يبدأ
    marketing_status = db.Column(db.String(50))  # جاهز، غير جاهز
    responsible = db.Column(db.String(100))
    current_count = db.Column(db.Integer, default=0)
    nizar_entry_count = db.Column(db.Integer, default=0)
    asmaa_entry_count = db.Column(db.Integer, default=0)
    total_entry_count = db.Column(db.Integer, default=0)
    difference = db.Column(db.Integer, default=0)
    asmaa_entitlement = db.Column(db.Integer, default=0)
    non_entered_value = db.Column(db.Float, default=0)
    pricing = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """تحويل بيانات مشروع إدخال المنشآت إلى قاموس"""
        return {
            'id': self.id,
            'entity': self.entity,
            'region_id': self.region_id,
            'city_id': self.city_id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'marketing_status': self.marketing_status,
            'responsible': self.responsible,
            'current_count': self.current_count,
            'nizar_entry_count': self.nizar_entry_count,
            'asmaa_entry_count': self.asmaa_entry_count,
            'total_entry_count': self.total_entry_count,
            'difference': self.difference,
            'asmaa_entitlement': self.asmaa_entitlement,
            'non_entered_value': self.non_entered_value,
            'pricing': self.pricing,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Statistic(db.Model):
    __tablename__ = 'statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))
    count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """تحويل بيانات الإحصائية إلى قاموس"""
        return {
            'id': self.id,
            'region_id': self.region_id,
            'count': self.count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """تحويل بيانات سجل النشاط إلى قاموس"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """تحويل بيانات الإعداد إلى قاموس"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config
from .models import db, jwt

def create_app():
    """إنشاء وتهيئة تطبيق Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # تهيئة الإضافات
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    
    # تسجيل النماذج
    with app.app_context():
        # استيراد نماذج التسويق
        from .marketing.models import MarketingCampaign, MarketingMessage, MarketingDelivery
        # استيراد نموذج Webhook
        from .api.models import Webhook
        
        db.create_all()
        
        # إنشاء مستخدم مسؤول افتراضي إذا لم يكن موجودًا
        from .models import User, Permission
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                full_name='مدير النظام',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            
            # إنشاء الصلاحيات الأساسية
            permissions = [
                Permission(name='user_create', description='إنشاء مستخدمين جدد'),
                Permission(name='user_read', description='عرض بيانات المستخدمين'),
                Permission(name='user_update', description='تعديل بيانات المستخدمين'),
                Permission(name='user_delete', description='حذف المستخدمين'),
                Permission(name='establishment_create', description='إنشاء منشآت جديدة'),
                Permission(name='establishment_read', description='عرض بيانات المنشآت'),
                Permission(name='establishment_update', description='تعديل بيانات المنشآت'),
                Permission(name='establishment_delete', description='حذف المنشآت'),
                Permission(name='project_manage', description='إدارة مشاريع إدخال البيانات'),
                Permission(name='statistics_view', description='عرض الإحصائيات'),
                Permission(name='settings_manage', description='إدارة إعدادات النظام'),
                Permission(name='marketing_manage', description='إدارة التسويق'),
                Permission(name='api_access', description='الوصول إلى واجهات برمجة التطبيقات'),
                Permission(name='ai_assistant_use', description='استخدام مساعد الذكاء الاصطناعي'),
                Permission(name='data_import_export', description='استيراد وتصدير البيانات')
            ]
            
            for permission in permissions:
                db.session.add(permission)
                admin_user.permissions.append(permission)
                
            db.session.commit()
    
    # تسجيل النماذج
    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # تسجيل نموذج لوحة تحكم المسؤول
    from .admin.routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # تسجيل نموذج التسويق
    from .marketing.routes import marketing_bp
    app.register_blueprint(marketing_bp, url_prefix='/api/marketing')
    
    # تسجيل نموذج الإحصائيات
    from .statistics.routes import statistics_bp
    app.register_blueprint(statistics_bp, url_prefix='/api/statistics')
    
    # تسجيل نموذج واجهات برمجة التطبيقات للتكامل
    from .api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # تسجيل نموذج مساعد الذكاء الاصطناعي
    from .ai_assistant.routes import ai_assistant_bp
    app.register_blueprint(ai_assistant_bp, url_prefix='/api/ai-assistant')
    
    # تسجيل نموذج استيراد وتصدير البيانات
    from .data_import.routes import data_import_bp
    app.register_blueprint(data_import_bp, url_prefix='/api/data')
    
    return app

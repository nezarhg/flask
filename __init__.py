# تكوين CORS للسماح بالاتصال بين الواجهة الأمامية والخلفية
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # تكوين CORS للسماح بالاتصال من أي مصدر في بيئة التطوير
    # في بيئة الإنتاج، يجب تحديد المصادر المسموح بها
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # تحميل الإعدادات من ملف config.py
    app.config.from_pyfile('config.py')
    
    # تسجيل النماذج وإعداد قاعدة البيانات
    from .models import db, jwt
    db.init_app(app)
    jwt.init_app(app)
    
    # إنشاء جميع الجداول إذا لم تكن موجودة
    with app.app_context():
        db.create_all()
    
    # تسجيل مسارات API
    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # تسجيل مسارات المسؤول
    from .admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # تسجيل مسارات التسويق
    from .marketing import marketing_bp
    app.register_blueprint(marketing_bp, url_prefix='/api/marketing')
    
    # تسجيل مسارات الإحصائيات
    from .statistics import statistics_bp
    app.register_blueprint(statistics_bp, url_prefix='/api/statistics')
    
    # تسجيل مسارات المساعد الذكي
    from .ai_assistant import ai_assistant_bp
    app.register_blueprint(ai_assistant_bp, url_prefix='/api/ai-assistant')
    
    # تسجيل مسارات استيراد البيانات
    from .data_import import data_import_bp
    app.register_blueprint(data_import_bp, url_prefix='/api/data-import')
    
    # مسار الصفحة الرئيسية
    @app.route('/')
    def index():
        return {"message": "مرحبًا بك في واجهة برمجة تطبيقات نظام E-deal لإدارة علاقات العملاء"}
    
    return app

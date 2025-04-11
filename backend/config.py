import os
from datetime import timedelta

class Config:
    # إعدادات التطبيق
    APP_NAME = 'E-deal'
    
    # إعدادات قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '../edeal.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # إعدادات الأمان
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'مفتاح_سري_آمن_للتطوير'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'مفتاح_سري_آمن_للتطوير_jwt'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # إعدادات CORS
    CORS_HEADERS = 'Content-Type'

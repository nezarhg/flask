import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية من ملف .env إذا كان موجودًا
load_dotenv()

# إعدادات قاعدة البيانات
# استخدام متغير بيئي DATABASE_URL إذا كان موجودًا (مثل في Render)
# وإلا استخدام قاعدة بيانات SQLite محلية
DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///edeal.db')

# إذا كان DATABASE_URL يبدأ بـ postgres:// (كما في Render)، قم بتحويله إلى postgresql://
if DATABASE_URI and DATABASE_URI.startswith('postgres://'):
    DATABASE_URI = DATABASE_URI.replace('postgres://', 'postgresql://', 1)

# المفتاح السري للتطبيق
SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key_change_in_production')

# مفتاح JWT
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt_dev_key_change_in_production')

# مدة صلاحية رمز JWT (بالدقائق)
JWT_ACCESS_TOKEN_EXPIRES = 60 * 24  # 24 ساعة

# إعدادات CORS
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

# وضع التطبيق (تطوير أو إنتاج)
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == 'development'

# مجلد التحميلات
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# الحد الأقصى لحجم الملف المرفوع (5 ميجابايت)
MAX_CONTENT_LENGTH = 5 * 1024 * 1024

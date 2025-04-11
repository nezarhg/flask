# دليل نشر تطبيق E-deal

هذا الدليل يشرح كيفية نشر تطبيق E-deal لإدارة علاقات العملاء على بيئة إنتاجية.

## متطلبات النظام

- نظام تشغيل: Linux (Ubuntu 20.04 أو أحدث) أو Windows Server
- Python 3.8 أو أحدث
- Node.js 14 أو أحدث
- قاعدة بيانات: SQLite (للبيئات الصغيرة) أو PostgreSQL/MySQL (للبيئات الإنتاجية)
- وصول للإنترنت (لتثبيت الحزم والمكتبات)

## خطوات النشر

### 1. إعداد البيئة

```bash
# تثبيت المتطلبات الأساسية
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm

# إنشاء بيئة افتراضية لـ Python
python3 -m venv venv
source venv/bin/activate

# تثبيت حزم Python المطلوبة
pip install -r requirements.txt

# تثبيت حزم Node.js المطلوبة للواجهة الأمامية
cd frontend
npm install
```

### 2. إعداد قاعدة البيانات

#### للاستخدام مع SQLite (الإعداد الافتراضي)
لا يلزم إجراء أي تغييرات إضافية، حيث سيتم إنشاء ملف قاعدة البيانات تلقائيًا.

#### للاستخدام مع PostgreSQL
```bash
# تثبيت PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# إنشاء قاعدة بيانات ومستخدم
sudo -u postgres psql -c "CREATE DATABASE edeal;"
sudo -u postgres psql -c "CREATE USER edealuser WITH PASSWORD 'password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE edeal TO edealuser;"

# تعديل ملف config.py
# تغيير SQLALCHEMY_DATABASE_URI إلى:
# SQLALCHEMY_DATABASE_URI = 'postgresql://edealuser:password@localhost/edeal'
```

### 3. بناء الواجهة الأمامية

```bash
cd frontend
npm run build
```

### 4. تهيئة قاعدة البيانات

```bash
cd ..
python3 -c "from backend import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 5. إنشاء مستخدم المسؤول الأول

```bash
python3 create_admin.py
```

### 6. تشغيل التطبيق

#### للتشغيل المباشر (مناسب للاختبار)

```bash
python3 app.py
```

#### للتشغيل في بيئة الإنتاج (باستخدام Gunicorn و Nginx)

```bash
# تثبيت Gunicorn
pip install gunicorn

# إنشاء ملف خدمة systemd
sudo nano /etc/systemd/system/edeal.service

# محتوى الملف:
# [Unit]
# Description=E-deal CRM Application
# After=network.target
# 
# [Service]
# User=ubuntu
# WorkingDirectory=/path/to/crm_project
# ExecStart=/path/to/crm_project/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
# Restart=always
# 
# [Install]
# WantedBy=multi-user.target

# تفعيل وتشغيل الخدمة
sudo systemctl daemon-reload
sudo systemctl enable edeal
sudo systemctl start edeal

# تثبيت وإعداد Nginx
sudo apt install -y nginx
sudo nano /etc/nginx/sites-available/edeal

# محتوى الملف:
# server {
#     listen 80;
#     server_name your_domain.com;
# 
#     location / {
#         proxy_pass http://127.0.0.1:5000;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#     }
# 
#     location /static {
#         alias /path/to/crm_project/frontend/build/static;
#     }
# }

# تفعيل الموقع وإعادة تشغيل Nginx
sudo ln -s /etc/nginx/sites-available/edeal /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

## ملاحظات هامة للنشر

1. **الأمان**: تأكد من تغيير كلمات المرور الافتراضية وتعيين مفاتيح سرية قوية في ملف config.py
2. **النسخ الاحتياطي**: قم بإعداد نظام للنسخ الاحتياطي المنتظم لقاعدة البيانات
3. **HTTPS**: للاستخدام في بيئة الإنتاج، يجب تفعيل HTTPS باستخدام Let's Encrypt
4. **المراقبة**: قم بإعداد نظام مراقبة للتطبيق للتنبيه في حالة حدوث أخطاء

## استكشاف الأخطاء وإصلاحها

### مشكلات قاعدة البيانات
- تأكد من صحة إعدادات الاتصال بقاعدة البيانات في ملف config.py
- تحقق من وجود الصلاحيات المناسبة للمستخدم

### مشكلات الواجهة الأمامية
- تأكد من اكتمال عملية البناء بنجاح
- تحقق من إعدادات CORS إذا كانت الواجهة الأمامية والخلفية على خوادم مختلفة

### مشكلات الخادم
- تحقق من سجلات الخطأ: `sudo journalctl -u edeal.service`
- تأكد من فتح المنافذ المطلوبة في جدار الحماية

## التحديثات المستقبلية

لتحديث التطبيق في المستقبل:

1. قم بعمل نسخة احتياطية من قاعدة البيانات
2. اسحب التغييرات الجديدة من مستودع الكود
3. قم بتحديث حزم Python و Node.js
4. أعد بناء الواجهة الأمامية
5. قم بتحديث هيكل قاعدة البيانات إذا لزم الأمر
6. أعد تشغيل الخدمة: `sudo systemctl restart edeal`

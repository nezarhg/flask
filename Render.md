# دليل النشر على منصة Render باستخدام GitHub

## المقدمة

هذا الدليل يشرح كيفية نشر تطبيق Flask على منصة Render باستخدام مستودع GitHub. سنتناول الخطوات اللازمة لتجنب المشاكل الشائعة في عملية النشر، خاصة تلك المتعلقة بهيكل المشروع وملفات التكوين.

## هيكل المشروع الصحيح

من أهم الأسباب التي تؤدي إلى فشل عملية النشر هو عدم تطابق هيكل المشروع مع ما تتوقعه منصة Render. يجب أن تكون الملفات الرئيسية موجودة في المجلد الرئيسي للمشروع:

```
/                   # المجلد الرئيسي للمشروع (الجذر)
├── app.py          # ملف التطبيق الرئيسي
├── requirements.txt # قائمة المكتبات المطلوبة
├── Procfile        # ملف تكوين لتحديد كيفية تشغيل التطبيق
├── render.yaml     # ملف تكوين Render (اختياري)
└── ...             # ملفات ومجلدات أخرى
```

## الملفات الأساسية المطلوبة للنشر

### 1. ملف `app.py`

هذا هو ملف التطبيق الرئيسي الذي يحتوي على تعريف تطبيق Flask. يجب أن يكون موجودًا في المجلد الرئيسي للمشروع.

### 2. ملف `requirements.txt`

يحتوي على قائمة المكتبات المطلوبة للتطبيق. يجب أن يكون موجودًا في المجلد الرئيسي للمشروع.

### 3. ملف `Procfile`

يحدد كيفية تشغيل التطبيق. المحتوى النموذجي لهذا الملف هو:

```
web: gunicorn app:app
```

حيث `app:app` تعني:
- الجزء الأول `app` هو اسم الملف (app.py بدون امتداد .py)
- الجزء الثاني `app` هو اسم متغير تطبيق Flask في ذلك الملف

### 4. ملف `render.yaml` (اختياري)

يوفر تكوينًا إضافيًا لمنصة Render. مثال:

```yaml
services:
  - type: web
    name: edeal-crm
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true
```

## خطوات النشر على منصة Render

### 1. تجهيز المشروع

1. تأكد من أن هيكل المشروع صحيح كما هو موضح أعلاه.
2. تأكد من وجود ملفات `app.py` و `requirements.txt` و `Procfile` في المجلد الرئيسي.
3. تأكد من أن ملف `requirements.txt` يحتوي على جميع المكتبات المطلوبة، بما في ذلك `gunicorn`.

### 2. رفع المشروع إلى GitHub

1. قم بإنشاء مستودع جديد على GitHub.
2. قم برفع المشروع إلى المستودع:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/username/repository-name.git
git push -u origin main
```

### 3. النشر على منصة Render

1. قم بإنشاء حساب على منصة [Render](https://render.com/) إذا لم يكن لديك حساب.
2. انقر على زر "New" واختر "Web Service".
3. اختر "Build and deploy from a Git repository".
4. اربط حسابك على GitHub واختر المستودع الذي قمت برفع المشروع إليه.
5. قم بتكوين الخدمة:
   - **Name**: اسم الخدمة (مثل edeal-crm)
   - **Environment**: Python
   - **Region**: اختر المنطقة الأقرب إليك
   - **Branch**: main (أو الفرع الذي ترغب في النشر منه)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. قم بإضافة متغيرات البيئة المطلوبة (Environment Variables) إذا كان التطبيق يحتاج إليها.
7. انقر على زر "Create Web Service" لبدء عملية النشر.

## حل المشاكل الشائعة

### مشكلة: خطأ في تشغيل Gunicorn

إذا ظهرت رسالة خطأ مثل:

```
Error: Failed to find application object 'app' in 'app'
```

الحلول المحتملة:
1. تأكد من أن ملف `app.py` موجود في المجلد الرئيسي للمشروع.
2. تأكد من أن متغير تطبيق Flask مسمى `app` في ملف `app.py`.
3. إذا كان اسم الملف أو المتغير مختلفًا، قم بتعديل ملف `Procfile` ليعكس الاسم الصحيح.

### مشكلة: خطأ في تثبيت المكتبات

إذا فشلت عملية تثبيت المكتبات، تأكد من:
1. أن ملف `requirements.txt` موجود في المجلد الرئيسي.
2. أن الإصدارات المحددة للمكتبات متوافقة مع بعضها البعض.
3. أن جميع المكتبات المطلوبة مدرجة في الملف.

## نصائح إضافية

1. **استخدام ملف .env**: إذا كان التطبيق يستخدم ملف `.env` للمتغيرات البيئية، تأكد من إضافة هذه المتغيرات في إعدادات الخدمة على Render.
2. **مراقبة السجلات**: بعد النشر، راقب سجلات التطبيق على Render للتحقق من أي أخطاء.
3. **تكوين المجال المخصص**: يمكنك إعداد مجال مخصص للخدمة من خلال إعدادات Render.

## الخلاصة

باتباع هذا الدليل، يمكنك تجنب المشاكل الشائعة في نشر تطبيقات Flask على منصة Render باستخدام GitHub. تذكر دائمًا أن هيكل المشروع الصحيح وملفات التكوين المناسبة هي مفتاح النجاح في عملية النشر.

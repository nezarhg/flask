import os
import pandas as pd
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from ..models import db, Establishment, EstablishmentType, Region, City
from flask_jwt_extended import jwt_required, get_jwt_identity

data_import_bp = Blueprint('data_import', __name__)

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@data_import_bp.route('/import/establishments', methods=['POST'])
@jwt_required()
def import_establishments():
    """استيراد بيانات المنشآت من ملف Excel أو CSV"""
    # التحقق من وجود الملف في الطلب
    if 'file' not in request.files:
        return jsonify({'error': 'لم يتم تحميل أي ملف'}), 400
    
    file = request.files['file']
    
    # التحقق من اسم الملف
    if file.filename == '':
        return jsonify({'error': 'لم يتم اختيار ملف'}), 400
    
    # التحقق من نوع الملف
    if not allowed_file(file.filename):
        return jsonify({'error': 'نوع الملف غير مسموح به. الأنواع المسموح بها: xlsx, xls, csv'}), 400
    
    # حفظ الملف مؤقتًا
    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.root_path, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    try:
        # قراءة الملف حسب نوعه
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # تحويل أسماء الأعمدة إلى أسماء قياسية
        column_mapping = {
            'اسم المنشأة': 'name',
            'الرقم الموحد': 'unified_number',
            'المنطقة': 'region',
            'المدينة': 'city',
            'نوع المنشأة': 'establishment_type',
            'رقم الجوال': 'mobile',
            'البريد الإلكتروني': 'email',
            'العنوان': 'address',
            'الموقع الإلكتروني': 'website',
            'ملاحظات': 'notes'
        }
        
        # تحديد الأعمدة الموجودة في الملف
        available_columns = {}
        for ar_col, en_col in column_mapping.items():
            if ar_col in df.columns:
                available_columns[ar_col] = en_col
        
        # إعادة تسمية الأعمدة
        df = df.rename(columns=available_columns)
        
        # تحضير البيانات للإدخال
        imported_count = 0
        updated_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # التحقق من وجود البيانات الإلزامية
                if 'name' not in df.columns or pd.isna(row['name']):
                    errors.append(f"الصف {index+2}: اسم المنشأة مطلوب")
                    continue
                
                # البحث عن المنشأة الحالية أو إنشاء منشأة جديدة
                establishment = None
                if 'unified_number' in df.columns and not pd.isna(row['unified_number']):
                    establishment = Establishment.query.filter_by(unified_number=row['unified_number']).first()
                
                if establishment is None:
                    establishment = Establishment.query.filter_by(name=row['name']).first()
                
                is_new = establishment is None
                if is_new:
                    establishment = Establishment()
                    establishment.name = row['name']
                
                # تعيين الرقم الموحد إذا كان موجودًا
                if 'unified_number' in df.columns and not pd.isna(row['unified_number']):
                    establishment.unified_number = str(row['unified_number'])
                
                # معالجة المنطقة
                if 'region' in df.columns and not pd.isna(row['region']):
                    region = Region.query.filter_by(name=row['region']).first()
                    if region is None:
                        region = Region(name=row['region'])
                        db.session.add(region)
                        db.session.flush()
                    establishment.region_id = region.id
                
                # معالجة المدينة
                if 'city' in df.columns and not pd.isna(row['city']):
                    city = City.query.filter_by(name=row['city']).first()
                    if city is None and establishment.region_id:
                        city = City(name=row['city'], region_id=establishment.region_id)
                        db.session.add(city)
                        db.session.flush()
                    if city:
                        establishment.city_id = city.id
                
                # معالجة نوع المنشأة
                if 'establishment_type' in df.columns and not pd.isna(row['establishment_type']):
                    est_type = EstablishmentType.query.filter_by(name=row['establishment_type']).first()
                    if est_type is None:
                        est_type = EstablishmentType(name=row['establishment_type'])
                        db.session.add(est_type)
                        db.session.flush()
                    establishment.establishment_type_id = est_type.id
                
                # تعيين بيانات الاتصال
                if 'mobile' in df.columns and not pd.isna(row['mobile']):
                    establishment.mobile = str(row['mobile'])
                
                if 'email' in df.columns and not pd.isna(row['email']):
                    establishment.email = row['email']
                
                if 'address' in df.columns and not pd.isna(row['address']):
                    establishment.address = row['address']
                
                if 'website' in df.columns and not pd.isna(row['website']):
                    establishment.website = row['website']
                
                if 'notes' in df.columns and not pd.isna(row['notes']):
                    establishment.notes = row['notes']
                
                # حفظ المنشأة
                if is_new:
                    db.session.add(establishment)
                    imported_count += 1
                else:
                    updated_count += 1
                
                db.session.flush()
                
            except Exception as e:
                errors.append(f"الصف {index+2}: {str(e)}")
        
        # حفظ التغييرات في قاعدة البيانات
        db.session.commit()
        
        # حذف الملف المؤقت
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'imported_count': imported_count,
            'updated_count': updated_count,
            'errors': errors
        })
        
    except Exception as e:
        # حذف الملف المؤقت في حالة حدوث خطأ
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({'error': f'حدث خطأ أثناء معالجة الملف: {str(e)}'}), 500

@data_import_bp.route('/export/establishments', methods=['POST'])
@jwt_required()
def export_establishments():
    """تصدير بيانات المنشآت إلى ملف Excel أو CSV"""
    # استلام معايير التصفية
    data = request.get_json()
    file_format = data.get('format', 'xlsx')
    criteria = data.get('criteria', {})
    
    # التحقق من صحة تنسيق الملف
    if file_format not in ['xlsx', 'csv']:
        return jsonify({'error': 'تنسيق الملف غير صالح. التنسيقات المدعومة: xlsx, csv'}), 400
    
    try:
        # بناء الاستعلام
        query = Establishment.query
        
        if 'region_id' in criteria and criteria['region_id']:
            query = query.filter(Establishment.region_id == criteria['region_id'])
        
        if 'city_id' in criteria and criteria['city_id']:
            query = query.filter(Establishment.city_id == criteria['city_id'])
        
        if 'establishment_type_id' in criteria and criteria['establishment_type_id']:
            query = query.filter(Establishment.establishment_type_id == criteria['establishment_type_id'])
        
        if 'search' in criteria and criteria['search']:
            search_term = f"%{criteria['search']}%"
            query = query.filter(Establishment.name.like(search_term) | 
                                Establishment.unified_number.like(search_term) |
                                Establishment.email.like(search_term) |
                                Establishment.mobile.like(search_term))
        
        # تنفيذ الاستعلام
        establishments = query.all()
        
        # تحضير البيانات للتصدير
        data = []
        for est in establishments:
            region = Region.query.get(est.region_id) if est.region_id else None
            city = City.query.get(est.city_id) if est.city_id else None
            est_type = EstablishmentType.query.get(est.establishment_type_id) if est.establishment_type_id else None
            
            data.append({
                'اسم المنشأة': est.name,
                'الرقم الموحد': est.unified_number,
                'المنطقة': region.name if region else '',
                'المدينة': city.name if city else '',
                'نوع المنشأة': est_type.name if est_type else '',
                'رقم الجوال': est.mobile,
                'البريد الإلكتروني': est.email,
                'العنوان': est.address,
                'الموقع الإلكتروني': est.website,
                'ملاحظات': est.notes
            })
        
        # إنشاء DataFrame
        df = pd.DataFrame(data)
        
        # إنشاء مجلد للتصدير إذا لم يكن موجودًا
        export_folder = os.path.join(current_app.root_path, 'exports')
        os.makedirs(export_folder, exist_ok=True)
        
        # تحديد اسم الملف
        filename = f"establishments_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.{file_format}"
        file_path = os.path.join(export_folder, filename)
        
        # حفظ الملف حسب التنسيق المطلوب
        if file_format == 'xlsx':
            df.to_excel(file_path, index=False)
        else:
            df.to_csv(file_path, index=False)
        
        # إرجاع مسار الملف للتحميل
        return jsonify({
            'success': True,
            'file_path': f"/api/download/{filename}",
            'file_name': filename,
            'records_count': len(data)
        })
        
    except Exception as e:
        return jsonify({'error': f'حدث خطأ أثناء تصدير البيانات: {str(e)}'}), 500

@data_import_bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    """تحميل ملف مصدر"""
    export_folder = os.path.join(current_app.root_path, 'exports')
    return send_from_directory(export_folder, filename, as_attachment=True)

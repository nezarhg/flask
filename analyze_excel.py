import pandas as pd
import os
import json

# قراءة ملف الإكسل
excel_file_path = "/home/ubuntu/upload/ملف الادخالات الجميع - المنشآت.xlsx"
print(f"تحليل الملف: {excel_file_path}")

# التحقق من وجود الملف
if not os.path.exists(excel_file_path):
    print("خطأ: الملف غير موجود!")
    exit(1)

# قراءة أسماء الأوراق في الملف
xl = pd.ExcelFile(excel_file_path)
sheet_names = xl.sheet_names
print(f"أوراق الإكسل الموجودة: {sheet_names}")

# تحليل كل ورقة وحفظ المعلومات
sheets_data = {}
sheets_structure = {}

for sheet_name in sheet_names:
    print(f"\nتحليل الورقة: {sheet_name}")
    
    # قراءة البيانات
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
    
    # حفظ عدد الصفوف والأعمدة
    rows, cols = df.shape
    print(f"عدد الصفوف: {rows}, عدد الأعمدة: {cols}")
    
    # حفظ أسماء الأعمدة
    columns = df.columns.tolist()
    print(f"الأعمدة: {columns}")
    
    # حفظ أنواع البيانات
    dtypes = df.dtypes.astype(str).to_dict()
    dtypes = {k: v for k, v in dtypes.items()}
    
    # حفظ عينة من البيانات (أول 5 صفوف)
    sample_data = df.head(5).to_dict(orient='records')
    
    # حفظ معلومات الورقة
    sheets_structure[sheet_name] = {
        "rows": rows,
        "columns": cols,
        "column_names": columns,
        "data_types": dtypes
    }
    
    sheets_data[sheet_name] = {
        "structure": sheets_structure[sheet_name],
        "sample_data": sample_data
    }

# حفظ المعلومات في ملف JSON
output_file = "/home/ubuntu/crm_project/excel_analysis.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(sheets_data, f, ensure_ascii=False, indent=4)

print(f"\nتم حفظ تحليل البيانات في: {output_file}")

# تحليل إضافي للعلاقات المحتملة بين الأوراق
print("\nتحليل العلاقات المحتملة بين الأوراق:")

# البحث عن الأعمدة المشتركة بين الأوراق
common_columns = {}
for sheet1 in sheet_names:
    for sheet2 in sheet_names:
        if sheet1 != sheet2:
            cols1 = set(sheets_structure[sheet1]["column_names"])
            cols2 = set(sheets_structure[sheet2]["column_names"])
            common = cols1.intersection(cols2)
            if common:
                key = f"{sheet1} - {sheet2}"
                common_columns[key] = list(common)
                print(f"الأعمدة المشتركة بين {sheet1} و {sheet2}: {list(common)}")

# حفظ معلومات العلاقات في ملف
relationships_file = "/home/ubuntu/crm_project/relationships_analysis.json"
with open(relationships_file, 'w', encoding='utf-8') as f:
    json.dump(common_columns, f, ensure_ascii=False, indent=4)

print(f"تم حفظ تحليل العلاقات في: {relationships_file}")

# استخراج المتطلبات الأساسية لنظام CRM
print("\nالمتطلبات الأساسية المقترحة لنظام CRM:")
crm_requirements = {
    "entities": [],
    "features": [
        "إدارة المنشآت",
        "إدارة العملاء",
        "إدارة المستخدمين والصلاحيات",
        "تسجيل الدخول والمصادقة",
        "لوحة تحكم إحصائية",
        "إدارة التقارير",
        "استيراد وتصدير البيانات"
    ]
}

# استخراج الكيانات من أسماء الأوراق وأسماء الأعمدة
for sheet_name in sheet_names:
    crm_requirements["entities"].append(sheet_name)

# حفظ المتطلبات في ملف
requirements_file = "/home/ubuntu/crm_project/crm_requirements.json"
with open(requirements_file, 'w', encoding='utf-8') as f:
    json.dump(crm_requirements, f, ensure_ascii=False, indent=4)

print(f"تم حفظ متطلبات النظام في: {requirements_file}")
print("\nاكتمل تحليل ملف الإكسل بنجاح!")

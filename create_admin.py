#!/usr/bin/env python3

"""
سكريبت إنشاء مستخدم المسؤول الأول لنظام E-deal
"""

import os
import sys
import getpass
from backend import create_app, db
from backend.models import User

def create_admin_user():
    """إنشاء مستخدم مسؤول جديد"""
    
    print("=== إنشاء مستخدم المسؤول الأول لنظام E-deal ===")
    
    # جمع معلومات المستخدم
    username = input("اسم المستخدم: ")
    email = input("البريد الإلكتروني: ")
    full_name = input("الاسم الكامل: ")
    
    # التحقق من كلمة المرور
    while True:
        password = getpass.getpass("كلمة المرور: ")
        confirm_password = getpass.getpass("تأكيد كلمة المرور: ")
        
        if password == confirm_password:
            break
        else:
            print("كلمات المرور غير متطابقة. الرجاء المحاولة مرة أخرى.")
    
    # إنشاء تطبيق Flask وسياق التطبيق
    app = create_app()
    
    with app.app_context():
        # التحقق من عدم وجود مستخدمين مسبقًا
        if User.query.count() > 0:
            confirm = input("يوجد مستخدمون بالفعل في النظام. هل تريد إنشاء مستخدم مسؤول جديد؟ (نعم/لا): ")
            if confirm.lower() not in ['نعم', 'y', 'yes']:
                print("تم إلغاء العملية.")
                return
        
        # إنشاء مستخدم جديد
        admin_user = User(
            username=username,
            email=email,
            full_name=full_name,
            role='admin'
        )
        admin_user.set_password(password)
        
        # حفظ المستخدم في قاعدة البيانات
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"\nتم إنشاء مستخدم المسؤول '{username}' بنجاح!")
        print("يمكنك الآن تسجيل الدخول إلى النظام باستخدام بيانات الاعتماد هذه.")

if __name__ == "__main__":
    create_admin_user()

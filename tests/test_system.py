import unittest
import os
import sys
import json
from flask import Flask
from backend import create_app
from backend.models import db, User, Establishment, Region, City, EstablishmentType

class TestCRMSystem(unittest.TestCase):
    """اختبارات شاملة لنظام E-deal لإدارة علاقات العملاء"""
    
    def setUp(self):
        """إعداد بيئة الاختبار قبل كل اختبار"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # إنشاء مستخدم اختبار
            test_user = User(
                username='testuser',
                email='test@example.com',
                full_name='مستخدم اختبار',
                role='admin'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            
            # إنشاء بيانات اختبار أساسية
            region = Region(name='المنطقة الوسطى')
            db.session.add(region)
            db.session.flush()
            
            city = City(name='الرياض', region_id=region.id)
            db.session.add(city)
            
            est_type = EstablishmentType(name='شركة تقنية')
            db.session.add(est_type)
            db.session.flush()
            
            establishment = Establishment(
                name='شركة اختبار',
                unified_number='1234567890',
                region_id=region.id,
                city_id=city.id,
                establishment_type_id=est_type.id,
                mobile='0500000000',
                email='company@example.com'
            )
            db.session.add(establishment)
            
            db.session.commit()
            
            # الحصول على رمز الوصول للاختبارات
            response = self.client.post('/api/auth/login', json={
                'username': 'testuser',
                'password': 'password123'
            })
            data = json.loads(response.data)
            self.access_token = data['access_token']
    
    def tearDown(self):
        """تنظيف بيئة الاختبار بعد كل اختبار"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_authentication(self):
        """اختبار نظام المصادقة"""
        # اختبار تسجيل الدخول بنجاح
        response = self.client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        
        # اختبار تسجيل الدخول بكلمة مرور خاطئة
        response = self.client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, 401)
        
        # اختبار الوصول إلى نقطة نهاية محمية بدون رمز وصول
        response = self.client.get('/api/establishments')
        self.assertEqual(response.status_code, 401)
        
        # اختبار الوصول إلى نقطة نهاية محمية برمز وصول صالح
        response = self.client.get('/api/establishments', headers={
            'Authorization': f'Bearer {self.access_token}'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_establishments_crud(self):
        """اختبار عمليات CRUD للمنشآت"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        # اختبار جلب قائمة المنشآت
        response = self.client.get('/api/establishments', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('establishments', data)
        self.assertEqual(len(data['establishments']), 1)
        
        # اختبار إنشاء منشأة جديدة
        new_establishment = {
            'name': 'شركة جديدة',
            'unified_number': '0987654321',
            'region_id': 1,
            'city_id': 1,
            'establishment_type_id': 1,
            'mobile': '0511111111',
            'email': 'new@example.com',
            'address': 'عنوان الشركة الجديدة',
            'website': 'https://example.com',
            'notes': 'ملاحظات اختبار'
        }
        
        response = self.client.post('/api/establishments', 
                                   json=new_establishment, 
                                   headers=headers)
        self.assertEqual(response.status_code, 201)
        
        # التحقق من إضافة المنشأة الجديدة
        response = self.client.get('/api/establishments', headers=headers)
        data = json.loads(response.data)
        self.assertEqual(len(data['establishments']), 2)
        
        # اختبار جلب منشأة محددة
        response = self.client.get('/api/establishments/2', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['establishment']['name'], 'شركة جديدة')
        
        # اختبار تحديث منشأة
        update_data = {
            'name': 'شركة محدثة',
            'mobile': '0522222222'
        }
        
        response = self.client.put('/api/establishments/2', 
                                  json=update_data, 
                                  headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # التحقق من تحديث المنشأة
        response = self.client.get('/api/establishments/2', headers=headers)
        data = json.loads(response.data)
        self.assertEqual(data['establishment']['name'], 'شركة محدثة')
        self.assertEqual(data['establishment']['mobile'], '0522222222')
        
        # اختبار حذف منشأة
        response = self.client.delete('/api/establishments/2', headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # التحقق من حذف المنشأة
        response = self.client.get('/api/establishments', headers=headers)
        data = json.loads(response.data)
        self.assertEqual(len(data['establishments']), 1)
    
    def test_marketing_campaigns(self):
        """اختبار نظام التسويق"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        # إنشاء حملة تسويقية جديدة
        campaign_data = {
            'name': 'حملة اختبار',
            'type': 'email',
            'status': 'draft',
            'subject': 'رسالة اختبار',
            'content': 'محتوى رسالة الاختبار',
            'recipients': [1],  # معرف المنشأة الأولى
            'scheduled_at': '2025-05-01T10:00:00'
        }
        
        response = self.client.post('/api/marketing/campaigns', 
                                   json=campaign_data, 
                                   headers=headers)
        self.assertEqual(response.status_code, 201)
        
        # التحقق من إنشاء الحملة
        response = self.client.get('/api/marketing/campaigns', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['campaigns']), 1)
        self.assertEqual(data['campaigns'][0]['name'], 'حملة اختبار')
    
    def test_data_import_export(self):
        """اختبار وظائف استيراد وتصدير البيانات"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        # اختبار تصدير البيانات
        response = self.client.post('/api/data/export/establishments', 
                                   json={'format': 'json'}, 
                                   headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('file_path', data)
        self.assertIn('records_count', data)
        self.assertEqual(data['records_count'], 1)

if __name__ == '__main__':
    unittest.main()

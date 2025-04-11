import unittest
import os
import sys

# إضافة مسار المشروع إلى مسارات البحث
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# استيراد اختبارات النظام
from tests.test_system import TestCRMSystem

if __name__ == '__main__':
    unittest.main()

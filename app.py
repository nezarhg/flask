# app.py
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

# إنشاء تطبيق Flask
app = Flask(__name__, static_folder='frontend/build', static_url_path='/')

# تكوين CORS للسماح بالاتصال من أي مصدر
CORS(app)

# مسار الصفحة الرئيسية
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# مسار اختبار API
@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"message": "API is working!", "status": "success"})

# التعامل مع المسارات غير الموجودة في الواجهة الأمامية
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

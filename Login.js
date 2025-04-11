import React, { useState } from 'react';
import { Container, Row, Col, Form, Button, Card, Alert } from 'react-bootstrap';
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faLock } from '@fortawesome/free-solid-svg-icons';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // تحديد عنوان API بناءً على بيئة التشغيل
  const getApiUrl = () => {
    // في بيئة الإنتاج على Render
    if (process.env.NODE_ENV === 'production') {
      // استخدام المسار النسبي (سيتم توجيهه عبر إعدادات Render)
      return '/api/auth/login';
    }
    // في بيئة التطوير المحلية
    return '/api/auth/login';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // التحقق من إدخال البيانات
    if (!username || !password) {
      setError('الرجاء إدخال اسم المستخدم وكلمة المرور');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // استخدام الدالة للحصول على عنوان API المناسب
      const apiUrl = getApiUrl();
      const response = await axios.post(apiUrl, {
        username,
        password
      });
      
      if (response.data && response.data.token) {
        // تمرير بيانات المستخدم والرمز المميز إلى الدالة المستلمة من الأب
        onLogin(response.data.user, response.data.token);
      } else {
        setError('حدث خطأ أثناء تسجيل الدخول');
      }
    } catch (err) {
      if (err.response && err.response.data && err.response.data.message) {
        setError(err.response.data.message);
      } else {
        setError('حدث خطأ أثناء الاتصال بالخادم');
        
        // للتطوير فقط: تسجيل دخول وهمي للاختبار
        if (process.env.NODE_ENV !== 'production') {
          console.warn('تسجيل دخول وهمي للتطوير');
          const mockUser = {
            id: 1,
            username: username,
            fullName: 'مستخدم النظام',
            role: 'admin'
          };
          const mockToken = 'mock-token-for-development';
          onLogin(mockUser, mockToken);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  // استخدام صورة الشعار مع معالجة أفضل للأخطاء
  const logoUrl = process.env.PUBLIC_URL + '/logo.png';
  const fallbackLogoUrl = 'https://via.placeholder.com/150?text=E-deal';

  return (
    <Container className="login-container">
      <Row className="justify-content-center align-items-center min-vh-100">
        <Col md={6} lg={5}>
          <Card className="shadow-lg border-0 rounded-lg">
            <Card.Header className="text-center bg-primary text-white">
              <h3 className="mb-0">نظام E-deal لإدارة علاقات العملاء</h3>
            </Card.Header>
            <Card.Body>
              <div className="text-center mb-4">
                <img 
                  src={logoUrl} 
                  alt="E-deal Logo" 
                  style={{ maxWidth: '150px' }} 
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = fallbackLogoUrl;
                  }}
                />
                <h4 className="mt-3">تسجيل الدخول</h4>
              </div>
              
              {error && <Alert variant="danger">{error}</Alert>}
              
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>اسم المستخدم</Form.Label>
                  <div className="input-group">
                    <span className="input-group-text">
                      <FontAwesomeIcon icon={faUser} />
                    </span>
                    <Form.Control
                      type="text"
                      placeholder="أدخل اسم المستخدم"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      disabled={loading}
                    />
                  </div>
                </Form.Group>
                
                <Form.Group className="mb-4">
                  <Form.Label>كلمة المرور</Form.Label>
                  <div className="input-group">
                    <span className="input-group-text">
                      <FontAwesomeIcon icon={faLock} />
                    </span>
                    <Form.Control
                      type="password"
                      placeholder="أدخل كلمة المرور"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      disabled={loading}
                    />
                  </div>
                </Form.Group>
                
                <div className="d-grid">
                  <Button 
                    variant="primary" 
                    type="submit" 
                    disabled={loading}
                  >
                    {loading ? 'جاري تسجيل الدخول...' : 'تسجيل الدخول'}
                  </Button>
                </div>
              </Form>
            </Card.Body>
            <Card.Footer className="text-center text-muted">
              <small>© {new Date().getFullYear()} E-deal CRM. جميع الحقوق محفوظة</small>
            </Card.Footer>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Login;

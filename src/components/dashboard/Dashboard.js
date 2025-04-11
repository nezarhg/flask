import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBuilding, faBullhorn, faChartBar, faUsers, faRobot } from '@fortawesome/free-solid-svg-icons';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import axios from 'axios';
import './Dashboard.css';

// تسجيل مكونات ChartJS
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const Dashboard = ({ user }) => {
  const [stats, setStats] = useState({
    establishments: 0,
    campaigns: 0,
    users: 0,
    regions: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // جلب البيانات الإحصائية
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/statistics/dashboard');
        setStats(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('حدث خطأ أثناء جلب بيانات لوحة التحكم');
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // بيانات مخطط توزيع المنشآت حسب المنطقة
  const regionChartData = {
    labels: stats.regions.map(region => region.name),
    datasets: [
      {
        label: 'عدد المنشآت',
        data: stats.regions.map(region => region.count),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
          'rgba(255, 159, 64, 0.6)',
          'rgba(199, 199, 199, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(199, 199, 199, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  // بيانات مخطط الحملات التسويقية
  const campaignChartData = {
    labels: ['بريد إلكتروني', 'واتساب', 'وسائل التواصل', 'مختلط'],
    datasets: [
      {
        label: 'عدد الحملات',
        data: [12, 19, 8, 5],
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 99, 132, 0.6)',
          'rgba(255, 206, 86, 0.6)',
        ],
      },
    ],
  };

  if (loading) {
    return <div className="loading-spinner">جاري تحميل البيانات...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <Container fluid className="dashboard-container">
      <h1 className="page-title">لوحة التحكم</h1>
      <p className="welcome-message">مرحباً بك، {user?.full_name}</p>

      {/* بطاقات الإحصائيات */}
      <Row className="stats-cards">
        <Col md={3} sm={6}>
          <Card className="stats-card">
            <Card.Body>
              <div className="stats-icon establishments">
                <FontAwesomeIcon icon={faBuilding} />
              </div>
              <div className="stats-info">
                <h3>{stats.establishments}</h3>
                <p>المنشآت</p>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6}>
          <Card className="stats-card">
            <Card.Body>
              <div className="stats-icon campaigns">
                <FontAwesomeIcon icon={faBullhorn} />
              </div>
              <div className="stats-info">
                <h3>{stats.campaigns}</h3>
                <p>الحملات التسويقية</p>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6}>
          <Card className="stats-card">
            <Card.Body>
              <div className="stats-icon users">
                <FontAwesomeIcon icon={faUsers} />
              </div>
              <div className="stats-info">
                <h3>{stats.users}</h3>
                <p>المستخدمين</p>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6}>
          <Card className="stats-card">
            <Card.Body>
              <div className="stats-icon ai">
                <FontAwesomeIcon icon={faRobot} />
              </div>
              <div className="stats-info">
                <h3>متاح</h3>
                <p>المساعد الذكي</p>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* المخططات البيانية */}
      <Row className="charts-row">
        <Col lg={6}>
          <Card className="chart-card">
            <Card.Header>توزيع المنشآت حسب المنطقة</Card.Header>
            <Card.Body>
              <div className="chart-container">
                <Pie data={regionChartData} options={{ maintainAspectRatio: false }} />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={6}>
          <Card className="chart-card">
            <Card.Header>الحملات التسويقية حسب النوع</Card.Header>
            <Card.Body>
              <div className="chart-container">
                <Bar 
                  data={campaignChartData} 
                  options={{ 
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true
                      }
                    }
                  }} 
                />
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* الإجراءات السريعة */}
      <Row className="quick-actions">
        <Col>
          <Card>
            <Card.Header>إجراءات سريعة</Card.Header>
            <Card.Body>
              <div className="actions-container">
                <Button variant="primary" href="/establishments/add">إضافة منشأة</Button>
                <Button variant="success" href="/marketing/campaigns/add">إنشاء حملة</Button>
                <Button variant="info" href="/statistics">عرض الإحصائيات</Button>
                <Button variant="secondary" href="/ai-assistant">المساعد الذكي</Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;

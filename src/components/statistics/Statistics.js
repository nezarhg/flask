import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Tabs, Tab } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDownload, faSync, faChartBar, faPieChart, faChartLine, faTable } from '@fortawesome/free-solid-svg-icons';
import { 
  Chart as ChartJS, 
  ArcElement, 
  Tooltip, 
  Legend, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title,
  PointElement,
  LineElement
} from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';
import axios from 'axios';
import './Statistics.css';

// تسجيل مكونات ChartJS
ChartJS.register(
  ArcElement, 
  Tooltip, 
  Legend, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title,
  PointElement,
  LineElement
);

const Statistics = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    period: 'month',
    region_id: '',
    establishment_type_id: ''
  });
  const [regions, setRegions] = useState([]);
  const [establishmentTypes, setEstablishmentTypes] = useState([]);
  const [stats, setStats] = useState({
    establishments: {
      total: 0,
      by_region: [],
      by_type: [],
      growth: []
    },
    marketing: {
      campaigns: 0,
      messages_sent: 0,
      open_rate: 0,
      response_rate: 0,
      by_type: []
    }
  });

  // جلب البيانات الإحصائية
  useEffect(() => {
    fetchReferenceData();
    fetchStatistics();
  }, [filters]);

  const fetchReferenceData = async () => {
    try {
      const [regionsRes, typesRes] = await Promise.all([
        axios.get('/api/reference/regions'),
        axios.get('/api/reference/establishment-types')
      ]);
      
      setRegions(regionsRes.data.regions);
      setEstablishmentTypes(typesRes.data.types);
    } catch (err) {
      console.error('Error fetching reference data:', err);
    }
  };

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/statistics', { params: filters });
      setStats(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching statistics:', err);
      setError('حدث خطأ أثناء جلب البيانات الإحصائية');
      setLoading(false);
    }
  };

  // تحديث الفلاتر
  const handleFilterChange = (field, value) => {
    setFilters({
      ...filters,
      [field]: value
    });
  };

  // تصدير البيانات
  const exportData = async (format) => {
    try {
      const response = await axios.post('/api/statistics/export', {
        entity_type: 'statistics',
        format: format,
        criteria: filters
      }, { responseType: 'blob' });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `statistics.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Error exporting data:', err);
      setError('حدث خطأ أثناء تصدير البيانات');
    }
  };

  // بيانات مخطط توزيع المنشآت حسب المنطقة
  const regionChartData = {
    labels: stats.establishments.by_region.map(item => item.name),
    datasets: [
      {
        label: 'عدد المنشآت',
        data: stats.establishments.by_region.map(item => item.count),
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

  // بيانات مخطط توزيع المنشآت حسب النوع
  const typeChartData = {
    labels: stats.establishments.by_type.map(item => item.name),
    datasets: [
      {
        label: 'عدد المنشآت',
        data: stats.establishments.by_type.map(item => item.count),
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 99, 132, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(255, 99, 132, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(153, 102, 255, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  // بيانات مخطط نمو المنشآت
  const growthChartData = {
    labels: stats.establishments.growth.map(item => item.period),
    datasets: [
      {
        label: 'عدد المنشآت الجديدة',
        data: stats.establishments.growth.map(item => item.count),
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
        tension: 0.4,
        fill: true,
      },
    ],
  };

  // بيانات مخطط الحملات التسويقية
  const marketingChartData = {
    labels: stats.marketing.by_type.map(item => item.name),
    datasets: [
      {
        label: 'عدد الحملات',
        data: stats.marketing.by_type.map(item => item.count),
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 99, 132, 0.6)',
          'rgba(255, 206, 86, 0.6)',
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(255, 99, 132, 1)',
          'rgba(255, 206, 86, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  if (loading && Object.keys(stats.establishments.by_region).length === 0) {
    return <div className="loading-spinner">جاري تحميل البيانات...</div>;
  }

  return (
    <Container fluid className="statistics-container">
      <h1 className="page-title">الإحصائيات والتقارير</h1>
      
      {/* شريط الفلاتر والإجراءات */}
      <Card className="mb-4">
        <Card.Body>
          <Row className="align-items-center">
            <Col md={8}>
              <Row>
                <Col md={4}>
                  <Form.Group>
                    <Form.Label>الفترة الزمنية</Form.Label>
                    <Form.Select 
                      value={filters.period} 
                      onChange={(e) => handleFilterChange('period', e.target.value)}
                    >
                      <option value="week">أسبوع</option>
                      <option value="month">شهر</option>
                      <option value="quarter">ربع سنة</option>
                      <option value="year">سنة</option>
                      <option value="all">الكل</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={4}>
                  <Form.Group>
                    <Form.Label>المنطقة</Form.Label>
                    <Form.Select 
                      value={filters.region_id} 
                      onChange={(e) => handleFilterChange('region_id', e.target.value)}
                    >
                      <option value="">جميع المناطق</option>
                      {regions.map(region => (
                        <option key={region.id} value={region.id}>{region.name}</option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={4}>
                  <Form.Group>
                    <Form.Label>نوع المنشأة</Form.Label>
                    <Form.Select 
                      value={filters.establishment_type_id} 
                      onChange={(e) => handleFilterChange('establishment_type_id', e.target.value)}
                    >
                      <option value="">جميع الأنواع</option>
                      {establishmentTypes.map(type => (
                        <option key={type.id} value={type.id}>{type.name}</option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </Col>
              </Row>
            </Col>
            <Col md={4} className="text-md-end mt-3 mt-md-0">
              <Button variant="primary" className="me-2" onClick={() => fetchStatistics()}>
                <FontAwesomeIcon icon={faSync} className="me-1" />
                تحديث
              </Button>
              <div className="btn-group">
                <Button variant="outline-primary" onClick={() => exportData('excel')}>
                  <FontAwesomeIcon icon={faDownload} className="me-1" />
                  تصدير Excel
                </Button>
                <Button variant="outline-primary" onClick={() => exportData('pdf')}>PDF</Button>
              </div>
            </Col>
          </Row>
        </Card.Body>
      </Card>
      
      {/* عرض الخطأ إذا وجد */}
      {error && (
        <div className="alert alert-danger">{error}</div>
      )}
      
      {/* بطاقات الإحصائيات */}
      <Row className="stats-summary mb-4">
        <Col md={3} sm={6}>
          <Card className="stats-card">
            <Card.Body>
              <div className="stats-icon establishments">
                <FontAwesomeIcon icon={faChartBar} />
              </div>
              <div className="stats-info">
                <h3>{stats.establishments.total}</h3>
                <p>إجمالي المنشآت</p>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6}>
          <Card className="stats-card">
            <Card.Body>
              <div className="stats-icon campaigns">
                <FontAwesomeIcon icon={faPieChart} />
              </div>
              <div className="stats-info">
                <h3>{stats.marketing.campaigns}</h3>
                <p>الحملات التسويقية</p>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6}>
          <Card className="stats-card">
            <Card.Body>
              <div className="stats-icon messages">
                <FontAwesomeIcon icon={faChartLine} />
              </div>
              <div className="stats-info">
                <h3>{stats.marketing.messages_sent}</h3>
                <p>الرسائل المرسلة</p>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6}>
          <Card className="stats-card">
            <Card.Body>
              <div className="stats-icon response">
                <FontAwesomeIcon icon={faTable} />
              </div>
              <div className="stats-info">
                <h3>{stats.marketing.response_rate}%</h3>
                <p>معدل الاستجابة</p>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {/* علامات التبويب للمخططات */}
      <Tabs defaultActiveKey="establishments" id="statistics-tabs" className="mb-4">
        <Tab eventKey="establishments" title="إحصائيات المنشآت">
          <Row>
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
                <Card.Header>توزيع المنشآت حسب النوع</Card.Header>
                <Card.Body>
                  <div className="chart-container">
                    <Pie data={typeChartData} options={{ maintainAspectRatio: false }} />
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
          <Row className="mt-4">
            <Col>
              <Card className="chart-card">
                <Card.Header>نمو المنشآت</Card.Header>
                <Card.Body>
                  <div className="chart-container">
                    <Line 
                      data={growthChartData} 
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
        </Tab>
        <Tab eventKey="marketing" title="إحصائيات التسويق">
          <Row>
            <Col lg={6}>
              <Card className="chart-card">
                <Card.Header>الحملات التسويقية حسب النوع</Card.Header>
                <Card.Body>
                  <div className="chart-container">
                    <Bar 
                      data={marketingChartData} 
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
            <Col lg={6}>
              <Card className="chart-card">
                <Card.Header>معدلات الاستجابة</Card.Header>
                <Card.Body>
                  <div className="chart-container">
                    <div className="response-rates">
                      <div className="rate-item">
                        <div className="rate-label">معدل فتح البريد الإلكتروني</div>
                        <div className="progress">
                          <div 
                            className="progress-bar bg-primary" 
                            role="progressbar" 
                            style={{ width: `${stats.marketing.open_rate}%` }} 
                            aria-valuenow={stats.marketing.open_rate} 
                            aria-valuemin="0" 
                            aria-valuemax="100"
                          >
                            {stats.marketing.open_rate}%
                          </div>
                        </div>
                      </div>
                      <div className="rate-item">
                        <div className="rate-label">معدل النقر في البريد الإلكتروني</div>
                        <div className="progress">
                          <div 
                            className="progress-bar bg-success" 
                            role="progressbar" 
                            style={{ width: `${stats.marketing.response_rate}%` }} 
                            aria-valuenow={stats.marketing.response_rate} 
                            aria-valuemin="0" 
                            aria-valuemax="100"
                          >
                            {stats.marketing.response_rate}%
                          </div>
                        </div>
                      </div>
                      <div className="rate-item">
                        <div className="rate-label">معدل تسليم الواتساب</div>
                        <div className="progress">
                          <div 
                            className="progress-bar bg-info" 
                            role="progressbar" 
                            style={{ width: "95%" }} 
                            aria-valuenow="95" 
                            aria-valuemin="0" 
                            aria-valuemax="100"
                          >
                            95%
                          </div>
                        </div>
                      </div>
                      <div className="rate-item">
                        <div className="rate-label">معدل قراءة الواتساب</div>
                        <div className="progress">
                          <div 
                            className="progress-bar bg-warning" 
                            role="progressbar" 
                            style={{ width: "80%" }} 
                            aria-valuenow="80" 
                            aria-valuemin="0" 
                            aria-valuemax="100"
                          >
                            80%
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>
      </Tabs>
    </Container>
  );
};

export default Statistics;

import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Button, Table, Form, 
  Modal, Alert, Tabs, Tab, Badge, Spinner 
} from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faUsers, faBuilding, faChartBar, faSyncAlt, 
  faPlus, faEdit, faTrash, faSearch, faEye 
} from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';

// مكون لوحة التحكم الرئيسية
const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // جلب الإحصائيات عند تحميل الصفحة
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('accessToken');
      const response = await axios.get('/api/admin/statistics', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStatistics(response.data);
      setError(null);
    } catch (err) {
      setError('حدث خطأ أثناء جلب الإحصائيات');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container fluid className="rtl">
      <Row className="mb-4">
        <Col>
          <h2 className="page-title">لوحة تحكم المسؤول</h2>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col>
          <Tabs
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k)}
            className="mb-3"
          >
            <Tab eventKey="overview" title="نظرة عامة">
              <OverviewTab statistics={statistics} loading={loading} error={error} onRefresh={fetchStatistics} />
            </Tab>
            <Tab eventKey="establishments" title="المنشآت">
              <EstablishmentsTab />
            </Tab>
            <Tab eventKey="users" title="المستخدمين">
              <UsersTab />
            </Tab>
            <Tab eventKey="projects" title="مشاريع الإدخال">
              <ProjectsTab />
            </Tab>
            <Tab eventKey="regions" title="المناطق والمدن">
              <RegionsTab />
            </Tab>
            <Tab eventKey="activities" title="سجل النشاطات">
              <ActivitiesTab />
            </Tab>
            <Tab eventKey="sync" title="مزامنة البيانات">
              <SyncTab />
            </Tab>
          </Tabs>
        </Col>
      </Row>
    </Container>
  );
};

// مكون نظرة عامة
const OverviewTab = ({ statistics, loading, error, onRefresh }) => {
  if (loading) {
    return (
      <div className="text-center p-5">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3">جاري تحميل الإحصائيات...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        {error}
        <Button variant="outline-danger" size="sm" className="mr-2" onClick={onRefresh}>
          إعادة المحاولة
        </Button>
      </Alert>
    );
  }

  if (!statistics) {
    return (
      <Alert variant="info">
        لا توجد إحصائيات متاحة
        <Button variant="outline-primary" size="sm" className="mr-2" onClick={onRefresh}>
          تحديث
        </Button>
      </Alert>
    );
  }

  return (
    <div>
      <Row className="mb-4">
        <Col md={3}>
          <Card className="dashboard-card">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h6 className="card-subtitle text-muted">إجمالي المنشآت</h6>
                  <h2 className="card-title mb-0">{statistics.establishments.total}</h2>
                </div>
                <div className="card-icon bg-primary">
                  <FontAwesomeIcon icon={faBuilding} />
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="dashboard-card">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h6 className="card-subtitle text-muted">إجمالي المستخدمين</h6>
                  <h2 className="card-title mb-0">{statistics.users.total}</h2>
                </div>
                <div className="card-icon bg-success">
                  <FontAwesomeIcon icon={faUsers} />
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="dashboard-card">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h6 className="card-subtitle text-muted">إجمالي المشاريع</h6>
                  <h2 className="card-title mb-0">{statistics.projects.total}</h2>
                </div>
                <div className="card-icon bg-warning">
                  <FontAwesomeIcon icon={faChartBar} />
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="dashboard-card">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h6 className="card-subtitle text-muted">المشاريع المكتملة</h6>
                  <h2 className="card-title mb-0">{statistics.projects.completed}</h2>
                </div>
                <div className="card-icon bg-info">
                  <FontAwesomeIcon icon={faChartBar} />
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col md={6}>
          <Card className="mb-4">
            <Card.Header>
              <h5 className="card-title mb-0">المنشآت حسب المنطقة</h5>
            </Card.Header>
            <Card.Body>
              <Table striped hover responsive>
                <thead>
                  <tr>
                    <th>المنطقة</th>
                    <th>عدد المنشآت</th>
                    <th>النسبة</th>
                  </tr>
                </thead>
                <tbody>
                  {statistics.establishments.by_region.map((item, index) => (
                    <tr key={index}>
                      <td>{item.region}</td>
                      <td>{item.count}</td>
                      <td>
                        {statistics.establishments.total > 0 
                          ? `${((item.count / statistics.establishments.total) * 100).toFixed(1)}%` 
                          : '0%'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card className="mb-4">
            <Card.Header>
              <h5 className="card-title mb-0">المنشآت حسب النوع</h5>
            </Card.Header>
            <Card.Body>
              <Table striped hover responsive>
                <thead>
                  <tr>
                    <th>النوع</th>
                    <th>عدد المنشآت</th>
                    <th>النسبة</th>
                  </tr>
                </thead>
                <tbody>
                  {statistics.establishments.by_type.map((item, index) => (
                    <tr key={index}>
                      <td>{item.type}</td>
                      <td>{item.count}</td>
                      <td>
                        {statistics.establishments.total > 0 
                          ? `${((item.count / statistics.establishments.total) * 100).toFixed(1)}%` 
                          : '0%'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

// مكون إدارة المنشآت
const EstablishmentsTab = () => {
  const [establishments, setEstablishments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [currentEstablishment, setCurrentEstablishment] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    unified_number: '',
    mobile: '',
    email: '',
    region_id: '',
    city_id: '',
    district_id: '',
    establishment_type_id: '',
    brokerage_license: '',
    property_management_license: '',
    facility_management_license: '',
    auction_license: '',
    real_estate_cooperation: '',
    whatsapp: '',
    campaign_type: '',
    action_taken: ''
  });
  const [regions, setRegions] = useState([]);
  const [cities, setCities] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [establishmentTypes, setEstablishmentTypes] = useState([]);

  useEffect(() => {
    fetchEstablishments();
    fetchRegions();
    fetchEstablishmentTypes();
  }, [currentPage, searchTerm]);

  const fetchEstablishments = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('accessToken');
      const response = await axios.get(`/api/admin/establishments?page=${currentPage}&search=${searchTerm}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEstablishments(response.data.establishments);
      setTotalPages(response.data.pages);
      setError(null);
    } catch (err) {
      setError('حدث خطأ أثناء جلب بيانات المنشآت');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRegions = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await axios.get('/api/admin/regions', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setRegions(response.data.regions);
    } catch (err) {
      console.error('حدث خطأ أثناء جلب المناطق:', err);
    }
  };

  const fetchCities = async (regionId) => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await axios.get(`/api/admin/cities?region_id=${regionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCities(response.data.cities);
    } catch (err) {
      console.error('حدث خطأ أثناء جلب المدن:', err);
    }
  };

  const fetchDistricts = async (cityId) => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await axios.get(`/api/admin/districts?city_id=${cityId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDistricts(response.data.districts);
    } catch (err) {
      console.error('حدث خطأ أثناء جلب الأحياء:', err);
    }
  };

  const fetchEstablishmentTypes = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await axios.get('/api/admin/establishment-types', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEstablishmentTypes(response.data.types);
    } catch (err) {
      console.error('حدث خطأ أثناء جلب أنواع المنشآت:', err);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchEstablishments();
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });

    // جلب المدن عند تغيير المنطقة
    if (name === 'region_id') {
      fetchCities(value);
      setFormData({ ...formData, region_id: value, city_id: '', district_id: '' });
    }

    // جلب الأحياء عند تغيير المدينة
    if (name === 'city_id') {
      fetchDistricts(value);
      setFormData({ ...formData, city_id: value, district_id: '' });
    }
  };

  const handleAddNew = () => {
    setCurrentEstablishment(null);
    setFormData({
      name: '',
      unified_number: '',
      mobile: '',
      email: '',
      region_id: '',
      city_id: '',
      district_id: '',
      establishment_type_id: '',
      brokerage_license: '',
      property_management_license: '',
      facility_management_license: '',
      auction_license: '',
      real_estate_cooperation: '',
      whatsapp: '',
      campaign_type: '',
      action_taken: ''
    });
    setShowModal(true);
  };

  const handleEdit = (establishment) => {
    setCurrentEstablishment(establishment);
    setFormData({
      name: establishment.name,
      unified_number: establishment.unified_number || '',
      mobile: establishment.mobile || '',
      email: establishment.email || '',
      region_id: establishment.region_id || '',
      city_id: establishment.city_id || '',
      district_id: establishment.district_id || '',
      establishment_type_id: establishment.establishment_type_id || '',
      brokerage_license: establishment.brokerage_license || '',
      property_management_license: establishment.property_management_license || '',
      facility_management_license: establishment.facility_management_license || '',
      auction_license: establishment.auction_license || '',
      real_estate_cooperation: establishment.real_estate_cooperation || '',
      whatsapp: establishment.whatsapp || '',
      campaign_type: establishment.campaign_type || '',
      action_taken: establishment.action_taken || ''
    });
    
    // جلب المدن والأحياء المرتبطة
    if (establishment.region_id) {
      fetchCities(establishment.region_id);
    }
    if (establishment.city_id) {
      fetchDistricts(establishment.city_id);
    }
    
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('accessToken');
      
      if (currentEstablishment) {
        // تحديث منشأة موجودة
        await axios.put(`/api/admin/establishments/${currentEstablishment.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        // إنشاء منشأة جديدة
        await axios.post('/api/admin/establishments', formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      
      setShowModal(false);
      fetchEstablishments();
    } catch (err) {
      console.error('حدث خطأ أثناء حفظ المنشأة:', err);
      alert('حدث خطأ أثناء حفظ المنشأة');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('هل أنت متأكد من حذف هذه المنشأة؟')) {
      try {
        const token = localStorage.getItem('accessToken');
        await axios.delete(`/api/admin/establishments/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        fetchEstablishments();
      } catch (err) {
        console.error('حدث خطأ أثناء حذف المنشأة:', err);
        alert('حدث خطأ أثناء حذف المنشأة');
      }
    }
  };

  if (loading && establishments.length === 0) {
    return (
      <div className="text-center p-5">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3">جاري تحميل بيانات المنشآت...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4>إدارة المنشآت</h4>
        <Button variant="primary" onClick={handleAddNew}>
          <FontAwesomeIcon icon={faPlus} className="mr-2" />
          إضافة منشأة جديدة
        </Button>
      </div>

      <Card className="mb-4">
        <Card.Body>
          <Form onSubmit={handleSearch}>
            <Row>
              <Col md={8}>
                <Form.Group>
                  <Form.Control
                    type="text"
                    placeholder="البحث عن منشأة..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Button variant="primary" type="submit" block>
                  <FontAwesomeIcon icon={faSearch} className="mr-2" />
                  بحث
                </Button>
              </Col>
            </Row>
          </Form>
        </Card.Body>
      </Card>

      {error && (
        <Alert variant="danger">
          {error}
          <Button variant="outline-danger" size="sm" className="mr-2" onClick={fetchEstablishments}>
            إعادة المحاولة
          </Button>
        </Alert>
      )}

      <Table striped bordered hover responsive>
        <thead>
          <tr>
            <th>#</th>
            <th>اسم المنشأة</th>
            <th>الرقم الموحد</th>
            <th>المنطقة</th>
            <th>المدينة</th>
            <th>نوع المنشأة</th>
            <th>الإجراءات</th>
          </tr>
        </thead>
        <tbody>
          {establishments.length > 0 ? (
            establishments.map((establishment) => (
              <tr key={establishment.id}>
                <td>{establishment.id}</td>
                <td>{establishment.name}</td>
                <td>{establishment.unified_number || '-'}</td>
                <td>{establishment.region?.name || '-'}</td>
                <td>{establishment.city?.name || '-'}</td>
                <td>{establishment.establishment_type?.name || '-'}</td>
                <td>
                  <Button variant="info" size="sm" className="mr-2" onClick={() => handleEdit(establishment)}>
                    <FontAwesomeIcon icon={faEdit} />
                  </Button>
                  <Button variant="danger" size="sm" onClick={() => handleDelete(establishment.id)}>
                    <FontAwesomeIcon icon={faTrash} />
                  </Button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="7" className="text-center">
                لا توجد منشآت
              </td>
            </tr>
          )}
        </tbody>
      </Table>

      {totalPages > 1 && (
        <div className="d-flex justify-content-center">
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
          />
        </div>
      )}

      {/* نموذج إضافة/تعديل منشأة */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {currentEstablishment ? 'تعديل منشأة' : 'إضافة منشأة جديدة'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>اسم المنشأة *</Form.Label>
                  <Form.Control
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>الرقم الموحد للمنشأة</Form.Label>
                  <Form.Control
                    type="text"
                    name="unified_number"
                    value={formData.unified_number}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>رقم الجوال</Form.Label>
                  <Form.Control
                    type="text"
                    name="mobile"
                    value={formData.mobile}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>البريد الإلكتروني</Form.Label>
                  <Form.Control
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>المنطقة</Form.Label>
                  <Form.Control
                    as="select"
                    name="region_id"
                    value={formData.region_id}
                    onChange={handleInputChange}
                  >
                    <option value="">اختر المنطقة</option>
                    {regions.map((region) => (
                      <option key={region.id} value={region.id}>
                        {region.name}
                      </option>
                    ))}
                  </Form.Control>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>المدينة</Form.Label>
                  <Form.Control
                    as="select"
                    name="city_id"
                    value={formData.city_id}
                    onChange={handleInputChange}
                    disabled={!formData.region_id}
                  >
                    <option value="">اختر المدينة</option>
                    {cities.map((city) => (
                      <option key={city.id} value={city.id}>
                        {city.name}
                      </option>
                    ))}
                  </Form.Control>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>الحي</Form.Label>
                  <Form.Control
                    as="select"
                    name="district_id"
                    value={formData.district_id}
                    onChange={handleInputChange}
                    disabled={!formData.city_id}
                  >
                    <option value="">اختر الحي</option>
                    {districts.map((district) => (
                      <option key={district.id} value={district.id}>
                        {district.name}
                      </option>
                    ))}
                  </Form.Control>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>نوع المنشأة</Form.Label>
                  <Form.Control
                    as="select"
                    name="establishment_type_id"
                    value={formData.establishment_type_id}
                    onChange={handleInputChange}
                  >
                    <option value="">اختر نوع المنشأة</option>
                    {establishmentTypes.map((type) => (
                      <option key={type.id} value={type.id}>
                        {type.name}
                      </option>
                    ))}
                  </Form.Control>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>رخصة الوساطة والتسويق</Form.Label>
                  <Form.Control
                    type="text"
                    name="brokerage_license"
                    value={formData.brokerage_license}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>رخصة إدارة الأملاك</Form.Label>
                  <Form.Control
                    type="text"
                    name="property_management_license"
                    value={formData.property_management_license}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>رخصة إدارة المرافق</Form.Label>
                  <Form.Control
                    type="text"
                    name="facility_management_license"
                    value={formData.facility_management_license}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>رخصة المزادات</Form.Label>
                  <Form.Control
                    type="text"
                    name="auction_license"
                    value={formData.auction_license}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>التعاون العقاري</Form.Label>
                  <Form.Control
                    type="text"
                    name="real_estate_cooperation"
                    value={formData.real_estate_cooperation}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>رقم الواتساب</Form.Label>
                  <Form.Control
                    type="text"
                    name="whatsapp"
                    value={formData.whatsapp}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>نوع الحملة</Form.Label>
                  <Form.Control
                    type="text"
                    name="campaign_type"
                    value={formData.campaign_type}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>الإجراء المتخذ</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                name="action_taken"
                value={formData.action_taken}
                onChange={handleInputChange}
              />
            </Form.Group>

            <div className="d-flex justify-content-end">
              <Button variant="secondary" className="ml-2" onClick={() => setShowModal(false)}>
                إلغاء
              </Button>
              <Button variant="primary" type="submit">
                حفظ
              </Button>
            </div>
          </Form>
        </Modal.Body>
      </Modal>
    </div>
  );
};

// مكون الصفحات
const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  const pages = [];
  
  for (let i = 1; i <= totalPages; i++) {
    pages.push(
      <li key={i} className={`page-item ${currentPage === i ? 'active' : ''}`}>
        <button className="page-link" onClick={() => onPageChange(i)}>
          {i}
        </button>
      </li>
    );
  }
  
  return (
    <nav>
      <ul className="pagination">
        <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
          <button 
            className="page-link" 
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            السابق
          </button>
        </li>
        {pages}
        <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
          <button 
            className="page-link" 
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            التالي
          </button>
        </li>
      </ul>
    </nav>
  );
};

// مكونات أخرى (يمكن تنفيذها بشكل مشابه)
const UsersTab = () => (
  <div className="text-center p-5">
    <h4>إدارة المستخدمين</h4>
    <p>سيتم تنفيذ هذا القسم لاحقًا</p>
  </div>
);

const ProjectsTab = () => (
  <div className="text-center p-5">
    <h4>إدارة مشاريع الإدخال</h4>
    <p>سيتم تنفيذ هذا القسم لاحقًا</p>
  </div>
);

const RegionsTab = () => (
  <div className="text-center p-5">
    <h4>إدارة المناطق والمدن</h4>
    <p>سيتم تنفيذ هذا القسم لاحقًا</p>
  </div>
);

const ActivitiesTab = () => (
  <div className="text-center p-5">
    <h4>سجل النشاطات</h4>
    <p>سيتم تنفيذ هذا القسم لاحقًا</p>
  </div>
);

const SyncTab = () => (
  <div className="text-center p-5">
    <h4>مزامنة البيانات</h4>
    <p>سيتم تنفيذ هذا القسم لاحقًا</p>
  </div>
);

export default AdminDashboard;

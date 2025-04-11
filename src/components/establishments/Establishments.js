import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Button, Form, InputGroup, Pagination, Modal } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faPlus, faEdit, faTrash, faFileExport, faFilter } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './Establishments.css';

const Establishments = () => {
  const [establishments, setEstablishments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    region_id: '',
    city_id: '',
    establishment_type_id: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [regions, setRegions] = useState([]);
  const [cities, setCities] = useState([]);
  const [establishmentTypes, setEstablishmentTypes] = useState([]);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [establishmentToDelete, setEstablishmentToDelete] = useState(null);

  // جلب بيانات المنشآت
  useEffect(() => {
    fetchEstablishments();
    fetchReferenceData();
  }, [currentPage, filters]);

  const fetchEstablishments = async () => {
    try {
      setLoading(true);
      const params = {
        page: currentPage,
        per_page: 10,
        search: searchTerm,
        ...filters
      };
      
      const response = await axios.get('/api/establishments', { params });
      setEstablishments(response.data.establishments);
      setTotalPages(response.data.pages);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching establishments:', err);
      setError('حدث خطأ أثناء جلب بيانات المنشآت');
      setLoading(false);
    }
  };

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

  const fetchCities = async (regionId) => {
    if (!regionId) {
      setCities([]);
      return;
    }
    
    try {
      const response = await axios.get(`/api/reference/cities?region_id=${regionId}`);
      setCities(response.data.cities);
    } catch (err) {
      console.error('Error fetching cities:', err);
    }
  };

  // تحديث المنطقة وجلب المدن المرتبطة بها
  const handleRegionChange = (e) => {
    const regionId = e.target.value;
    setFilters({
      ...filters,
      region_id: regionId,
      city_id: ''
    });
    fetchCities(regionId);
  };

  // تحديث المدينة
  const handleCityChange = (e) => {
    setFilters({
      ...filters,
      city_id: e.target.value
    });
  };

  // تحديث نوع المنشأة
  const handleTypeChange = (e) => {
    setFilters({
      ...filters,
      establishment_type_id: e.target.value
    });
  };

  // البحث
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchEstablishments();
  };

  // إعادة تعيين الفلاتر
  const resetFilters = () => {
    setFilters({
      region_id: '',
      city_id: '',
      establishment_type_id: ''
    });
    setSearchTerm('');
    setCurrentPage(1);
  };

  // تغيير الصفحة
  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  // فتح نافذة تأكيد الحذف
  const confirmDelete = (establishment) => {
    setEstablishmentToDelete(establishment);
    setShowDeleteModal(true);
  };

  // حذف منشأة
  const deleteEstablishment = async () => {
    try {
      await axios.delete(`/api/establishments/${establishmentToDelete.id}`);
      setShowDeleteModal(false);
      fetchEstablishments();
    } catch (err) {
      console.error('Error deleting establishment:', err);
      setError('حدث خطأ أثناء حذف المنشأة');
    }
  };

  // تصدير البيانات
  const exportData = async (format) => {
    try {
      const response = await axios.post('/api/statistics/export', {
        entity_type: 'establishments',
        format: format,
        criteria: filters
      }, { responseType: 'blob' });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `establishments.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Error exporting data:', err);
      setError('حدث خطأ أثناء تصدير البيانات');
    }
  };

  // إنشاء عناصر الترقيم
  const renderPagination = () => {
    const pages = [];
    
    // زر الصفحة السابقة
    pages.push(
      <Pagination.Prev 
        key="prev" 
        onClick={() => handlePageChange(currentPage - 1)}
        disabled={currentPage === 1}
      />
    );
    
    // أزرار الصفحات
    for (let i = 1; i <= totalPages; i++) {
      if (
        i === 1 || 
        i === totalPages || 
        (i >= currentPage - 1 && i <= currentPage + 1)
      ) {
        pages.push(
          <Pagination.Item 
            key={i} 
            active={i === currentPage}
            onClick={() => handlePageChange(i)}
          >
            {i}
          </Pagination.Item>
        );
      } else if (
        i === currentPage - 2 || 
        i === currentPage + 2
      ) {
        pages.push(<Pagination.Ellipsis key={`ellipsis-${i}`} />);
      }
    }
    
    // زر الصفحة التالية
    pages.push(
      <Pagination.Next 
        key="next" 
        onClick={() => handlePageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      />
    );
    
    return <Pagination>{pages}</Pagination>;
  };

  if (loading && establishments.length === 0) {
    return <div className="loading-spinner">جاري تحميل البيانات...</div>;
  }

  return (
    <Container fluid className="establishments-container">
      <h1 className="page-title">إدارة المنشآت</h1>
      
      {/* شريط البحث والإجراءات */}
      <Card className="mb-4">
        <Card.Body>
          <Row className="align-items-center">
            <Col md={6}>
              <Form onSubmit={handleSearch}>
                <InputGroup>
                  <Form.Control
                    type="text"
                    placeholder="بحث عن منشأة..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                  <Button variant="primary" type="submit">
                    <FontAwesomeIcon icon={faSearch} />
                  </Button>
                  <Button 
                    variant="outline-secondary" 
                    onClick={() => setShowFilters(!showFilters)}
                  >
                    <FontAwesomeIcon icon={faFilter} />
                  </Button>
                </InputGroup>
              </Form>
            </Col>
            <Col md={6} className="text-md-end mt-3 mt-md-0">
              <Link to="/establishments/add" className="btn btn-success me-2">
                <FontAwesomeIcon icon={faPlus} className="me-1" />
                إضافة منشأة
              </Link>
              <div className="btn-group">
                <Button variant="outline-primary" onClick={() => exportData('excel')}>
                  <FontAwesomeIcon icon={faFileExport} className="me-1" />
                  تصدير Excel
                </Button>
                <Button variant="outline-primary" onClick={() => exportData('csv')}>CSV</Button>
              </div>
            </Col>
          </Row>
          
          {/* فلاتر البحث */}
          {showFilters && (
            <Row className="mt-3">
              <Col md={3}>
                <Form.Group>
                  <Form.Label>المنطقة</Form.Label>
                  <Form.Select 
                    value={filters.region_id} 
                    onChange={handleRegionChange}
                  >
                    <option value="">جميع المناطق</option>
                    {regions.map(region => (
                      <option key={region.id} value={region.id}>{region.name}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group>
                  <Form.Label>المدينة</Form.Label>
                  <Form.Select 
                    value={filters.city_id} 
                    onChange={handleCityChange}
                    disabled={!filters.region_id}
                  >
                    <option value="">جميع المدن</option>
                    {cities.map(city => (
                      <option key={city.id} value={city.id}>{city.name}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group>
                  <Form.Label>نوع المنشأة</Form.Label>
                  <Form.Select 
                    value={filters.establishment_type_id} 
                    onChange={handleTypeChange}
                  >
                    <option value="">جميع الأنواع</option>
                    {establishmentTypes.map(type => (
                      <option key={type.id} value={type.id}>{type.name}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={3} className="d-flex align-items-end">
                <Button variant="secondary" onClick={resetFilters} className="w-100">
                  إعادة تعيين الفلاتر
                </Button>
              </Col>
            </Row>
          )}
        </Card.Body>
      </Card>
      
      {/* عرض الخطأ إذا وجد */}
      {error && (
        <div className="alert alert-danger">{error}</div>
      )}
      
      {/* جدول المنشآت */}
      <Card>
        <Card.Body>
          <div className="table-responsive">
            <Table hover>
              <thead>
                <tr>
                  <th>#</th>
                  <th>اسم المنشأة</th>
                  <th>الرقم الموحد</th>
                  <th>المنطقة</th>
                  <th>المدينة</th>
                  <th>نوع المنشأة</th>
                  <th>رقم الجوال</th>
                  <th>البريد الإلكتروني</th>
                  <th>الإجراءات</th>
                </tr>
              </thead>
              <tbody>
                {establishments.length > 0 ? (
                  establishments.map(establishment => (
                    <tr key={establishment.id}>
                      <td>{establishment.id}</td>
                      <td>{establishment.name}</td>
                      <td>{establishment.unified_number || '-'}</td>
                      <td>{establishment.region || '-'}</td>
                      <td>{establishment.city || '-'}</td>
                      <td>{establishment.establishment_type || '-'}</td>
                      <td>{establishment.mobile || '-'}</td>
                      <td>{establishment.email || '-'}</td>
                      <td>
                        <Link 
                          to={`/establishments/edit/${establishment.id}`} 
                          className="btn btn-sm btn-primary me-1"
                        >
                          <FontAwesomeIcon icon={faEdit} />
                        </Link>
                        <Button 
                          variant="danger" 
                          size="sm"
                          onClick={() => confirmDelete(establishment)}
                        >
                          <FontAwesomeIcon icon={faTrash} />
                        </Button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="9" className="text-center">لا توجد منشآت</td>
                  </tr>
                )}
              </tbody>
            </Table>
          </div>
          
          {/* ترقيم الصفحات */}
          {totalPages > 1 && (
            <div className="d-flex justify-content-center mt-4">
              {renderPagination()}
            </div>
          )}
        </Card.Body>
      </Card>
      
      {/* نافذة تأكيد الحذف */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>تأكيد الحذف</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          هل أنت متأكد من حذف المنشأة "{establishmentToDelete?.name}"؟
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            إلغاء
          </Button>
          <Button variant="danger" onClick={deleteEstablishment}>
            حذف
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Establishments;

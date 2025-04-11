import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Button, Form, InputGroup, Pagination, Modal, Nav, Tab } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faPlus, faEdit, faTrash, faFileExport, faFilter, faEnvelope, faShareAlt } from '@fortawesome/free-solid-svg-icons';
import { faWhatsapp } from '@fortawesome/free-brands-svg-icons';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './Marketing.css';

const Marketing = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: '',
    type: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [campaignToDelete, setCampaignToDelete] = useState(null);
  const [showSendModal, setShowSendModal] = useState(false);
  const [sendType, setSendType] = useState('');
  const [messageData, setMessageData] = useState({
    subject: '',
    content: '',
    recipients: []
  });
  const [establishments, setEstablishments] = useState([]);
  const [selectedEstablishments, setSelectedEstablishments] = useState([]);

  // جلب بيانات الحملات التسويقية
  useEffect(() => {
    fetchCampaigns();
  }, [currentPage, filters]);

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      const params = {
        page: currentPage,
        per_page: 10,
        search: searchTerm,
        ...filters
      };
      
      const response = await axios.get('/api/marketing/campaigns', { params });
      setCampaigns(response.data.campaigns);
      setTotalPages(response.data.pages);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching campaigns:', err);
      setError('حدث خطأ أثناء جلب بيانات الحملات التسويقية');
      setLoading(false);
    }
  };

  // جلب بيانات المنشآت للرسائل
  const fetchEstablishments = async () => {
    try {
      const response = await axios.get('/api/establishments', { 
        params: { per_page: 100 } 
      });
      setEstablishments(response.data.establishments);
    } catch (err) {
      console.error('Error fetching establishments:', err);
    }
  };

  // البحث
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchCampaigns();
  };

  // تحديث الفلاتر
  const handleFilterChange = (field, value) => {
    setFilters({
      ...filters,
      [field]: value
    });
  };

  // إعادة تعيين الفلاتر
  const resetFilters = () => {
    setFilters({
      status: '',
      type: ''
    });
    setSearchTerm('');
    setCurrentPage(1);
  };

  // تغيير الصفحة
  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  // فتح نافذة تأكيد الحذف
  const confirmDelete = (campaign) => {
    setCampaignToDelete(campaign);
    setShowDeleteModal(true);
  };

  // حذف حملة
  const deleteCampaign = async () => {
    try {
      await axios.delete(`/api/marketing/campaigns/${campaignToDelete.id}`);
      setShowDeleteModal(false);
      fetchCampaigns();
    } catch (err) {
      console.error('Error deleting campaign:', err);
      setError('حدث خطأ أثناء حذف الحملة');
    }
  };

  // فتح نافذة إرسال رسالة
  const openSendModal = (type) => {
    setSendType(type);
    setMessageData({
      subject: type === 'email' ? 'رسالة من E-deal' : '',
      content: '',
      recipients: []
    });
    fetchEstablishments();
    setShowSendModal(true);
  };

  // تحديث بيانات الرسالة
  const handleMessageChange = (field, value) => {
    setMessageData({
      ...messageData,
      [field]: value
    });
  };

  // تحديث المستلمين المحددين
  const handleRecipientChange = (establishmentId) => {
    if (selectedEstablishments.includes(establishmentId)) {
      setSelectedEstablishments(selectedEstablishments.filter(id => id !== establishmentId));
    } else {
      setSelectedEstablishments([...selectedEstablishments, establishmentId]);
    }
  };

  // إرسال رسالة
  const sendMessage = async () => {
    try {
      const recipients = establishments
        .filter(est => selectedEstablishments.includes(est.id))
        .map(est => sendType === 'email' ? est.email : est.whatsapp)
        .filter(Boolean);
      
      if (recipients.length === 0) {
        setError('يرجى اختيار مستلمين صالحين');
        return;
      }
      
      const endpoint = sendType === 'email' ? '/api/marketing/send-email' : '/api/marketing/send-whatsapp';
      const payload = sendType === 'email' 
        ? { 
            recipients, 
            subject: messageData.subject, 
            content: messageData.content 
          }
        : { 
            recipients, 
            message: messageData.content 
          };
      
      await axios.post(endpoint, payload);
      setShowSendModal(false);
      // إظهار رسالة نجاح
    } catch (err) {
      console.error('Error sending message:', err);
      setError('حدث خطأ أثناء إرسال الرسالة');
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

  if (loading && campaigns.length === 0) {
    return <div className="loading-spinner">جاري تحميل البيانات...</div>;
  }

  return (
    <Container fluid className="marketing-container">
      <h1 className="page-title">نظام التسويق</h1>
      
      <Tab.Container id="marketing-tabs" defaultActiveKey="campaigns">
        <Card className="mb-4">
          <Card.Header>
            <Nav variant="tabs">
              <Nav.Item>
                <Nav.Link eventKey="campaigns">الحملات التسويقية</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="messages">الرسائل</Nav.Link>
              </Nav.Item>
            </Nav>
          </Card.Header>
          <Card.Body>
            <Tab.Content>
              <Tab.Pane eventKey="campaigns">
                {/* شريط البحث والإجراءات للحملات */}
                <Row className="align-items-center mb-4">
                  <Col md={6}>
                    <Form onSubmit={handleSearch}>
                      <InputGroup>
                        <Form.Control
                          type="text"
                          placeholder="بحث عن حملة..."
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
                    <Link to="/marketing/campaigns/add" className="btn btn-success me-2">
                      <FontAwesomeIcon icon={faPlus} className="me-1" />
                      إنشاء حملة
                    </Link>
                  </Col>
                </Row>
                
                {/* فلاتر البحث للحملات */}
                {showFilters && (
                  <Row className="mb-4">
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label>الحالة</Form.Label>
                        <Form.Select 
                          value={filters.status} 
                          onChange={(e) => handleFilterChange('status', e.target.value)}
                        >
                          <option value="">جميع الحالات</option>
                          <option value="new">جديدة</option>
                          <option value="active">نشطة</option>
                          <option value="paused">متوقفة</option>
                          <option value="completed">مكتملة</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label>النوع</Form.Label>
                        <Form.Select 
                          value={filters.type} 
                          onChange={(e) => handleFilterChange('type', e.target.value)}
                        >
                          <option value="">جميع الأنواع</option>
                          <option value="email">بريد إلكتروني</option>
                          <option value="whatsapp">واتساب</option>
                          <option value="social">وسائل التواصل</option>
                          <option value="mixed">مختلط</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={4} className="d-flex align-items-end">
                      <Button variant="secondary" onClick={resetFilters} className="w-100">
                        إعادة تعيين الفلاتر
                      </Button>
                    </Col>
                  </Row>
                )}
                
                {/* عرض الخطأ إذا وجد */}
                {error && (
                  <div className="alert alert-danger">{error}</div>
                )}
                
                {/* جدول الحملات */}
                <div className="table-responsive">
                  <Table hover>
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>اسم الحملة</th>
                        <th>النوع</th>
                        <th>الحالة</th>
                        <th>تاريخ البدء</th>
                        <th>تاريخ الانتهاء</th>
                        <th>الإجراءات</th>
                      </tr>
                    </thead>
                    <tbody>
                      {campaigns.length > 0 ? (
                        campaigns.map(campaign => (
                          <tr key={campaign.id}>
                            <td>{campaign.id}</td>
                            <td>{campaign.name}</td>
                            <td>
                              {campaign.type === 'email' && 'بريد إلكتروني'}
                              {campaign.type === 'whatsapp' && 'واتساب'}
                              {campaign.type === 'social' && 'وسائل التواصل'}
                              {campaign.type === 'mixed' && 'مختلط'}
                            </td>
                            <td>
                              <span className={`status-badge ${campaign.status}`}>
                                {campaign.status === 'new' && 'جديدة'}
                                {campaign.status === 'active' && 'نشطة'}
                                {campaign.status === 'paused' && 'متوقفة'}
                                {campaign.status === 'completed' && 'مكتملة'}
                              </span>
                            </td>
                            <td>{new Date(campaign.start_date).toLocaleDateString('ar-SA')}</td>
                            <td>{campaign.end_date ? new Date(campaign.end_date).toLocaleDateString('ar-SA') : '-'}</td>
                            <td>
                              <Link 
                                to={`/marketing/campaigns/edit/${campaign.id}`} 
                                className="btn btn-sm btn-primary me-1"
                              >
                                <FontAwesomeIcon icon={faEdit} />
                              </Link>
                              <Button 
                                variant="danger" 
                                size="sm"
                                onClick={() => confirmDelete(campaign)}
                              >
                                <FontAwesomeIcon icon={faTrash} />
                              </Button>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="7" className="text-center">لا توجد حملات</td>
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
              </Tab.Pane>
              
              <Tab.Pane eventKey="messages">
                {/* أزرار إرسال الرسائل */}
                <Row className="mb-4">
                  <Col>
                    <Card>
                      <Card.Body>
                        <h5 className="mb-3">إرسال رسائل</h5>
                        <div className="d-flex flex-wrap gap-2">
                          <Button 
                            variant="primary" 
                            onClick={() => openSendModal('email')}
                          >
                            <FontAwesomeIcon icon={faEnvelope} className="me-2" />
                            إرسال بريد إلكتروني
                          </Button>
                          <Button 
                            variant="success" 
                            onClick={() => openSendModal('whatsapp')}
                          >
                            <FontAwesomeIcon icon={faWhatsapp} className="me-2" />
                            إرسال واتساب
                          </Button>
                          <Button variant="info">
                            <FontAwesomeIcon icon={faShareAlt} className="me-2" />
                            نشر على وسائل التواصل
                          </Button>
                        </div>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>
                
                {/* إحصائيات الرسائل */}
                <Row>
                  <Col md={4}>
                    <Card className="stats-card">
                      <Card.Body>
                        <h5>رسائل البريد الإلكتروني</h5>
                        <div className="d-flex justify-content-between align-items-center mt-3">
                          <div>
                            <h3>245</h3>
                            <p>إجمالي الرسائل المرسلة</p>
                          </div>
                          <div className="stats-icon email">
                            <FontAwesomeIcon icon={faEnvelope} />
                       
(Content truncated due to size limit. Use line ranges to read in chunks)
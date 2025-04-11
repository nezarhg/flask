import React, { useState, useRef } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Table, Spinner, ProgressBar } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUpload, faDownload, faFileExcel, faFileCsv, faFilter, faSync, faCheck, faTimes } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';
import './DataImport.css';

const DataImport = () => {
  const [activeTab, setActiveTab] = useState('import');
  const [file, setFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [exportFilters, setExportFilters] = useState({
    region_id: '',
    city_id: '',
    establishment_type_id: '',
    search: ''
  });
  const [exporting, setExporting] = useState(false);
  const [exportResult, setExportResult] = useState(null);
  const [regions, setRegions] = useState([]);
  const [cities, setCities] = useState([]);
  const [establishmentTypes, setEstablishmentTypes] = useState([]);
  const [error, setError] = useState(null);
  
  const fileInputRef = useRef(null);

  // جلب البيانات المرجعية عند تحميل المكون
  React.useEffect(() => {
    fetchReferenceData();
  }, []);

  // جلب البيانات المرجعية (المناطق، المدن، أنواع المنشآت)
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
      setError('حدث خطأ أثناء جلب البيانات المرجعية');
    }
  };

  // جلب المدن عند اختيار منطقة
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

  // معالجة تغيير المنطقة
  const handleRegionChange = (e) => {
    const regionId = e.target.value;
    setExportFilters({
      ...exportFilters,
      region_id: regionId,
      city_id: ''
    });
    fetchCities(regionId);
  };

  // معالجة تغيير الفلاتر الأخرى
  const handleFilterChange = (field, value) => {
    setExportFilters({
      ...exportFilters,
      [field]: value
    });
  };

  // معالجة اختيار ملف
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // التحقق من نوع الملف
      const fileExt = selectedFile.name.split('.').pop().toLowerCase();
      if (['xlsx', 'xls', 'csv'].includes(fileExt)) {
        setFile(selectedFile);
        setError(null);
      } else {
        setFile(null);
        setError('نوع الملف غير مدعوم. الأنواع المدعومة: Excel (.xlsx, .xls) و CSV (.csv)');
      }
    }
  };

  // استيراد البيانات
  const importData = async () => {
    if (!file) {
      setError('الرجاء اختيار ملف للاستيراد');
      return;
    }

    setImporting(true);
    setError(null);
    setImportResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/data/import/establishments', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setImportResult(response.data);
    } catch (err) {
      console.error('Error importing data:', err);
      setError(err.response?.data?.error || 'حدث خطأ أثناء استيراد البيانات');
    } finally {
      setImporting(false);
    }
  };

  // تصدير البيانات
  const exportData = async (format) => {
    setExporting(true);
    setError(null);
    setExportResult(null);

    try {
      const response = await axios.post('/api/data/export/establishments', {
        format: format,
        criteria: exportFilters
      });

      setExportResult(response.data);
      
      // تنزيل الملف تلقائيًا
      if (response.data.success) {
        window.location.href = response.data.file_path;
      }
    } catch (err) {
      console.error('Error exporting data:', err);
      setError(err.response?.data?.error || 'حدث خطأ أثناء تصدير البيانات');
    } finally {
      setExporting(false);
    }
  };

  // إعادة تعيين نموذج الاستيراد
  const resetImportForm = () => {
    setFile(null);
    setImportResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // إعادة تعيين نموذج التصدير
  const resetExportForm = () => {
    setExportFilters({
      region_id: '',
      city_id: '',
      establishment_type_id: '',
      search: ''
    });
    setExportResult(null);
    setError(null);
  };

  return (
    <Container fluid className="data-import-container">
      <h1 className="page-title">استيراد وتصدير البيانات</h1>
      
      <Row className="mb-4">
        <Col>
          <div className="tabs">
            <div 
              className={`tab ${activeTab === 'import' ? 'active' : ''}`}
              onClick={() => setActiveTab('import')}
            >
              <FontAwesomeIcon icon={faUpload} className="me-2" />
              استيراد البيانات
            </div>
            <div 
              className={`tab ${activeTab === 'export' ? 'active' : ''}`}
              onClick={() => setActiveTab('export')}
            >
              <FontAwesomeIcon icon={faDownload} className="me-2" />
              تصدير البيانات
            </div>
          </div>
        </Col>
      </Row>
      
      {error && (
        <Alert variant="danger" onClose={() => setError(null)} dismissible>
          {error}
        </Alert>
      )}
      
      {activeTab === 'import' ? (
        <Card className="mb-4">
          <Card.Header>استيراد بيانات المنشآت</Card.Header>
          <Card.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>اختر ملف للاستيراد</Form.Label>
                  <div className="custom-file-upload">
                    <input 
                      type="file" 
                      className="form-control" 
                      onChange={handleFileChange}
                      accept=".xlsx,.xls,.csv"
                      ref={fileInputRef}
                      disabled={importing}
                    />
                    <div className="file-format-hint">
                      الصيغ المدعومة: Excel (.xlsx, .xls), CSV (.csv)
                    </div>
                  </div>
                </Form.Group>
                
                {file && (
                  <div className="selected-file mb-3">
                    <FontAwesomeIcon 
                      icon={file.name.endsWith('.csv') ? faFileCsv : faFileExcel} 
                      className="me-2"
                    />
                    <span>{file.name}</span>
                  </div>
                )}
                
                <div className="d-flex">
                  <Button 
                    variant="primary" 
                    onClick={importData}
                    disabled={!file || importing}
                    className="me-2"
                  >
                    {importing ? (
                      <>
                        <Spinner
                          as="span"
                          animation="border"
                          size="sm"
                          role="status"
                          aria-hidden="true"
                          className="me-2"
                        />
                        جاري الاستيراد...
                      </>
                    ) : (
                      <>
                        <FontAwesomeIcon icon={faUpload} className="me-2" />
                        استيراد البيانات
                      </>
                    )}
                  </Button>
                  
                  <Button 
                    variant="outline-secondary" 
                    onClick={resetImportForm}
                    disabled={importing}
                  >
                    إعادة تعيين
                  </Button>
                </div>
              </Col>
              
              <Col md={6}>
                <div className="import-instructions">
                  <h5>تعليمات الاستيراد:</h5>
                  <ul>
                    <li>يجب أن يحتوي الملف على عمود "اسم المنشأة" كحد أدنى.</li>
                    <li>الأعمدة المدعومة: اسم المنشأة، الرقم الموحد، المنطقة، المدينة، نوع المنشأة، رقم الجوال، البريد الإلكتروني، العنوان، الموقع الإلكتروني، ملاحظات.</li>
                    <li>سيتم تحديث بيانات المنشآت الموجودة إذا تطابق الرقم الموحد أو اسم المنشأة.</li>
                    <li>سيتم إنشاء المناطق والمدن وأنواع المنشآت تلقائيًا إذا لم تكن موجودة.</li>
                  </ul>
                  
                  <div className="mt-3">
                    <a href="/api/data/templates/establishments" className="btn btn-sm btn-outline-primary">
                      <FontAwesomeIcon icon={faDownload} className="me-1" />
                      تحميل قالب الاستيراد
                    </a>
                  </div>
                </div>
              </Col>
            </Row>
            
            {importResult && (
              <div className="import-result mt-4">
                <h5>نتائج الاستيراد:</h5>
                <div className="result-summary">
                  <div className="result-item">
                    <div className="result-label">تم استيراد:</div>
                    <div className="result-value success">{importResult.imported_count} منشأة</div>
                  </div>
                  <div className="result-item">
                    <div className="result-label">تم تحديث:</div>
                    <div className="result-value info">{importResult.updated_count} منشأة</div>
                  </div>
                  <div className="result-item">
                    <div className="result-label">أخطاء:</div>
                    <div className="result-value danger">{importResult.errors.length}</div>
                  </div>
                </div>
                
                {importResult.errors.length > 0 && (
                  <div className="errors-container mt-3">
                    <h6>تفاصيل الأخطاء:</h6>
                    <ul className="error-list">
                      {importResult.errors.map((error, index) => (
                        <li key={index}>{error}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </Card.Body>
        </Card>
      ) : (
        <Card className="mb-4">
          <Card.Header>تصدير بيانات المنشآت</Card.Header>
          <Card.Body>
            <Row>
              <Col md={6}>
                <Form>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>المنطقة</Form.Label>
                        <Form.Select 
                          value={exportFilters.region_id} 
                          onChange={handleRegionChange}
                          disabled={exporting}
                        >
                          <option value="">جميع المناطق</option>
                          {regions.map(region => (
                            <option key={region.id} value={region.id}>{region.name}</option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>المدينة</Form.Label>
                        <Form.Select 
                          value={exportFilters.city_id} 
                          onChange={(e) => handleFilterChange('city_id', e.target.value)}
                          disabled={!exportFilters.region_id || exporting}
                        >
                          <option value="">جميع المدن</option>
                          {cities.map(city => (
                            <option key={city.id} value={city.id}>{city.name}</option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                    </Col>
                  </Row>
                  
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>نوع المنشأة</Form.Label>
                        <Form.Select 
                          value={exportFilters.establishment_type_id} 
                          onChange={(e) => handleFilterChange('establishment_type_id', e.target.value)}
                          disabled={exporting}
                        >
                          <option value="">جميع الأنواع</option>
                          {establishmentTypes.map(type => (
                            <option key={type.id} value={type.id}>{type.name}</option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>بحث</Form.Label>
                        <Form.Control 
                          type="text" 
                          placeholder="اسم المنشأة، الرقم الموحد، البريد الإلكتروني..." 
                          value={exportFilters.search}
                          onChange={(e) => handleFilterChange('search', e.target.value)}
                          disabled={exporting}
                        />
                      </Form.Group>
                    </Col>
                  </Row>
                  
                  <div className="export-buttons">
                    <Button 
                      variant="success" 
                      onClick={() => exportData('xlsx')}
                      disabled={exporting}
                      className="me-2"
                    >
                      {exporting ? (
                        <>
                          <Spinner
                            as="span"
                            animation="border"
                            size="sm"
                            role="status"
                            aria-hidden="true"
                            className="me-2"
                          />
                          جاري التصدير...
                        </>
                      ) : (
                        <>
                          <FontAwesomeIcon icon={faFileExcel} className="me-2" />
                          تصدير Excel
                        </>
                      )}
                    </Button>
                    
                    <Button 
                      variant="info" 
                      onClick={() => exportData('csv')}
                      disabled={exporting}
                      className="me-2"
                    >
                      <FontAwesomeIcon icon={faFileCsv} className="me-2" />
                      تصدير CSV
                    </Button>
                    
                    <Button 
                      variant="outline-secondary" 
                      onClick={resetExportForm}
                      disabled={exporting}
                    >
                      <FontAwesomeIcon icon={faSync} className="me-2" />
                      إعادة تعيين الفلاتر
                    </Button>
                  </div>
                </Form>
              </Col>
              
              <Col md={6}>
                <div className="export-instructions">
                  <h5>تعليمات التصدير:</h5>
                  <ul>
                    <li>يمكنك تصفية البيانات حسب المنطقة، المدينة، نوع المنشأة، أو البحث النصي.</li>
                    <li>اترك الفلاتر فارغة لتصدير جميع البيانات.</li>
                    <li>يمكنك اختيار تنسيق التصدير (Excel أو CSV).</li>
                    <li>سيتم تنزيل الملف تلقائيًا بعد اكتمال عملية التصدير.</li>
                  </ul>
                </div>
              </Col>
            </Row>
            
            {exportResult && (
              <div className="export-result mt-4">
                <h5>نتائج التصدير:</h5>
                <div className="result-summary">
                  <div className="result-item">
                    <div className="result-label">عدد السجلات:</div>
                    <div className="result-value success">{exportResult.records_count}</div>
                  </div>
                  <div className="result-item">
                    <div className="result-label">اسم الملف:</div>
                    <div className="result-value">{exportResult.file_name}</div>
                  </div>
                  <div className="result-item">
                    <div className="result-label">الحالة:</div>
                    <div className="result-value success">
                      <FontAwesomeIcon icon={faCheck} className="me-1" />
                      تم التصدير بنجاح
                    </div>
                  </div>
                </div>
                
                <div className="mt-3">
                  <a 
                    href={exportResult.file_path} 
                    className="btn btn-primary"
                    download
                  >
                    <FontAwesomeIcon icon={faDownload} className="me-2" />
                    تنزيل الملف مرة أخرى
                  </a>
                </div>
              </div>
            )}
          </Card.Body>
        </Card>
      )}
    </Container>
  );
};

export default DataImport;

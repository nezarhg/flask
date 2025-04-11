import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import Dashboard from './components/dashboard/Dashboard';
import Establishments from './components/establishments/Establishments';
import Marketing from './components/marketing/Marketing';
import Statistics from './components/statistics/Statistics';
import AIAssistant from './components/ai-assistant/AIAssistant';
import DataImport from './components/data-import/DataImport';
import Login from './components/auth/Login';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);
  const [user, setUser] = React.useState(null);
  const [sidebarOpen, setSidebarOpen] = React.useState(true);
  
  // التحقق من حالة تسجيل الدخول عند تحميل التطبيق
  React.useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      setIsAuthenticated(true);
      setUser(JSON.parse(userData));
    }
  }, []);
  
  // تسجيل الدخول
  const handleLogin = (userData, token) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setIsAuthenticated(true);
    setUser(userData);
  };
  
  // تسجيل الخروج
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
  };
  
  // التبديل بين فتح وإغلاق الشريط الجانبي
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
  
  return (
    <Router>
      {isAuthenticated ? (
        <div className="app-container">
          <Sidebar isOpen={sidebarOpen} user={user} />
          <div className={`main-content ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
            <Header 
              user={user} 
              onLogout={handleLogout} 
              toggleSidebar={toggleSidebar}
            />
            <Container fluid className="content-container">
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/establishments" element={<Establishments />} />
                <Route path="/marketing" element={<Marketing />} />
                <Route path="/statistics" element={<Statistics />} />
                <Route path="/ai-assistant" element={<AIAssistant />} />
                <Route path="/data-import" element={<DataImport />} />
                <Route path="*" element={<Navigate to="/dashboard" />} />
              </Routes>
            </Container>
          </div>
        </div>
      ) : (
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      )}
    </Router>
  );
}

export default App;

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faHome, 
  faBuilding, 
  faBullhorn, 
  faChartBar, 
  faUsers, 
  faRobot, 
  faCode, 
  faCog,
  faFileImport
} from '@fortawesome/free-solid-svg-icons';
import './Sidebar.css';

const Sidebar = ({ isOpen, user }) => {
  const location = useLocation();
  
  // التحقق من الصلاحيات
  const hasPermission = (permission) => {
    if (user?.role === 'admin') return true;
    return user?.permissions?.includes(permission);
  };
  
  // التحقق من المسار النشط
  const isActive = (path) => {
    return location.pathname.startsWith(path);
  };

  return (
    <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-header">
        <h3>E-deal</h3>
        <p>إدارة علاقات العملاء</p>
      </div>
      
      <div className="sidebar-content">
        <ul className="sidebar-menu">
          <li className={isActive('/dashboard') ? 'active' : ''}>
            <Link to="/dashboard">
              <FontAwesomeIcon icon={faHome} />
              <span>لوحة التحكم</span>
            </Link>
          </li>
          
          {hasPermission('establishment_read') && (
            <li className={isActive('/establishments') ? 'active' : ''}>
              <Link to="/establishments">
                <FontAwesomeIcon icon={faBuilding} />
                <span>المنشآت</span>
              </Link>
            </li>
          )}
          
          {hasPermission('marketing_manage') && (
            <li className={isActive('/marketing') ? 'active' : ''}>
              <Link to="/marketing">
                <FontAwesomeIcon icon={faBullhorn} />
                <span>التسويق</span>
              </Link>
            </li>
          )}
          
          {hasPermission('statistics_view') && (
            <li className={isActive('/statistics') ? 'active' : ''}>
              <Link to="/statistics">
                <FontAwesomeIcon icon={faChartBar} />
                <span>الإحصائيات</span>
              </Link>
            </li>
          )}
          
          {user?.role === 'admin' && (
            <li className={isActive('/users') ? 'active' : ''}>
              <Link to="/users">
                <FontAwesomeIcon icon={faUsers} />
                <span>المستخدمين</span>
              </Link>
            </li>
          )}
          
          {hasPermission('ai_assistant_use') && (
            <li className={isActive('/ai-assistant') ? 'active' : ''}>
              <Link to="/ai-assistant">
                <FontAwesomeIcon icon={faRobot} />
                <span>المساعد الذكي</span>
              </Link>
            </li>
          )}
          
          {hasPermission('api_access') && (
            <li className={isActive('/api-docs') ? 'active' : ''}>
              <Link to="/api-docs">
                <FontAwesomeIcon icon={faCode} />
                <span>توثيق API</span>
              </Link>
            </li>
          )}
          
          {hasPermission('data_import_export') && (
            <li className={isActive('/data-import') ? 'active' : ''}>
              <Link to="/data-import">
                <FontAwesomeIcon icon={faFileImport} />
                <span>استيراد وتصدير البيانات</span>
              </Link>
            </li>
          )}
          
          {user?.role === 'admin' && (
            <li className={isActive('/settings') ? 'active' : ''}>
              <Link to="/settings">
                <FontAwesomeIcon icon={faCog} />
                <span>الإعدادات</span>
              </Link>
            </li>
          )}
        </ul>
      </div>
      
      <div className="sidebar-footer">
        <p>الإصدار 1.0.0</p>
      </div>
    </div>
  );
};

export default Sidebar;

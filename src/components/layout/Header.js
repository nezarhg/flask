import React, { useState } from 'react';
import { Navbar, Container, Nav, NavDropdown } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBars, faUser, faBell, faSignOutAlt, faCog } from '@fortawesome/free-solid-svg-icons';
import './Header.css';

const Header = ({ toggleSidebar, user, onLogout }) => {
  const [notificationsCount, setNotificationsCount] = useState(3);
  
  return (
    <Navbar bg="white" expand="lg" className="header-navbar">
      <Container fluid>
        <div className="d-flex align-items-center">
          <button className="sidebar-toggle" onClick={toggleSidebar}>
            <FontAwesomeIcon icon={faBars} />
          </button>
          <Navbar.Brand href="/dashboard" className="mr-3">E-deal</Navbar.Brand>
        </div>
        
        <div className="header-right">
          <div className="notifications-dropdown">
            <div className="icon-button">
              <FontAwesomeIcon icon={faBell} />
              {notificationsCount > 0 && (
                <span className="badge">{notificationsCount}</span>
              )}
            </div>
          </div>
          
          <NavDropdown 
            title={
              <div className="user-dropdown-toggle">
                <span className="user-name">{user?.full_name}</span>
                <FontAwesomeIcon icon={faUser} className="user-icon" />
              </div>
            } 
            id="user-dropdown"
            align="end"
          >
            <NavDropdown.Item href="/profile">
              <FontAwesomeIcon icon={faUser} className="dropdown-icon" />
              الملف الشخصي
            </NavDropdown.Item>
            
            {user?.role === 'admin' && (
              <NavDropdown.Item href="/settings">
                <FontAwesomeIcon icon={faCog} className="dropdown-icon" />
                الإعدادات
              </NavDropdown.Item>
            )}
            
            <NavDropdown.Divider />
            
            <NavDropdown.Item onClick={onLogout}>
              <FontAwesomeIcon icon={faSignOutAlt} className="dropdown-icon" />
              تسجيل الخروج
            </NavDropdown.Item>
          </NavDropdown>
        </div>
      </Container>
    </Navbar>
  );
};

export default Header;

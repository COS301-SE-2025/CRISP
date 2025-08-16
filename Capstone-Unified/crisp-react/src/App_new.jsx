import React, { useState } from 'react';

// Import all components
import UserManagement from './components/enhanced/UserManagement';
import TrustManagement from './components/trust/TrustManagement';
import UserProfile from './components/user/UserProfile';
import Notifications from './components/notifications/Notifications';
import Institutions from './components/institutions/Institutions';
import Reports from './components/reports/Reports';
import ThreatFeedList from './components/threat/ThreatFeedList';
import IndicatorTable from './components/threat/IndicatorTable';
import UnifiedDashboard from './components/dashboard/UnifiedDashboard';

// Dashboard component - now uses UnifiedDashboard
const Dashboard = () => <UnifiedDashboard />;

function App() {
  const [activePage, setActivePage] = useState('dashboard');

  const renderActivePage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard />;
      case 'users':
        return <UserManagement />;
      case 'trust':
        return <TrustManagement />;
      case 'profile':
        return <UserProfile />;
      case 'notifications':
        return <Notifications />;
      case 'institutions':
        return <Institutions />;
      case 'reports':
        return <Reports />;
      case 'threat-feeds':
        return <ThreatFeedList />;
      case 'indicators':
        return <IndicatorTable />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      {/* Navigation Sidebar */}
      <nav className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <i className="fas fa-shield-alt"></i>
            <span>CRISP</span>
          </div>
        </div>
        
        <div className="nav-menu">
          <button 
            className={`nav-item ${activePage === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActivePage('dashboard')}
          >
            <i className="fas fa-tachometer-alt"></i>
            <span>Dashboard</span>
          </button>
          
          <button 
            className={`nav-item ${activePage === 'users' ? 'active' : ''}`}
            onClick={() => setActivePage('users')}
          >
            <i className="fas fa-users"></i>
            <span>User Management</span>
          </button>
          
          <button 
            className={`nav-item ${activePage === 'trust' ? 'active' : ''}`}
            onClick={() => setActivePage('trust')}
          >
            <i className="fas fa-handshake"></i>
            <span>Trust Management</span>
          </button>
          
          <button 
            className={`nav-item ${activePage === 'threat-feeds' ? 'active' : ''}`}
            onClick={() => setActivePage('threat-feeds')}
          >
            <i className="fas fa-rss"></i>
            <span>Threat Feeds</span>
          </button>
          
          <button 
            className={`nav-item ${activePage === 'indicators' ? 'active' : ''}`}
            onClick={() => setActivePage('indicators')}
          >
            <i className="fas fa-shield-alt"></i>
            <span>Threat Indicators</span>
          </button>
          
          <button 
            className={`nav-item ${activePage === 'institutions' ? 'active' : ''}`}
            onClick={() => setActivePage('institutions')}
          >
            <i className="fas fa-building"></i>
            <span>Institutions</span>
          </button>
          
          <button 
            className={`nav-item ${activePage === 'reports' ? 'active' : ''}`}
            onClick={() => setActivePage('reports')}
          >
            <i className="fas fa-chart-line"></i>
            <span>Reports</span>
          </button>
          
          <button 
            className={`nav-item ${activePage === 'notifications' ? 'active' : ''}`}
            onClick={() => setActivePage('notifications')}
          >
            <i className="fas fa-bell"></i>
            <span>Notifications</span>
          </button>
          
          <button 
            className={`nav-item ${activePage === 'profile' ? 'active' : ''}`}
            onClick={() => setActivePage('profile')}
          >
            <i className="fas fa-user-circle"></i>
            <span>Profile</span>
          </button>
        </div>
        
        <div className="sidebar-footer">
          <button className="nav-item logout">
            <i className="fas fa-sign-out-alt"></i>
            <span>Logout</span>
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="main-content">
        <div className="content-wrapper">
          {renderActivePage()}
        </div>
      </main>

      <style jsx>{`
        .app {
          display: flex;
          height: 100vh;
          background: #f8f9fa;
        }

        .sidebar {
          width: 250px;
          background: linear-gradient(135deg, #0056b3, #004494);
          color: white;
          display: flex;
          flex-direction: column;
          box-shadow: 2px 0 4px rgba(0,0,0,0.1);
          z-index: 1000;
        }

        .sidebar-header {
          padding: 20px;
          border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .logo {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 20px;
          font-weight: 700;
        }

        .logo i {
          font-size: 24px;
        }

        .nav-menu {
          flex: 1;
          padding: 20px 0;
          overflow-y: auto;
        }

        .nav-item {
          width: 100%;
          padding: 12px 20px;
          background: none;
          border: none;
          color: rgba(255,255,255,0.8);
          display: flex;
          align-items: center;
          gap: 12px;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
          text-align: left;
        }

        .nav-item:hover {
          background: rgba(255,255,255,0.1);
          color: white;
        }

        .nav-item.active {
          background: rgba(255,255,255,0.15);
          color: white;
          border-right: 3px solid #28a745;
        }

        .nav-item i {
          width: 18px;
          text-align: center;
        }

        .sidebar-footer {
          padding: 20px 0;
          border-top: 1px solid rgba(255,255,255,0.1);
        }

        .nav-item.logout:hover {
          background: rgba(220, 53, 69, 0.2);
          color: #ff6b6b;
        }

        .main-content {
          flex: 1;
          overflow-y: auto;
          background: #f8f9fa;
        }

        .content-wrapper {
          min-height: 100%;
        }

        /* Global styles for components */
        :global(.btn) {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          transition: all 0.2s;
          text-decoration: none;
          line-height: 1.5;
        }

        :global(.btn-primary) {
          background: #0056b3;
          color: white;
        }

        :global(.btn-primary:hover) {
          background: #004494;
        }

        :global(.btn-secondary) {
          background: #6c757d;
          color: white;
        }

        :global(.btn-secondary:hover) {
          background: #5a6268;
        }

        :global(.btn-outline) {
          background: transparent;
          border: 1px solid #dee2e6;
          color: #495057;
        }

        :global(.btn-outline:hover) {
          background: #f8f9fa;
          border-color: #adb5bd;
        }

        :global(.btn-sm) {
          padding: 6px 12px;
          font-size: 12px;
        }

        :global(.btn-danger) {
          background: #dc3545;
          color: white;
        }

        :global(.btn-danger:hover) {
          background: #c82333;
        }

        /* Font Awesome styles */
        :global(.fas) {
          font-family: "Font Awesome 5 Free";
          font-weight: 900;
        }

        :global(.far) {
          font-family: "Font Awesome 5 Free";
          font-weight: 400;
        }

        /* Responsive design */
        @media (max-width: 768px) {
          .app {
            flex-direction: column;
          }

          .sidebar {
            width: 100%;
            height: auto;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1000;
          }

          .main-content {
            margin-top: 60px;
          }

          .nav-menu {
            display: flex;
            overflow-x: auto;
            padding: 10px;
          }

          .nav-item {
            flex-shrink: 0;
            padding: 8px 16px;
            border-radius: 20px;
            margin-right: 8px;
          }

          .nav-item span {
            display: none;
          }
        }
      `}</style>
    </div>
  );
}

export default App;
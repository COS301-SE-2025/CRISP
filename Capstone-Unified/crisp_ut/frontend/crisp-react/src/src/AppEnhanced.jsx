import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { useNavigate } from 'react-router-dom';
import CSSStyles from './assets/CSSStyles';
import './assets/trust-management.css'; // Import Trust Management CSS
import './assets/notifications.css'; // Import notification styles
import './App.css'; // Import working App.css
import logoImage from './assets/BlueV2.png';
import { getUserProfile, updateUserProfile, getUserStatistics, changePassword, getEmailStatistics, getSystemHealth, sendTestEmail, testGmailConnection, getAuditLogs, getComprehensiveAuditLogs, getOrganizations, markAllNotificationsRead } from './api.js';
import * as api from './api.js'; // Keep App.jsx's general API import for compatibility
import LoadingSpinner from './components/LoadingSpinner.jsx';
import UserManagement from './components/UserManagement.jsx';
import UserManagementComponent from './components/UserManagement'; // App.jsx import
import OrganisationManagement from './components/OrganisationManagement.jsx';
import TrustManagement from './components/TrustManagement.jsx';
import ErrorBoundary from './components/ErrorBoundary.jsx';
import ThreatFeedList from './components/ThreatFeedList.jsx';
import IndicatorTable from './components/IndicatorTable.jsx';
import PhoneNumberInput from './components/PhoneNumberInput.jsx';
import Pagination from './components/Pagination.jsx';
import { NotificationProvider, useNotifications } from './components/NotificationManager.jsx';
import NotificationWatcher from './components/NotificationWatcher';

// Error Boundary for Chart Component (from working version)
class ChartErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Chart Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '20px',
          textAlign: 'center',
          background: '#fff5f5',
          border: '1px solid #fed7d7',
          borderRadius: '4px',
          color: '#c53030'
        }}>
          <i className="fas fa-exclamation-triangle" style={{fontSize: '24px', marginBottom: '10px'}}></i>
          <h3>Chart Error</h3>
          <p>Something went wrong with the chart visualization.</p>
          <button 
            onClick={() => this.setState({ hasError: false, error: null })}
            style={{
              background: '#0056b3',
              color: 'white',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Additional API Configuration for enhanced components
const API_BASE_URL = 'http://localhost:8000';

// API Helper Functions with Authentication (enhanced version)
const getAuthHeaders = () => {
  const token = localStorage.getItem('crisp_auth_token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  } else {
    console.warn('No authentication token found in localStorage');
  }
  return headers;
};

const enhancedApi = {
  get: async (endpoint) => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: getAuthHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`API Error: ${endpoint}`, error);
      return null;
    }
  },
  
  post: async (endpoint, data) => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`API Error: ${endpoint}`, error);
      return null;
    }
  },
  
  put: async (endpoint, data) => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`API Error: ${endpoint}`, error);
      return null;
    }
  },
  
  delete: async (endpoint) => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      // For DELETE requests, we might get 204 No Content with no response body
      if (response.status === 204) {
        return { success: true };
      }
      
      // Try to parse JSON, but handle empty responses
      const text = await response.text();
      return text ? JSON.parse(text) : { success: true };
    } catch (error) {
      console.error(`API Error: ${endpoint}`, error);
      return null;
    }
  }
};

function AppEnhanced({ user, onLogout, isAdmin }) {
  const navigate = useNavigate();
  
  // State to manage the active page and navigation parameters
  const [activePage, setActivePage] = useState(() => {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('page') || 'dashboard';
  });
  const [isLoading, setIsLoading] = useState(false);
  const [urlParams, setUrlParams] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    return {
      page: params.get('page') || 'dashboard',
      tab: params.get('tab') || null,
      section: params.get('section') || null
    };
  });
  
  // Navigation state for enhanced components
  const [navigationState, setNavigationState] = useState({
    triggerModal: null,
    modalParams: {}
  });
  
  // Function to get current URL parameters
  const getUrlParams = () => urlParams;
  
  // Determine user role and permissions
  const userRole = user?.role || 'viewer';
  const isBlueVisionAdmin = userRole === 'BlueVisionAdmin';
  const isPublisher = userRole === 'publisher' || isBlueVisionAdmin;
  const isViewer = userRole === 'viewer';
  
  // Organization context
  const userOrganization = user?.organization || null;
  const userOrganizationId = userOrganization?.id || null;
  
  // Backward compatibility for isAdmin prop
  const hasAdminAccess = isAdmin || isBlueVisionAdmin;
  
  // Shared notification state for both header and notifications page
  const [notifications, setNotifications] = useState([]);
  const [isLoadingNotifications, setIsLoadingNotifications] = useState(false);
  
  // Function to switch between pages
  const showPage = (pageId, triggerAction = null, actionParams = {}) => {
    console.log(`Navigating to page: ${pageId}`, { triggerAction, actionParams });
    
    setActivePage(pageId);
    
    // Update URL parameters
    const newParams = { ...urlParams, page: pageId };
    if (actionParams.tab) newParams.tab = actionParams.tab;
    if (actionParams.section) newParams.section = actionParams.section;
    
    setUrlParams(newParams);
    
    // Set navigation state for modal triggers
    if (triggerAction) {
      setNavigationState({
        triggerModal: triggerAction,
        modalParams: actionParams
      });
    } else {
      setNavigationState({
        triggerModal: null,
        modalParams: {}
      });
    }
    
    // Update browser URL
    const searchParams = new URLSearchParams();
    Object.entries(newParams).forEach(([key, value]) => {
      if (value) searchParams.set(key, value);
    });
    
    const newUrl = `${window.location.pathname}?${searchParams.toString()}`;
    window.history.pushState(null, '', newUrl);
  };

  // Handle browser back/forward navigation
  useEffect(() => {
    const handlePopState = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const page = urlParams.get('page') || 'dashboard';
      const tab = urlParams.get('tab') || null;
      const section = urlParams.get('section') || null;
      
      setActivePage(page);
      setUrlParams({ page, tab, section });
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);
  
  // Fetch notifications on component mount
  useEffect(() => {
    fetchNotifications();
  }, [user]);

  const fetchNotifications = async () => {
    setIsLoadingNotifications(true);
    try {
      // Try to get email statistics and system health as notification sources
      const [emailStats, systemHealth] = await Promise.all([
        getEmailStatistics().catch(() => null),
        getSystemHealth().catch(() => null)
      ]);

      const generatedNotifications = [];
      let notificationId = 1;

      // Generate notifications based on email statistics
      if (emailStats) {
        if (emailStats.total_sent > 0) {
          generatedNotifications.push({
            id: notificationId++,
            type: 'info',
            title: 'Email notifications sent',
            message: `${emailStats.total_sent} email notifications sent successfully`,
            timestamp: new Date(Date.now() - 30 * 60000),
            read: false,
          });
        }
        
        if (emailStats.failed_emails > 0) {
          generatedNotifications.push({
            id: notificationId++,
            type: 'warning',
            title: 'Failed email notifications',
            message: `${emailStats.failed_emails} email notifications failed to send`,
            timestamp: new Date(Date.now() - 60 * 60000),
            read: false,
          });
        }
      }

      setNotifications(generatedNotifications);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setIsLoadingNotifications(false);
    }
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="App">
      {/* Custom Styles */}
      <CSSStyles />
      
      {/* Header */}
      <Header 
        user={user} 
        onLogout={onLogout}
        showPage={showPage}
        notifications={notifications}
        setNotifications={setNotifications}
        isLoadingNotifications={isLoadingNotifications}
        isAdmin={hasAdminAccess}
        isBlueVisionAdmin={isBlueVisionAdmin}
        isPublisher={isPublisher}
        userRole={userRole}
        unreadCount={unreadCount}
      />
      
      {/* Main Navigation */}
      <MainNav 
        activePage={activePage} 
        showPage={showPage} 
        isAdmin={hasAdminAccess}
        userRole={userRole}
        isPublisher={isPublisher}
      />

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {/* Dashboard */}
          <Dashboard active={activePage === 'dashboard'} showPage={showPage} />

          {/* Threat Feeds */}
          <ThreatFeeds active={activePage === 'threat-feeds'} navigationState={navigationState} setNavigationState={setNavigationState} />

          {/* IoC Management */}
          <IoCManagement active={activePage === 'ioc-management'} />

          {/* TTP Analysis */}
          <TTPAnalysis active={activePage === 'ttp-analysis'} />

          {/* Institutions */}
          <Institutions active={activePage === 'institutions'} />

          {/* Reports */}
          <Reports active={activePage === 'reports'} />

          {/* Trust Management - Publisher/Admin access only */}
          {(isPublisher || hasAdminAccess) && (
            <TrustManagement active={activePage === 'trust-management'} />
          )}

          {/* User Management - Admin access only */}
          {hasAdminAccess && (
            <UserManagement active={activePage === 'user-management'} />
          )}

          {/* Organisation Management - Admin access only */}
          {hasAdminAccess && (
            <OrganisationManagement active={activePage === 'organisation-management'} />
          )}

          {/* Alerts */}
          <Alerts active={activePage === 'alerts'} />
        </div>
      </main>
    </div>
  );
}
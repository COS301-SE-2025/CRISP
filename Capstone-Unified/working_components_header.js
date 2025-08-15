import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';

// Error Boundary for Chart Component
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

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// API Helper Functions with Authentication
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

const api = {
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

function App() {
  // State to manage the active page and navigation parameters
  const [activePage, setActivePage] = useState('dashboard');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAuthenticating, setIsAuthenticating] = useState(true);

  // Automatically login as admin on component mount
  useEffect(() => {
    const autoLogin = async () => {
      // Check if already has valid token
      const existingToken = localStorage.getItem('crisp_auth_token');
      if (existingToken) {
        setIsAuthenticated(true);
        setIsAuthenticating(false);
        return;
      }

      // Auto-login as admin
      try {
        console.log('Attempting auto-login...');
        const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: 'admin', password: 'admin123' })
        });

        console.log('Login response status:', response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log('Login response data:', data);
          if (data.access) {
            localStorage.setItem('crisp_auth_token', data.access);
            localStorage.setItem('crisp_refresh_token', data.refresh);
            localStorage.setItem('crisp_user', JSON.stringify(data.user));
            console.log('Login successful, token stored');
            setIsAuthenticated(true);
            setIsAuthenticating(false);
          } else {
            console.error('No access token in response');
            setIsAuthenticated(false);
            setIsAuthenticating(false);
          }
        } else {
          console.error('Auto-login failed with status:', response.status, response.statusText);
          setIsAuthenticated(false);
          setIsAuthenticating(false);
        }
      } catch (error) {
        console.error('Auto-login error:', error);
        setIsAuthenticated(false);
        setIsAuthenticating(false);
      }
    };

    autoLogin();
  }, []);
  const [navigationState, setNavigationState] = useState({
    triggerModal: null,
    modalParams: {}
  });

  // Function to switch between pages with optional modal triggers
  const showPage = (pageId, modalTrigger = null, modalParams = {}) => {
    setActivePage(pageId);
    setNavigationState({
      triggerModal: modalTrigger,
      modalParams: modalParams
    });
    
    // Update URL with parameters if modal trigger is provided
    if (modalTrigger) {
      const url = new URL(window.location);
      url.searchParams.set('modal', modalTrigger);
      if (Object.keys(modalParams).length > 0) {
        url.searchParams.set('params', JSON.stringify(modalParams));
      }
      window.history.pushState({}, '', url);
    } else {
      // Clear URL parameters when no modal trigger
      const url = new URL(window.location);
      url.searchParams.delete('modal');
      url.searchParams.delete('params');
      window.history.pushState({}, '', url);
    }
  };

  // Handle browser back/forward navigation
  useEffect(() => {
    const handlePopState = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const modalTrigger = urlParams.get('modal');
      const modalParams = urlParams.get('params');
      
      if (modalTrigger) {
        setNavigationState({
          triggerModal: modalTrigger,
          modalParams: modalParams ? JSON.parse(modalParams) : {}
        });
      } else {
        setNavigationState({
          triggerModal: null,
          modalParams: {}
        });
      }
    };

    window.addEventListener('popstate', handlePopState);
    
    // Check for initial URL parameters on page load
    handlePopState();
    
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);


  // Show loading screen during authentication
  if (isAuthenticating) {
    return (
      <div className="App">
        <div className="loading-screen">
          <div className="loading-spinner"></div>
          <h2>Loading CRISP System...</h2>
          <p>Authenticating...</p>
        </div>
      </div>
    );
  }

  // Show login screen when not authenticated
  if (!isAuthenticated) {
    return (
      <div className="App">
        <div className="login-screen">
          <div className="login-container">
            <h2>CRISP System Login</h2>
            <p>Please login to continue</p>
            <button 
              className="btn btn-primary"
              onClick={() => {
                setIsAuthenticating(true);
                setIsAuthenticated(false);
                // Clear any existing tokens
                localStorage.removeItem('crisp_auth_token');
                localStorage.removeItem('crisp_refresh_token');
                localStorage.removeItem('crisp_user');
                // Retry auto-login
                window.location.reload();
              }}
            >
              <i className="fas fa-sign-in-alt"></i> Login as Admin
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      {/* Header */}
      <Header showPage={showPage} />
      
      {/* Main Navigation */}
      <MainNav activePage={activePage} showPage={showPage} />

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
          
          {/* Notifications */}
          <Notifications active={activePage === 'notifications'} />
          
          {/* User Profile */}
          <UserProfile active={activePage === 'profile'} />
        </div>
      </main>

    </div>
  );
}

// Header Component
function Header({ showPage }) {
  return (
    <header>
      <div className="container header-container">
        <a href="#" className="logo">
          <div className="logo-icon"><i className="fas fa-shield-alt"></i></div>
          <div className="logo-text">CRISP</div>
        </a>
        <div className="nav-actions">
          <div className="search-bar">
            <span className="search-icon"><i className="fas fa-search"></i></span>
            <input type="text" placeholder="Search platform..." />
          </div>
          <div className="notifications" onClick={() => showPage('notifications')} style={{cursor: 'pointer'}}>
            <i className="fas fa-bell"></i>
            <span className="notification-count">3</span>
          </div>
          <div className="user-profile" onClick={() => showPage('profile')} style={{cursor: 'pointer'}}>
            <div className="avatar">A</div>
            <div className="user-info">
              <div className="user-name">Admin</div>
              <div className="user-role">Security Analyst</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

// Main Navigation Component
function MainNav({ activePage, showPage }) {
  const [systemStatus, setSystemStatus] = useState('loading');
  
  // Check system status periodically
  useEffect(() => {
    const checkStatus = async () => {
      const status = await api.get('/api/threat-feeds/');
      setSystemStatus(status ? 'active' : 'offline');
    };
    
    checkStatus();
    const statusInterval = setInterval(checkStatus, 30000); // Check every 30 seconds
    
    return () => clearInterval(statusInterval);
  }, []);
  
  return (
    <nav className="main-nav">
      <div className="container nav-container">
        <ul className="nav-links">
          <li>
            <a 
              onClick={() => showPage('dashboard')} 
              className={activePage === 'dashboard' ? 'active' : ''}
            >
              <i className="fas fa-chart-line"></i> Dashboard
            </a>
          </li>
          <li>
            <a 
              onClick={() => showPage('threat-feeds')} 
              className={activePage === 'threat-feeds' ? 'active' : ''}
            >
              <i className="fas fa-rss"></i> Threat Feeds
            </a>
          </li>
          <li>
            <a 
              onClick={() => showPage('ioc-management')} 
              className={activePage === 'ioc-management' ? 'active' : ''}
            >
              <i className="fas fa-search"></i> IoC Management
            </a>
          </li>
          <li>
            <a 
              onClick={() => showPage('ttp-analysis')} 
              className={activePage === 'ttp-analysis' ? 'active' : ''}
            >
              <i className="fas fa-sitemap"></i> TTP Analysis
            </a>
          </li>
          <li>
            <a 
              onClick={() => showPage('institutions')} 
              className={activePage === 'institutions' ? 'active' : ''}
            >
              <i className="fas fa-building"></i> Institutions
            </a>
          </li>
          <li>
            <a 
              onClick={() => showPage('reports')} 
              className={activePage === 'reports' ? 'active' : ''}
            >
              <i className="fas fa-file-alt"></i> Reports
            </a>
          </li>
        </ul>
        <div className="nav-right">
          <div className="status-indicator">
            <span 
              className="status-dot" 
              style={{
                backgroundColor: systemStatus === 'active' ? '#28a745' : 
                                systemStatus === 'loading' ? '#ffc107' : '#dc3545'
              }}
            ></span>
            <span>
              {systemStatus === 'active' ? 'System Online' : 
               systemStatus === 'loading' ? 'Checking...' : 'System Offline'}
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
}

// Dashboard Component

import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import UserProfile from './components/user/UserProfile.jsx';
import UserManagement from './components/enhanced/UserManagement.jsx';
import OrganisationManagement from './components/enhanced/OrganisationManagement.jsx';
import TrustManagement from './components/enhanced/TrustManagement.jsx';
import Institutions from './components/institutions/Institutions.jsx';

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
      const headers = getAuthHeaders();
      const token = localStorage.getItem('crisp_auth_token');
      
      // Don't make API calls if we don't have a token (except for auth endpoints)
      if (!token && !endpoint.includes('/auth/')) {
        console.warn(`Skipping API call to ${endpoint} - no authentication token`);
        return null;
      }
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: headers
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          console.warn(`Authentication failed for ${endpoint} - token may be expired`);
          // Could trigger re-authentication here if needed
        }
        throw new Error(`HTTP ${response.status}`);
      }
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

function App({ user, onLogout, isAdmin }) {
  // State to manage the active page and navigation parameters
  const [activePage, setActivePage] = useState('dashboard');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAuthenticating, setIsAuthenticating] = useState(true);

  // Automatically login as admin on component mount
  useEffect(() => {
    const validateToken = async (token) => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/profile/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.ok;
      } catch (error) {
        console.error('Token validation error:', error);
        return false;
      }
    };

    const autoLogin = async () => {
      setIsAuthenticating(true);
      
      // Check if already has valid token
      const existingToken = localStorage.getItem('crisp_auth_token');
      if (existingToken) {
        console.log('Validating existing token...');
        const isTokenValid = await validateToken(existingToken);
        if (isTokenValid) {
          console.log('Existing token is valid');
          setIsAuthenticated(true);
          setIsAuthenticating(false);
          return;
        } else {
          console.log('Existing token is invalid, clearing and re-authenticating...');
          localStorage.removeItem('crisp_auth_token');
          localStorage.removeItem('crisp_refresh_token');
          localStorage.removeItem('crisp_user');
        }
      }

      // Auto-login as admin
      try {
        console.log('Attempting auto-login as admin...');
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
            if (data.refresh) {
              localStorage.setItem('crisp_refresh_token', data.refresh);
            }
            if (data.user) {
              localStorage.setItem('crisp_user', JSON.stringify(data.user));
            }
            console.log('Auto-login successful, token stored');
            setIsAuthenticated(true);
          } else {
            console.error('No access token in response');
            setIsAuthenticated(false);
          }
        } else {
          const errorText = await response.text();
          console.error('Auto-login failed with status:', response.status, response.statusText);
          console.error('Error response:', errorText);
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Auto-login error:', error);
        console.error('This might indicate the backend server is not running');
        setIsAuthenticated(false);
      }
      
      setIsAuthenticating(false);
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

  // Function to navigate to register user page/modal
  const navigateToRegisterUser = () => {
    showPage('user-management', 'addUser');
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
      <Header showPage={showPage} user={user} onLogout={onLogout} isAdmin={isAdmin} navigateToRegisterUser={navigateToRegisterUser} />
      
      {/* Main Navigation */}
      <MainNav activePage={activePage} showPage={showPage} user={user} onLogout={onLogout} isAdmin={isAdmin} />

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {/* Dashboard */}
          <Dashboard active={activePage === 'dashboard'} showPage={showPage} isAuthenticated={isAuthenticated} isAuthenticating={isAuthenticating} />

          {/* Threat Feeds */}
          <ThreatFeeds active={activePage === 'threat-feeds'} navigationState={navigationState} setNavigationState={setNavigationState} />

          {/* IoC Management */}
          <IoCManagement active={activePage === 'ioc-management'} />

          {/* TTP Analysis */}
          <TTPAnalysis active={activePage === 'ttp-analysis'} />

          {/* Organisations */}
          <Institutions active={activePage === 'institutions'} api={api} showPage={showPage} />

          

          {/* Reports */}
          <Reports active={activePage === 'reports'} />
          
          {/* Notifications */}
          <Notifications active={activePage === 'notifications'} />
          
          {/* User Profile */}
          <UserProfile active={activePage === 'profile'} />
          
          {/* Management Components */}
          <UserManagement active={activePage === 'user-management'} />
          <OrganisationManagement active={activePage === 'organisation-management'} />
          <TrustManagement active={activePage === 'trust-management'} />
        </div>
      </main>

    </div>
  );
}

// Header Component with Enhanced Profile Dropdown
function Header({ showPage, user, onLogout, isAdmin, navigateToRegisterUser }) {
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showManagementSubmenu, setShowManagementSubmenu] = useState(false);
  
  // User profile data processing
  const userInitial = user && user.username ? user.username.charAt(0).toUpperCase() : 'A';
  const userName = user && user.username ? user.username.split('@')[0] : 'Admin';
  const userRole = user?.role || 'Security Analyst';
  
  // Event handlers
  const handleUserMenuClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setShowUserMenu(!showUserMenu);
  };

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.user-profile-container')) {
        setShowUserMenu(false);
        setShowManagementSubmenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close submenu when main menu closes
  useEffect(() => {
    if (!showUserMenu) {
      setShowManagementSubmenu(false);
    }
  }, [showUserMenu]);

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
          
          {/* Enhanced User Profile Menu */}
          <div className="user-profile-container">
            <button className="user-profile" onClick={handleUserMenuClick} type="button">
              <div className="avatar">{userInitial}</div>
              <div className="user-info">
                <div className="user-name">{userName}</div>
                <div className="user-role">{userRole}</div>
              </div>
              <i className="fas fa-chevron-down"></i>
            </button>
            
            {showUserMenu && (
              <div className="user-menu-dropdown">
                <div className="dropdown-header">
                  <div className="user-avatar-large">{userInitial}</div>
                  <div>
                    <div className="user-name-large">{userName}</div>
                    <div className="user-email">{user?.username || 'admin@example.com'}</div>
                  </div>
                </div>
                <div className="menu-divider"></div>
                <div className="menu-items">
                  <button className="menu-item" onClick={() => {setShowUserMenu(false); showPage('profile');}} type="button">
                    <i className="fas fa-user"></i>
                    <span>My Profile</span>
                  </button>
                  <button className="menu-item" onClick={() => {setShowUserMenu(false); showPage('account-settings');}} type="button">
                    <i className="fas fa-cog"></i>
                    <span>Account Settings</span>
                  </button>
                  <div className="menu-divider"></div>
                  <div className="menu-item-submenu">
                    <button className="menu-item" onClick={() => setShowManagementSubmenu(!showManagementSubmenu)} type="button">
                      <i className="fas fa-users"></i>
                      <span>Management</span>
                      <i className={`fas fa-chevron-${showManagementSubmenu ? 'up' : 'down'} submenu-arrow`}></i>
                    </button>
                    {showManagementSubmenu && (
                      <div className="submenu">
                        <button className="submenu-item" onClick={() => {setShowUserMenu(false); setShowManagementSubmenu(false); showPage('user-management');}} type="button">
                          <i className="fas fa-users"></i>
                          <span>User Management</span>
                        </button>
                        <button className="submenu-item" onClick={() => {setShowUserMenu(false); setShowManagementSubmenu(false); showPage('organisation-management');}} type="button">
                          <i className="fas fa-university"></i>
                          <span>Organisation Management</span>
                        </button>
                        <button className="submenu-item" onClick={() => {setShowUserMenu(false); setShowManagementSubmenu(false); showPage('trust-management');}} type="button">
                          <i className="fas fa-handshake"></i>
                          <span>Trust Management</span>
                        </button>
                      </div>
                    )}
                  </div>
                  {/* Admin Settings - BlueVision Admins only */}
                  {userRole === 'BlueVisionAdmin' && (
                    <button className="menu-item" onClick={() => {setShowUserMenu(false); showPage('admin-settings');}} type="button">
                      <i className="fas fa-shield-alt"></i>
                      <span>Admin Settings</span>
                    </button>
                  )}
                  {/* Register User - BlueVision Admins only */}
                  {userRole === 'BlueVisionAdmin' && navigateToRegisterUser && (
                    <button className="menu-item" onClick={() => {setShowUserMenu(false); navigateToRegisterUser();}} type="button">
                      <i className="fas fa-user-plus"></i>
                      <span>Register New User</span>
                    </button>
                  )}
                </div>
                <div className="menu-divider"></div>
                <button className="menu-item logout-item" onClick={() => {setShowUserMenu(false); onLogout();}} type="button">
                  <i className="fas fa-sign-out-alt"></i>
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

// Main Navigation Component
function MainNav({ activePage, showPage, user, onLogout, isAdmin }) {
  const [systemStatus, setSystemStatus] = useState('loading');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showManagementSubmenu, setShowManagementSubmenu] = useState(false);
  
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
              <i className="fas fa-building"></i> Organisations
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
          
          {/* User Profile Dropdown */}
          {user && (
            <div className="user-profile-container">
              <button 
                className="user-profile" 
                onClick={() => setShowUserMenu(!showUserMenu)}
              >
                <div className="avatar">
                  {(user.first_name || user.username || 'U').charAt(0).toUpperCase()}
                </div>
                <div className="user-info">
                  <div className="user-name">
                    {user.first_name && user.last_name 
                      ? `${user.first_name} ${user.last_name}`
                      : user.username
                    }
                  </div>
                  <div className="user-role">{user.role}</div>
                </div>
                <i className="fas fa-chevron-down"></i>
              </button>
              
              {showUserMenu && (
                <div className="user-menu-dropdown">
                  <div className="dropdown-header">
                    <div className="user-avatar-large">
                      {(user.first_name || user.username || 'U').charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="user-name-large">
                        {user.first_name && user.last_name 
                          ? `${user.first_name} ${user.last_name}`
                          : user.username
                        }
                      </div>
                      <div className="user-email">{user.email || user.username}</div>
                    </div>
                  </div>
                  <div className="menu-divider"></div>
                  <div className="menu-items">
                    {/* Profile & Settings */}
                    <button className="menu-item" onClick={() => { showPage('profile'); setShowUserMenu(false); }}>
                      <i className="fas fa-user"></i>
                      <span>My Profile</span>
                    </button>
                    
                    {/* Management Submenu */}
                    <div className="menu-item-submenu">
                      <button 
                        className="menu-item" 
                        onClick={() => setShowManagementSubmenu(!showManagementSubmenu)}
                      >
                        <i className="fas fa-users"></i>
                        <span>Management</span>
                        <i className={`fas fa-chevron-${showManagementSubmenu ? 'up' : 'down'} submenu-arrow`}></i>
                      </button>
                      {showManagementSubmenu && (
                        <div className="submenu">
                          <button 
                            className="submenu-item" 
                            onClick={() => { showPage('user-management'); setShowUserMenu(false); setShowManagementSubmenu(false); }}
                          >
                            <i className="fas fa-users"></i>
                            <span>User Management</span>
                          </button>
                          <button 
                            className="submenu-item" 
                            onClick={() => { showPage('institutions'); setShowUserMenu(false); setShowManagementSubmenu(false); }}
                          >
                            <i className="fas fa-university"></i>
                            <span>Organisation Management</span>
                          </button>
                          <button 
                            className="submenu-item" 
                            onClick={() => { showPage('trust-management'); setShowUserMenu(false); setShowManagementSubmenu(false); }}
                          >
                            <i className="fas fa-handshake"></i>
                            <span>Trust Management</span>
                          </button>
                        </div>
                      )}
                    </div>
                    
                    {/* Admin-only options */}
                    {isAdmin && (
                      <button 
                        className="menu-item" 
                        onClick={() => { showPage('notifications'); setShowUserMenu(false); }}
                      >
                        <i className="fas fa-shield-alt"></i>
                        <span>Admin Settings</span>
                      </button>
                    )}
                  </div>
                  <div className="menu-divider"></div>
                  <button className="menu-item logout-item" onClick={() => { onLogout(); setShowUserMenu(false); }}>
                    <i className="fas fa-sign-out-alt"></i>
                    <span>Logout</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

// Dashboard Component
function Dashboard({ active, showPage, isAuthenticated, isAuthenticating }) {
  if (!active) return null;
  
  // State for dashboard data
  const [dashboardStats, setDashboardStats] = useState({
    threat_feeds: 0,
    indicators: 0,
    ttps: 0,
    status: 'loading'
  });
  
  // State for recent IoC data
  const [recentIoCs, setRecentIoCs] = useState([]);
  const [iocLoading, setIocLoading] = useState(false);
  const [iocError, setIocError] = useState(null);
  
  // D3 Chart References and State
  const chartRef = useRef(null);
  const tooltipRef = useRef(null);
  const cleanupRef = useRef(null);
  const [chartData, setChartData] = useState([]);
  const [chartLoading, setChartLoading] = useState(false);
  const [chartError, setChartError] = useState(null);
  const [chartFilters, setChartFilters] = useState({
    days: 30,
    type: null,
    feed_id: null
  });
  const [chartSummary, setChartSummary] = useState({
    total_indicators: 0,
    avg_daily: 0,
    type_distribution: []
  });

  // System Health Monitoring State
  const [systemHealth, setSystemHealth] = useState({
    status: 'unknown',
    database: { status: 'unknown' },
    services: { redis: { status: 'unknown' } },
    system: { cpu_percent: 0, memory_percent: 0, disk_percent: 0 },
    feeds: { total: 0, active: 0, external: 0, feeds: [] },
    errors: [],
    timestamp: null
  });
  const [healthLoading, setHealthLoading] = useState(false);
  const [healthError, setHealthError] = useState(null);
  
  // Recent Activities State
  const [recentActivities, setRecentActivities] = useState([]);
  const [activitiesLoading, setActivitiesLoading] = useState(false);
  const [activitiesError, setActivitiesError] = useState(null);

  // Dashboard Export State
  const [showDashboardExportModal, setShowDashboardExportModal] = useState(false);
  const [dashboardExportFormat, setDashboardExportFormat] = useState('json');
  const [dashboardExporting, setDashboardExporting] = useState(false);
  
  // Fetch dashboard data from backend
  useEffect(() => {
    if (active && !isAuthenticating && isAuthenticated) {
      fetchDashboardData();
      fetchRecentIoCs();
      fetchChartData();
      fetchSystemHealth();
      fetchRecentActivities();
    }
  }, [active, isAuthenticated, isAuthenticating]);

  // Refetch chart data when filters change
  useEffect(() => {
    if (active && !isAuthenticating && isAuthenticated) {
      fetchChartData();
    }
  }, [chartFilters, active, isAuthenticated, isAuthenticating]);

  // Auto-refresh system health every 30 seconds
  useEffect(() => {
    if (!active || isAuthenticating || !isAuthenticated) return;
    
    const interval = setInterval(() => {
      fetchSystemHealth();
    }, 30000);
    
    return () => clearInterval(interval);
  }, [active, isAuthenticated, isAuthenticating]);
  
  const fetchDashboardData = async () => {
    const feedsData = await api.get('/api/threat-feeds/');
    if (feedsData) {
      let totalIndicators = 0;
      let totalTTPs = 0;
      
      // Get indicator and TTP counts from each feed
      if (feedsData.results) {
        for (const feed of feedsData.results) {
          const feedStatus = await api.get(`/api/threat-feeds/${feed.id}/status/`);
          if (feedStatus) {
            totalIndicators += feedStatus.indicator_count || 0;
            totalTTPs += feedStatus.ttp_count || 0;
          }
        }
      }
      
      setDashboardStats({
        threat_feeds: feedsData.count || 0,
        indicators: totalIndicators,
        ttps: totalTTPs,
        status: 'active'
      });
    }
  };

  // Fetch recent IoCs for dashboard table
  const fetchRecentIoCs = async () => {
    setIocLoading(true);
    setIocError(null);
    
    try {
      const indicatorsData = await api.get('/api/indicators/');
      if (indicatorsData && indicatorsData.results) {
        // Transform and limit to most recent 6 IoCs
        const transformedIoCs = indicatorsData.results
          .slice(0, 6)
          .map(indicator => transformIoCForDashboard(indicator));
        
        setRecentIoCs(transformedIoCs);
      } else {
        setRecentIoCs([]);
      }
    } catch (error) {
      console.error('Error fetching recent IoCs:', error);
      setIocError('Failed to load recent threat intelligence');
      setRecentIoCs([]);
    } finally {
      setIocLoading(false);
    }
  };

  // Fetch chart data from API
  const fetchChartData = async () => {
    setChartLoading(true);
    setChartError(null);
    
    try {
      const queryParams = new URLSearchParams({
        days: chartFilters.days.toString()
      });
      
      if (chartFilters.type) {
        queryParams.append('type', chartFilters.type);
      }
      if (chartFilters.feed_id) {
        queryParams.append('feed_id', chartFilters.feed_id);
      }
      
      const response = await api.get(`/api/threat-activity-chart/?${queryParams}`);
      
      if (response && response.success) {
        setChartData(response.data);
        setChartSummary(response.summary);
        
        // Redraw chart with new data
        if (chartRef.current) {
          createThreatActivityChart(response.data, response.summary);
        }
      } else {
        throw new Error('Failed to fetch chart data');
      }
    } catch (error) {
      console.error('Error fetching chart data:', error);
      setChartError('Failed to load chart data');
      setChartData([]);
    } finally {
      setChartLoading(false);
    }
  };

  // Fetch system health data from API
  const fetchSystemHealth = async () => {
    setHealthLoading(true);
    setHealthError(null);
    
    try {
      const response = await api.get('/api/system-health/');
      
      if (response) {
        setSystemHealth({
          status: response.status || 'unknown',
          database: response.database || { status: 'unknown' },
          services: response.services || { redis: { status: 'unknown' } },
          system: response.system || { cpu_percent: 0, memory_percent: 0, disk_percent: 0 },
          feeds: response.feeds || { total: 0, active: 0, external: 0, feeds: [] },
          errors: response.errors || [],
          timestamp: response.timestamp || new Date().toISOString()
        });
      } else {
        throw new Error('Failed to fetch system health data');
      }
    } catch (error) {
      console.error('Error fetching system health:', error);
      setHealthError('Failed to load system health data');
      // Set fallback data
      setSystemHealth(prev => ({
        ...prev,
        status: 'error',
        timestamp: new Date().toISOString()
      }));
    } finally {
      setHealthLoading(false);
    }
  };

  // Transform IoC data for dashboard display
  const transformIoCForDashboard = (indicator) => {
    // Map indicator types to display names
    const typeMapping = {
      'ip': 'IP Address',
      'domain': 'Domain',
      'url': 'URL',
      'file_hash': 'File Hash',
      'email': 'Email Address',
      'user_agent': 'User Agent'
    };

    // Determine severity based on confidence level
    const getSeverity = (confidence) => {
      if (confidence >= 80) return { level: 'high', label: 'High' };
      if (confidence >= 50) return { level: 'medium', label: 'Medium' };
      return { level: 'low', label: 'Low' };
    };

    // Format IoC value for display (truncate if too long)
    const formatValue = (value, type) => {
      if (type === 'file_hash' && value.length > 16) {
        return value.substring(0, 16) + '...';
      }
      if (value.length > 30) {
        return value.substring(0, 30) + '...';
      }
      return value;
    };

    const severity = getSeverity(indicator.confidence || 50);

    // Type icons mapping
    const typeIcons = {
      'ip': 'fa-network-wired',
      'domain': 'fa-globe',
      'url': 'fa-link',
      'file_hash': 'fa-file-signature',
      'email': 'fa-envelope',
      'user_agent': 'fa-browser'
    };

    // Age calculation
    const getAge = (dateString) => {
      const date = new Date(dateString);
      const now = new Date();
      const diffTime = Math.abs(now - date);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 1) return '1 day ago';
      if (diffDays < 7) return `${diffDays} days ago`;
      if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
      return `${Math.ceil(diffDays / 30)} months ago`;
    };
    
    return {
      id: indicator.id,
      displayType: typeMapping[indicator.type] || indicator.type.charAt(0).toUpperCase() + indicator.type.slice(1),
      typeIcon: typeIcons[indicator.type] || 'fa-question-circle',
      rawType: indicator.type,
      title: indicator.name || '',
      value: indicator.value,
      truncatedValue: formatValue(indicator.value, indicator.type),
      source: indicator.threat_feed?.name || indicator.source || 'Internal',
      severity: severity.label,
      severityClass: severity.level,
      confidence: indicator.confidence || 50,
      status: indicator.is_active !== false ? 'active' : 'inactive',
      isAnonymized: indicator.is_anonymized || false,
      age: getAge(indicator.created_at || new Date().toISOString()),
      created_at: indicator.created_at || new Date().toISOString()
    };
  };

  // Fetch recent activities
  const fetchRecentActivities = async () => {
    setActivitiesLoading(true);
    setActivitiesError(null);
    
    try {
      const response = await api.get('/api/recent-activities/?limit=10');
      if (response && response.success) {
        setRecentActivities(response.activities || []);
      } else {
        setActivitiesError('Failed to load recent activities');
      }
    } catch (error) {
      console.error('Error fetching recent activities:', error);
      setActivitiesError('Failed to load recent activities');
    } finally {
      setActivitiesLoading(false);
    }
  };

  // Utility functions for system health display
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'connected':
      case 'active':
      case 'success':
        return '#28a745';
      case 'warning':
      case 'stale':
        return '#ffc107';
      case 'error':
      case 'disconnected':
      case 'failed':
      case 'inactive':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'connected':
      case 'active':
      case 'success':
        return 'fas fa-check-circle';
      case 'warning':
      case 'stale':
        return 'fas fa-exclamation-triangle';
      case 'error':
      case 'disconnected':
      case 'failed':
      case 'inactive':
        return 'fas fa-times-circle';
      default:
        return 'fas fa-question-circle';
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  };

  const formatUptime = (seconds) => {
    if (!seconds) return 'Unknown';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      const remainingHours = hours % 24;
      return `${days}d ${remainingHours}h`;
    }
    
    return `${hours}h ${minutes}m`;
  };

  const testFeedConnection = async (feedId) => {
    try {
      const response = await api.post(`/api/threat-feeds/${feedId}/test-connection/`);
      if (response && response.success) {
        // Refresh system health to show updated connection status
        fetchSystemHealth();
        alert('Connection test successful!');
      } else {
        alert('Connection test failed. Please check the feed configuration.');
      }
    } catch (error) {
      console.error('Error testing feed connection:', error);
      alert('Connection test failed due to an error.');
    }
  };
  
  // Set up D3 charts when component mounts or data changes
  useEffect(() => {
    if (active && chartRef.current && chartData.length > 0) {
      createThreatActivityChart(chartData, chartSummary);
    }
    
    // Cleanup function
    return () => {
      if (cleanupRef.current) {
        cleanupRef.current();
      }
    };
  }, [active, chartData, chartSummary]);

  // Real-time updates - refresh chart data every 5 minutes
  useEffect(() => {
    if (!active) return;

    const interval = setInterval(() => {
      console.log('Auto-refreshing chart data...');
      fetchChartData();
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [active, chartFilters]);

  // Handle window resize for responsive chart
  useEffect(() => {
    const handleResize = () => {
      if (active && chartRef.current && chartData.length > 0) {
        // Debounce resize events
        clearTimeout(window.chartResizeTimeout);
        window.chartResizeTimeout = setTimeout(() => {
          createThreatActivityChart(chartData, chartSummary);
        }, 300);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      clearTimeout(window.chartResizeTimeout);
    };
  }, [active, chartData, chartSummary]);

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      // Clean up chart elements
      if (cleanupRef.current) {
        cleanupRef.current();
      }
      
      // Clean up any remaining tooltips
      d3.selectAll('.chart-tooltip').remove();
      
      // Clear any remaining timeouts
      clearTimeout(window.chartResizeTimeout);
    };
  }, []);

  const createThreatActivityChart = (data = [], summary = {}) => {
    // Clean up previous chart and tooltip
    if (cleanupRef.current) {
      cleanupRef.current();
    }
    
    // Clear the container safely
    if (chartRef.current) {
      // Use React-safe approach to clear D3 content
      const container = d3.select(chartRef.current);
      container.selectAll("*").remove();
    }
    
    // Return early if no container or data
    if (!chartRef.current || !data || data.length === 0) {
      if (chartRef.current) {
        const svg = d3.select(chartRef.current)
          .append("svg")
          .attr("width", "100%")
          .attr("height", 300)
          .attr("viewBox", `0 0 ${chartRef.current.clientWidth || 400} 300`);
        
        svg.append("text")
          .attr("x", "50%")
          .attr("y", "50%")
          .attr("text-anchor", "middle")
          .attr("dominant-baseline", "middle")
          .style("font-size", "14px")
          .style("fill", "#666")
          .text(chartLoading ? "Loading chart data..." : "No data available");
      }
      return;
    }

    try {
      // Responsive dimensions
      const containerWidth = chartRef.current.clientWidth || 400;
      const width = Math.max(containerWidth, 400);
      const height = 350;
      const margin = { 
        top: 40, 
        right: 60, 
        bottom: 60, 
        left: 70 
      };
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;

      // Create SVG with proper cleanup
      const svg = d3.select(chartRef.current)
        .append("svg")
        .attr("width", "100%")
        .attr("height", height)
        .attr("viewBox", `0 0 ${width} ${height}`)
        .style("max-width", "100%")
        .style("height", "auto");

      const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

      // Parse dates and prepare data
      const parseDate = d3.timeParse("%Y-%m-%d");
      const formattedData = data.map(d => ({
        date: parseDate(d.date),
        count: d.count,
        types: d.types || {},
        originalDate: d.date
      })).filter(d => d.date && !isNaN(d.count));

      if (formattedData.length === 0) {
        svg.append("text")
          .attr("x", "50%")
          .attr("y", "50%")
          .attr("text-anchor", "middle")
          .attr("dominant-baseline", "middle")
          .style("font-size", "14px")
          .style("fill", "#666")
          .text("No valid data to display");
        return;
      }

      // Dynamic scales
      const x = d3.scaleTime()
        .domain(d3.extent(formattedData, d => d.date))
        .range([0, innerWidth]);

      const maxCount = d3.max(formattedData, d => d.count) || 1;
      const y = d3.scaleLinear()
        .domain([0, maxCount * 1.1])
        .range([innerHeight, 0])
        .nice();

      // Create tooltip - ensure it's properly tracked
      let tooltip = tooltipRef.current;
      if (!tooltip) {
        tooltip = d3.select("body").append("div")
          .attr("class", "chart-tooltip")
          .style("opacity", 0)
          .style("position", "absolute")
          .style("background", "rgba(0, 0, 0, 0.9)")
          .style("color", "white")
          .style("padding", "12px")
          .style("border-radius", "6px")
          .style("font-size", "13px")
          .style("pointer-events", "none")
          .style("z-index", "1000")
          .style("box-shadow", "0 4px 12px rgba(0, 0, 0, 0.3)");
        
        tooltipRef.current = tooltip;
      }

      // Add gradient
      const defs = svg.append("defs");
      const gradientId = `areaGradient-${Date.now()}`;
      
      const gradient = defs.append("linearGradient")
        .attr("id", gradientId)
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "0%")
        .attr("y2", "100%");

      gradient.append("stop")
        .attr("offset", "0%")
        .attr("stop-color", "#0056b3")
        .attr("stop-opacity", 0.8);

      gradient.append("stop")
        .attr("offset", "100%")
        .attr("stop-color", "#00a0e9")
        .attr("stop-opacity", 0.1);

      // Add grid lines
      g.append("g")
        .attr("class", "grid")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x)
          .ticks(Math.min(7, formattedData.length))
          .tickSize(-innerHeight)
          .tickFormat("")
        )
        .style("stroke-dasharray", "3,3")
        .style("opacity", 0.3);

      g.append("g")
        .attr("class", "grid")
        .call(d3.axisLeft(y)
          .ticks(6)
          .tickSize(-innerWidth)
          .tickFormat("")
        )
        .style("stroke-dasharray", "3,3")
        .style("opacity", 0.3);

      // Add area chart
      const area = d3.area()
        .x(d => x(d.date))
        .y0(innerHeight)
        .y1(d => y(d.count))
        .curve(d3.curveCardinal);

      g.append("path")
        .datum(formattedData)
        .attr("fill", `url(#${gradientId})`)
        .attr("d", area);

      // Add line chart
      const line = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.count))
        .curve(d3.curveCardinal);

      g.append("path")
        .datum(formattedData)
        .attr("fill", "none")
        .attr("stroke", "#0056b3")
        .attr("stroke-width", 3)
        .attr("d", line);

      // Add interactive dots
      g.selectAll(".dot")
        .data(formattedData)
        .enter().append("circle")
        .attr("class", "dot")
        .attr("cx", d => x(d.date))
        .attr("cy", d => y(d.count))
        .attr("r", 4)
        .attr("fill", "#0056b3")
        .attr("stroke", "white")
        .attr("stroke-width", 2)
        .style("cursor", "pointer")
        .on("mouseover", function(event, d) {
          d3.select(this)
            .transition().duration(200)
            .attr("r", 6)
            .attr("fill", "#ff6b35");

          const formatDate = d3.timeFormat("%B %d, %Y");
          const typeBreakdown = Object.entries(d.types)
            .map(([type, count]) => `${type}: ${count}`)
            .join("<br>");

          if (tooltip) {
            tooltip.transition().duration(200).style("opacity", .9);
            tooltip.html(`
              <strong>${formatDate(d.date)}</strong><br/>
              Total IoCs: <strong>${d.count}</strong><br/>
              ${typeBreakdown ? `<br/><em>Breakdown:</em><br/>${typeBreakdown}` : ''}
            `)
              .style("left", (event.pageX + 10) + "px")
              .style("top", (event.pageY - 28) + "px");
          }
        })
        .on("mouseout", function(event, d) {
          d3.select(this)
            .transition().duration(200)
            .attr("r", 4)
            .attr("fill", "#0056b3");

          if (tooltip) {
            tooltip.transition().duration(500).style("opacity", 0);
          }
        });

      // Add axes
      const formatTick = d3.timeFormat("%m/%d");
      g.append("g")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x)
          .ticks(Math.min(7, formattedData.length))
          .tickFormat(formatTick)
        )
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-45)");

      g.append("g")
        .call(d3.axisLeft(y).ticks(6))
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end")
        .style("fill", "#666")
        .text("IoC Count");

      // Add title
      g.append("text")
        .attr("x", innerWidth / 2)
        .attr("y", -15)
        .attr("text-anchor", "middle")
        .style("font-size", "18px")
        .style("font-weight", "600")
        .style("fill", "#2d3748")
        .text("Threat Activity Trends");

      // Add summary stats
      const statsText = `Total: ${summary.total_indicators || 0} IoCs | Daily Avg: ${summary.avg_daily || 0}`;
      g.append("text")
        .attr("x", innerWidth / 2)
        .attr("y", innerHeight + 50)
        .attr("text-anchor", "middle")
        .style("font-size", "12px")
        .style("fill", "#666")
        .text(statsText);

      // Set up cleanup function
      cleanupRef.current = () => {
        if (tooltipRef.current) {
          tooltipRef.current.remove();
          tooltipRef.current = null;
        }
        if (chartRef.current) {
          d3.select(chartRef.current).selectAll("*").remove();
        }
      };

    } catch (error) {
      console.error('Error creating chart:', error);
      setChartError('Failed to create chart visualization');
    }
  };

  // Dashboard Export Functions
  function closeDashboardExportModal() {
    setShowDashboardExportModal(false);
    setDashboardExportFormat('json');
  }

  async function handleDashboardExport() {
    setDashboardExporting(true);
    
    try {
      let exportData;
      let filename;
      let mimeType;

      const exportPayload = {
        export_date: new Date().toISOString(),
        dashboard_stats: dashboardStats,
        recent_iocs: recentIoCs,
        system_health: systemHealth,
        chart_data: chartData,
        chart_summary: chartSummary,
        chart_filters: chartFilters
      };

      switch (dashboardExportFormat) {
        case 'csv':
          exportData = exportDashboardToCSV(exportPayload);
          filename = `dashboard_export_${new Date().toISOString().split('T')[0]}.csv`;
          mimeType = 'text/csv';
          break;
          
        case 'json':
          exportData = exportDashboardToJSON(exportPayload);
          filename = `dashboard_export_${new Date().toISOString().split('T')[0]}.json`;
          mimeType = 'application/json';
          break;
          
        case 'summary':
          exportData = exportDashboardToSummary(exportPayload);
          filename = `dashboard_summary_${new Date().toISOString().split('T')[0]}.txt`;
          mimeType = 'text/plain';
          break;
          
        default:
          throw new Error('Unsupported export format');
      }

      // Create and download file
      const blob = new Blob([exportData], { type: mimeType });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      closeDashboardExportModal();
      
      console.log(`Successfully exported dashboard data as ${dashboardExportFormat.toUpperCase()}`);
      
    } catch (error) {
      console.error('Dashboard export failed:', error);
      alert('Export failed. Please try again.');
    } finally {
      setDashboardExporting(false);
    }
  }

  function exportDashboardToCSV(data) {
    let csvContent = '';
    
    // Add header
    csvContent += 'CRISP Dashboard Export\n';
    csvContent += `Export Date: ${new Date(data.export_date).toLocaleString()}\n\n`;
    
    // Dashboard Statistics
    csvContent += 'DASHBOARD STATISTICS\n';
    csvContent += 'Metric,Value\n';
    csvContent += `Active IoCs,${data.dashboard_stats.indicators || 0}\n`;
    csvContent += `TTPs,${data.dashboard_stats.ttps || 0}\n`;
    csvContent += `Threat Feeds,${data.dashboard_stats.threat_feeds || 0}\n`;
    csvContent += `Platform Status,${data.dashboard_stats.status || 'Unknown'}\n\n`;

    // Recent IoCs Table
    if (data.recent_iocs && data.recent_iocs.length > 0) {
      csvContent += 'RECENT INDICATORS OF COMPROMISE\n';
      csvContent += 'Type,Indicator,Source,Severity,Status,Created\n';
      
      data.recent_iocs.forEach(ioc => {
        const csvRow = [
          ioc.displayType || '',
          `"${(ioc.value || '').replace(/"/g, '""')}"`,
          ioc.source || '',
          ioc.severity || '',
          'Active',
          ioc.created_at || ''
        ].join(',');
        csvContent += csvRow + '\n';
      });
      csvContent += '\n';
    }

    // System Health Summary
    if (data.system_health) {
      csvContent += 'SYSTEM HEALTH\n';
      csvContent += 'Component,Status,Details\n';
      csvContent += `Overall Status,${data.system_health.status || 'Unknown'},\n`;
      csvContent += `Database,${data.system_health.database?.status || 'Unknown'},${data.system_health.database?.details || ''}\n`;
      csvContent += `Redis,${data.system_health.services?.redis?.status || 'Unknown'},${data.system_health.services?.redis?.details || ''}\n`;
      if (data.system_health.system) {
        csvContent += `CPU Usage,${data.system_health.system.cpu_percent?.toFixed(1) || 'N/A'}%,\n`;
        csvContent += `Memory Usage,${data.system_health.system.memory_percent?.toFixed(1) || 'N/A'}%,\n`;
        csvContent += `Disk Usage,${data.system_health.system.disk_percent?.toFixed(1) || 'N/A'}%,\n`;
      }
    }

    return csvContent;
  }

  function exportDashboardToJSON(data) {
    return JSON.stringify(data, null, 2);
  }

  function exportDashboardToSummary(data) {
    let summary = '';
    
    summary += 'CRISP THREAT INTELLIGENCE DASHBOARD SUMMARY\n';
    summary += '=' + '='.repeat(48) + '\n\n';
    summary += `Export Date: ${new Date(data.export_date).toLocaleString()}\n\n`;

    // Overview
    summary += 'OVERVIEW\n';
    summary += '-'.repeat(20) + '\n';
    summary += `• Active IoCs: ${data.dashboard_stats.indicators || 0}\n`;
    summary += `• TTPs: ${data.dashboard_stats.ttps || 0}\n`;
    summary += `• Threat Feeds: ${data.dashboard_stats.threat_feeds || 0}\n`;
    summary += `• Platform Status: ${data.dashboard_stats.status || 'Unknown'}\n\n`;

    // Recent Activity
    if (data.recent_iocs && data.recent_iocs.length > 0) {
      summary += 'RECENT THREAT INTELLIGENCE\n';
      summary += '-'.repeat(30) + '\n';
      summary += `Total Recent IoCs: ${data.recent_iocs.length}\n\n`;
      
      const typeDistribution = data.recent_iocs.reduce((acc, ioc) => {
        acc[ioc.displayType] = (acc[ioc.displayType] || 0) + 1;
        return acc;
      }, {});
      
      summary += 'Type Distribution:\n';
      Object.entries(typeDistribution).forEach(([type, count]) => {
        summary += `  • ${type}: ${count}\n`;
      });
      summary += '\n';
    }

    // System Health
    if (data.system_health) {
      summary += 'SYSTEM HEALTH\n';
      summary += '-'.repeat(20) + '\n';
      summary += `Overall Status: ${data.system_health.status || 'Unknown'}\n`;
      summary += `Database: ${data.system_health.database?.status || 'Unknown'}\n`;
      summary += `Redis: ${data.system_health.services?.redis?.status || 'Unknown'}\n`;
      
      if (data.system_health.system) {
        summary += `CPU Usage: ${data.system_health.system.cpu_percent?.toFixed(1) || 'N/A'}%\n`;
        summary += `Memory Usage: ${data.system_health.system.memory_percent?.toFixed(1) || 'N/A'}%\n`;
        summary += `Disk Usage: ${data.system_health.system.disk_percent?.toFixed(1) || 'N/A'}%\n`;
      }
      summary += '\n';
    }

    // Chart Summary
    if (data.chart_summary && data.chart_summary.total_indicators > 0) {
      summary += 'THREAT ACTIVITY TRENDS\n';
      summary += '-'.repeat(25) + '\n';
      summary += `Total Indicators (${data.chart_filters.days} days): ${data.chart_summary.total_indicators}\n`;
      summary += `Daily Average: ${data.chart_summary.avg_daily}\n`;
      summary += `Date Range: ${data.chart_summary.start_date} to ${data.chart_summary.end_date}\n\n`;
    }

    summary += 'Generated by CRISP Threat Intelligence Platform\n';
    
    return summary;
  }

  return (
    <section id="dashboard" className={`page-section ${active ? 'active' : ''}`}>
      {/* Dashboard Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Threat Intelligence Dashboard</h1>
          <p className="page-subtitle">Overview of threat intelligence and platform activity</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline" onClick={() => setShowDashboardExportModal(true)}><i className="fas fa-download"></i> Export Data</button>
          <button className="btn btn-primary" onClick={() => showPage('threat-feeds', 'addFeed')}><i className="fas fa-plus"></i> Add New Feed</button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-search"></i></div>
            <span>Active IoCs</span>
          </div>
          <div className="stat-value">
            {dashboardStats.indicators || 0}
          </div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>Live data</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-sitemap"></i></div>
            <span>TTPs</span>
          </div>
          <div className="stat-value">
            {dashboardStats.ttps || 0}
          </div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>Live data</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-rss"></i></div>
            <span>Threat Feeds</span>
          </div>
          <div className="stat-value">
            {dashboardStats.threat_feeds || 0}
          </div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>Live data</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-server"></i></div>
            <span>Platform Status</span>
          </div>
          <div className="stat-value">
            {dashboardStats.status === 'active' ? 'Online' : 'Offline'}
          </div>
          <div className="stat-change">
            <span><i className="fas fa-circle" style={{color: dashboardStats.status === 'active' ? '#28a745' : '#dc3545'}}></i></span>
            <span>Live status</span>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="main-grid">
        {/* Threat Feed */}
        <div>
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-shield-alt card-icon"></i> Recent Threat Intelligence</h2>
              <div className="card-actions">
                <button 
                  className="btn btn-outline btn-sm" 
                  onClick={fetchRecentIoCs}
                  disabled={iocLoading}
                >
                  <i className={`fas fa-sync-alt ${iocLoading ? 'fa-spin' : ''}`}></i> 
                  {iocLoading ? 'Refreshing...' : 'Refresh'}
                </button>
              </div>
            </div>
            <div className="card-content">
              {iocLoading ? (
                <div className="loading-state">
                  <div className="loading-spinner"></div>
                  <p>Loading recent threat intelligence...</p>
                </div>
              ) : iocError ? (
                <div className="error-state">
                  <i className="fas fa-exclamation-triangle"></i>
                  <p>{iocError}</p>
                  <button className="btn btn-primary btn-sm" onClick={fetchRecentIoCs}>
                    <i className="fas fa-retry"></i> Retry
                  </button>
                </div>
              ) : recentIoCs.length === 0 ? (
                <div className="empty-state">
                  <i className="fas fa-shield-alt"></i>
                  <p>No threat intelligence available</p>
                  <p className="text-muted">IoCs will appear here once feeds are consumed</p>
                </div>
              ) : (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Type</th>
                      <th>Indicator</th>
                      <th>Source</th>
                      <th>Severity</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentIoCs.map((ioc, index) => (
                      <tr key={`${ioc.id || index}`}>
                        <td>
                          <div className="type-indicator">
                            <i className={`fas ${ioc.typeIcon}`}></i>
                            <span>{ioc.displayType}</span>
                          </div>
                        </td>
                        <td>
                          <div className="indicator-value">
                            <span className="value" title={ioc.value}>{ioc.truncatedValue}</span>
                            {ioc.isAnonymized && (
                              <span className="badge badge-anonymized">
                                <i className="fas fa-mask"></i> Anonymized
                              </span>
                            )}
                          </div>
                        </td>
                        <td>
                          <div className="source-info">
                            <span className="source-name">{ioc.source}</span>
                            <div className="source-meta">
                              <span className="age-indicator" title={`Created: ${ioc.created_at}`}>
                                {ioc.age}
                              </span>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className={`badge badge-${ioc.severityClass}`}>
                            {ioc.severity}
                          </span>
                        </td>
                        <td>
                          <div className="badge-tags">
                            <span className="badge badge-active">Active</span>
                            {ioc.confidence >= 80 && (
                              <span className="badge badge-verified">
                                <i className="fas fa-check-circle"></i> High Confidence
                              </span>
                            )}
                            {ioc.confidence < 50 && (
                              <span className="badge badge-warning">
                                <i className="fas fa-exclamation-triangle"></i> Low Confidence
                              </span>
                            )}
                            <span className="badge badge-realtime" title="Real-time data">
                              <i className="fas fa-broadcast-tower"></i> Live
                            </span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-chart-area card-icon"></i> Threat Activity Trends</h2>
              <div className="card-actions">
                <select 
                  className="btn btn-outline btn-sm"
                  value={chartFilters.days}
                  onChange={(e) => setChartFilters({...chartFilters, days: parseInt(e.target.value)})}
                  style={{marginRight: '10px'}}
                >
                  <option value="7">Last 7 Days</option>
                  <option value="14">Last 14 Days</option>
                  <option value="30">Last 30 Days</option>
                  <option value="60">Last 60 Days</option>
                  <option value="90">Last 90 Days</option>
                </select>
                
                <select 
                  className="btn btn-outline btn-sm"
                  value={chartFilters.type || ''}
                  onChange={(e) => setChartFilters({...chartFilters, type: e.target.value || null})}
                  style={{marginRight: '10px'}}
                >
                  <option value="">All Types</option>
                  <option value="ip">IP Address</option>
                  <option value="domain">Domain</option>
                  <option value="url">URL</option>
                  <option value="file_hash">File Hash</option>
                  <option value="email">Email</option>
                </select>
                
                <button 
                  className="btn btn-outline btn-sm"
                  onClick={fetchChartData}
                  disabled={chartLoading}
                  title="Refresh chart data"
                >
                  <i className={`fas fa-sync-alt ${chartLoading ? 'fa-spin' : ''}`}></i>
                  {chartLoading ? ' Loading...' : ' Refresh'}
                </button>
              </div>
            </div>
            
            {/* Chart Status Bar */}
            {chartSummary.total_indicators > 0 && (
              <div className="card-status-bar" style={{
                background: '#f8f9fa', 
                padding: '8px 16px', 
                fontSize: '12px', 
                color: '#666',
                borderBottom: '1px solid #e9ecef'
              }}>
                <span><strong>Total IoCs:</strong> {chartSummary.total_indicators}</span>
                <span style={{margin: '0 15px'}}>|</span>
                <span><strong>Daily Average:</strong> {chartSummary.avg_daily}</span>
                <span style={{margin: '0 15px'}}>|</span>
                <span><strong>Date Range:</strong> {chartSummary.start_date} to {chartSummary.end_date}</span>
              </div>
            )}
            
            <div className="card-content">
              {chartError && (
                <div className="alert alert-error" style={{
                  background: '#fff5f5',
                  border: '1px solid #fed7d7',
                  color: '#c53030',
                  padding: '12px',
                  borderRadius: '4px',
                  marginBottom: '16px'
                }}>
                  <i className="fas fa-exclamation-triangle"></i> {chartError}
                </div>
              )}
              
              <ChartErrorBoundary>
                <div style={{position: 'relative', minHeight: '350px'}}>
                  {chartLoading && (
                    <div style={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      textAlign: 'center',
                      zIndex: 10
                    }}>
                      <i className="fas fa-spinner fa-spin" style={{fontSize: '24px', color: '#0056b3'}}></i>
                      <p style={{marginTop: '10px', color: '#666'}}>Loading chart data...</p>
                    </div>
                  )}
                  <div 
                    className="chart-container" 
                    ref={chartRef} 
                    style={{
                      minHeight: '350px',
                      width: '100%',
                      overflow: 'visible'
                    }}
                  >
                    {/* D3.js Chart will be rendered here */}
                  </div>
                </div>
              </ChartErrorBoundary>
            </div>
          </div>
        </div>

        {/* Side Panel */}
        <div className="side-panels">
          {/* Connected Organisations */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-building card-icon"></i> Connected Organisations</h2>
            </div>
            <div className="card-content">
              <ul className="organisation-list">
                <li className="organisation-item">
                  <div className="organisation-logo">UP</div>
                  <div className="organisation-details">
                    <div className="organisation-name">University of Pretoria</div>
                    <div className="organisation-stats">
                      <div className="stat-item"><i className="fas fa-exchange-alt"></i> 125 IoCs</div>
                      <div className="stat-item"><i className="fas fa-clock"></i> 5m ago</div>
                    </div>
                  </div>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '90%' }}></div>
                  </div>
                </li>
                <li className="organisation-item">
                  <div className="organisation-logo">CS</div>
                  <div className="organisation-details">
                    <div className="organisation-name">Cyber Security Hub</div>
                    <div className="organisation-stats">
                      <div className="stat-item"><i className="fas fa-exchange-alt"></i> 342 IoCs</div>
                      <div className="stat-item"><i className="fas fa-clock"></i> 17m ago</div>
                    </div>
                  </div>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '85%' }}></div>
                  </div>
                </li>
                <li className="organisation-item">
                  <div className="organisation-logo">SR</div>
                  <div className="organisation-details">
                    <div className="organisation-name">SANReN CSIRT</div>
                    <div className="organisation-stats">
                      <div className="stat-item"><i className="fas fa-exchange-alt"></i> 208 IoCs</div>
                      <div className="stat-item"><i className="fas fa-clock"></i> 32m ago</div>
                    </div>
                  </div>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '75%' }}></div>
                  </div>
                </li>
                <li className="organisation-item">
                  <div className="organisation-logo">SB</div>
                  <div className="organisation-details">
                    <div className="organisation-name">SABRIC</div>
                    <div className="organisation-stats">
                      <div className="stat-item"><i className="fas fa-exchange-alt"></i> 156 IoCs</div>
                      <div className="stat-item"><i className="fas fa-clock"></i> 1h ago</div>
                    </div>
                  </div>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '70%' }}></div>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-history card-icon"></i> Recent Activity</h2>
            </div>
            <div className="card-content">
              {activitiesLoading ? (
                <div className="loading-state">
                  <div className="loading-spinner"></div>
                  <p>Loading recent activities...</p>
                </div>
              ) : activitiesError ? (
                <div className="error-state">
                  <i className="fas fa-exclamation-triangle"></i>
                  <p>{activitiesError}</p>
                  <button className="btn btn-primary btn-sm" onClick={fetchRecentActivities}>
                    <i className="fas fa-retry"></i> Retry
                  </button>
                </div>
              ) : recentActivities.length === 0 ? (
                <div className="empty-state">
                  <i className="fas fa-history"></i>
                  <p>No recent activities</p>
                  <p className="text-muted">System activities will appear here</p>
                </div>
              ) : (
                <ul className="activity-stream">
                  {recentActivities.map((activity) => (
                    <li key={activity.id} className="activity-item">
                      <div className="activity-icon">
                        <i className={activity.icon}></i>
                      </div>
                      <div className="activity-details">
                        <div className="activity-text">{activity.title}</div>
                        {activity.description && (
                          <div className="activity-description">{activity.description}</div>
                        )}
                        <div className="activity-meta">
                          <div className="activity-time">{activity.time_ago}</div>
                          <span className={`badge ${activity.badge_type}`}>
                            {activity.badge_text}
                          </span>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* System Health & Feed Status Monitoring */}
      <div className="card" style={{marginTop: '24px'}}>
        <div className="card-header">
          <h2 className="card-title">
            <i className="fas fa-heartbeat card-icon"></i> System Health & Feed Status
          </h2>
          <div className="card-actions">
            <button 
              className="btn btn-outline btn-sm"
              onClick={fetchSystemHealth}
              disabled={healthLoading}
              title="Refresh system health"
            >
              <i className={`fas fa-sync-alt ${healthLoading ? 'fa-spin' : ''}`}></i>
              {healthLoading ? ' Loading...' : ' Refresh'}
            </button>
          </div>
        </div>

        <div className="card-content">
          {healthError && (
            <div className="alert alert-error" style={{
              background: '#fff5f5',
              border: '1px solid #fed7d7',
              color: '#c53030',
              padding: '12px',
              borderRadius: '4px',
              marginBottom: '16px'
            }}>
              <i className="fas fa-exclamation-triangle"></i> {healthError}
            </div>
          )}

          {/* System Status Overview */}
          <div className="system-status-overview" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px',
            marginBottom: '24px'
          }}>
            <div className="status-card" style={{
              background: '#f8f9fa',
              border: '1px solid #dee2e6',
              borderRadius: '8px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '24px',
                color: getStatusColor(systemHealth.status),
                marginBottom: '8px'
              }}>
                <i className={getStatusIcon(systemHealth.status)}></i>
              </div>
              <h3 style={{margin: '0 0 4px 0', fontSize: '16px'}}>Overall Status</h3>
              <p style={{
                margin: '0',
                color: getStatusColor(systemHealth.status),
                fontWeight: 'bold',
                textTransform: 'capitalize'
              }}>
                {systemHealth.status}
              </p>
              <small style={{color: '#666'}}>
                Last Check: {formatTimestamp(systemHealth.timestamp)}
              </small>
            </div>

            <div className="status-card" style={{
              background: '#f8f9fa',
              border: '1px solid #dee2e6',
              borderRadius: '8px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '24px',
                color: getStatusColor(systemHealth.database?.status || 'unknown'),
                marginBottom: '8px'
              }}>
                <i className="fas fa-database"></i>
              </div>
              <h3 style={{margin: '0 0 4px 0', fontSize: '16px'}}>Database</h3>
              <p style={{
                margin: '0',
                color: getStatusColor(systemHealth.database?.status || 'unknown'),
                fontWeight: 'bold',
                textTransform: 'capitalize'
              }}>
                {systemHealth.database?.status || 'Unknown'}
              </p>
              <small style={{color: '#666'}}>
                {systemHealth.database?.connection_count 
                  ? `${systemHealth.database.connection_count} connections`
                  : 'Connection info unavailable'
                }
              </small>
            </div>

            <div className="status-card" style={{
              background: '#f8f9fa',
              border: '1px solid #dee2e6',
              borderRadius: '8px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '24px',
                color: getStatusColor(systemHealth.services?.redis?.status || 'unknown'),
                marginBottom: '8px'
              }}>
                <i className="fas fa-memory"></i>
              </div>
              <h3 style={{margin: '0 0 4px 0', fontSize: '16px'}}>Redis</h3>
              <p style={{
                margin: '0',
                color: getStatusColor(systemHealth.services?.redis?.status || 'unknown'),
                fontWeight: 'bold',
                textTransform: 'capitalize'
              }}>
                {systemHealth.services?.redis?.status || 'Unknown'}
              </p>
              <small style={{color: '#666'}}>
                {systemHealth.services?.redis?.info 
                  ? `v${systemHealth.services.redis.info}`
                  : 'Version unavailable'
                }
              </small>
            </div>

            <div className="status-card" style={{
              background: '#f8f9fa',
              border: '1px solid #dee2e6',
              borderRadius: '8px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '24px',
                color: systemHealth.system?.cpu_percent > 80 ? '#dc3545' : 
                      systemHealth.system?.cpu_percent > 60 ? '#ffc107' : '#28a745',
                marginBottom: '8px'
              }}>
                <i className="fas fa-microchip"></i>
              </div>
              <h3 style={{margin: '0 0 4px 0', fontSize: '16px'}}>System Resources</h3>
              <p style={{margin: '0', fontWeight: 'bold'}}>
                CPU: {systemHealth.system?.cpu_percent?.toFixed(1) || 'N/A'}%
              </p>
              <small style={{color: '#666'}}>
                RAM: {systemHealth.system?.memory_percent?.toFixed(1) || 'N/A'}% | 
                Disk: {systemHealth.system?.disk_percent?.toFixed(1) || 'N/A'}%
              </small>
            </div>
          </div>

          {/* Feed Status Section */}
          <div className="feed-status-section">
            <h3 style={{
              margin: '0 0 16px 0',
              fontSize: '18px',
              borderBottom: '2px solid #dee2e6',
              paddingBottom: '8px'
            }}>
              Feed Status Monitoring
            </h3>

            {/* Feed Summary */}
            {systemHealth.feeds && systemHealth.feeds.total > 0 && (
              <div className="feed-summary" style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                gap: '12px',
                marginBottom: '20px',
                padding: '16px',
                background: '#f1f3f4',
                borderRadius: '6px'
              }}>
                <div style={{textAlign: 'center'}}>
                  <div style={{fontSize: '24px', fontWeight: 'bold', color: '#0056b3'}}>
                    {systemHealth.feeds.total}
                  </div>
                  <small>Total Feeds</small>
                </div>
                <div style={{textAlign: 'center'}}>
                  <div style={{fontSize: '24px', fontWeight: 'bold', color: '#28a745'}}>
                    {systemHealth.feeds.active}
                  </div>
                  <small>Active</small>
                </div>
                <div style={{textAlign: 'center'}}>
                  <div style={{fontSize: '24px', fontWeight: 'bold', color: '#17a2b8'}}>
                    {systemHealth.feeds.external}
                  </div>
                  <small>External</small>
                </div>
                <div style={{textAlign: 'center'}}>
                  <div style={{fontSize: '24px', fontWeight: 'bold', color: '#6c757d'}}>
                    {systemHealth.feeds.total - systemHealth.feeds.external}
                  </div>
                  <small>Internal</small>
                </div>
              </div>
            )}

            {/* Quick Feed Management Action */}
            {systemHealth.feeds && systemHealth.feeds.total === 0 ? (
              <div style={{
                textAlign: 'center',
                color: '#666',
                padding: '24px',
                background: '#f8f9fa',
                borderRadius: '6px',
                marginTop: '16px'
              }}>
                <i className="fas fa-rss" style={{fontSize: '32px', marginBottom: '12px'}}></i>
                <p style={{margin: '0 0 12px 0'}}>No threat feeds configured yet.</p>
                <button 
                  className="btn btn-primary btn-sm"
                  onClick={() => showPage('threat-feeds')}
                >
                  <i className="fas fa-plus"></i> Manage Feeds
                </button>
              </div>
            ) : (
              <div style={{
                textAlign: 'center',
                padding: '16px',
                marginTop: '16px'
              }}>
                <button 
                  className="btn btn-outline btn-sm"
                  onClick={() => showPage('threat-feeds')}
                >
                  <i className="fas fa-cog"></i> Manage All Feeds
                </button>
              </div>
            )}
          </div>

          {/* Error Summary */}
          {systemHealth.errors && systemHealth.errors.length > 0 && (
            <div className="error-summary" style={{
              marginTop: '24px',
              padding: '16px',
              background: '#fff5f5',
              border: '1px solid #fed7d7',
              borderRadius: '6px'
            }}>
              <h4 style={{
                margin: '0 0 12px 0',
                color: '#c53030',
                fontSize: '16px'
              }}>
                <i className="fas fa-exclamation-triangle"></i> System Errors ({systemHealth.errors.length})
              </h4>
              <ul style={{margin: '0', paddingLeft: '20px'}}>
                {systemHealth.errors.map((error, index) => (
                  <li key={index} style={{
                    color: '#c53030',
                    marginBottom: '4px'
                  }}>
                    {error}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* System Metrics */}
          {systemHealth.system && Object.keys(systemHealth.system).length > 0 && (
            <div className="system-metrics" style={{
              marginTop: '24px',
              padding: '16px',
              background: '#f8f9fa',
              borderRadius: '6px'
            }}>
              <h4 style={{
                margin: '0 0 12px 0',
                fontSize: '16px'
              }}>
                <i className="fas fa-chart-line"></i> System Metrics
              </h4>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '12px',
                fontSize: '14px'
              }}>
                {systemHealth.system.uptime && (
                  <div>
                    <strong>Uptime:</strong> {formatUptime(systemHealth.system.uptime)}
                  </div>
                )}
                {systemHealth.system.load_average && (
                  <div>
                    <strong>Load Average:</strong> {systemHealth.system.load_average.join(', ')}
                  </div>
                )}
                <div>
                  <strong>Last Updated:</strong> {formatTimestamp(systemHealth.system.last_check)}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Dashboard Export Modal */}
      {showDashboardExportModal && (
        <div className="modal-overlay" onClick={closeDashboardExportModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2><i className="fas fa-download"></i> Export Dashboard Data</h2>
              <button className="modal-close" onClick={closeDashboardExportModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">Export Format</label>
                <select 
                  className="form-control"
                  value={dashboardExportFormat} 
                  onChange={(e) => setDashboardExportFormat(e.target.value)}
                >
                  <option value="json">JSON - Complete Data</option>
                  <option value="csv">CSV - Tabular Format</option>
                  <option value="summary">Summary Report</option>
                </select>
              </div>

              <div className="export-info">
                <div className="export-preview">
                  <div>
                    <strong>Export Details:</strong>
                    <p>Dashboard export will include:</p>
                    <ul>
                      <li>System statistics ({dashboardStats.indicators} IoCs, {dashboardStats.ttps} TTPs, {dashboardStats.threat_feeds} feeds)</li>
                      <li>Recent threat intelligence ({recentIoCs.length} items)</li>
                      <li>System health data</li>
                      <li>Threat activity chart data ({chartData.length} data points)</li>
                    </ul>
                    {dashboardExportFormat === 'csv' && (
                      <p><em>CSV format includes IoCs table and summary metrics.</em></p>
                    )}
                    {dashboardExportFormat === 'json' && (
                      <p><em>JSON format includes complete structured data export.</em></p>
                    )}
                    {dashboardExportFormat === 'summary' && (
                      <p><em>Summary report includes key insights and formatted overview.</em></p>
                    )}
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <div className="modal-actions">
                <button type="button" className="btn btn-outline" onClick={closeDashboardExportModal} disabled={dashboardExporting}>
                  Cancel
                </button>
                <button type="button" className="btn btn-primary" onClick={handleDashboardExport} disabled={dashboardExporting}>
                  {dashboardExporting ? (
                    <><i className="fas fa-spinner fa-spin"></i> Exporting...</>
                  ) : (
                    <><i className="fas fa-download"></i> Export Dashboard</>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

// Threat Feeds Component
function ThreatFeeds({ active, navigationState, setNavigationState }) {
  if (!active) return null;
  
  const [threatFeeds, setThreatFeeds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [activeTab, setActiveTab] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    type: '',
    status: '',
    source: '',
    search: ''
  });
  const itemsPerPage = 10;
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    is_external: true,
    taxii_server_url: '',
    taxii_api_root: '',
    taxii_collection_id: '',
    taxii_username: '',
    taxii_password: ''
  });

  // Feed consumption and deletion states
  const [consumingFeeds, setConsumingFeeds] = useState(new Set());
  const [feedProgress, setFeedProgress] = useState(new Map());
  const [showDeleteFeedModal, setShowDeleteFeedModal] = useState(false);
  const [feedToDelete, setFeedToDelete] = useState(null);
  const [deletingFeed, setDeletingFeed] = useState(false);
  
  // Fetch threat feeds from backend
  useEffect(() => {
    if (active) {
      fetchThreatFeeds();
    }
  }, [active]);

  // Handle navigation state for modal triggers
  useEffect(() => {
    if (active && navigationState?.triggerModal === 'addFeed') {
      setShowAddModal(true);
      // Clear navigation state after handling
      setNavigationState({
        triggerModal: null,
        modalParams: {}
      });
    }
  }, [active, navigationState, setNavigationState]);
  
  const fetchThreatFeeds = async () => {
    setLoading(true);
    const data = await api.get('/api/threat-feeds/');
    if (data && data.results) {
      setThreatFeeds(data.results);
    }
    setLoading(false);
  };
  
  const handleConsumeFeed = async (feedId) => {
    // Add feed to consuming set
    setConsumingFeeds(prev => new Set([...prev, feedId]));
    
    // Initialize progress
    setFeedProgress(prev => new Map(prev.set(feedId, {
      stage: 'Initiating',
      message: 'Starting consumption process...',
      percentage: 0
    })));
    
    try {
      const result = await api.post(`/api/threat-feeds/${feedId}/consume/`);
      if (result) {
        console.log('Feed consumption started:', result);
        
        // Start polling for progress
        const progressInterval = setInterval(async () => {
          try {
            const progressData = await api.get(`/api/threat-feeds/${feedId}/consumption_progress/`);
            if (progressData && progressData.success) {
              const progress = progressData.progress;
              
              setFeedProgress(prev => new Map(prev.set(feedId, {
                stage: progress.stage,
                message: progress.message || `${progress.stage}...`,
                percentage: progress.percentage || 0,
                current: progress.current,
                total: progress.total
              })));
              
              // If completed, stop polling
              if (progress.stage === 'Completed' || progress.percentage >= 100) {
                clearInterval(progressInterval);
                
                // Remove from consuming set after a brief delay to show completion
                setTimeout(() => {
                  setConsumingFeeds(prev => {
                    const newSet = new Set(prev);
                    newSet.delete(feedId);
                    return newSet;
                  });
                  setFeedProgress(prev => {
                    const newMap = new Map(prev);
                    newMap.delete(feedId);
                    return newMap;
                  });
                }, 2000);
                
                // Refresh feeds after consumption
                await fetchThreatFeeds();
              }
            }
          } catch (progressError) {
            console.error('Error fetching progress:', progressError);
            // Continue polling - might be temporary error
          }
        }, 2000); // Poll every 2 seconds
        
        // Set a maximum timeout to prevent infinite polling
        setTimeout(() => {
          clearInterval(progressInterval);
          setConsumingFeeds(prev => {
            const newSet = new Set(prev);
            newSet.delete(feedId);
            return newSet;
          });
          setFeedProgress(prev => {
            const newMap = new Map(prev);
            newMap.delete(feedId);
            return newMap;
          });
        }, 300000); // 5 minutes maximum
        
      }
    } catch (error) {
      console.error('Error consuming feed:', error);
      alert('Failed to consume feed. Please try again.');
      
      // Remove feed from consuming set on error
      setConsumingFeeds(prev => {
        const newSet = new Set(prev);
        newSet.delete(feedId);
        return newSet;
      });
      setFeedProgress(prev => {
        const newMap = new Map(prev);
        newMap.delete(feedId);
        return newMap;
      });
    }
  };

  const handleDeleteFeed = (feed) => {
    setFeedToDelete(feed);
    setShowDeleteFeedModal(true);
  };

  const confirmDeleteFeed = async () => {
    if (!feedToDelete) return;

    setDeletingFeed(true);
    try {
      const result = await api.delete(`/api/threat-feeds/${feedToDelete.id}/`);
      if (result !== null) {
        console.log('Feed deleted successfully:', feedToDelete.name);
        // Refresh feeds list
        await fetchThreatFeeds();
        // Close modal
        closeDeleteFeedModal();
      } else {
        alert('Failed to delete threat feed. Please try again.');
      }
    } catch (error) {
      console.error('Error deleting feed:', error);
      alert('Error deleting threat feed. Please try again.');
    } finally {
      setDeletingFeed(false);
    }
  };

  const closeDeleteFeedModal = () => {
    setShowDeleteFeedModal(false);
    setFeedToDelete(null);
  };

  const handleAddFeed = () => {
    setShowAddModal(true);
  };

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    const result = await api.post('/api/threat-feeds/', formData);
    if (result) {
      setShowAddModal(false);
      setFormData({
        name: '',
        description: '',
        is_external: true,
        taxii_server_url: '',
        taxii_api_root: '',
        taxii_collection_id: '',
        taxii_username: '',
        taxii_password: ''
      });
      fetchThreatFeeds();
    }
  };

  const closeModal = () => {
    setShowAddModal(false);
  };

  // Filter and paginate feeds
  const getFilteredFeeds = () => {
    let filtered = threatFeeds;

    // Apply tab filter
    if (activeTab === 'active') {
      filtered = filtered.filter(f => f.is_active);
    } else if (activeTab === 'external') {
      filtered = filtered.filter(f => f.is_external);
    } else if (activeTab === 'internal') {
      filtered = filtered.filter(f => !f.is_external);
    }

    // Apply dropdown filters
    if (filters.type) {
      filtered = filtered.filter(f => 
        (filters.type === 'stix-taxii' && f.taxii_server_url) ||
        (filters.type === 'internal' && !f.is_external) ||
        (filters.type === 'external' && f.is_external)
      );
    }

    if (filters.status) {
      filtered = filtered.filter(f => 
        (filters.status === 'active' && f.is_active) ||
        (filters.status === 'disabled' && !f.is_active)
      );
    }

    if (filters.source) {
      filtered = filtered.filter(f => 
        (filters.source === 'external' && f.is_external) ||
        (filters.source === 'internal' && !f.is_external)
      );
    }

    if (filters.search) {
      filtered = filtered.filter(f => 
        f.name.toLowerCase().includes(filters.search.toLowerCase()) ||
        (f.description && f.description.toLowerCase().includes(filters.search.toLowerCase())) ||
        (f.taxii_server_url && f.taxii_server_url.toLowerCase().includes(filters.search.toLowerCase()))
      );
    }

    return filtered;
  };

  const getPaginatedFeeds = () => {
    const filtered = getFilteredFeeds();
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filtered.slice(startIndex, startIndex + itemsPerPage);
  };

  const getTotalPages = () => {
    return Math.ceil(getFilteredFeeds().length / itemsPerPage);
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setCurrentPage(1);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
    setCurrentPage(1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const toggleFilters = () => {
    setShowFilters(!showFilters);
  };
  
  return (
    <section id="threat-feeds" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Threat Feeds</h1>
          <p className="page-subtitle">Manage and monitor all threat intelligence feeds</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline" onClick={toggleFilters}>
            <i className="fas fa-filter"></i> Filter Feeds {showFilters ? '▲' : '▼'}
          </button>
          <button className="btn btn-primary" onClick={handleAddFeed}><i className="fas fa-plus"></i> Add New Feed</button>
        </div>
      </div>

      {showFilters && (
        <div className="filters-section">
          <div className="filters-grid">
          <div className="filter-group">
            <label className="filter-label">Feed Type</label>
            <div className="filter-control">
              <select value={filters.type} onChange={(e) => handleFilterChange('type', e.target.value)}>
                <option value="">All Types</option>
                <option value="stix-taxii">STIX/TAXII</option>
                <option value="misp">MISP</option>
                <option value="custom">Custom</option>
                <option value="internal">Internal</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Status</label>
            <div className="filter-control">
              <select value={filters.status} onChange={(e) => handleFilterChange('status', e.target.value)}>
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="disabled">Disabled</option>
                <option value="error">Error</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Source</label>
            <div className="filter-control">
              <select value={filters.source} onChange={(e) => handleFilterChange('source', e.target.value)}>
                <option value="">All Sources</option>
                <option value="external">External</option>
                <option value="internal">Internal</option>
                <option value="partner">Partner</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Search Feeds</label>
            <div className="filter-control">
              <input 
                type="text" 
                placeholder="Search by name or URL..." 
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
              />
            </div>
          </div>
          </div>
        </div>
      )}

      <div className="tabs">
        <div 
          className={`tab ${activeTab === 'active' ? 'active' : ''}`}
          onClick={() => handleTabChange('active')}
        >
          Active Feeds ({threatFeeds.filter(f => f.is_active).length})
        </div>
        <div 
          className={`tab ${activeTab === 'external' ? 'active' : ''}`}
          onClick={() => handleTabChange('external')}
        >
          External ({threatFeeds.filter(f => f.is_external).length})
        </div>
        <div 
          className={`tab ${activeTab === 'internal' ? 'active' : ''}`}
          onClick={() => handleTabChange('internal')}
        >
          Internal ({threatFeeds.filter(f => !f.is_external).length})
        </div>
        <div 
          className={`tab ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => handleTabChange('all')}
        >
          All Feeds ({threatFeeds.length})
        </div>
      </div>

      <div className="card">
        <div className="card-content">
          {loading ? (
            <div style={{textAlign: 'center', padding: '2rem'}}>
              <i className="fas fa-spinner fa-spin"></i> Loading feeds...
            </div>
          ) : (
            <ul className="feed-items">
              {getPaginatedFeeds().map((feed) => (
                <li key={feed.id} className="feed-item">
                  <div className="feed-icon">
                    <i className={feed.is_external ? "fas fa-globe" : "fas fa-server"}></i>
                  </div>
                  <div className="feed-details">
                    <div className="feed-name">{feed.name}</div>
                    <div className="feed-description">{feed.description || 'No description available'}</div>
                    <div className="feed-meta">
                      <div className="feed-stats">
                        <div className="stat-item">
                          <i className="fas fa-link"></i> {feed.taxii_collection_id || 'N/A'}
                        </div>
                        <div className="stat-item">
                          <i className="fas fa-sync-alt"></i> {feed.last_sync ? new Date(feed.last_sync).toLocaleString() : 'Never'}
                        </div>
                        <div className="stat-item">
                          <i className="fas fa-globe"></i> {feed.is_external ? 'External' : 'Internal'}
                        </div>
                      </div>
                      <div className="feed-badges">
                        <span className={`badge ${feed.is_public ? 'badge-active' : 'badge-medium'}`}>
                          {feed.is_public ? 'Public' : 'Private'}
                        </span>
                        <span className="badge badge-connected">STIX/TAXII</span>
                        <button 
                          className="btn btn-sm btn-primary"
                          onClick={() => handleConsumeFeed(feed.id)}
                          disabled={consumingFeeds.has(feed.id)}
                          style={{minWidth: '140px'}}
                        >
                          {consumingFeeds.has(feed.id) ? (
                            <>
                              <i className="fas fa-spinner fa-spin"></i>
                              <div style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-start', fontSize: '11px'}}>
                                <span>{feedProgress.get(feed.id)?.stage || 'Processing'}</span>
                                {feedProgress.get(feed.id)?.current && feedProgress.get(feed.id)?.total && (
                                  <span style={{opacity: 0.8}}>
                                    {feedProgress.get(feed.id).current}/{feedProgress.get(feed.id).total}
                                  </span>
                                )}
                                {feedProgress.get(feed.id)?.percentage > 0 && (
                                  <span style={{opacity: 0.8}}>
                                    {feedProgress.get(feed.id).percentage}%
                                  </span>
                                )}
                              </div>
                            </>
                          ) : (
                            <>
                              <i className="fas fa-download"></i> Consume
                            </>
                          )}
                        </button>
                        <button 
                          className="btn btn-sm btn-danger"
                          onClick={() => handleDeleteFeed(feed)}
                          disabled={consumingFeeds.has(feed.id)}
                          title={consumingFeeds.has(feed.id) ? "Cannot delete while consuming" : "Delete this threat feed"}
                        >
                          <i className="fas fa-trash"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {getTotalPages() > 1 && (
        <div className="pagination">
          <div 
            className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}
            onClick={() => currentPage > 1 && handlePageChange(currentPage - 1)}
          >
            <i className="fas fa-chevron-left"></i>
          </div>
          {Array.from({ length: getTotalPages() }, (_, i) => i + 1).map(page => (
            <div 
              key={page}
              className={`page-item ${page === currentPage ? 'active' : ''}`}
              onClick={() => handlePageChange(page)}
            >
              {page}
            </div>
          ))}
          <div 
            className={`page-item ${currentPage === getTotalPages() ? 'disabled' : ''}`}
            onClick={() => currentPage < getTotalPages() && handlePageChange(currentPage + 1)}
          >
            <i className="fas fa-chevron-right"></i>
          </div>
        </div>
      )}

      {/* Add New Feed Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Add New Threat Feed</h2>
              <button className="modal-close" onClick={closeModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <form onSubmit={handleFormSubmit} className="modal-body">
              <div className="form-group">
                <label>Feed Name *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleFormChange}
                  placeholder="Enter feed name"
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleFormChange}
                  placeholder="Enter feed description"
                  rows="3"
                />
              </div>
              
              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    name="is_external"
                    checked={formData.is_external}
                    onChange={handleFormChange}
                  />
                  External Feed
                </label>
              </div>
              
              <div className="form-group">
                <label>TAXII Server URL *</label>
                <input
                  type="url"
                  name="taxii_server_url"
                  value={formData.taxii_server_url}
                  onChange={handleFormChange}
                  placeholder="https://example.com/taxii"
                  required
                />
              </div>
              
              <div className="form-group">
                <label>API Root</label>
                <input
                  type="text"
                  name="taxii_api_root"
                  value={formData.taxii_api_root}
                  onChange={handleFormChange}
                  placeholder="api-root"
                />
              </div>
              
              <div className="form-group">
                <label>Collection ID</label>
                <input
                  type="text"
                  name="taxii_collection_id"
                  value={formData.taxii_collection_id}
                  onChange={handleFormChange}
                  placeholder="collection-id"
                />
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Username</label>
                  <input
                    type="text"
                    name="taxii_username"
                    value={formData.taxii_username}
                    onChange={handleFormChange}
                    placeholder="Username"
                  />
                </div>
                
                <div className="form-group">
                  <label>Password</label>
                  <input
                    type="password"
                    name="taxii_password"
                    value={formData.taxii_password}
                    onChange={handleFormChange}
                    placeholder="Password"
                  />
                </div>
              </div>
              
              <div className="modal-footer">
                <button type="button" className="btn btn-outline" onClick={closeModal}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  <i className="fas fa-plus"></i> Add Feed
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Feed Confirmation Modal */}
      {showDeleteFeedModal && (
        <div className="modal-overlay" onClick={closeDeleteFeedModal}>
          <div className="modal-content delete-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                <i className="fas fa-exclamation-triangle" style={{color: '#dc3545'}}></i>
                Delete Threat Feed
              </h2>
              <button className="modal-close" onClick={closeDeleteFeedModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <div className="modal-body">
              <div className="delete-confirmation">
                <p>
                  Are you sure you want to delete the threat feed <strong>"{feedToDelete?.name}"</strong>?
                </p>
                <div className="warning-text">
                  <i className="fas fa-warning"></i>
                  <span>This action cannot be undone. All associated indicators and TTP data will also be removed.</span>
                </div>
                
                {feedToDelete && (
                  <div className="feed-info">
                    <div className="info-row">
                      <strong>Type:</strong> {feedToDelete.is_external ? 'External TAXII' : 'Internal'}
                    </div>
                    <div className="info-row">
                      <strong>Collection:</strong> {feedToDelete.taxii_collection_id || 'N/A'}
                    </div>
                    <div className="info-row">
                      <strong>Last Sync:</strong> {feedToDelete.last_sync ? new Date(feedToDelete.last_sync).toLocaleString() : 'Never'}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="modal-footer">
              <div className="modal-actions">
                <button 
                  type="button" 
                  className="btn btn-outline" 
                  onClick={closeDeleteFeedModal}
                  disabled={deletingFeed}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-danger" 
                  onClick={confirmDeleteFeed}
                  disabled={deletingFeed}
                >
                  {deletingFeed ? (
                    <>
                      <i className="fas fa-spinner fa-spin"></i> Deleting...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-trash"></i> Delete Feed
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

// IoC Management Component
function IoCManagement({ active }) {
  if (!active) return null;
  
  const [indicators, setIndicators] = useState([]);
  const [filteredIndicators, setFilteredIndicators] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newIoC, setNewIoC] = useState({
    type: '',
    value: '',
    severity: 'Medium',
    description: '',
    source: '',
    confidence: 50,
    threatFeed: '',
    createNewFeed: false,
    newFeedName: '',
    newFeedDescription: ''
  });
  const [formErrors, setFormErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportFormat, setExportFormat] = useState('csv');
  const [exporting, setExporting] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importFormat, setImportFormat] = useState('auto');
  const [importing, setImporting] = useState(false);
  const [importPreview, setImportPreview] = useState([]);
  const [showPreview, setShowPreview] = useState(false);
  
  // Edit modal state
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingIndicator, setEditingIndicator] = useState(null);
  const [editFormData, setEditFormData] = useState({
    type: '',
    value: '',
    description: '',
    confidence: 50,
    threat_feed_id: '',
    threatFeedMode: 'existing'
  });
  const [editFormErrors, setEditFormErrors] = useState({});
  const [updating, setUpdating] = useState(false);
  const [editNewFeedName, setEditNewFeedName] = useState('');
  const [editNewFeedDescription, setEditNewFeedDescription] = useState('');
  
  // Share modal state
  const [showShareModal, setShowShareModal] = useState(false);
  const [sharingIndicator, setSharingIndicator] = useState(null);
  const [shareFormData, setShareFormData] = useState({
    organisations: [],
    anonymizationLevel: 'medium',
    shareMethod: 'taxii'
  });
  const [sharing, setSharing] = useState(false);
  const [organisationSearch, setOrganisationSearch] = useState('');
  const [showOrganisationDropdown, setShowOrganisationDropdown] = useState(false);
  const [selectedOrganisationIndex, setSelectedOrganisationIndex] = useState(-1);
  const [shareOrganisationMode, setShareOrganisationMode] = useState('existing');
  const [organisationDropdownSearch, setOrganisationDropdownSearch] = useState('');
  const [showOrganisationSelectDropdown, setShowOrganisationSelectDropdown] = useState(false);
  
  // Threat feeds for Add IoC modal
  const [threatFeeds, setThreatFeeds] = useState([]);
  
  // Mock organisations list - in real app, this would come from API
  const availableOrganisations = [
    'University of Pretoria',
    'Cyber Security Hub',
    'SANReN CSIRT',
    'SABRIC',
    'University of Johannesburg',
    'University of Cape Town',
    'University of the Witwatersrand',
    'Stellenbosch University',
    'Rhodes University',
    'North-West University',
    'University of KwaZulu-Natal',
    'University of the Free State',
    'Nelson Mandela University',
    'University of Limpopo',
    'Walter Sisulu University',
    'Vaal University of Technology',
    'Central University of Technology',
    'Durban University of Technology',
    'Cape Peninsula University of Technology',
    'Tshwane University of Technology',
    'CSIR',
    'Council for Scientific and Industrial Research',
    'South African Police Service',
    'State Security Agency',
    'Department of Communications',
    'SITA (State Information Technology Agency)',
    'Nedbank',
    'Standard Bank',
    'First National Bank',
    'ABSA Bank',
    'Capitec Bank',
    'African Bank',
    'Investec'
  ];
  
  // Filter state management
  const [filters, setFilters] = useState({
    type: '',
    severity: '',
    status: '',
    source: '',
    dateRange: '',
    searchTerm: ''
  });
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(20);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  
  // Fetch indicators from backend
  useEffect(() => {
    if (active) {
      fetchIndicators();
      fetchThreatFeeds();
    }
  }, [active]);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (showOrganisationDropdown && !event.target.closest('.organisation-search-container')) {
        setShowOrganisationDropdown(false);
        setSelectedOrganisationIndex(-1);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showOrganisationDropdown]);
  
  const fetchThreatFeeds = async () => {
    const data = await api.get('/api/threat-feeds/');
    if (data && data.results) {
      setThreatFeeds(data.results);
    }
  };

  // Apply filters when indicators, filters, or pagination settings change
  useEffect(() => {
    applyFilters();
  }, [indicators, filters, currentPage, itemsPerPage]);

  const fetchIndicators = async () => {
    setLoading(true);
    try {
      // Get real indicator data from feeds
      const feedData = await api.get('/api/threat-feeds/');
      if (feedData && feedData.results) {
        let allIndicators = [];
        let totalIndicatorCount = 0;
        
        for (const feed of feedData.results) {
          const feedStatus = await api.get(`/api/threat-feeds/${feed.id}/status/`);
          if (feedStatus && feedStatus.indicator_count > 0) {
            totalIndicatorCount += feedStatus.indicator_count;
            
            // Fetch ALL indicators from this feed, not just 50
            let page = 1;
            let hasMore = true;
            
            while (hasMore) {
              const indicatorsData = await api.get(`/api/threat-feeds/${feed.id}/indicators/?page=${page}&page_size=100`);
              if (indicatorsData && indicatorsData.results && indicatorsData.results.length > 0) {
                const realIndicators = indicatorsData.results.map(indicator => ({
                  id: indicator.id,
                  type: indicator.type === 'ip' ? 'IP Address' : 
                        indicator.type === 'domain' ? 'Domain' :
                        indicator.type === 'url' ? 'URL' :
                        indicator.type === 'file_hash' ? 'File Hash' :
                        indicator.type === 'email' ? 'Email' : 
                        indicator.type === 'user_agent' ? 'User Agent' :
                        indicator.type === 'registry' ? 'Registry Key' :
                        indicator.type === 'mutex' ? 'Mutex' :
                        indicator.type === 'process' ? 'Process' : indicator.type,
                  rawType: indicator.type,
                  title: indicator.name || '',
                  value: indicator.value,
                  severity: indicator.confidence >= 75 ? 'High' : 
                           indicator.confidence >= 50 ? 'Medium' : 'Low',
                  confidence: indicator.confidence,
                  source: indicator.source || feed.name || 'Unknown',
                  description: indicator.description || '',
                  created: new Date(indicator.created_at).toISOString().split('T')[0],
                  createdDate: new Date(indicator.created_at),
                  status: indicator.is_anonymized ? 'Anonymized' : 'Active',
                  feedId: feed.id,
                  feedName: feed.name
                }));
                allIndicators.push(...realIndicators);
                
                // Check if there are more pages
                hasMore = indicatorsData.next !== null;
                page++;
              } else {
                hasMore = false;
              }
            }
          }
        }
        
        // Sort indicators by creation date (newest first)
        allIndicators.sort((a, b) => b.createdDate - a.createdDate);
        
        setIndicators(allIndicators);
        setTotalItems(allIndicators.length);
        console.log(`Loaded ${allIndicators.length} indicators from ${feedData.results.length} feeds`);
      }
    } catch (error) {
      console.error('Error fetching indicators:', error);
    }
    setLoading(false);
  };

  // Filter application logic
  const applyFilters = () => {
    let filtered = [...indicators];

    // Filter by type
    if (filters.type) {
      filtered = filtered.filter(indicator => 
        indicator.rawType === filters.type
      );
    }

    // Filter by severity
    if (filters.severity) {
      filtered = filtered.filter(indicator => 
        indicator.severity.toLowerCase() === filters.severity.toLowerCase()
      );
    }

    // Filter by status
    if (filters.status) {
      filtered = filtered.filter(indicator => 
        indicator.status.toLowerCase() === filters.status.toLowerCase()
      );
    }

    // Filter by source
    if (filters.source) {
      filtered = filtered.filter(indicator => 
        indicator.source.toLowerCase().includes(filters.source.toLowerCase())
      );
    }

    // Filter by search term (searches in title, value, and description)
    if (filters.searchTerm) {
      const searchTerm = filters.searchTerm.toLowerCase();
      filtered = filtered.filter(indicator => 
        indicator.value.toLowerCase().includes(searchTerm) ||
        indicator.description.toLowerCase().includes(searchTerm) ||
        (indicator.title && indicator.title.toLowerCase().includes(searchTerm)) ||
        (indicator.name && indicator.name.toLowerCase().includes(searchTerm))
      );
    }

    // Filter by date range
    if (filters.dateRange) {
      const now = new Date();
      let cutoffDate;
      
      switch (filters.dateRange) {
        case 'today':
          cutoffDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
          break;
        case 'week':
          cutoffDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          break;
        case 'month':
          cutoffDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
          break;
        case 'quarter':
          cutoffDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
          break;
        default:
          cutoffDate = null;
      }
      
      if (cutoffDate) {
        filtered = filtered.filter(indicator => 
          indicator.createdDate >= cutoffDate
        );
      }
    }

    setFilteredIndicators(filtered);
    setTotalPages(Math.ceil(filtered.length / itemsPerPage));
    
    // Reset to first page if current page is beyond available pages
    if (currentPage > Math.ceil(filtered.length / itemsPerPage)) {
      setCurrentPage(1);
    }
  };

  // Handle filter changes
  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
    setCurrentPage(1); // Reset to first page when filters change
  };

  // Reset all filters
  const resetFilters = () => {
    setFilters({
      type: '',
      severity: '',
      status: '',
      source: '',
      dateRange: '',
      searchTerm: ''
    });
    setCurrentPage(1);
  };

  // Get paginated indicators
  const getPaginatedIndicators = () => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredIndicators.slice(startIndex, endIndex);
  };

  // Handle page changes
  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  // Handle refresh
  const handleRefresh = () => {
    fetchIndicators();
  };
  
  return (
    <section id="ioc-management" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">IoC Management</h1>
          <p className="page-subtitle">Manage and analyze indicators of compromise</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline" onClick={() => setShowExportModal(true)}><i className="fas fa-file-export"></i> Export IoCs</button>
          <button className="btn btn-outline" onClick={() => setShowImportModal(true)}><i className="fas fa-file-import"></i> Import IoCs</button>
          <button className="btn btn-primary" onClick={() => setShowAddModal(true)}><i className="fas fa-plus"></i> Add New IoC</button>
        </div>
      </div>

      <div className="filters-section">
        <div className="filters-header">
          <h3><i className="fas fa-filter"></i> Filter & Search IoCs</h3>
          <div className="filter-actions">
            {Object.values(filters).some(value => value !== '') && (
              <button 
                className="btn btn-secondary btn-sm" 
                onClick={resetFilters}
                title="Clear all active filters"
              >
                <i className="fas fa-times"></i> Clear Filters
              </button>
            )}
            <div className="results-summary">
              {Object.values(filters).some(value => value !== '') ? (
                <span className="filtered-count">
                  <strong>{filteredIndicators.length}</strong> of <strong>{indicators.length}</strong> indicators match
                </span>
              ) : (
                <span className="total-count">
                  <strong>{indicators.length}</strong> total indicators
                </span>
              )}
            </div>
          </div>
        </div>
        
        <div className="filters-grid">
          <div className="filter-group">
            <label className="filter-label">Search</label>
            <div className="filter-control">
              <input
                type="text"
                placeholder="Search by value or description..."
                value={filters.searchTerm}
                onChange={(e) => handleFilterChange('searchTerm', e.target.value)}
                className="form-control"
              />
            </div>
          </div>
          
          <div className="filter-group">
            <label className="filter-label">IoC Type</label>
            <div className="filter-control">
              <select 
                value={filters.type}
                onChange={(e) => handleFilterChange('type', e.target.value)}
                className="form-control"
              >
                <option value="">All Types</option>
                <option value="ip">IP Address</option>
                <option value="domain">Domain</option>
                <option value="url">URL</option>
                <option value="file_hash">File Hash</option>
                <option value="email">Email</option>
                <option value="user_agent">User Agent</option>
                <option value="registry">Registry Key</option>
                <option value="mutex">Mutex</option>
                <option value="process">Process</option>
              </select>
            </div>
          </div>
          
          <div className="filter-group">
            <label className="filter-label">Severity</label>
            <div className="filter-control">
              <select 
                value={filters.severity}
                onChange={(e) => handleFilterChange('severity', e.target.value)}
                className="form-control"
              >
                <option value="">All Severities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>
          
          <div className="filter-group">
            <label className="filter-label">Status</label>
            <div className="filter-control">
              <select 
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="form-control"
              >
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="anonymized">Anonymized</option>
                <option value="inactive">Inactive</option>
                <option value="review">Under Review</option>
              </select>
            </div>
          </div>
          
          <div className="filter-group">
            <label className="filter-label">Source</label>
            <div className="filter-control">
              <input
                type="text"
                placeholder="Filter by source..."
                value={filters.source}
                onChange={(e) => handleFilterChange('source', e.target.value)}
                className="form-control"
              />
            </div>
          </div>
          
          <div className="filter-group">
            <label className="filter-label">Date Range</label>
            <div className="filter-control">
              <select 
                value={filters.dateRange}
                onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                className="form-control"
              >
                <option value="">All Time</option>
                <option value="today">Today</option>
                <option value="week">Last Week</option>
                <option value="month">Last Month</option>
                <option value="quarter">Last Quarter</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title"><i className="fas fa-search card-icon"></i> Indicators of Compromise</h2>
          <div className="card-actions">
            <div className="items-per-page-selector" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginRight: '1rem' }}>
              <label htmlFor="itemsPerPage" style={{ fontSize: '0.75rem', color: '#666', whiteSpace: 'nowrap' }}>Show:</label>
              <select 
                id="itemsPerPage"
                value={itemsPerPage} 
                onChange={(e) => {
                  setItemsPerPage(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="form-control form-control-sm"
                style={{
                  height: '32px',
                  fontSize: '0.875rem',
                  padding: '0.25rem 0.5rem',
                  minWidth: '100px',
                  borderRadius: '4px',
                  border: '1px solid #ccc'
                }}
              >
                <option value={10}>10 per page</option>
                <option value={20}>20 per page</option>
                <option value={50}>50 per page</option>
                <option value={100}>100 per page</option>
              </select>
            </div>
            <button 
              className="btn btn-outline btn-sm" 
              onClick={handleRefresh} 
              disabled={loading}
              style={{
                height: '32px',
                fontSize: '0.875rem',
                padding: '0.25rem 0.75rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                borderRadius: '4px',
                lineHeight: '1',
                minHeight: '32px',
                maxHeight: '32px'
              }}
            >
              <i className={`fas fa-sync-alt ${loading ? 'fa-spin' : ''}`}></i> 
              {loading ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>
        <div className="card-content">
          <div className="table-responsive">
            <table className="data-table">
            <thead>
              <tr>
                <th><input type="checkbox" /></th>
                <th>Type</th>
                <th>Title</th>
                <th>Value</th>
                <th>Description</th>
                <th>Severity</th>
                <th>Source</th>
                <th>Date Added</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="10" style={{textAlign: 'center', padding: '2rem'}}>
                    <i className="fas fa-spinner fa-spin"></i> Loading indicators...
                  </td>
                </tr>
              ) : getPaginatedIndicators().length > 0 ? (
                getPaginatedIndicators().map((indicator) => (
                  <tr key={indicator.id}>
                    <td><input type="checkbox" /></td>
                    <td>
                      <span className={`type-badge type-${indicator.rawType}`}>
                        {indicator.type}
                      </span>
                    </td>
                    <td className="indicator-title" title={indicator.title || ''}>
                      {indicator.title ? 
                        (indicator.title.length > 30 ? 
                          `${indicator.title.substring(0, 30)}...` : 
                          indicator.title
                        ) : 
                        <em className="text-muted">No title</em>
                      }
                    </td>
                    <td className="indicator-value" title={indicator.value}>
                      {indicator.value.length > 50 ? 
                        `${indicator.value.substring(0, 50)}...` : 
                        indicator.value
                      }
                    </td>
                    <td className="indicator-description" title={indicator.description || ''}>
                      {indicator.description ? 
                        (indicator.description.length > 40 ? 
                          `${indicator.description.substring(0, 40)}...` : 
                          indicator.description
                        ) : 
                        <em className="text-muted">No description</em>
                      }
                    </td>
                    <td>
                      <span className={`badge badge-${indicator.severity.toLowerCase()}`}>
                        {indicator.severity}
                      </span>
                    </td>
                    <td>{indicator.source}</td>
                    <td>{indicator.created}</td>
                    <td>
                      <span className={`badge badge-${indicator.status.toLowerCase()}`}>
                        {indicator.status}
                      </span>
                    </td>
                    <td>
                      <button 
                        className="btn btn-outline btn-sm" 
                        title="Edit Indicator"
                        onClick={() => handleEditIndicator(indicator)}
                      >
                        <i className="fas fa-edit"></i>
                      </button>
                      <button 
                        className="btn btn-outline btn-sm" 
                        title="Share Indicator"
                        onClick={() => handleShareIndicator(indicator)}
                      >
                        <i className="fas fa-share-alt"></i>
                      </button>
                    </td>
                  </tr>
                ))
              ) : filteredIndicators.length === 0 && indicators.length > 0 ? (
                <tr>
                  <td colSpan="10" style={{textAlign: 'center', padding: '2rem'}}>
                    <i className="fas fa-filter"></i> No indicators match the current filters.
                    <br />
                    <button className="btn btn-outline btn-sm mt-2" onClick={resetFilters}>
                      <i className="fas fa-times"></i> Clear Filters
                    </button>
                  </td>
                </tr>
              ) : (
                <tr>
                  <td colSpan="10" style={{textAlign: 'center', padding: '2rem'}}>
                    <i className="fas fa-info-circle"></i> No indicators found. 
                    Try consuming threat feeds to populate data.
                  </td>
                </tr>
              )}
            </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Enhanced Pagination */}
      <div 
        className="pagination-wrapper"
        style={{
          margin: '2rem auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
          padding: '1.5rem',
          background: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #dee2e6',
          maxWidth: 'fit-content',
          width: 'auto',
          textAlign: 'center'
        }}
      >
        <div className="pagination-info-detailed">
          <span className="pagination-summary">
            Showing <strong>{Math.min((currentPage - 1) * itemsPerPage + 1, filteredIndicators.length)}</strong> to <strong>{Math.min(currentPage * itemsPerPage, filteredIndicators.length)}</strong> of <strong>{filteredIndicators.length}</strong> 
            {Object.values(filters).some(value => value !== '') ? ' filtered' : ''} indicators
          </span>
        </div>
        
        {totalPages > 1 && (
          <div 
            className="pagination-controls-enhanced"
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: '0.5rem',
              flexWrap: 'nowrap',
              overflowX: 'auto',
              padding: '0.5rem',
              margin: '0 auto',
              width: 'fit-content'
            }}
          >
            {/* First button */}
            <button 
              className="btn btn-outline btn-sm"
              onClick={() => handlePageChange(1)}
              disabled={currentPage === 1}
              title="First page"
            >
              <i className="fas fa-angle-double-left"></i>
            </button>
            
            {/* Previous button */}
            <button 
              className="btn btn-outline btn-sm"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              title="Previous page"
            >
              <i className="fas fa-angle-left"></i>
            </button>

            {/* Page numbers - all inline */}
            {(() => {
              const pages = [];
              const startPage = Math.max(1, currentPage - 2);
              const endPage = Math.min(totalPages, currentPage + 2);
              
              if (startPage > 1) {
                pages.push(
                  <button 
                    key={1}
                    className="btn btn-outline btn-sm"
                    onClick={() => handlePageChange(1)}
                  >
                    1
                  </button>
                );
                if (startPage > 2) {
                  pages.push(<span key="ellipsis1" className="pagination-ellipsis">...</span>);
                }
              }
              
              for (let i = startPage; i <= endPage; i++) {
                pages.push(
                  <button 
                    key={i}
                    className={`btn btn-sm ${i === currentPage ? 'btn-primary' : 'btn-outline'}`}
                    onClick={() => handlePageChange(i)}
                  >
                    {i}
                  </button>
                );
              }
              
              if (endPage < totalPages) {
                if (endPage < totalPages - 1) {
                  pages.push(<span key="ellipsis2" className="pagination-ellipsis">...</span>);
                }
                pages.push(
                  <button 
                    key={totalPages}
                    className="btn btn-outline btn-sm"
                    onClick={() => handlePageChange(totalPages)}
                  >
                    {totalPages}
                  </button>
                );
              }
              
              return pages;
            })()}

            {/* Next button */}
            <button 
              className="btn btn-outline btn-sm"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              title="Next page"
            >
              <i className="fas fa-angle-right"></i>
            </button>
            
            {/* Last button */}
            <button 
              className="btn btn-outline btn-sm"
              onClick={() => handlePageChange(totalPages)}
              disabled={currentPage === totalPages}
              title="Last page"
            >
              <i className="fas fa-angle-double-right"></i>
            </button>
          </div>
        )}
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h2 className="card-title"><i className="fas fa-chart-pie card-icon"></i> IoC Statistics</h2>
        </div>
        <div className="card-content">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-title">
                <div className="stat-icon"><i className="fas fa-search"></i></div>
                <span>Total IoCs{Object.values(filters).some(f => f !== '') ? ' (Filtered)' : ''}</span>
              </div>
              <div className="stat-value">{Object.values(filters).some(f => f !== '') ? filteredIndicators.length : indicators.length}</div>
              <div className="stat-description">
                {Object.values(filters).some(f => f !== '') ? 
                  `${filteredIndicators.length} of ${indicators.length} match filters` :
                  'All indicators in system'
                }
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-title">
                <div className="stat-icon"><i className="fas fa-exclamation-triangle"></i></div>
                <span>High Severity</span>
              </div>
              <div className="stat-value">
                {(Object.values(filters).some(f => f !== '') ? filteredIndicators : indicators)
                  .filter(ind => ind.severity.toLowerCase() === 'high').length}
              </div>
              <div className="stat-description">
                Critical threat indicators
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-title">
                <div className="stat-icon"><i className="fas fa-user-secret"></i></div>
                <span>Anonymized</span>
              </div>
              <div className="stat-value">
                {(Object.values(filters).some(f => f !== '') ? filteredIndicators : indicators)
                  .filter(ind => ind.status.toLowerCase() === 'anonymized').length}
              </div>
              <div className="stat-description">
                Privacy-protected IoCs
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-title">
                <div className="stat-icon"><i className="fas fa-chart-line"></i></div>
                <span>Active</span>
              </div>
              <div className="stat-value">
                {(Object.values(filters).some(f => f !== '') ? filteredIndicators : indicators)
                  .filter(ind => ind.status.toLowerCase() === 'active').length}
              </div>
              <div className="stat-description">
                Currently monitored IoCs
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add New IoC Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={closeAddModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2><i className="fas fa-plus"></i> Add New IoC</h2>
              <button className="modal-close" onClick={closeAddModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleAddIoC}>
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">IoC Type *</label>
                    <select 
                      value={newIoC.type} 
                      onChange={(e) => setNewIoC({...newIoC, type: e.target.value})}
                      className={formErrors.type ? 'form-control error' : 'form-control'}
                      required
                    >
                      <option value="">Select Type</option>
                      <option value="ip">IP Address</option>
                      <option value="domain">Domain</option>
                      <option value="url">URL</option>
                      <option value="file_hash">File Hash</option>
                      <option value="email">Email</option>
                      <option value="user_agent">User Agent</option>
                      <option value="registry">Registry Key</option>
                      <option value="mutex">Mutex</option>
                      <option value="process">Process</option>
                    </select>
                    {formErrors.type && <span className="error-text">{formErrors.type}</span>}
                  </div>

                  <div className="form-group">
                    <label className="form-label">Severity</label>
                    <select 
                      value={newIoC.severity} 
                      onChange={(e) => setNewIoC({...newIoC, severity: e.target.value})}
                      className="form-control"
                    >
                      <option value="Low">Low</option>
                      <option value="Medium">Medium</option>
                      <option value="High">High</option>
                    </select>
                  </div>
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">IoC Value *</label>
                    <input 
                      type="text" 
                      value={newIoC.value} 
                      onChange={(e) => setNewIoC({...newIoC, value: e.target.value})}
                      className={formErrors.value ? 'form-control error' : 'form-control'}
                      placeholder="Enter the indicator value (e.g., 192.168.1.1, malicious.com, etc.)"
                      required
                    />
                    {formErrors.value && <span className="error-text">{formErrors.value}</span>}
                  </div>

                  <div className="form-group">
                    <label className="form-label">Source</label>
                    <input 
                      type="text" 
                      value={newIoC.source} 
                      onChange={(e) => setNewIoC({...newIoC, source: e.target.value})}
                      className="form-control"
                      placeholder="Source of this IoC (e.g., Internal Analysis, OSINT, etc.)"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Confidence Level: {newIoC.confidence}%</label>
                    <input 
                      type="range" 
                      min="0" 
                      max="100" 
                      value={newIoC.confidence} 
                      onChange={(e) => setNewIoC({...newIoC, confidence: parseInt(e.target.value)})}
                      className="form-range"
                    />
                    <div className="range-labels">
                      <span>Low (0%)</span>
                      <span>High (100%)</span>
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Description</label>
                    <textarea 
                      value={newIoC.description} 
                      onChange={(e) => setNewIoC({...newIoC, description: e.target.value})}
                      className="form-control"
                      rows="3"
                      placeholder="Additional notes or description about this IoC..."
                    ></textarea>
                  </div>

                <div className="modal-actions">
                  <button type="button" className="btn btn-outline" onClick={closeAddModal} disabled={submitting}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={submitting}>
                    {submitting ? (
                      <><i className="fas fa-spinner fa-spin"></i> Adding...</>
                    ) : (
                      <><i className="fas fa-plus"></i> Add IoC</>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Export IoCs Modal */}
      {showExportModal && (
        <div className="modal-overlay" onClick={closeExportModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2><i className="fas fa-file-export"></i> Export IoCs</h2>
              <button className="modal-close" onClick={closeExportModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">Export Format</label>
                <select 
                  value={exportFormat} 
                  onChange={(e) => setExportFormat(e.target.value)}
                  className="form-control"
                >
                  <option value="csv">CSV (Comma Separated Values)</option>
                  <option value="json">JSON (JavaScript Object Notation)</option>
                  <option value="stix">STIX 2.1 (Structured Threat Information)</option>
                </select>
              </div>

              <div className="export-info">
                <div className="info-card">
                  <i className="fas fa-info-circle"></i>
                  <div>
                    <strong>Export Details:</strong>
                    <p>You are about to export {indicators.length} indicators of compromise.</p>
                    {exportFormat === 'csv' && (
                      <p><strong>CSV Format:</strong> Suitable for spreadsheet analysis. Includes all indicator fields in tabular format.</p>
                    )}
                    {exportFormat === 'json' && (
                      <p><strong>JSON Format:</strong> Machine-readable format suitable for programmatic processing and API integration.</p>
                    )}
                    {exportFormat === 'stix' && (
                      <p><strong>STIX 2.1 Format:</strong> Industry-standard format for threat intelligence sharing. Compatible with TAXII servers.</p>
                    )}
                  </div>
                </div>
              </div>

              <div className="modal-actions">
                <button type="button" className="btn btn-outline" onClick={closeExportModal} disabled={exporting}>
                  Cancel
                </button>
                <button type="button" className="btn btn-primary" onClick={handleExport} disabled={exporting}>
                  {exporting ? (
                    <><i className="fas fa-spinner fa-spin"></i> Exporting...</>
                  ) : (
                    <><i className="fas fa-download"></i> Export {indicators.length} IoCs</>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Import IoCs Modal */}
      {showImportModal && (
        <div className="modal-overlay" onClick={closeImportModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2><i className="fas fa-file-import"></i> Import IoCs</h2>
              <button className="modal-close" onClick={closeImportModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              {!showPreview ? (
                <>
                  <div className="form-group">
                    <label className="form-label">Import Format</label>
                    <select 
                      value={importFormat} 
                      onChange={(e) => setImportFormat(e.target.value)}
                      className="form-control"
                    >
                      <option value="auto">Auto-detect from file</option>
                      <option value="csv">CSV (Comma Separated Values)</option>
                      <option value="json">JSON (JavaScript Object Notation)</option>
                      <option value="stix">STIX 2.1 (Structured Threat Information)</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Select File</label>
                    <div className="file-upload-area" onDrop={handleFileDrop} onDragOver={handleDragOver}>
                      <input 
                        type="file" 
                        accept=".csv,.json" 
                        onChange={handleFileSelect}
                        className="file-input"
                        id="import-file"
                      />
                      <label htmlFor="import-file" className="file-upload-label">
                        <i className="fas fa-cloud-upload-alt"></i>
                        <span>
                          {importFile ? importFile.name : 'Drop file here or click to browse'}
                        </span>
                        <small>Supported formats: CSV, JSON, STIX (.json)</small>
                      </label>
                    </div>
                  </div>

                  <div className="import-info">
                    <div className="info-card">
                      <i className="fas fa-info-circle"></i>
                      <div>
                        <strong>Import Guidelines:</strong>
                        <ul>
                          <li><strong>CSV:</strong> Must include headers: Type, Value, Severity, Source, Status</li>
                          <li><strong>JSON:</strong> Should match the export format structure</li>
                          <li><strong>STIX:</strong> Must be valid STIX 2.1 bundle format</li>
                          <li>Duplicate indicators will be skipped automatically</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="modal-actions">
                    <button type="button" className="btn btn-outline" onClick={closeImportModal} disabled={importing}>
                      Cancel
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-primary" 
                      onClick={handleFilePreview} 
                      disabled={!importFile || importing}
                    >
                      {importing ? (
                        <><i className="fas fa-spinner fa-spin"></i> Processing...</>
                      ) : (
                        <><i className="fas fa-eye"></i> Preview Import</>
                      )}
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <div className="preview-header">
                    <h3>Import Preview</h3>
                    <p>Review {importPreview.length} indicators before importing:</p>
                  </div>

                  <div className="preview-table-container">
                    <table className="preview-table">
                      <thead>
                        <tr>
                          <th>Type</th>
                          <th>Title</th>
                          <th>Value</th>
                          <th>Description</th>
                          <th>Severity</th>
                          <th>Source</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {importPreview.slice(0, 10).map((indicator, index) => (
                          <tr key={index}>
                            <td>{indicator.type}</td>
                            <td className="truncate" title={indicator.name || ''}>{indicator.name || <em>No title</em>}</td>
                            <td className="truncate">{indicator.value}</td>
                            <td className="truncate" title={indicator.description || ''}>{indicator.description || <em>No description</em>}</td>
                            <td>
                              <span className={`badge badge-${indicator.severity?.toLowerCase()}`}>
                                {indicator.severity}
                              </span>
                            </td>
                            <td>{indicator.source}</td>
                            <td>{indicator.status}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {importPreview.length > 10 && (
                      <p className="preview-note">
                        ... and {importPreview.length - 10} more indicators
                      </p>
                    )}
                  </div>

                  <div className="modal-actions">
                    <button type="button" className="btn btn-outline" onClick={goBackToUpload} disabled={importing}>
                      <i className="fas fa-arrow-left"></i> Back
                    </button>
                    <button type="button" className="btn btn-primary" onClick={handleImport} disabled={importing}>
                      {importing ? (
                        <><i className="fas fa-spinner fa-spin"></i> Importing...</>
                      ) : (
                        <><i className="fas fa-upload"></i> Import {importPreview.length} IoCs</>
                      )}
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Edit IoC Modal */}
      {showEditModal && (
        <div className="modal-overlay" onClick={closeEditModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2><i className="fas fa-edit"></i> Edit IoC</h2>
              <button className="modal-close" onClick={closeEditModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleUpdateIndicator}>
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">IoC Type *</label>
                    <select 
                      value={editFormData.type} 
                      onChange={(e) => setEditFormData({...editFormData, type: e.target.value})}
                      className={editFormErrors.type ? 'form-control error' : 'form-control'}
                      required
                    >
                      <option value="">Select Type</option>
                      <option value="ip">IP Address</option>
                      <option value="domain">Domain</option>
                      <option value="url">URL</option>
                      <option value="file_hash">File Hash</option>
                      <option value="email">Email</option>
                      <option value="user_agent">User Agent</option>
                      <option value="registry">Registry Key</option>
                      <option value="mutex">Mutex</option>
                      <option value="process">Process</option>
                    </select>
                    {editFormErrors.type && <span className="error-text">{editFormErrors.type}</span>}
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">Confidence Level: {editFormData.confidence}%</label>
                    <input 
                      type="range" 
                      min="0" 
                      max="100" 
                      value={editFormData.confidence} 
                      onChange={(e) => setEditFormData({...editFormData, confidence: parseInt(e.target.value)})}
                      className="form-range"
                    />
                    <div className="range-labels">
                      <span>Low (0%)</span>
                      <span>High (100%)</span>
                    </div>
                  </div>
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">IoC Value *</label>
                    <input 
                      type="text" 
                      value={editFormData.value} 
                      onChange={(e) => setEditFormData({...editFormData, value: e.target.value})}
                      className={editFormErrors.value ? 'form-control error' : 'form-control'}
                      placeholder="Enter IoC value (IP, domain, hash, etc.)"
                      required
                    />
                    {editFormErrors.value && <span className="error-text">{editFormErrors.value}</span>}
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">Description</label>
                    <textarea 
                      value={editFormData.description} 
                      onChange={(e) => setEditFormData({...editFormData, description: e.target.value})}
                      className="form-control"
                      placeholder="Optional description or notes"
                      rows="3"
                    />
                  </div>
                
                {editFormErrors.submit && (
                  <div className="error-message">
                    <i className="fas fa-exclamation-triangle"></i>
                    {editFormErrors.submit}
                  </div>
                )}
                
                <div className="modal-actions">
                  <button type="button" className="btn btn-outline" onClick={closeEditModal} disabled={updating}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={updating}>
                    {updating ? (
                      <><i className="fas fa-spinner fa-spin"></i> Updating...</>
                    ) : (
                      <><i className="fas fa-save"></i> Update IoC</>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Share IoC Modal */}
      {showShareModal && (
        <div className="modal-overlay" onClick={closeShareModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2><i className="fas fa-share-alt"></i> Share IoC</h2>
              <button className="modal-close" onClick={closeShareModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleShareIndicatorSubmit}>
                <div className="form-group">
                  <label className="form-label">IoC Details</label>
                  <div className="info-box">
                    <p><strong>Type:</strong> {sharingIndicator?.type}</p>
                    <p><strong>Value:</strong> {sharingIndicator?.value}</p>
                    <p><strong>Source:</strong> {sharingIndicator?.source}</p>
                  </div>
                </div>
                
                <div className="form-group">
                  <label className="form-label">
                    <i className="fas fa-share-nodes form-icon"></i>
                    Target Organizations
                  </label>
                  <p className="form-description">
                    Select trusted organisations to share this threat intelligence with
                  </p>
                  
                  {/* Sleek Organization Selector */}
                  <div className="sleek-org-selector">
                    {/* Search Input */}
                    <div className="search-field">
                      <input
                        type="text"
                        className="sleek-search-input"
                        value={organisationDropdownSearch}
                        onChange={(e) => {
                          setOrganisationDropdownSearch(e.target.value);
                          setShowOrganisationSelectDropdown(true);
                        }}
                        onFocus={() => setShowOrganisationSelectDropdown(true)}
                        onBlur={(e) => {
                          setTimeout(() => {
                            if (!e.relatedTarget || !e.relatedTarget.closest('.results-list')) {
                              setShowOrganisationSelectDropdown(false);
                            }
                          }, 200);
                        }}
                        placeholder="Type to search organizations..."
                      />
                      <i className="fas fa-search search-icon"></i>
                    </div>
                    
                    {/* Results List */}
                    {showOrganisationSelectDropdown && organisationDropdownSearch && (
                      <div className="results-list">
                        {availableOrganisations
                          .filter(organisation => 
                            !shareFormData.organisations.includes(organisation) &&
                            organisation.toLowerCase().includes(organisationDropdownSearch.toLowerCase())
                          )
                          .slice(0, 5)
                          .map(organisation => (
                            <div
                              key={organisation}
                              className="result-item"
                              onClick={() => {
                                addOrganisation(organisation);
                                setOrganisationDropdownSearch('');
                                setShowOrganisationSelectDropdown(false);
                              }}
                            >
                              <span className="result-name">{organisation}</span>
                              <i className="fas fa-plus add-icon"></i>
                            </div>
                          ))
                        }
                        {availableOrganisations
                          .filter(organisation => 
                            !shareFormData.organisations.includes(organisation) &&
                            organisation.toLowerCase().includes(organisationDropdownSearch.toLowerCase())
                          ).length === 0 && (
                            <div className="no-results">
                              No organizations found
                            </div>
                          )
                        }
                      </div>
                    )}
                    
                    {/* Selected Organizations */}
                    {shareFormData.organisations.length > 0 && (
                      <div className="selected-orgs">
                        <div className="selected-label">
                          Selected ({shareFormData.organisations.length})
                        </div>
                        <div className="org-tags">
                          {shareFormData.organisations.map(organisation => (
                            <div key={organisation} className="org-tag">
                              <span>{organisation}</span>
                              <button 
                                type="button" 
                                className="remove-tag"
                                onClick={() => removeOrganisation(organisation)}
                              >
                                ×
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">
                      <i className="fas fa-user-secret form-icon"></i>
                      Anonymization Level
                    </label>
                    <p className="form-description">
                      Choose how much detail to share with receiving organizations
                    </p>
                    <select 
                      value={shareFormData.anonymizationLevel} 
                      onChange={(e) => setShareFormData({...shareFormData, anonymizationLevel: e.target.value})}
                      className="form-control enhanced-select multiline-select"
                    >
                      <option value="none">None - Full Details
Complete IoC values and metadata shared</option>
                      <option value="low">Low - Minor Obfuscation
Remove source identifiers and timestamps</option>
                      <option value="medium">Medium - Partial Anonymization
Generalize IPs/domains (evil.com → *.com)</option>
                      <option value="high">High - Strong Anonymization
Only patterns and techniques, no indicators</option>
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">Share Method</label>
                    <select 
                      value={shareFormData.shareMethod} 
                      onChange={(e) => setShareFormData({...shareFormData, shareMethod: e.target.value})}
                      className="form-control"
                    >
                      <option value="taxii">TAXII 2.1 Protocol</option>
                      <option value="email">Email Export</option>
                      <option value="api">Direct API Push</option>
                    </select>
                  </div>
                </div>
                
                <div className="modal-actions">
                  <button type="button" className="btn btn-outline" onClick={closeShareModal} disabled={sharing}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={sharing || shareFormData.organisations.length === 0}>
                    {sharing ? (
                      <><i className="fas fa-spinner fa-spin"></i> Sharing...</>
                    ) : (
                      <><i className="fas fa-share-alt"></i> Share with {shareFormData.organisations.length} Organisation(s)</>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </section>
  );

  // Helper functions
  function closeAddModal() {
    setShowAddModal(false);
    setNewIoC({
      type: '',
      value: '',
      severity: 'Medium',
      description: '',
      source: '',
      confidence: 50,
      threatFeed: '',
      createNewFeed: false,
      newFeedName: '',
      newFeedDescription: ''
    });
    setFormErrors({});
  }

  function closeExportModal() {
    setShowExportModal(false);
    setExportFormat('csv');
  }

  async function handleExport() {
    if (indicators.length === 0) {
      alert('No indicators to export');
      return;
    }

    setExporting(true);
    
    try {
      let exportData;
      let filename;
      let mimeType;

      switch (exportFormat) {
        case 'csv':
          exportData = exportToCSV(indicators);
          filename = `iocs_export_${new Date().toISOString().split('T')[0]}.csv`;
          mimeType = 'text/csv';
          break;
        case 'json':
          exportData = exportToJSON(indicators);
          filename = `iocs_export_${new Date().toISOString().split('T')[0]}.json`;
          mimeType = 'application/json';
          break;
        case 'stix':
          exportData = exportToSTIX(indicators);
          filename = `iocs_export_${new Date().toISOString().split('T')[0]}.json`;
          mimeType = 'application/json';
          break;
        default:
          throw new Error('Unsupported export format');
      }

      // Create and download file
      const blob = new Blob([exportData], { type: mimeType });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      // Close modal
      closeExportModal();
      
      console.log(`Successfully exported ${indicators.length} IoCs as ${exportFormat.toUpperCase()}`);
      
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please try again.');
    } finally {
      setExporting(false);
    }
  }

  function exportToCSV(data) {
    const headers = ['Type', 'Value', 'Severity', 'Source', 'Date Added', 'Status'];
    const csvHeaders = headers.join(',');
    
    const csvRows = data.map(indicator => [
      `"${indicator.type}"`,
      `"${indicator.value}"`,
      `"${indicator.severity}"`,
      `"${indicator.source}"`,
      `"${indicator.created}"`,
      `"${indicator.status}"`
    ].join(','));

    return [csvHeaders, ...csvRows].join('\n');
  }

  function exportToJSON(data) {
    const exportObject = {
      export_date: new Date().toISOString(),
      total_indicators: data.length,
      indicators: data.map(indicator => ({
        id: indicator.id,
        type: indicator.type,
        value: indicator.value,
        severity: indicator.severity,
        source: indicator.source,
        created: indicator.created,
        status: indicator.status
      }))
    };
    
    return JSON.stringify(exportObject, null, 2);
  }

  function exportToSTIX(data) {
    const stixBundle = {
      type: "bundle",
      id: `bundle--${generateUUID()}`,
      spec_version: "2.1",
      created: new Date().toISOString(),
      modified: new Date().toISOString(),
      objects: data.map(indicator => ({
        type: "indicator",
        id: `indicator--${generateUUID()}`,
        created: new Date(indicator.created).toISOString(),
        modified: new Date().toISOString(),
        labels: ["malicious-activity"],
        pattern: generateSTIXPattern(indicator),
        indicator_types: ["malicious-activity"],
        confidence: getConfidenceFromSeverity(indicator.severity),
        x_crisp_source: indicator.source,
        x_crisp_severity: indicator.severity,
        x_crisp_status: indicator.status
      }))
    };

    return JSON.stringify(stixBundle, null, 2);
  }

  function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  function generateSTIXPattern(indicator) {
    switch (indicator.type.toLowerCase()) {
      case 'ip address':
        return `[ipv4-addr:value = '${indicator.value}']`;
      case 'domain':
        return `[domain-name:value = '${indicator.value}']`;
      case 'url':
        return `[url:value = '${indicator.value}']`;
      case 'file hash':
        return `[file:hashes.MD5 = '${indicator.value}' OR file:hashes.SHA1 = '${indicator.value}' OR file:hashes.SHA256 = '${indicator.value}']`;
      case 'email':
        return `[email-addr:value = '${indicator.value}']`;
      default:
        return `[x-custom:value = '${indicator.value}']`;
    }
  }

  function getConfidenceFromSeverity(severity) {
    switch (severity.toLowerCase()) {
      case 'high': return 85;
      case 'medium': return 60;
      case 'low': return 30;
      default: return 50;
    }
  }

  // Import functions
  function closeImportModal() {
    setShowImportModal(false);
    setImportFile(null);
    setImportFormat('auto');
    setImportPreview([]);
    setShowPreview(false);
  }

  function handleFileSelect(event) {
    const file = event.target.files[0];
    setImportFile(file);
  }

  function handleFileDrop(event) {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file && (file.type === 'text/csv' || file.type === 'application/json' || file.name.endsWith('.csv') || file.name.endsWith('.json'))) {
      setImportFile(file);
    }
  }

  function handleDragOver(event) {
    event.preventDefault();
  }

  async function handleFilePreview() {
    if (!importFile) return;

    setImporting(true);
    try {
      // Step 1: Generate file hash for integrity verification
      const fileHash = await generateFileHash(importFile);
      console.log(`File hash (SHA-256): ${fileHash}`);
      
      // Step 2: Read file content
      const fileContent = await readFileContent(importFile);
      
      // Step 3: Validate file type and content structure
      validateFileType(importFile, fileContent);
      
      // Step 4: Detect format and parse
      const detectedFormat = importFormat === 'auto' ? detectFileFormat(importFile.name, fileContent) : importFormat;
      const parsedData = await parseFileContent(fileContent, detectedFormat);
      
      // Step 5: Store file metadata for security audit
      const fileMetadata = {
        name: importFile.name,
        size: importFile.size,
        type: importFile.type,
        hash: fileHash,
        lastModified: new Date(importFile.lastModified).toISOString(),
        detectedFormat: detectedFormat,
        recordCount: parsedData.length
      };
      
      console.log('File security validation passed:', fileMetadata);
      setImportPreview(parsedData);
      setShowPreview(true);
      
    } catch (error) {
      console.error('File validation failed:', error);
      alert(`Security validation failed: ${error.message}`);
    } finally {
      setImporting(false);
    }
  }

  function goBackToUpload() {
    setShowPreview(false);
    setImportPreview([]);
  }

  async function handleImport() {
    if (importPreview.length === 0) return;

    setImporting(true);
    try {
      // Prepare indicators for bulk import
      const indicatorsToImport = importPreview.map(indicator => ({
        type: indicator.rawType || indicator.type.toLowerCase().replace(' ', '_'),
        value: indicator.value.trim(),
        name: indicator.name || '',
        description: indicator.description || '',
        confidence: parseInt(indicator.confidence) || 50
      }));
      
      // Call bulk import API
      const response = await api.post('/api/indicators/bulk-import/', {
        indicators: indicatorsToImport
      });
      
      if (response && response.success) {
        // Add successfully created indicators to local state
        const formattedIndicators = response.created_indicators.map(indicator => ({
          ...indicator,
          rawType: indicator.type,
          title: indicator.name || '',
          type: indicator.type === 'ip' ? 'IP Address' : 
                indicator.type === 'domain' ? 'Domain' :
                indicator.type === 'url' ? 'URL' :
                indicator.type === 'file_hash' ? 'File Hash' :
                indicator.type === 'email' ? 'Email' : indicator.type,
          severity: 'Medium', // Default severity for imported items
          status: 'Active',
          created: indicator.created_at ? indicator.created_at.split('T')[0] : new Date().toISOString().split('T')[0]
        }));
        
        setIndicators(prev => [...formattedIndicators, ...prev]);
        
        // Close modal
        closeImportModal();
        
        // Show results
        const message = `Import completed! Added ${response.created_count} new indicators.`;
        const errorMessage = response.error_count > 0 ? ` ${response.error_count} errors occurred.` : '';
        console.log(`${message}${errorMessage}`, response.errors);
        alert(`${message}${errorMessage}`);
        
      } else {
        throw new Error('Bulk import failed');
      }
      
    } catch (error) {
      console.error('Import failed:', error);
      alert('Import failed. Please try again.');
    } finally {
      setImporting(false);
    }
  }

  function readFileContent(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  }

  // Generate file hash for integrity verification
  async function generateFileHash(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const arrayBuffer = e.target.result;
          const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
          const hashArray = Array.from(new Uint8Array(hashBuffer));
          const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
          resolve(hashHex);
        } catch (error) {
          reject(error);
        }
      };
      reader.onerror = () => reject(new Error('Failed to read file for hashing'));
      reader.readAsArrayBuffer(file);
    });
  }

  // Validate file type by checking magic bytes/signatures
  function validateFileType(file, content) {
    const fileName = file.name.toLowerCase();
    const maxSize = 10 * 1024 * 1024; // 10MB limit
    
    // File size check
    if (file.size > maxSize) {
      throw new Error('File size exceeds 10MB limit');
    }
    
    // Allowed file types with their magic bytes
    const allowedTypes = {
      'csv': {
        extensions: ['.csv'],
        mimeTypes: ['text/csv', 'application/csv', 'text/plain'],
        maxSize: 5 * 1024 * 1024, // 5MB for CSV
        contentValidation: (content) => {
          // Basic CSV validation - should contain commas and reasonable structure
          const lines = content.split('\n').filter(line => line.trim());
          if (lines.length < 2) return false; // Should have header + at least one data row
          const firstLine = lines[0];
          return firstLine.includes(',') && firstLine.split(',').length >= 2;
        }
      },
      'json': {
        extensions: ['.json'],
        mimeTypes: ['application/json', 'text/json'],
        maxSize: 5 * 1024 * 1024, // 5MB for JSON
        contentValidation: (content) => {
          try {
            const parsed = JSON.parse(content);
            return typeof parsed === 'object' && parsed !== null;
          } catch {
            return false;
          }
        }
      },
      'txt': {
        extensions: ['.txt'],
        mimeTypes: ['text/plain'],
        maxSize: 2 * 1024 * 1024, // 2MB for TXT
        contentValidation: (content) => {
          // Basic text validation - should not contain suspicious patterns
          const suspiciousPatterns = [
            /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
            /<iframe\b[^>]*>/gi,
            /javascript:/gi,
            /on\w+\s*=/gi
          ];
          return !suspiciousPatterns.some(pattern => pattern.test(content));
        }
      }
    };
    
    // Check file extension
    const fileExt = fileName.substring(fileName.lastIndexOf('.'));
    const validType = Object.values(allowedTypes).find(type => 
      type.extensions.includes(fileExt)
    );
    
    if (!validType) {
      throw new Error(`Unsupported file type: ${fileExt}. Allowed types: CSV, JSON, TXT`);
    }
    
    // Check MIME type
    if (!validType.mimeTypes.includes(file.type) && file.type !== '') {
      console.warn(`MIME type mismatch: expected ${validType.mimeTypes.join('/')}, got ${file.type}`);
    }
    
    // Check file size for specific type
    if (file.size > validType.maxSize) {
      throw new Error(`File size exceeds limit for ${fileExt.substring(1).toUpperCase()} files (${(validType.maxSize / 1024 / 1024)}MB)`);
    }
    
    // Validate content structure
    if (!validType.contentValidation(content)) {
      throw new Error(`Invalid ${fileExt.substring(1).toUpperCase()} file format or content`);
    }
    
    return true;
  }

  function detectFileFormat(filename, content) {
    if (filename.endsWith('.csv')) return 'csv';
    if (filename.endsWith('.json')) {
      try {
        const parsed = JSON.parse(content);
        if (parsed.type === 'bundle' && parsed.objects) return 'stix';
        return 'json';
      } catch {
        return 'json';
      }
    }
    return 'csv';
  }

  async function parseFileContent(content, format) {
    switch (format) {
      case 'csv':
        return parseCSV(content);
      case 'json':
        return parseJSON(content);
      case 'stix':
        return parseSTIX(content);
      default:
        throw new Error('Unsupported file format');
    }
  }

  function parseCSV(content) {
    const lines = content.trim().split('\n');
    if (lines.length < 2) throw new Error('CSV file must have headers and at least one data row');
    
    const headers = lines[0].split(',').map(h => h.replace(/"/g, '').trim().toLowerCase());
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.replace(/"/g, '').trim());
      
      const indicator = {
        type: getColumnValue(headers, values, ['type', 'ioc_type', 'indicator_type']) || 'Unknown',
        value: getColumnValue(headers, values, ['value', 'ioc_value', 'indicator']) || '',
        name: getColumnValue(headers, values, ['name', 'title', 'indicator_name']) || '',
        description: getColumnValue(headers, values, ['description', 'desc', 'details']) || '',
        severity: getColumnValue(headers, values, ['severity', 'priority', 'threat_level']) || 'Medium',
        source: getColumnValue(headers, values, ['source', 'origin', 'feed']) || 'Import',
        status: getColumnValue(headers, values, ['status', 'state']) || 'Active'
      };
      
      if (indicator.value) {
        data.push(indicator);
      }
    }
    
    return data;
  }

  function parseJSON(content) {
    const data = JSON.parse(content);
    
    if (data.indicators && Array.isArray(data.indicators)) {
      return data.indicators.map(ind => ({
        type: ind.type || 'Unknown',
        value: ind.value || '',
        name: ind.name || '',
        description: ind.description || '',
        severity: ind.severity || 'Medium',
        source: ind.source || 'Import',
        status: ind.status || 'Active'
      }));
    }
    
    if (Array.isArray(data)) {
      return data.map(ind => ({
        type: ind.type || 'Unknown',
        value: ind.value || '',
        name: ind.name || '',
        description: ind.description || '',
        severity: ind.severity || 'Medium',
        source: ind.source || 'Import',
        status: ind.status || 'Active'
      }));
    }
    
    throw new Error('Invalid JSON format. Expected array or object with indicators property.');
  }

  function parseSTIX(content) {
    const bundle = JSON.parse(content);
    
    if (bundle.type !== 'bundle' || !bundle.objects) {
      throw new Error('Invalid STIX format. Expected bundle with objects.');
    }
    
    const indicators = bundle.objects.filter(obj => obj.type === 'indicator');
    
    return indicators.map(ind => ({
      type: extractTypeFromPattern(ind.pattern),
      value: extractValueFromPattern(ind.pattern),
      name: ind.name || '',
      description: ind.description || '',
      severity: mapConfidenceToSeverity(ind.confidence || 50),
      source: ind.x_crisp_source || 'STIX Import',
      status: ind.x_crisp_status || 'Active'
    }));
  }

  function getColumnValue(headers, values, possibleNames) {
    for (const name of possibleNames) {
      const index = headers.indexOf(name);
      if (index !== -1 && values[index]) {
        return values[index];
      }
    }
    return null;
  }

  function extractTypeFromPattern(pattern) {
    if (pattern.includes('ipv4-addr')) return 'IP Address';
    if (pattern.includes('domain-name')) return 'Domain';
    if (pattern.includes('url')) return 'URL';
    if (pattern.includes('file:hashes')) return 'File Hash';
    if (pattern.includes('email-addr')) return 'Email';
    return 'Unknown';
  }

  function extractValueFromPattern(pattern) {
    const match = pattern.match(/'([^']+)'/);
    return match ? match[1] : '';
  }

  function mapConfidenceToSeverity(confidence) {
    if (confidence >= 75) return 'High';
    if (confidence >= 45) return 'Medium';
    return 'Low';
  }


  function validateForm() {
    const errors = {};
    
    if (!newIoC.type) {
      errors.type = 'IoC type is required';
    }
    
    if (!newIoC.value.trim()) {
      errors.value = 'IoC value is required';
    } else {
      // Validate based on type
      const value = newIoC.value.trim();
      switch (newIoC.type) {
        case 'ip':
          const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
          if (!ipRegex.test(value)) {
            errors.value = 'Invalid IP address format';
          }
          break;
        case 'domain':
          const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$/;
          if (!domainRegex.test(value)) {
            errors.value = 'Invalid domain format';
          }
          break;
        case 'url':
          try {
            new URL(value);
          } catch {
            errors.value = 'Invalid URL format';
          }
          break;
        case 'email':
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(value)) {
            errors.value = 'Invalid email format';
          }
          break;
        case 'file_hash':
          const hashRegex = /^[a-fA-F0-9]+$/;
          if (!hashRegex.test(value) || ![32, 40, 64, 128].includes(value.length)) {
            errors.value = 'Invalid hash format (MD5, SHA1, SHA256, or SHA512)';
          }
          break;
      }
    }
    
    return errors;
  }

  // Edit indicator functions
  function handleEditIndicator(indicator) {
    setEditingIndicator(indicator);
    setEditFormData({
      type: indicator.rawType || indicator.type.toLowerCase().replace(' ', '_'),
      value: indicator.value,
      description: indicator.description || '',
      confidence: indicator.confidence || 50,
      threat_feed_id: indicator.feedId || '',
      threatFeedMode: 'existing'
    });
    setEditNewFeedName('');
    setEditNewFeedDescription('');
    setEditFormErrors({});
    setShowEditModal(true);
  }

  function closeEditModal() {
    setShowEditModal(false);
    setEditingIndicator(null);
    setEditFormData({
      type: '',
      value: '',
      description: '',
      confidence: 50,
      threat_feed_id: '',
      threatFeedMode: 'existing'
    });
    setEditNewFeedName('');
    setEditNewFeedDescription('');
    setEditFormErrors({});
  }

  async function handleUpdateIndicator(e) {
    e.preventDefault();
    
    if (!editingIndicator) return;
    
    setUpdating(true);
    setEditFormErrors({});
    
    try {
      let threatFeedId = editFormData.threat_feed_id;
      
      // Handle new threat feed creation
      if (editFormData.threatFeedMode === 'new' && editNewFeedName.trim()) {
        try {
          const newFeedData = {
            name: editNewFeedName.trim(),
            description: editNewFeedDescription.trim() || '',
            is_external: false,
            is_active: true
          };
          
          const feedResponse = await api.post('/api/threat-feeds/', newFeedData);
          if (feedResponse && feedResponse.id) {
            threatFeedId = feedResponse.id;
            // Update local threat feeds list
            setThreatFeeds(prev => [...prev, feedResponse]);
          }
        } catch (feedError) {
          console.error('Error creating new threat feed:', feedError);
          setEditFormErrors({ submit: 'Failed to create new threat feed. Please try again.' });
          return;
        }
      }
      
      const updateData = {
        type: editFormData.type,
        value: editFormData.value.trim(),
        description: editFormData.description || '',
        confidence: parseInt(editFormData.confidence) || 50,
        threat_feed_id: threatFeedId
      };
      
      const response = await api.put(`/api/indicators/${editingIndicator.id}/update/`, updateData);
      
      if (response) {
        // Update the indicator in local state
        const updatedIndicator = {
          ...response,
          rawType: response.type,
          type: response.type === 'ip' ? 'IP Address' : 
                response.type === 'domain' ? 'Domain' :
                response.type === 'url' ? 'URL' :
                response.type === 'file_hash' ? 'File Hash' :
                response.type === 'email' ? 'Email' : response.type,
          severity: editingIndicator.severity, // Keep existing severity
          status: editingIndicator.status, // Keep existing status
          created: response.created_at ? response.created_at.split('T')[0] : editingIndicator.created
        };
        
        setIndicators(prev => prev.map(ind => 
          ind.id === editingIndicator.id ? updatedIndicator : ind
        ));
        
        closeEditModal();
        alert('Indicator updated successfully!');
      } else {
        throw new Error('Failed to update indicator');
      }
      
    } catch (error) {
      console.error('Error updating indicator:', error);
      setEditFormErrors({ submit: 'Failed to update indicator. Please try again.' });
    } finally {
      setUpdating(false);
    }
  }

  // Share indicator functions
  function handleShareIndicator(indicator) {
    setSharingIndicator(indicator);
    setShareFormData({
      organisations: [],
      anonymizationLevel: 'medium',
      shareMethod: 'taxii'
    });
    setShowShareModal(true);
  }

  function closeShareModal() {
    setShowShareModal(false);
    setSharingIndicator(null);
    setShareFormData({
      organisations: [],
      anonymizationLevel: 'medium',
      shareMethod: 'taxii'
    });
    setOrganisationSearch('');
    setShowOrganisationDropdown(false);
    setSelectedOrganisationIndex(-1);
  }

  // Organisation search helper functions
  function getFilteredOrganisations() {
    return availableOrganisations.filter(organisation =>
      organisation.toLowerCase().includes(organisationSearch.toLowerCase()) &&
      !shareFormData.organisations.includes(organisation)
    );
  }

  function addOrganisation(organisation) {
    setShareFormData(prev => ({
      ...prev,
      organisations: [...prev.organisations, organisation]
    }));
    setOrganisationSearch('');
    setShowOrganisationDropdown(false);
    setSelectedOrganisationIndex(-1);
  }

  function handleKeyDown(e) {
    const filteredOrganisations = getFilteredOrganisations().slice(0, 10);
    
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedOrganisationIndex(prev => 
        prev < filteredOrganisations.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedOrganisationIndex(prev => prev > 0 ? prev - 1 : -1);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedOrganisationIndex >= 0 && selectedOrganisationIndex < filteredOrganisations.length) {
        addOrganisation(filteredOrganisations[selectedOrganisationIndex]);
      }
    } else if (e.key === 'Escape') {
      setShowOrganisationDropdown(false);
      setSelectedOrganisationIndex(-1);
    }
  }

  function removeOrganisation(organisation) {
    setShareFormData(prev => ({
      ...prev,
      institutions: prev.institutions.filter(inst => inst !== organisation)
    }));
  }

  async function handleShareIndicatorSubmit(e) {
    e.preventDefault();
    
    if (!sharingIndicator || shareFormData.organisations.length === 0) {
      alert('Please select at least one organisation to share with.');
      return;
    }
    
    setSharing(true);
    
    try {
      const shareData = {
        institutions: shareFormData.organisations,
        anonymization_level: shareFormData.anonymizationLevel,
        share_method: shareFormData.shareMethod
      };
      
      const response = await api.post(`/api/indicators/${sharingIndicator.id}/share/`, shareData);
      
      if (response && response.success) {
        closeShareModal();
        alert(`Indicator shared with ${response.shared_with} organisation(s) successfully!`);
      } else {
        throw new Error('Failed to share indicator');
      }
      
    } catch (error) {
      console.error('Error sharing indicator:', error);
      alert('Failed to share indicator. Please try again.');
    } finally {
      setSharing(false);
    }
  }

  async function handleAddIoC(e) {
    e.preventDefault();
    
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    
    setSubmitting(true);
    setFormErrors({});
    
    try {
      // Create indicator via API
      const indicatorData = {
        type: newIoC.type,
        value: newIoC.value.trim(),
        description: newIoC.description || '',
        confidence: parseInt(newIoC.confidence) || 50
      };
      
      const response = await api.post('/api/indicators/', indicatorData);
      
      if (response) {
        // Add the new indicator to the local state
        const formattedIndicator = {
          ...response,
          rawType: response.type,
          title: response.name || '',
          type: response.type === 'ip' ? 'IP Address' : 
                response.type === 'domain' ? 'Domain' :
                response.type === 'url' ? 'URL' :
                response.type === 'file_hash' ? 'File Hash' :
                response.type === 'email' ? 'Email' : response.type,
          severity: newIoC.severity || 'Medium',
          status: 'Active',
          created: response.created_at ? response.created_at.split('T')[0] : new Date().toISOString().split('T')[0]
        };
        
        setIndicators(prev => [formattedIndicator, ...prev]);
        
        // Close modal and reset form
        closeAddModal();
        
        // Show success message
        console.log('IoC added successfully:', response);
        alert('IoC added successfully!');
      } else {
        throw new Error('Failed to create indicator');
      }
      
    } catch (error) {
      console.error('Error adding IoC:', error);
      setFormErrors({ submit: 'Failed to add IoC. Please try again.' });
    } finally {
      setSubmitting(false);
    }
  }
}

// TTP Analysis Component
function TTPAnalysis({ active }) {
  if (!active) return null;
  
  const [ttpData, setTtpData] = useState([]);
  const [trendsData, setTrendsData] = useState([]);
  const [matrixData, setMatrixData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [trendsLoading, setTrendsLoading] = useState(false);
  const [matrixLoading, setMatrixLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Feed analysis state
  const [feedComparisonData, setFeedComparisonData] = useState(null);
  const [frequencyData, setFrequencyData] = useState(null);
  const [seasonalData, setSeasonalData] = useState(null);
  const [aggregationLoading, setAggregationLoading] = useState(false);
  
  // Table sorting state
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  
  // Table pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);
  
  // Table filtering state
  const [showFilters, setShowFilters] = useState(false);
  const [filterOptions, setFilterOptions] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    tactics: [],
    techniques: [],
    severity_levels: [],
    date_from: '',
    date_to: '',
    threat_feed_ids: [],
    anonymized_only: '',
    has_subtechniques: ''
  });
  const [activeFiltersCount, setActiveFiltersCount] = useState(0);
  
  // TTP Detail Modal state
  const [showTTPModal, setShowTTPModal] = useState(false);
  const [selectedTTP, setSelectedTTP] = useState(null);
  const [ttpDetailLoading, setTtpDetailLoading] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [editFormData, setEditFormData] = useState({});

  
  // Feed consumption state
  const [availableFeeds, setAvailableFeeds] = useState([]);
  const [selectedFeedForConsumption, setSelectedFeedForConsumption] = useState('');
  const [consumptionInProgress, setConsumptionInProgress] = useState(false);
  const [consumptionStatus, setConsumptionStatus] = useState('');
  
  // TTP Export Modal state
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportFormat, setExportFormat] = useState('json');
  const [exportFilters, setExportFilters] = useState({
    tactic: '',
    technique_id: '',
    feed_id: '',
    include_anonymized: true,
    include_original: false,
    created_after: '',
    created_before: '',
    limit: 1000,
    fields: ''
  });
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState('');
  
  // Matrix Cell Details Modal state
  const [showMatrixCellModal, setShowMatrixCellModal] = useState(false);
  const [matrixCellData, setMatrixCellData] = useState(null);
  const [matrixCellLoading, setMatrixCellLoading] = useState(false);
  const [selectedTactic, setSelectedTactic] = useState('');
  const [selectedTechnique, setSelectedTechnique] = useState('');
  
  // Technique Details Modal state
  const [showTechniqueModal, setShowTechniqueModal] = useState(false);
  const [techniqueData, setTechniqueData] = useState(null);
  const [techniqueLoading, setTechniqueLoading] = useState(false);
  const [selectedTechniqueId, setSelectedTechniqueId] = useState('');
  
  const ttpChartRef = useRef(null);
  
  // Fetch TTP data from backend
  useEffect(() => {
    if (active) {
      fetchTTPData();
      fetchMatrixData();
      fetchFilterOptions();
      fetchAvailableFeeds();
      fetchAggregationData();
    }
  }, [active]);
  
  // Fetch available threat feeds
  const fetchAvailableFeeds = async () => {
    try {
      const response = await api.get('/api/threat-feeds/');
      if (response && response.results) {
        setAvailableFeeds(response.results);
      } else {
        console.log('No threat feeds found or invalid response:', response);
        setAvailableFeeds([]);
      }
    } catch (error) {
      console.error('Error fetching available feeds:', error);
      setAvailableFeeds([]);
    }
  };

  // Fetch aggregation data for feed analysis
  const fetchAggregationData = async () => {
    setAggregationLoading(true);
    try {
      // Fetch multiple aggregation endpoints individually to handle failures gracefully
      const feedComparisonPromise = api.get('/api/ttps/feed-comparison/?days=30').catch(err => {
        console.warn('Feed comparison endpoint not available:', err);
        return null;
      });
      
      const techniqueFreqPromise = api.get('/api/ttps/technique-frequencies/?days=30').catch(err => {
        console.warn('Technique frequencies endpoint not available:', err);
        return null;
      });
      
      const seasonalPatternsPromise = api.get('/api/ttps/seasonal-patterns/?days=180').catch(err => {
        console.warn('Seasonal patterns endpoint not available:', err);
        return null;
      });

      const [feedComparison, techniqueFreq, seasonalPatterns] = await Promise.all([
        feedComparisonPromise,
        techniqueFreqPromise,
        seasonalPatternsPromise
      ]);

      if (feedComparison && feedComparison.success) {
        setFeedComparisonData(feedComparison);
      }
      if (techniqueFreq && techniqueFreq.success) {
        setFrequencyData(techniqueFreq);
      }
      if (seasonalPatterns && seasonalPatterns.success) {
        setSeasonalData(seasonalPatterns);
      }
    } catch (error) {
      console.error('Error fetching aggregation data:', error);
    }
    setAggregationLoading(false);
  };

  // Trigger feed consumption
  // Load TTPs from selected feed (like IoC Management)
  const loadFeedTTPs = async () => {
    if (!selectedFeedForConsumption) {
      alert('Please select a threat feed to analyze');
      return;
    }

    setConsumptionInProgress(true);
    setConsumptionStatus('Loading TTPs from feed...');

    try {
      // First get the feed name for display
      const selectedFeed = availableFeeds.find(feed => feed.id == selectedFeedForConsumption);
      const feedName = selectedFeed ? selectedFeed.name : 'Selected Feed';

      // Load TTPs from the specific feed using the same pattern as IoC Management
      await loadAllFeedTTPs(selectedFeedForConsumption, feedName);
      
    } catch (error) {
      console.error('Error loading feed TTPs:', error);
      setConsumptionStatus(`❌ Failed to load TTPs: ${error.message || 'Unknown error'}`);
      
      // Clear error status after 10 seconds
      setTimeout(() => {
        setConsumptionStatus('');
      }, 10000);
    } finally {
      setConsumptionInProgress(false);
    }
  };

  // Load all TTPs from feed with pagination (like IoC Management)
  const loadAllFeedTTPs = async (feedId, feedName) => {
    let allTTPs = [];
    let page = 1;
    let hasMore = true;
    const pageSize = 100;

    while (hasMore) {
      try {
        const response = await api.get(`/api/threat-feeds/${feedId}/ttps/?page=${page}&page_size=${pageSize}`);
        
        if (response && response.results) {
          // Add results from this page (even if 0 results)
          allTTPs = [...allTTPs, ...response.results];
          setConsumptionStatus(`Loading TTPs from "${feedName}"... (${allTTPs.length} loaded)`);
          
          // Continue pagination based on 'next' field, like IoC Management
          hasMore = response.next !== null;
          page++;
        } else {
          hasMore = false;
        }
      } catch (error) {
        console.error(`Error loading page ${page} of TTPs:`, error);
        hasMore = false;
        throw error;
      }
    }

    // Update the TTP data display
    setTtpData(allTTPs);
    setTotalCount(allTTPs.length);
    
    // Update status
    setConsumptionStatus(`✅ Loaded ${allTTPs.length} TTPs from "${feedName}"`);
    
    // Also refresh other data
    fetchMatrixData();
    fetchAggregationData();

    // Clear status after 5 seconds
    setTimeout(() => {
      setConsumptionStatus('');
    }, 5000);
  };
  
  const fetchTTPData = async (sortByField = null, sortOrderValue = null, pageNumber = null, pageSizeValue = null, filtersOverride = null) => {
    setLoading(true);
    try {
      // Use provided parameters or current state
      const currentSortBy = sortByField || sortBy;
      const currentSortOrder = sortOrderValue || sortOrder;
      const currentPageNumber = pageNumber || currentPage;
      const currentPageSize = pageSizeValue || pageSize;
      const currentFilters = filtersOverride || filters;
      
      // Build API URL with sorting, pagination, and filtering parameters
      const params = new URLSearchParams();
      params.append('sort_by', currentSortBy);
      params.append('sort_order', currentSortOrder);
      params.append('page', currentPageNumber.toString());
      params.append('page_size', currentPageSize.toString());
      
      // Add filtering parameters
      if (currentFilters.search && currentFilters.search.trim()) {
        params.append('search', currentFilters.search.trim());
      }
      if (currentFilters.tactics && currentFilters.tactics.length > 0) {
        params.append('tactics', currentFilters.tactics.join(','));
      }
      if (currentFilters.techniques && currentFilters.techniques.length > 0) {
        params.append('techniques', currentFilters.techniques.join(','));
      }
      if (currentFilters.severity_levels && currentFilters.severity_levels.length > 0) {
        params.append('severity_levels', currentFilters.severity_levels.join(','));
      }
      if (currentFilters.date_from && currentFilters.date_from.trim()) {
        params.append('created_after', currentFilters.date_from.trim());
      }
      if (currentFilters.date_to && currentFilters.date_to.trim()) {
        params.append('created_before', currentFilters.date_to.trim());
      }
      if (currentFilters.threat_feed_ids && currentFilters.threat_feed_ids.length > 0) {
        params.append('threat_feed_ids', currentFilters.threat_feed_ids.join(','));
      }
      if (currentFilters.anonymized_only && currentFilters.anonymized_only !== '') {
        params.append('anonymized_only', currentFilters.anonymized_only);
      }
      if (currentFilters.has_subtechniques && currentFilters.has_subtechniques !== '') {
        params.append('has_subtechniques', currentFilters.has_subtechniques);
      }
      
      const response = await api.get(`/api/ttps/?${params.toString()}`);
      if (response && response.success) {
        setTtpData(response.results || []);
        setTotalCount(response.count || 0);
        setTotalPages(response.num_pages || 0);
        setHasNext(response.has_next || false);
        setHasPrevious(response.has_previous || false);
      } else {
        setTtpData([]);
        setTotalCount(0);
        setTotalPages(0);
        setHasNext(false);
        setHasPrevious(false);
      }
    } catch (error) {
      console.error('Error fetching TTP data:', error);
      setTtpData([]);
      setTotalCount(0);
      setTotalPages(0);
      setHasNext(false);
      setHasPrevious(false);
    }
    setLoading(false);
  };

  // Fetch filter options for dropdowns
  const fetchFilterOptions = async () => {
    try {
      const response = await api.get('/api/ttps/filter-options/');
      if (response && response.success) {
        setFilterOptions(response.options);
      }
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
  };

  // Handle column sorting
  const handleSort = (column) => {
    let newSortOrder = 'asc';
    
    // If clicking the same column, toggle sort order
    if (sortBy === column) {
      newSortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
      // New column, default to descending for dates, ascending for others
      newSortOrder = (column === 'created_at' || column === 'updated_at') ? 'desc' : 'asc';
    }
    
    setSortBy(column);
    setSortOrder(newSortOrder);
    
    // Reset to first page when sorting changes
    setCurrentPage(1);
    
    // Fetch data with new sorting and reset pagination
    fetchTTPData(column, newSortOrder, 1, pageSize, filters);
  };

  // Get sort icon for column headers
  const getSortIcon = (column) => {
    if (sortBy !== column) {
      return <i className="fas fa-sort" style={{color: '#ccc', marginLeft: '5px'}}></i>;
    }
    
    const iconClass = sortOrder === 'asc' ? 'fa-sort-up' : 'fa-sort-down';
    return <i className={`fas ${iconClass}`} style={{color: '#0056b3', marginLeft: '5px'}}></i>;
  };

  // Handle pagination
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages && newPage !== currentPage) {
      setCurrentPage(newPage);
      fetchTTPData(sortBy, sortOrder, newPage, pageSize, filters);
    }
  };

  const handlePageSizeChange = (newPageSize) => {
    setPageSize(newPageSize);
    setCurrentPage(1); // Reset to first page when page size changes
    fetchTTPData(sortBy, sortOrder, 1, newPageSize, filters);
  };

  // Generate page numbers for pagination display
  const generatePageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    
    if (totalPages <= maxVisiblePages) {
      // Show all pages if total is small
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Show first, last, and pages around current
      const startPage = Math.max(1, currentPage - 2);
      const endPage = Math.min(totalPages, currentPage + 2);
      
      if (startPage > 1) {
        pages.push(1);
        if (startPage > 2) pages.push('...');
      }
      
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
      
      if (endPage < totalPages) {
        if (endPage < totalPages - 1) pages.push('...');
        pages.push(totalPages);
      }
    }
    
    return pages;
  };

  // Handle filter changes
  const handleFilterChange = (filterKey, value) => {
    const newFilters = { ...filters, [filterKey]: value };
    setFilters(newFilters);
    
    // Reset to first page when filters change
    setCurrentPage(1);
    
    // Count active filters
    const activeCount = countActiveFilters(newFilters);
    setActiveFiltersCount(activeCount);
    
    // For search, use debounced fetch; for others, fetch immediately
    if (filterKey === 'search') {
      debouncedFetchTTPData(sortBy, sortOrder, 1, pageSize, newFilters);
    } else {
      fetchTTPData(sortBy, sortOrder, 1, pageSize, newFilters);
    }
  };

  // Debounced search for better performance
  const debouncedFetchTTPData = useRef(
    debounce((sortBy, sortOrder, page, pageSize, filters) => {
      fetchTTPData(sortBy, sortOrder, page, pageSize, filters);
    }, 500)
  ).current;

  // Simple debounce utility
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // Handle multi-select filter changes (for arrays)
  const handleMultiSelectFilter = (filterKey, value, isChecked) => {
    const currentValues = filters[filterKey] || [];
    let newValues;
    
    if (isChecked) {
      newValues = [...currentValues, value];
    } else {
      newValues = currentValues.filter(v => v !== value);
    }
    
    handleFilterChange(filterKey, newValues);
  };

  // Count active filters
  const countActiveFilters = (filtersToCount) => {
    let count = 0;
    
    if (filtersToCount.search && filtersToCount.search.trim()) count++;
    if (filtersToCount.tactics && filtersToCount.tactics.length > 0) count++;
    if (filtersToCount.techniques && filtersToCount.techniques.length > 0) count++;
    if (filtersToCount.severity_levels && filtersToCount.severity_levels.length > 0) count++;
    if (filtersToCount.date_from && filtersToCount.date_from.trim()) count++;
    if (filtersToCount.date_to && filtersToCount.date_to.trim()) count++;
    if (filtersToCount.threat_feed_ids && filtersToCount.threat_feed_ids.length > 0) count++;
    if (filtersToCount.anonymized_only && filtersToCount.anonymized_only !== '') count++;
    if (filtersToCount.has_subtechniques && filtersToCount.has_subtechniques !== '') count++;
    
    return count;
  };

  // Clear all filters
  const clearAllFilters = () => {
    const clearedFilters = {
      search: '',
      tactics: [],
      techniques: [],
      severity_levels: [],
      date_from: '',
      date_to: '',
      threat_feed_ids: [],
      anonymized_only: '',
      has_subtechniques: ''
    };
    
    setFilters(clearedFilters);
    setActiveFiltersCount(0);
    setCurrentPage(1);
    
    // Fetch data without filters
    fetchTTPData(sortBy, sortOrder, 1, pageSize, clearedFilters);
  };

  const fetchTTPTrendsData = async () => {
    setTrendsLoading(true);
    try {
      // Get TTP trends data from the API
      const response = await api.get('/api/ttps/trends/?days=120&granularity=month&group_by=tactic');
      if (response && response.series) {
        setTrendsData(response.series);
      } else {
        setTrendsData([]);
      }
    } catch (error) {
      console.error('Error fetching TTP trends data:', error);
      setTrendsData([]);
    }
    setTrendsLoading(false);
  };

  const fetchMatrixData = async () => {
    setMatrixLoading(true);
    try {
      // Get MITRE matrix data from the API
      const response = await api.get('/api/ttps/mitre-matrix/');
      if (response && response.success) {
        setMatrixData(response);
      } else {
        setMatrixData(null);
      }
    } catch (error) {
      console.error('Error fetching MITRE matrix data:', error);
      setMatrixData(null);
    }
    setMatrixLoading(false);
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  // Matrix cell click handlers
  const handleMatrixCellClick = async (tactic, technique = null) => {
    setSelectedTactic(tactic);
    setSelectedTechnique(technique || '');
    setMatrixCellLoading(true);
    setShowMatrixCellModal(true);
    
    try {
      let url = `/api/ttps/matrix-cell-details/?tactic=${tactic}`;
      if (technique) {
        url += `&technique_id=${technique}`;
      }
      url += '&include_related=true&page_size=50';
      
      const response = await api.get(url);
      if (response && response.success) {
        setMatrixCellData(response);
      } else {
        setMatrixCellData(null);
      }
    } catch (error) {
      console.error('Error fetching matrix cell details:', error);
      setMatrixCellData(null);
    }
    
    setMatrixCellLoading(false);
  };

  const handleTechniqueClick = async (techniqueId) => {
    setSelectedTechniqueId(techniqueId);
    setTechniqueLoading(true);
    setShowTechniqueModal(true);
    
    try {
      const url = `/api/ttps/technique-details/${techniqueId}/`;
      const response = await api.get(url);
      if (response && response.success) {
        setTechniqueData(response);
      } else {
        setTechniqueData(null);
      }
    } catch (error) {
      console.error('Error fetching technique details:', error);
      setTechniqueData(null);
    }
    
    setTechniqueLoading(false);
  };

  const closeMatrixCellModal = () => {
    setShowMatrixCellModal(false);
    setMatrixCellData(null);
    setSelectedTactic('');
    setSelectedTechnique('');
  };

  const closeTechniqueModal = () => {
    setShowTechniqueModal(false);
    setTechniqueData(null);
    setSelectedTechniqueId('');
  };

  const refreshMatrixData = () => {
    fetchMatrixData();
  };

  // TTP Detail Modal functions
  const openTTPModal = async (ttpId) => {
    setShowTTPModal(true);
    setTtpDetailLoading(true);
    setIsEditMode(false);
    
    try {
      const response = await api.get(`/api/ttps/${ttpId}/`);
      if (response && response.success) {
        setSelectedTTP(response.ttp);
        setEditFormData({
          name: response.ttp.name || '',
          description: response.ttp.description || '',
          mitre_technique_id: response.ttp.mitre_technique_id || '',
          mitre_tactic: response.ttp.mitre_tactic || '',
          mitre_subtechnique: response.ttp.mitre_subtechnique || '',
          threat_feed_id: response.ttp.threat_feed?.id || ''
        });
      } else {
        console.error('Failed to fetch TTP details');
        setSelectedTTP(null);
      }
    } catch (error) {
      console.error('Error fetching TTP details:', error);
      setSelectedTTP(null);
    }
    setTtpDetailLoading(false);
  };

  const closeTTPModal = () => {
    setShowTTPModal(false);
    setSelectedTTP(null);
    setIsEditMode(false);
    setEditFormData({});
  };

  const toggleEditMode = () => {
    setIsEditMode(!isEditMode);
  };

  const handleEditFormChange = (field, value) => {
    setEditFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const saveTTPChanges = async () => {
    if (!selectedTTP) return;
    
    try {
      const response = await api.put(`/api/ttps/${selectedTTP.id}/`, editFormData);
      if (response && response.success) {
        // Update the TTP in local state
        setTtpData(prevData => 
          prevData.map(ttp => 
            ttp.id === selectedTTP.id 
              ? { ...ttp, ...editFormData }
              : ttp
          )
        );
        setSelectedTTP({ ...selectedTTP, ...editFormData });
        setIsEditMode(false);
        alert('TTP updated successfully');
        
        // Refresh trends data to reflect changes
        fetchTTPTrendsData();
      } else {
        alert('Failed to update TTP');
      }
    } catch (error) {
      console.error('Error updating TTP:', error);
      alert('Error updating TTP: ' + (error.message || 'Unknown error'));
    }
  };



  // Export Modal functions
  const openExportModal = () => {
    setShowExportModal(true);
    setExportError('');
  };

  const closeExportModal = () => {
    setShowExportModal(false);
    setExportError('');
  };

  const handleExportFilterChange = (field, value) => {
    setExportFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const downloadFile = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const exportTTPData = async () => {
    setIsExporting(true);
    setExportError('');
    
    try {
      // Build query parameters
      const params = new URLSearchParams();
      params.append('format', exportFormat);
      
      // Add filters if specified
      if (exportFilters.tactic) params.append('tactic', exportFilters.tactic);
      if (exportFilters.technique_id) params.append('technique_id', exportFilters.technique_id);
      if (exportFilters.feed_id) params.append('feed_id', exportFilters.feed_id);
      if (exportFilters.created_after) params.append('created_after', exportFilters.created_after);
      if (exportFilters.created_before) params.append('created_before', exportFilters.created_before);
      if (exportFilters.fields) params.append('fields', exportFilters.fields);
      
      params.append('include_anonymized', exportFilters.include_anonymized.toString());
      params.append('include_original', exportFilters.include_original.toString());
      params.append('limit', exportFilters.limit.toString());
      
      // Make the API request
      const response = await fetch(`/api/ttps/export/?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Accept': exportFormat === 'csv' ? 'text/csv' : 
                   exportFormat === 'stix' ? 'application/stix+json' : 
                   'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`Export failed: ${response.status} ${response.statusText}`);
      }
      
      // Get the blob and filename from response
      const blob = await response.blob();
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `ttps_export_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.${exportFormat}`;
      
      if (contentDisposition) {
        const matches = contentDisposition.match(/filename="([^"]+)"/);
        if (matches) {
          filename = matches[1];
        }
      }
      
      // Download the file
      downloadFile(blob, filename);
      
      // Close modal and show success message
      closeExportModal();
      alert(`Export completed successfully! Downloaded: ${filename}`);
      
    } catch (error) {
      console.error('Export failed:', error);
      setExportError('Export failed: ' + (error.message || 'Unknown error'));
    }
    
    setIsExporting(false);
  };

  const renderMatrixHeaders = () => {
    if (!matrixData || !matrixData.matrix) {
      return null;
    }

    // MITRE ATT&CK Enterprise tactics in order with display names
    const tacticOrder = [
      { code: 'initial-access', name: 'Initial Access' },
      { code: 'execution', name: 'Execution' },
      { code: 'persistence', name: 'Persistence' },
      { code: 'privilege-escalation', name: 'Privilege Escalation' },
      { code: 'defense-evasion', name: 'Defense Evasion' },
      { code: 'credential-access', name: 'Credential Access' },
      { code: 'discovery', name: 'Discovery' },
      { code: 'lateral-movement', name: 'Lateral Movement' },
      { code: 'collection', name: 'Collection' },
      { code: 'exfiltration', name: 'Exfiltration' },
      { code: 'impact', name: 'Impact' }
    ];

    return (
      <thead>
        <tr>
          {tacticOrder.map(tactic => {
            const tacticData = matrixData.matrix[tactic.code];
            const count = tacticData ? tacticData.technique_count : 0;
            return (
              <th 
                key={tactic.code} 
                title={`${count} techniques in ${tactic.name} - Click to view details`}
                onClick={() => count > 0 && handleMatrixCellClick(tactic.code)}
                style={{ 
                  cursor: count > 0 ? 'pointer' : 'default',
                  backgroundColor: count > 0 ? '#f8f9fa' : 'transparent',
                  transition: 'background-color 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  if (count > 0) {
                    e.target.style.backgroundColor = '#e9ecef';
                  }
                }}
                onMouseLeave={(e) => {
                  if (count > 0) {
                    e.target.style.backgroundColor = '#f8f9fa';
                  }
                }}
              >
                {tactic.name}
                <div className="tactic-count">({count})</div>
              </th>
            );
          })}
        </tr>
      </thead>
    );
  };

  const renderDynamicMatrix = () => {
    if (!matrixData || !matrixData.matrix) {
      return null;
    }

    const tactics = Object.values(matrixData.matrix);
    
    // MITRE ATT&CK Enterprise tactics in order
    const tacticOrder = [
      'initial-access',
      'execution', 
      'persistence',
      'privilege-escalation',
      'defense-evasion',
      'credential-access',
      'discovery',
      'lateral-movement',
      'collection',
      'exfiltration',
      'impact'
    ];

    // Create rows - we'll show up to 5 techniques per tactic
    const maxRows = 5;
    const rows = [];

    for (let rowIndex = 0; rowIndex < maxRows; rowIndex++) {
      const row = [];
      
      tacticOrder.forEach(tacticCode => {
        const tacticData = matrixData.matrix[tacticCode];
        if (tacticData && tacticData.techniques && tacticData.techniques.length > rowIndex) {
          const technique = tacticData.techniques[rowIndex];
          row.push({
            technique: technique,
            hasData: true,
            isActive: tacticData.technique_count > 0
          });
        } else {
          // Empty cell
          row.push({
            technique: null,
            hasData: false,
            isActive: false
          });
        }
      });
      
      // Only add row if it has at least one technique
      if (row.some(cell => cell.hasData)) {
        rows.push(row);
      }
    }

    return (
      <tbody>
        {rows.map((row, rowIndex) => (
          <tr key={rowIndex}>
            {row.map((cell, cellIndex) => {
              const tacticCode = tacticOrder[cellIndex];
              return (
                <td 
                  key={cellIndex} 
                  className={`matrix-cell ${cell.isActive ? 'active' : ''} ${cell.technique ? 'clickable' : ''}`}
                  title={cell.technique ? `${cell.technique.name} (${cell.technique.technique_id}) - Click to view details` : 'No techniques'}
                  onClick={() => {
                    if (cell.technique) {
                      handleTechniqueClick(cell.technique.technique_id);
                    } else if (cell.isActive && tacticCode) {
                      // Click on tactic column if no specific technique but tactic has data
                      handleMatrixCellClick(tacticCode);
                    }
                  }}
                  style={{
                    cursor: (cell.technique || cell.isActive) ? 'pointer' : 'default',
                    transition: 'all 0.2s ease',
                    position: 'relative'
                  }}
                  onMouseEnter={(e) => {
                    if (cell.technique || cell.isActive) {
                      e.target.style.transform = 'scale(1.02)';
                      e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                      e.target.style.zIndex = '1';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (cell.technique || cell.isActive) {
                      e.target.style.transform = 'scale(1)';
                      e.target.style.boxShadow = 'none';
                      e.target.style.zIndex = 'auto';
                    }
                  }}
                >
                  {cell.technique ? (
                    <>
                      <div className="technique-name">
                        {cell.technique.name.length > 20 
                          ? cell.technique.name.substring(0, 20) + '...'
                          : cell.technique.name
                        }
                      </div>
                      {cell.technique.technique_id && (
                        <div className="technique-id">{cell.technique.technique_id}</div>
                      )}
                    </>
                  ) : (
                    <div className="empty-cell">
                      {cell.isActive ? '🔍' : '-'}
                    </div>
                  )}
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    );
  };

  const transformTrendsDataForChart = (apiData) => {
    // Group data by date and aggregate by tactic
    const dateMap = new Map();
    
    // Process each series (tactic) from the API response
    apiData.forEach(series => {
      const tactic = series.group_name ? series.group_name.toLowerCase().replace(/\s+/g, '-') : 'unknown';
      
      // Process each data point in the series
      series.data_points.forEach(point => {
        const date = point.date;
        if (!dateMap.has(date)) {
          dateMap.set(date, {
            date: date,
            'initial-access': 0,
            'execution': 0,
            'persistence': 0,
            'defense-evasion': 0,
            'impact': 0,
            'privilege-escalation': 0,
            'discovery': 0,
            'lateral-movement': 0,
            'collection': 0,
            'command-and-control': 0,
            'exfiltration': 0
          });
        }
        
        const dateEntry = dateMap.get(date);
        if (dateEntry.hasOwnProperty(tactic)) {
          dateEntry[tactic] = point.count || 0;
        }
      });
    });
    
    // Convert to array and sort by date
    return Array.from(dateMap.values()).sort((a, b) => new Date(a.date) - new Date(b.date));
  };

  const deleteTTP = async (ttpId) => {
    if (!confirm('Are you sure you want to delete this TTP? This action cannot be undone.')) {
      return;
    }
    
    try {
      const response = await api.delete(`/api/ttps/${ttpId}/`);
      if (response && response.success) {
        // Remove the deleted TTP from the local state
        setTtpData(prevData => prevData.filter(ttp => ttp.id !== ttpId));
        alert('TTP deleted successfully');
        
        // Refresh trends data to reflect deletion
        fetchTTPTrendsData();
      } else {
        alert('Failed to delete TTP');
      }
    } catch (error) {
      console.error('Error deleting TTP:', error);
      alert('Error deleting TTP: ' + (error.message || 'Unknown error'));
    }
  };
  
  useEffect(() => {
    if (active && ttpChartRef.current && trendsData.length > 0) {
      createTTPTrendsChart();
    }
  }, [active, trendsData]);

  const createTTPTrendsChart = () => {
    try {
      // Clear previous chart if any
      if (ttpChartRef.current) {
        d3.select(ttpChartRef.current).selectAll("*").remove();
      }
      
      // Return early if no trends data or ref not available
      if (!trendsData || trendsData.length === 0 || !ttpChartRef.current) {
        return;
      }
      
      // Transform API data to chart format
      const data = transformTrendsDataForChart(trendsData);
      
      // Return early if transformed data is empty
      if (!data || data.length === 0) {
        console.warn('No chart data available after transformation');
        return;
      }

    // Set dimensions and margins for the chart
    const width = ttpChartRef.current.clientWidth;
    const height = 300;
    const margin = { top: 30, right: 120, bottom: 40, left: 50 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Create the SVG container
    const svg = d3.select(ttpChartRef.current)
      .append("svg")
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Set up scales
    const x = d3.scalePoint()
      .domain(data.map(d => d.date))
      .range([0, innerWidth])
      .padding(0.5);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => Math.max(...Object.keys(colors).map(tactic => d[tactic] || 0))) * 1.1])
      .range([innerHeight, 0]);

    // Define line generator
    const line = d3.line()
      .x(d => x(d.date))
      .y(d => y(d.value))
      .curve(d3.curveMonotoneX);

    // Define colors for different TTP categories (MITRE ATT&CK tactics)
    const colors = {
      'initial-access': "#0056b3",
      'execution': "#00a0e9", 
      'persistence': "#38a169",
      'defense-evasion': "#e53e3e",
      'impact': "#f6ad55",
      'privilege-escalation': "#805ad5",
      'discovery': "#ed8936",
      'lateral-movement': "#38b2ac",
      'collection': "#d53f8c",
      'command-and-control': "#319795",
      'exfiltration': "#dd6b20"
    };

    // Get only tactics that have data in the dataset
    const categories = Object.keys(colors).filter(tactic => 
      data.some(d => d[tactic] > 0)
    );
    
    const categoryLabels = {
      'initial-access': "Initial Access",
      'execution': "Execution",
      'persistence': "Persistence", 
      'defense-evasion': "Defense Evasion",
      'impact': "Impact",
      'privilege-escalation': "Privilege Escalation",
      'discovery': "Discovery",
      'lateral-movement': "Lateral Movement",
      'collection': "Collection",
      'command-and-control': "Command and Control",
      'exfiltration': "Exfiltration"
    };

    categories.forEach(category => {
      const categoryData = data.map(d => ({
        date: d.date,
        value: d[category]
      }));

      svg.append("path")
        .datum(categoryData)
        .attr("fill", "none")
        .attr("stroke", colors[category])
        .attr("stroke-width", 2)
        .attr("d", line);

      // Add dots
      svg.selectAll(`.dot-${category}`)
        .data(categoryData)
        .enter()
        .append("circle")
        .attr("class", `dot-${category}`)
        .attr("cx", d => x(d.date))
        .attr("cy", d => y(d.value))
        .attr("r", 4)
        .attr("fill", colors[category]);
    });

    // Add x-axis
    svg.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x).tickFormat(d => d));

    // Add y-axis
    svg.append("g")
      .call(d3.axisLeft(y));

    // Add title
    svg.append("text")
      .attr("x", innerWidth / 2)
      .attr("y", -10)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "600")
      .style("fill", "#2d3748")
      .text("TTP Trends Over Time");

    // Add legend
    const legend = svg.append("g")
      .attr("transform", `translate(${innerWidth + 10}, 0)`);

    categories.forEach((category, i) => {
      const legendRow = legend.append("g")
        .attr("transform", `translate(0, ${i * 20})`);
      
      legendRow.append("rect")
        .attr("width", 10)
        .attr("height", 10)
        .attr("fill", colors[category]);
      
      legendRow.append("text")
        .attr("x", 15)
        .attr("y", 10)
        .attr("text-anchor", "start")
        .style("font-size", "12px")
        .text(categoryLabels[category]);
    });
    } catch (error) {
      console.error('Error creating TTP trends chart:', error);
      // Display error message in the chart container
      if (ttpChartRef.current) {
        d3.select(ttpChartRef.current).selectAll("*").remove();
        d3.select(ttpChartRef.current)
          .append("div")
          .style("text-align", "center")
          .style("color", "#e53e3e")
          .style("padding", "20px")
          .text("Error loading chart data. Please try refreshing.");
      }
    }
  };

  return (
    <section id="ttp-analysis" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">TTP Analysis</h1>
          <p className="page-subtitle">Track and analyze tactics, techniques, and procedures from threat intelligence feeds</p>
        </div>
        <div className="action-buttons">
          <div className="feed-consumption-controls">
            <div className="feed-selection-wrapper">
              <select 
                value={selectedFeedForConsumption} 
                onChange={(e) => setSelectedFeedForConsumption(e.target.value)}
                className="form-control feed-selector"
                disabled={consumptionInProgress}
              >
                <option value="">Select Threat Feed to Analyze</option>
                {availableFeeds.length === 0 ? (
                  <option disabled>No threat feeds available</option>
                ) : (
                  availableFeeds.map(feed => (
                    <option key={feed.id} value={feed.id}>
                      {feed.name} - {feed.is_external ? 'External TAXII' : 'Internal'} 
                      {feed.is_active ? ' ✓' : ' (Inactive)'}
                      {feed.description ? ` - ${feed.description}` : ''}
                    </option>
                  ))
                )}
              </select>
              {selectedFeedForConsumption && (
                <div className="consumption-options">
                  <small className="consumption-info">
                    <i className="fas fa-info-circle"></i>
                    Will show TTPs from this feed
                  </small>
                </div>
              )}
            </div>
            <button 
              className="btn btn-primary consume-btn" 
              onClick={loadFeedTTPs}
              disabled={!selectedFeedForConsumption || consumptionInProgress}
              title={selectedFeedForConsumption ? 'Load TTPs from selected feed' : 'Select a feed first'}
            >
              {consumptionInProgress ? (
                <>
                  <i className="fas fa-spinner fa-spin"></i> Loading...
                </>
              ) : (
                <>
                  <i className="fas fa-download"></i> Load Feed TTPs
                </>
              )}
            </button>
          </div>
          <button className="btn btn-outline" onClick={openExportModal}>
            <i className="fas fa-upload"></i> Export Analysis
          </button>
        </div>
      </div>

      {consumptionStatus && (
        <div className={`alert ${consumptionStatus.includes('failed') ? 'alert-error' : 'alert-success'}`}>
          <i className={`fas ${consumptionStatus.includes('failed') ? 'fa-exclamation-triangle' : 'fa-check-circle'}`}></i>
          {consumptionStatus}
        </div>
      )}

      <div className="tabs">
        <div 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => handleTabChange('overview')}
        >
          Feed Overview
        </div>
        <div 
          className={`tab ${activeTab === 'matrix' ? 'active' : ''}`}
          onClick={() => handleTabChange('matrix')}
        >
          MITRE ATT&CK Matrix
        </div>
        <div 
          className={`tab ${activeTab === 'list' ? 'active' : ''}`}
          onClick={() => handleTabChange('list')}
        >
          TTP Intelligence
        </div>
        <div 
          className={`tab ${activeTab === 'trends' ? 'active' : ''}`}
          onClick={() => handleTabChange('trends')}
        >
          Trends & Patterns
        </div>
      </div>

      {/* Feed Overview Tab */}
      {activeTab === 'overview' && (
        <div className="feed-analysis-overview">
          <div className="overview-cards">
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">
                  <i className="fas fa-chart-bar card-icon"></i> 
                  Feed Comparison Statistics
                </h2>
                <button 
                  className="btn btn-outline btn-sm" 
                  onClick={fetchAggregationData}
                  disabled={aggregationLoading}
                >
                  <i className={`fas ${aggregationLoading ? 'fa-spinner fa-spin' : 'fa-sync-alt'}`}></i> Refresh
                </button>
              </div>
              <div className="card-content">
                {aggregationLoading ? (
                  <div className="loading-state">
                    <i className="fas fa-spinner fa-spin"></i>
                    <p>Loading feed comparison data...</p>
                  </div>
                ) : feedComparisonData ? (
                  <div className="feed-comparison-grid">
                    {feedComparisonData.feed_statistics && feedComparisonData.feed_statistics.map((feed, index) => (
                      <div key={index} className="feed-stat-card">
                        <div className="feed-name">{feed.threat_feed__name}</div>
                        <div className="feed-stats">
                          <div className="stat-item">
                            <span className="stat-value">{feed.ttp_count}</span>
                            <span className="stat-label">TTPs</span>
                          </div>
                          <div className="stat-item">
                            <span className="stat-value">{feed.unique_techniques}</span>
                            <span className="stat-label">Unique Techniques</span>
                          </div>
                          <div className="stat-item">
                            <span className="stat-value">{feed.avg_techniques_per_day}</span>
                            <span className="stat-label">Avg/Day</span>
                          </div>
                        </div>
                        <div className={`feed-type ${feed.threat_feed__is_external ? 'external' : 'internal'}`}>
                          {feed.threat_feed__is_external ? 'External Feed' : 'Internal Feed'}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    <i className="fas fa-chart-bar"></i>
                    <p>No feed comparison data available</p>
                    <p className="text-muted">Consume threat feeds to see comparison statistics</p>
                  </div>
                )}
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h2 className="card-title">
                  <i className="fas fa-fire card-icon"></i> 
                  Top Techniques
                </h2>
              </div>
              <div className="card-content">
                {frequencyData && frequencyData.techniques ? (
                  <div className="technique-frequency-list">
                    {Object.entries(frequencyData.techniques)
                      .sort(([,a], [,b]) => b.count - a.count)
                      .slice(0, 10)
                      .map(([techniqueId, data], index) => (
                        <div key={techniqueId} className="frequency-item">
                          <div className="technique-rank">#{data.rank}</div>
                          <div className="technique-details">
                            <div className="technique-id">{techniqueId}</div>
                            <div className="technique-stats">
                              <span className="count">{data.count} occurrences</span>
                              <span className="percentage">({data.percentage}%)</span>
                            </div>
                          </div>
                          <div className="frequency-bar">
                            <div 
                              className="frequency-fill" 
                              style={{width: `${Math.min(data.percentage * 2, 100)}%`}}
                            ></div>
                          </div>
                        </div>
                      ))
                    }
                  </div>
                ) : (
                  <div className="empty-state">
                    <i className="fas fa-fire"></i>
                    <p>No technique frequency data available</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title">
                <i className="fas fa-calendar-alt card-icon"></i> 
                Seasonal Patterns
              </h2>
            </div>
            <div className="card-content">
              {seasonalData && seasonalData.statistics ? (
                <div className="seasonal-analysis">
                  <div className="seasonal-stats">
                    <div className="stat-card">
                      <div className="stat-value">{seasonalData.statistics.seasonality_strength}</div>
                      <div className="stat-label">Seasonality Strength</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-value">{seasonalData.statistics.peak_period.label}</div>
                      <div className="stat-label">Peak Period</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-value">{seasonalData.statistics.valley_period.label}</div>
                      <div className="stat-label">Valley Period</div>
                    </div>
                  </div>
                  <div className="seasonal-interpretation">
                    <p>{seasonalData.interpretation}</p>
                  </div>
                </div>
              ) : (
                <div className="empty-state">
                  <i className="fas fa-calendar-alt"></i>
                  <p>No seasonal pattern data available</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* MITRE ATT&CK Matrix Tab */}
      {activeTab === 'matrix' && (
        <>
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-sitemap card-icon"></i> MITRE ATT&CK Enterprise Matrix</h2>
          <div className="card-actions">
            <button 
              className="btn btn-outline btn-sm" 
              onClick={refreshMatrixData} 
              disabled={matrixLoading}
              title="Refresh matrix data"
            >
              <i className={`fas ${matrixLoading ? 'fa-spinner fa-spin' : 'fa-sync-alt'}`}></i> Refresh
            </button>
            <button className="btn btn-outline btn-sm"><i className="fas fa-filter"></i> Filter</button>
          </div>
        </div>
        <div className="card-content">
          <div className="matrix-container">
            {matrixLoading ? (
              <div style={{textAlign: 'center', padding: '4rem'}}>
                <i className="fas fa-spinner fa-spin" style={{fontSize: '2rem', color: '#0056b3'}}></i>
                <p style={{marginTop: '1rem', color: '#666'}}>Loading MITRE ATT&CK Matrix...</p>
              </div>
            ) : matrixData ? (
              <>
                <table className="mitre-matrix">
                  {renderMatrixHeaders()}
                  {renderDynamicMatrix()}
                </table>
                {matrixData.statistics && (
                  <div className="matrix-stats" style={{marginTop: '1rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px'}}>
                    <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem'}}>
                      <div>
                        <strong>Total Techniques:</strong> {matrixData.total_techniques}
                      </div>
                      <div>
                        <strong>Active Tactics:</strong> {matrixData.statistics.tactics_with_techniques}
                      </div>
                      <div>
                        <strong>Avg per Tactic:</strong> {matrixData.statistics.average_techniques_per_tactic}
                      </div>
                      {matrixData.statistics.most_common_tactic && (
                        <div>
                          <strong>Top Tactic:</strong> {matrixData.matrix[matrixData.statistics.most_common_tactic]?.tactic_name}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div style={{textAlign: 'center', padding: '4rem'}}>
                <i className="fas fa-sitemap" style={{fontSize: '3rem', color: '#ccc'}}></i>
                <p style={{marginTop: '1rem', color: '#666'}}>No MITRE ATT&CK data available</p>
                <p style={{color: '#888', fontSize: '0.9rem'}}>Matrix will populate as TTP data becomes available</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h2 className="card-title"><i className="fas fa-chart-line card-icon"></i> TTP Trends</h2>
          <div className="card-actions">
            <button className="btn btn-outline btn-sm"><i className="fas fa-calendar-alt"></i> Last 90 Days</button>
          </div>
        </div>
        <div className="card-content">
          <div className="chart-container" ref={ttpChartRef}>
            {trendsLoading ? (
              <div style={{textAlign: 'center', padding: '4rem'}}>
                <i className="fas fa-spinner fa-spin" style={{fontSize: '2rem', color: '#0056b3'}}></i>
                <p style={{marginTop: '1rem', color: '#666'}}>Loading TTP trends data...</p>
              </div>
            ) : trendsData.length === 0 ? (
              <div style={{textAlign: 'center', padding: '4rem'}}>
                <i className="fas fa-chart-line" style={{fontSize: '2rem', color: '#ccc'}}></i>
                <p style={{marginTop: '1rem', color: '#666'}}>No TTP trends data available</p>
                <p style={{color: '#888', fontSize: '0.9rem'}}>TTP data will appear here as it becomes available</p>
              </div>
            ) : null}
          </div>
        </div>
      </div>
        </>
      )}

      {/* TTP List Tab */}
      {activeTab === 'list' && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title"><i className="fas fa-shield-alt card-icon"></i> TTP Intelligence from Threat Feeds</h2>
            <div className="card-actions">
              <button 
                className="btn btn-outline btn-sm" 
                onClick={() => setShowFilters(!showFilters)}
              >
                <i className="fas fa-filter"></i> Filter
                {activeFiltersCount > 0 && (
                  <span className="filter-count">{activeFiltersCount}</span>
                )}
              </button>
              <button className="btn btn-outline btn-sm" onClick={openExportModal}>
                <i className="fas fa-download"></i> Export
              </button>
            </div>
          </div>
          
          <div className="intelligence-summary" style={{padding: '1rem', backgroundColor: '#f8f9fa', borderBottom: '1px solid #dee2e6'}}>
            <div className="summary-stats">
              <div className="stat-item">
                <i className="fas fa-database"></i>
                <span>{totalCount} TTPs from threat intelligence feeds</span>
              </div>
              <div className="stat-item">
                <i className="fas fa-rss"></i>
                <span>{availableFeeds.length} connected threat feeds</span>
              </div>
              <div className="stat-item">
                <i className="fas fa-shield-alt"></i>
                <span>Automatically mapped to MITRE ATT&CK</span>
              </div>
            </div>
          </div>
          
          <div className="card-content">
            <table className="data-table">
              <thead>
                <tr>
                  <th onClick={() => handleSort('id')} style={{cursor: 'pointer'}}>
                    ID {getSortIcon('id')}
                  </th>
                  <th onClick={() => handleSort('name')} style={{cursor: 'pointer'}}>
                    TTP Name {getSortIcon('name')}
                  </th>
                  <th onClick={() => handleSort('mitre_technique_id')} style={{cursor: 'pointer'}}>
                    MITRE Technique {getSortIcon('mitre_technique_id')}
                  </th>
                  <th onClick={() => handleSort('mitre_tactic')} style={{cursor: 'pointer'}}>
                    Tactic {getSortIcon('mitre_tactic')}
                  </th>
                  <th>Source Feed</th>
                  <th>Intelligence Status</th>
                  <th onClick={() => handleSort('created_at')} style={{cursor: 'pointer'}}>
                    Discovered {getSortIcon('created_at')}
                  </th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="8" style={{textAlign: 'center', padding: '2rem'}}>
                      <i className="fas fa-spinner fa-spin"></i> Loading threat intelligence...
                    </td>
                  </tr>
                ) : ttpData.length > 0 ? (
                  ttpData.map((ttp) => (
                    <tr key={ttp.id}>
                      <td>{ttp.id}</td>
                      <td>
                        <div className="ttp-name-cell">
                          <div className="ttp-title">{ttp.name}</div>
                          {ttp.mitre_subtechnique && (
                            <div className="ttp-subtechnique">{ttp.mitre_subtechnique}</div>
                          )}
                        </div>
                      </td>
                      <td>
                        <span className="technique-badge">{ttp.mitre_technique_id}</span>
                      </td>
                      <td>
                        <span className="tactic-badge">{ttp.mitre_tactic_display || ttp.mitre_tactic}</span>
                      </td>
                      <td>
                        {ttp.threat_feed ? (
                          <div className="feed-source-cell">
                            <span className="feed-name">{ttp.threat_feed.name}</span>
                            <span className={`feed-type ${ttp.threat_feed.is_external ? 'external' : 'internal'}`}>
                              {ttp.threat_feed.is_external ? 'External' : 'Internal'}
                            </span>
                          </div>
                        ) : (
                          <span className="text-muted">No Feed</span>
                        )}
                      </td>
                      <td>
                        <div className="intelligence-status">
                          {ttp.is_anonymized ? (
                            <span className="status-badge anonymized">
                              <i className="fas fa-mask"></i> Anonymized
                            </span>
                          ) : (
                            <span className="status-badge raw">
                              <i className="fas fa-eye"></i> Raw Intel
                            </span>
                          )}
                        </div>
                      </td>
                      <td>{ttp.created_at ? new Date(ttp.created_at).toLocaleDateString() : 'Unknown'}</td>
                      <td>
                        <button 
                          className="btn btn-outline btn-sm" 
                          onClick={() => openTTPModal(ttp.id)}
                          title="View Intelligence Details"
                          style={{marginRight: '5px'}}
                        >
                          <i className="fas fa-search"></i>
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="8" style={{textAlign: 'center', padding: '2rem'}}>
                      <div className="empty-state">
                        <i className="fas fa-shield-alt"></i>
                        <p>No TTP intelligence available</p>
                        <p className="text-muted">
                          Consume threat feeds to populate TTP intelligence data
                        </p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          
          {/* TTP Pagination Controls */}
          {(totalPages > 0 || loading) && (
            <div className="pagination-wrapper" style={{marginTop: '1.5rem'}}>
              <div className="pagination-info-detailed">
                <span className="pagination-summary">
                  {loading ? (
                    <>
                      <i className="fas fa-spinner fa-spin" style={{marginRight: '5px'}}></i>
                      Loading TTPs...
                    </>
                  ) : (
                    <>
                      Showing <strong>{Math.min((currentPage - 1) * pageSize + 1, totalCount)}</strong> to <strong>{Math.min(currentPage * pageSize, totalCount)}</strong> of <strong>{totalCount}</strong> TTPs
                    </>
                  )}
                </span>
              </div>
              
              {totalPages > 1 && (
                <div className="pagination-controls-enhanced">
                  {/* Page Size Selector */}
                  <div className="items-per-page-selector" style={{marginRight: '1rem'}}>
                    <label htmlFor="ttp-page-size" style={{fontSize: '0.85rem', marginRight: '0.5rem'}}>
                      Items per page:
                    </label>
                    <select
                      id="ttp-page-size"
                      className="form-control-sm"
                      value={pageSize}
                      onChange={(e) => handlePageSizeChange(parseInt(e.target.value))}
                      style={{minWidth: '70px'}}
                      disabled={loading}
                    >
                      <option value={10}>10</option>
                      <option value={20}>20</option>
                      <option value={50}>50</option>
                      <option value={100}>100</option>
                    </select>
                  </div>

                  {/* Previous Button */}
                  <button
                    className={`btn btn-outline btn-sm ${!hasPrevious || loading ? 'disabled' : ''}`}
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={!hasPrevious || loading}
                    style={{marginRight: '0.25rem'}}
                  >
                    <i className="fas fa-chevron-left"></i>
                  </button>

                  {/* Page Numbers */}
                  <div className="pagination-pages">
                    {generatePageNumbers().map((page, index) => (
                      page === '...' ? (
                        <span key={`ellipsis-${index}`} className="pagination-ellipsis">...</span>
                      ) : (
                        <button
                          key={page}
                          className={`btn btn-sm ${page === currentPage ? 'btn-primary' : 'btn-outline'}`}
                          onClick={() => handlePageChange(page)}
                          disabled={loading}
                        >
                          {page}
                        </button>
                      )
                    ))}
                  </div>

                  {/* Next Button */}
                  <button
                    className={`btn btn-outline btn-sm ${!hasNext || loading ? 'disabled' : ''}`}
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={!hasNext || loading}
                    style={{marginLeft: '0.25rem'}}
                  >
                    <i className="fas fa-chevron-right"></i>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* TTP Trends Chart (shared across relevant tabs) */}
      {(activeTab === 'matrix' || activeTab === 'list') && (
        <div className="card mt-4">
          <div className="card-header">
            <h2 className="card-title"><i className="fas fa-chart-line card-icon"></i> TTP Trends Chart</h2>
            <div className="card-actions">
              <button className="btn btn-outline btn-sm"><i className="fas fa-calendar-alt"></i> Last 90 Days</button>
            </div>
          </div>
          <div className="card-content">
            <div className="chart-container" ref={ttpChartRef}>
              {trendsLoading ? (
                <div style={{textAlign: 'center', padding: '4rem'}}>
                  <i className="fas fa-spinner fa-spin" style={{fontSize: '2rem', color: '#0056b3'}}></i>
                  <p style={{marginTop: '1rem', color: '#666'}}>Loading TTP trends data...</p>
                </div>
              ) : trendsData.length === 0 ? (
                <div style={{textAlign: 'center', padding: '4rem'}}>
                  <i className="fas fa-chart-line" style={{fontSize: '2rem', color: '#ccc'}}></i>
                  <p style={{marginTop: '1rem', color: '#666'}}>No TTP trends data available</p>
                  <p style={{color: '#888', fontSize: '0.9rem'}}>TTP data will appear here as it becomes available</p>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      )}

      {/* Threat Actors Tab */}
      {activeTab === 'trends' && (
        <div className="trends-analysis">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-chart-line card-icon"></i> TTP Trends & Patterns</h2>
              <div className="card-actions">
                <select className="form-control" style={{width: 'auto', marginRight: '10px'}}>
                  <option value="30">Last 30 Days</option>
                  <option value="90">Last 90 Days</option>
                  <option value="180">Last 6 Months</option>
                  <option value="365">Last Year</option>
                </select>
                <button 
                  className="btn btn-outline btn-sm"
                  onClick={fetchAggregationData}
                  disabled={aggregationLoading}
                >
                  <i className={`fas ${aggregationLoading ? 'fa-spinner fa-spin' : 'fa-sync-alt'}`}></i> Refresh
                </button>
              </div>
            </div>
            <div className="card-content">
              {aggregationLoading ? (
                <div className="loading-state">
                  <i className="fas fa-spinner fa-spin"></i>
                  <p>Loading trends analysis...</p>
                </div>
              ) : (
                <div className="trends-content">
                  <div className="trend-charts-grid">
                    <div className="chart-container">
                      <h3>Technique Frequency Over Time</h3>
                      <div 
                        className="trend-chart" 
                        ref={ttpChartRef}
                        style={{minHeight: '300px', width: '100%'}}
                      >
                        {/* D3.js Trend Chart will be rendered here */}
                      </div>
                    </div>
                    
                    <div className="tactic-distribution">
                      <h3>Tactic Distribution</h3>
                      {frequencyData && frequencyData.tactics ? (
                        <div className="tactic-bars">
                          {Object.entries(frequencyData.tactics)
                            .sort(([,a], [,b]) => b.count - a.count)
                            .slice(0, 8)
                            .map(([tacticId, data]) => (
                              <div key={tacticId} className="tactic-bar-item">
                                <div className="tactic-label">{tacticId.replace('-', ' ')}</div>
                                <div className="bar-container">
                                  <div 
                                    className="bar-fill"
                                    style={{width: `${data.percentage}%`}}
                                  ></div>
                                </div>
                                <div className="bar-value">{data.count}</div>
                              </div>
                            ))
                          }
                        </div>
                      ) : (
                        <div className="empty-state">
                          <p>No tactic distribution data available</p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="trend-insights">
                    <h3>Key Insights</h3>
                    <div className="insights-grid">
                      <div className="insight-card">
                        <i className="fas fa-trending-up"></i>
                        <div>
                          <h4>Emerging Techniques</h4>
                          <p>New techniques appearing in recent threat intelligence</p>
                        </div>
                      </div>
                      <div className="insight-card">
                        <i className="fas fa-clock"></i>
                        <div>
                          <h4>Seasonal Patterns</h4>
                          <p>{seasonalData && seasonalData.interpretation ? 
                            seasonalData.interpretation : 
                            'Analyzing temporal patterns in TTP usage'
                          }</p>
                        </div>
                      </div>
                      <div className="insight-card">
                        <i className="fas fa-exclamation-triangle"></i>
                        <div>
                          <h4>High-Frequency TTPs</h4>
                          <p>Most commonly observed techniques across all feeds</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Recent TTP Analyses (only shown on matrix and list tabs) */}
      {(activeTab === 'matrix' || activeTab === 'list') && (
        <div className="card mt-4">
          <div className="card-header">
            <div className="filters-header">
              <h2 className="card-title"><i className="fas fa-tasks card-icon"></i> Recent TTP Analyses</h2>
              <div className="filter-actions">
                {loading && (
                  <span style={{fontSize: '0.85rem', color: '#6c757d'}}>
                    <i className="fas fa-spinner fa-spin" style={{marginRight: '5px'}}></i>
                    Filtering...
                  </span>
                )}
                {activeFiltersCount > 0 && (
                  <span className="filtered-count">
                    {activeFiltersCount} filter{activeFiltersCount !== 1 ? 's' : ''} applied
                  </span>
                )}
                <button 
                  className={`btn btn-outline btn-sm ${showFilters ? 'active' : ''}`}
                  onClick={() => setShowFilters(!showFilters)}
                  disabled={loading}
                >
                  <i className="fas fa-filter"></i> Filters
                </button>
                {activeFiltersCount > 0 && (
                  <button 
                    className="btn btn-outline btn-sm text-danger"
                    onClick={clearAllFilters}
                    title="Clear all filters"
                  >
                    <i className="fas fa-times"></i> Clear
                  </button>
                )}
              </div>
            </div>
        </div>

          {/* Filter Panel */}
          {showFilters && (
            <div className="filters-panel" style={{borderBottom: '1px solid #e9ecef', padding: '1.5rem', background: '#f8f9fa'}}>
              <div className="filters-grid" style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem'}}>
                
                {/* Search Filter */}
                <div className="filter-group">
                  <label className="filter-label">
                    <i className="fas fa-search" style={{marginRight: '5px'}}></i> Search
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Search TTPs, techniques, descriptions..."
                    value={filters.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        // Force immediate search on Enter key
                        e.preventDefault();
                        fetchTTPData(sortBy, sortOrder, 1, pageSize, filters);
                      }
                    }}
                    disabled={loading}
                  />
                </div>

                {/* Tactic Filter */}
                <div className="filter-group">
                  <label className="filter-label">
                    <i className="fas fa-crosshairs" style={{marginRight: '5px'}}></i> MITRE Tactics
                  </label>
                  <select 
                    className="form-control"
                    multiple 
                    size="4"
                    value={filters.tactics}
                    onChange={(e) => {
                      const values = Array.from(e.target.selectedOptions, option => option.value);
                      handleFilterChange('tactics', values);
                    }}
                    style={{fontSize: '0.85rem'}}
                    disabled={loading}
                  >
                    {filterOptions?.tactics?.map(tactic => (
                      <option key={tactic.value} value={tactic.value}>
                        {tactic.label} ({tactic.count || 0})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Severity Filter */}
                <div className="filter-group">
                  <label className="filter-label">
                    <i className="fas fa-exclamation-triangle" style={{marginRight: '5px'}}></i> Severity Levels
                  </label>
                  <div className="checkbox-group" style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem'}}>
                    {['critical', 'high', 'medium', 'low'].map(severity => (
                      <label key={severity} className="checkbox-item" style={{display: 'flex', alignItems: 'center', fontSize: '0.85rem'}}>
                        <input
                          type="checkbox"
                          checked={filters.severity_levels.includes(severity)}
                          onChange={(e) => handleMultiSelectFilter('severity_levels', severity, e.target.checked)}
                          style={{marginRight: '5px'}}
                          disabled={loading}
                        />
                        <span className={`severity-badge severity-${severity}`} style={{
                          padding: '2px 8px', 
                          borderRadius: '12px', 
                          fontSize: '0.75rem',
                          fontWeight: '500',
                          textTransform: 'capitalize'
                        }}>
                          {severity}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Date Range Filter */}
                <div className="filter-group">
                  <label className="filter-label">
                    <i className="fas fa-calendar-alt" style={{marginRight: '5px'}}></i> Date Range
                  </label>
                  <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem'}}>
                    <input
                      type="date"
                      className="form-control"
                      value={filters.date_from}
                      onChange={(e) => handleFilterChange('date_from', e.target.value)}
                      placeholder="From"
                      title="From date"
                      disabled={loading}
                    />
                    <input
                      type="date"
                      className="form-control"
                      value={filters.date_to}
                      onChange={(e) => handleFilterChange('date_to', e.target.value)}
                      placeholder="To"
                      title="To date"
                      disabled={loading}
                    />
                  </div>
                </div>

                {/* Threat Feed Filter */}
                <div className="filter-group">
                  <label className="filter-label">
                    <i className="fas fa-rss" style={{marginRight: '5px'}}></i> Threat Feeds
                  </label>
                  <select 
                    className="form-control"
                    multiple 
                    size="3"
                    value={filters.threat_feed_ids}
                    onChange={(e) => {
                      const values = Array.from(e.target.selectedOptions, option => option.value);
                      handleFilterChange('threat_feed_ids', values);
                    }}
                    style={{fontSize: '0.85rem'}}
                  >
                    {filterOptions?.threat_feeds?.map(feed => (
                      <option key={feed.id} value={feed.id.toString()}>
                        {feed.name} ({feed.ttp_count || 0})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Status Filters */}
                <div className="filter-group">
                  <label className="filter-label">
                    <i className="fas fa-toggle-on" style={{marginRight: '5px'}}></i> Status Filters
                  </label>
                  <div style={{display: 'grid', gap: '0.5rem'}}>
                    <select
                      className="form-control"
                      value={filters.anonymized_only}
                      onChange={(e) => handleFilterChange('anonymized_only', e.target.value)}
                      style={{fontSize: '0.85rem'}}
                    >
                      <option value="">All TTPs</option>
                      <option value="true">Anonymized Only</option>
                      <option value="false">Active Only</option>
                    </select>
                    <select
                      className="form-control"
                      value={filters.has_subtechniques}
                      onChange={(e) => handleFilterChange('has_subtechniques', e.target.value)}
                      style={{fontSize: '0.85rem'}}
                    >
                      <option value="">All Techniques</option>
                      <option value="true">With Sub-techniques</option>
                      <option value="false">Without Sub-techniques</option>
                    </select>
                  </div>
                </div>

              </div>
            </div>
          )}

          {/* Active Filters Summary */}
          {activeFiltersCount > 0 && (
            <div className="active-filters-summary" style={{padding: '1rem', borderBottom: '1px solid #e9ecef', background: '#fff'}}>
              <div style={{display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem'}}>
                <span style={{fontSize: '0.875rem', fontWeight: '600', color: '#495057'}}>
                  Active Filters:
                </span>
                
                {filters.search && (
                  <span className="filter-badge" style={{
                    background: '#e3f2fd', 
                    color: '#1976d2', 
                    padding: '2px 8px', 
                    borderRadius: '12px', 
                    fontSize: '0.75rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    Search: "{filters.search}"
                    <button 
                      onClick={() => handleFilterChange('search', '')}
                      style={{
                        background: 'none', 
                        border: 'none', 
                        color: '#1976d2', 
                        cursor: 'pointer', 
                        padding: '0',
                        fontSize: '0.75rem'
                      }}
                    >
                      ×
                    </button>
                  </span>
                )}
                
                {filters.tactics.length > 0 && (
                  <span className="filter-badge" style={{
                    background: '#f3e5f5', 
                    color: '#7b1fa2', 
                    padding: '2px 8px', 
                    borderRadius: '12px', 
                    fontSize: '0.75rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    {filters.tactics.length} Tactic{filters.tactics.length !== 1 ? 's' : ''}
                    <button 
                      onClick={() => handleFilterChange('tactics', [])}
                      style={{
                        background: 'none', 
                        border: 'none', 
                        color: '#7b1fa2', 
                        cursor: 'pointer', 
                        padding: '0',
                        fontSize: '0.75rem'
                      }}
                    >
                      ×
                    </button>
                  </span>
                )}
                
                {filters.severity_levels.length > 0 && (
                  <span className="filter-badge" style={{
                    background: '#ffebee', 
                    color: '#c62828', 
                    padding: '2px 8px', 
                    borderRadius: '12px', 
                    fontSize: '0.75rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    {filters.severity_levels.length} Severity Level{filters.severity_levels.length !== 1 ? 's' : ''}
                    <button 
                      onClick={() => handleFilterChange('severity_levels', [])}
                      style={{
                        background: 'none', 
                        border: 'none', 
                        color: '#c62828', 
                        cursor: 'pointer', 
                        padding: '0',
                        fontSize: '0.75rem'
                      }}
                    >
                      ×
                    </button>
                  </span>
                )}
                
                {(filters.date_from || filters.date_to) && (
                  <span className="filter-badge" style={{
                    background: '#e8f5e8', 
                    color: '#2e7d32', 
                    padding: '2px 8px', 
                    borderRadius: '12px', 
                    fontSize: '0.75rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    Date Range
                    <button 
                      onClick={() => {
                        const clearedFilters = { ...filters, date_from: '', date_to: '' };
                        setFilters(clearedFilters);
                        setCurrentPage(1);
                        const activeCount = countActiveFilters(clearedFilters);
                        setActiveFiltersCount(activeCount);
                        fetchTTPData(sortBy, sortOrder, 1, pageSize, clearedFilters);
                      }}
                      style={{
                        background: 'none', 
                        border: 'none', 
                        color: '#2e7d32', 
                        cursor: 'pointer', 
                        padding: '0',
                        fontSize: '0.75rem'
                      }}
                    >
                      ×
                    </button>
                  </span>
                )}
                
                {filters.threat_feed_ids.length > 0 && (
                  <span className="filter-badge" style={{
                    background: '#fff3e0', 
                    color: '#ef6c00', 
                    padding: '2px 8px', 
                    borderRadius: '12px', 
                    fontSize: '0.75rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    {filters.threat_feed_ids.length} Feed{filters.threat_feed_ids.length !== 1 ? 's' : ''}
                    <button 
                      onClick={() => handleFilterChange('threat_feed_ids', [])}
                      style={{
                        background: 'none', 
                        border: 'none', 
                        color: '#ef6c00', 
                        cursor: 'pointer', 
                        padding: '0',
                        fontSize: '0.75rem'
                      }}
                    >
                      ×
                    </button>
                  </span>
                )}
              </div>
            </div>
          )}

        <div className="card-content">
          <table className="data-table">
            <thead>
              <tr>
                <th 
                  className="sortable-header"
                  onClick={() => handleSort('id')}
                  style={{cursor: 'pointer', userSelect: 'none'}}
                >
                  ID
                  {getSortIcon('id')}
                </th>
                <th 
                  className="sortable-header"
                  onClick={() => handleSort('name')}
                  style={{cursor: 'pointer', userSelect: 'none'}}
                >
                  Name
                  {getSortIcon('name')}
                </th>
                <th 
                  className="sortable-header"
                  onClick={() => handleSort('mitre_technique_id')}
                  style={{cursor: 'pointer', userSelect: 'none'}}
                >
                  MITRE Technique
                  {getSortIcon('mitre_technique_id')}
                </th>
                <th 
                  className="sortable-header"
                  onClick={() => handleSort('mitre_tactic')}
                  style={{cursor: 'pointer', userSelect: 'none'}}
                >
                  Tactic
                  {getSortIcon('mitre_tactic')}
                </th>
                <th>Threat Feed</th>
                <th 
                  className="sortable-header"
                  onClick={() => handleSort('created_at')}
                  style={{cursor: 'pointer', userSelect: 'none'}}
                >
                  Created
                  {getSortIcon('created_at')}
                </th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="8" style={{textAlign: 'center', padding: '2rem'}}>
                    <i className="fas fa-spinner fa-spin"></i> Loading TTPs...
                  </td>
                </tr>
              ) : ttpData.length > 0 ? (
                ttpData.map((ttp) => (
                  <tr key={ttp.id}>
                    <td>{ttp.id}</td>
                    <td>{ttp.name}</td>
                    <td>{ttp.mitre_technique_id}</td>
                    <td>{ttp.mitre_tactic_display || ttp.mitre_tactic}</td>
                    <td>{ttp.threat_feed ? ttp.threat_feed.name : 'N/A'}</td>
                    <td>{new Date(ttp.created_at).toLocaleDateString()}</td>
                    <td>
                      <span className={`badge ${ttp.is_anonymized ? 'badge-info' : 'badge-success'}`}>
                        {ttp.is_anonymized ? 'Anonymized' : 'Active'}
                      </span>
                    </td>
                    <td>
                      <button 
                        className="btn btn-outline btn-sm" 
                        title="View TTP Details"
                        onClick={() => openTTPModal(ttp.id)}
                        style={{marginRight: '5px'}}
                      >
                        <i className="fas fa-eye"></i>
                      </button>
                      <button className="btn btn-outline btn-sm" title="Share" style={{marginRight: '5px'}}>
                        <i className="fas fa-share-alt"></i>
                      </button>
                      <button 
                        className="btn btn-outline btn-sm text-danger" 
                        title="Delete TTP"
                        onClick={() => deleteTTP(ttp.id)}
                      >
                        <i className="fas fa-trash"></i>
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" style={{textAlign: 'center', padding: '2rem'}}>
                    No TTPs found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        </div>
      )}

      {/* TTP Detail Modal */}
      {showTTPModal && (
        <div className="modal-overlay" onClick={closeTTPModal}>
          <div className="modal-content ttp-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                <i className="fas fa-crosshairs"></i> 
                {isEditMode ? 'Edit TTP Details' : 'TTP Details'}
              </h2>
              <button className="modal-close" onClick={closeTTPModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <div className="modal-body">
              {ttpDetailLoading ? (
                <div style={{textAlign: 'center', padding: '3rem'}}>
                  <i className="fas fa-spinner fa-spin" style={{fontSize: '2rem', color: '#0056b3'}}></i>
                  <p style={{marginTop: '1rem', color: '#666'}}>Loading TTP details...</p>
                </div>
              ) : selectedTTP ? (
                <div className="ttp-detail-content">
                  {/* TTP Header Info */}
                  <div className="ttp-header-section">
                    <div className="ttp-title-section">
                      {isEditMode ? (
                        <input
                          type="text"
                          className="form-control ttp-name-input"
                          value={editFormData.name}
                          onChange={(e) => handleEditFormChange('name', e.target.value)}
                          placeholder="TTP Name"
                        />
                      ) : (
                        <h3 className="ttp-title">{selectedTTP.name}</h3>
                      )}
                      
                      <div className="ttp-badges">
                        <span className="badge badge-primary">
                          {selectedTTP.mitre_technique_id || 'No MITRE ID'}
                        </span>
                        <span className="badge badge-secondary">
                          {selectedTTP.mitre_tactic_display || selectedTTP.mitre_tactic || 'No Tactic'}
                        </span>
                        {selectedTTP.is_anonymized && (
                          <span className="badge badge-info">Anonymized</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* TTP Details Grid */}
                  <div className="ttp-details-grid">
                    <div className="detail-section">
                      <h4><i className="fas fa-info-circle"></i> Basic Information</h4>
                      <div className="detail-row">
                        <label>Description:</label>
                        <div className="detail-value">
                          {isEditMode ? (
                            <textarea
                              className="form-control"
                              value={editFormData.description}
                              onChange={(e) => handleEditFormChange('description', e.target.value)}
                              placeholder="TTP Description"
                              rows="4"
                            />
                          ) : (
                            <p>{selectedTTP.description || 'No description available'}</p>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="detail-section">
                      <h4><i className="fas fa-crosshairs"></i> MITRE ATT&CK Mapping</h4>
                      <div className="detail-row">
                        <label>Technique ID:</label>
                        <div className="detail-value">
                          {isEditMode ? (
                            <input
                              type="text"
                              className="form-control"
                              value={editFormData.mitre_technique_id}
                              onChange={(e) => handleEditFormChange('mitre_technique_id', e.target.value)}
                              placeholder="e.g., T1566.001"
                            />
                          ) : (
                            <span className="technique-id-display">
                              {selectedTTP.mitre_technique_id || 'Not specified'}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="detail-row">
                        <label>Tactic:</label>
                        <div className="detail-value">
                          {isEditMode ? (
                            <select
                              className="form-control"
                              value={editFormData.mitre_tactic}
                              onChange={(e) => handleEditFormChange('mitre_tactic', e.target.value)}
                            >
                              <option value="">Select Tactic</option>
                              <option value="initial-access">Initial Access</option>
                              <option value="execution">Execution</option>
                              <option value="persistence">Persistence</option>
                              <option value="privilege-escalation">Privilege Escalation</option>
                              <option value="defense-evasion">Defense Evasion</option>
                              <option value="credential-access">Credential Access</option>
                              <option value="discovery">Discovery</option>
                              <option value="lateral-movement">Lateral Movement</option>
                              <option value="collection">Collection</option>
                              <option value="command-and-control">Command and Control</option>
                              <option value="exfiltration">Exfiltration</option>
                              <option value="impact">Impact</option>
                            </select>
                          ) : (
                            <span>{selectedTTP.mitre_tactic_display || selectedTTP.mitre_tactic || 'Not specified'}</span>
                          )}
                        </div>
                      </div>
                      {(selectedTTP.mitre_subtechnique || isEditMode) && (
                        <div className="detail-row">
                          <label>Sub-technique:</label>
                          <div className="detail-value">
                            {isEditMode ? (
                              <input
                                type="text"
                                className="form-control"
                                value={editFormData.mitre_subtechnique}
                                onChange={(e) => handleEditFormChange('mitre_subtechnique', e.target.value)}
                                placeholder="Sub-technique name"
                              />
                            ) : (
                              <span>{selectedTTP.mitre_subtechnique || 'None'}</span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="detail-section">
                      <h4><i className="fas fa-rss"></i> Threat Feed Information</h4>
                      <div className="detail-row">
                        <label>Source Feed:</label>
                        <div className="detail-value">
                          {selectedTTP.threat_feed ? (
                            <div className="feed-info">
                              <span className="feed-name">{selectedTTP.threat_feed.name}</span>
                              <span className={`feed-type ${selectedTTP.threat_feed.is_external ? 'external' : 'internal'}`}>
                                {selectedTTP.threat_feed.is_external ? 'External' : 'Internal'}
                              </span>
                            </div>
                          ) : (
                            <span className="no-data">Manual Entry</span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="detail-section">
                      <h4><i className="fas fa-clock"></i> Metadata</h4>
                      <div className="detail-row">
                        <label>Created:</label>
                        <div className="detail-value">
                          {selectedTTP.created_at ? new Date(selectedTTP.created_at).toLocaleString() : 'Unknown'}
                        </div>
                      </div>
                      <div className="detail-row">
                        <label>Last Modified:</label>
                        <div className="detail-value">
                          {selectedTTP.updated_at ? new Date(selectedTTP.updated_at).toLocaleString() : 'Never'}
                        </div>
                      </div>
                      {selectedTTP.stix_id && (
                        <div className="detail-row">
                          <label>STIX ID:</label>
                          <div className="detail-value">
                            <code>{selectedTTP.stix_id}</code>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div style={{textAlign: 'center', padding: '3rem'}}>
                  <i className="fas fa-exclamation-triangle" style={{fontSize: '2rem', color: '#dc3545'}}></i>
                  <p style={{marginTop: '1rem', color: '#666'}}>Failed to load TTP details</p>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button className="btn btn-outline" onClick={closeTTPModal}>
                Close
              </button>
              {selectedTTP && !ttpDetailLoading && (
                <>
                  {isEditMode ? (
                    <>
                      <button className="btn btn-outline" onClick={toggleEditMode}>
                        Cancel Edit
                      </button>
                      <button className="btn btn-primary" onClick={saveTTPChanges}>
                        <i className="fas fa-save"></i> Save Changes
                      </button>
                    </>
                  ) : (
                    <button className="btn btn-primary" onClick={toggleEditMode}>
                      <i className="fas fa-edit"></i> Edit TTP
                    </button>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}


      {/* TTP Export Modal */}
      {showExportModal && (
        <div className="modal-overlay" onClick={closeExportModal}>
          <div className="modal-content export-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3><i className="fas fa-download"></i> Export TTP Analysis</h3>
              <button className="modal-close" onClick={closeExportModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>

            <div className="modal-body">
              {exportError && (
                <div className="alert alert-error">
                  <i className="fas fa-exclamation-triangle"></i>
                  {exportError}
                </div>
              )}

              <div className="export-info">
                <div className="info-card">
                  <i className="fas fa-info-circle"></i>
                  <div>
                    <strong>Export Information</strong>
                    <p>Export your TTP analysis data in multiple formats. You can filter the data and customize the export to meet your specific needs.</p>
                  </div>
                </div>
              </div>

              <form>
                {/* Export Format Selection */}
                <div className="form-section">
                  <h4><i className="fas fa-file-alt"></i> Export Format</h4>
                  <div className="format-options">
                    <label className="format-option">
                      <input
                        type="radio"
                        name="exportFormat"
                        value="json"
                        checked={exportFormat === 'json'}
                        onChange={(e) => setExportFormat(e.target.value)}
                      />
                      <div className="format-card">
                        <i className="fas fa-code"></i>
                        <span>JSON</span>
                        <small>Structured data format</small>
                      </div>
                    </label>
                    <label className="format-option">
                      <input
                        type="radio"
                        name="exportFormat"
                        value="csv"
                        checked={exportFormat === 'csv'}
                        onChange={(e) => setExportFormat(e.target.value)}
                      />
                      <div className="format-card">
                        <i className="fas fa-table"></i>
                        <span>CSV</span>
                        <small>Spreadsheet compatible</small>
                      </div>
                    </label>
                    <label className="format-option">
                      <input
                        type="radio"
                        name="exportFormat"
                        value="stix"
                        checked={exportFormat === 'stix'}
                        onChange={(e) => setExportFormat(e.target.value)}
                      />
                      <div className="format-card">
                        <i className="fas fa-shield-alt"></i>
                        <span>STIX</span>
                        <small>Threat intelligence standard</small>
                      </div>
                    </label>
                  </div>
                </div>

                {/* Export Filters */}
                <div className="form-section">
                  <h4><i className="fas fa-filter"></i> Filters</h4>
                  <div className="form-grid">
                    <div className="form-group">
                      <label>MITRE Tactic</label>
                      <select
                        className="form-control"
                        value={exportFilters.tactic}
                        onChange={(e) => handleExportFilterChange('tactic', e.target.value)}
                      >
                        <option value="">All Tactics</option>
                        <option value="initial-access">Initial Access</option>
                        <option value="execution">Execution</option>
                        <option value="persistence">Persistence</option>
                        <option value="privilege-escalation">Privilege Escalation</option>
                        <option value="defense-evasion">Defense Evasion</option>
                        <option value="credential-access">Credential Access</option>
                        <option value="discovery">Discovery</option>
                        <option value="lateral-movement">Lateral Movement</option>
                        <option value="collection">Collection</option>
                        <option value="command-and-control">Command and Control</option>
                        <option value="exfiltration">Exfiltration</option>
                        <option value="impact">Impact</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label>Technique ID</label>
                      <input
                        type="text"
                        className="form-control"
                        value={exportFilters.technique_id}
                        onChange={(e) => handleExportFilterChange('technique_id', e.target.value)}
                        placeholder="e.g., T1059"
                      />
                    </div>

                    <div className="form-group">
                      <label>Threat Feed ID</label>
                      <input
                        type="number"
                        className="form-control"
                        value={exportFilters.feed_id}
                        onChange={(e) => handleExportFilterChange('feed_id', e.target.value)}
                        placeholder="Enter feed ID"
                      />
                    </div>

                    <div className="form-group">
                      <label>Maximum Records</label>
                      <input
                        type="number"
                        className="form-control"
                        value={exportFilters.limit}
                        onChange={(e) => handleExportFilterChange('limit', parseInt(e.target.value) || 1000)}
                        min="1"
                        max="10000"
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Created After</label>
                      <input
                        type="date"
                        className="form-control"
                        value={exportFilters.created_after}
                        onChange={(e) => handleExportFilterChange('created_after', e.target.value)}
                      />
                    </div>

                    <div className="form-group">
                      <label>Created Before</label>
                      <input
                        type="date"
                        className="form-control"
                        value={exportFilters.created_before}
                        onChange={(e) => handleExportFilterChange('created_before', e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Specific Fields (comma-separated)</label>
                    <input
                      type="text"
                      className="form-control"
                      value={exportFilters.fields}
                      onChange={(e) => handleExportFilterChange('fields', e.target.value)}
                      placeholder="e.g., id,name,mitre_technique_id,description"
                    />
                    <small className="form-help">Leave empty to export all available fields</small>
                  </div>
                </div>

                {/* Advanced Options */}
                <div className="form-section">
                  <h4><i className="fas fa-cog"></i> Advanced Options</h4>
                  <div className="checkbox-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={exportFilters.include_anonymized}
                        onChange={(e) => handleExportFilterChange('include_anonymized', e.target.checked)}
                      />
                      <span>Include anonymized TTPs</span>
                    </label>

                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={exportFilters.include_original}
                        onChange={(e) => handleExportFilterChange('include_original', e.target.checked)}
                      />
                      <span>Include original data for anonymized TTPs</span>
                    </label>
                  </div>
                </div>
              </form>
            </div>

            <div className="modal-footer">
              <button className="btn btn-outline" onClick={closeExportModal}>
                Cancel
              </button>
              <button 
                className="btn btn-primary" 
                onClick={exportTTPData}
                disabled={isExporting}
              >
                {isExporting ? (
                  <>
                    <i className="fas fa-spinner fa-spin"></i> Exporting...
                  </>
                ) : (
                  <>
                    <i className="fas fa-download"></i> Export Data
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Matrix Cell Details Modal */}
      {showMatrixCellModal && (
        <div className="modal-overlay" onClick={closeMatrixCellModal}>
          <div className="modal-content matrix-cell-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                <i className="fas fa-th-large"></i>
                {selectedTechnique 
                  ? `Technique ${selectedTechnique} in ${selectedTactic.replace(/_/g, ' ')}`
                  : `${selectedTactic.replace(/_/g, ' ')} Tactic Details`
                }
              </h3>
              <button className="modal-close" onClick={closeMatrixCellModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <div className="modal-body">
              {matrixCellLoading ? (
                <div className="loading-state">
                  <i className="fas fa-spinner fa-spin"></i>
                  <span>Loading matrix cell details...</span>
                </div>
              ) : matrixCellData ? (
                <div className="matrix-cell-details">
                  {/* Cell Information */}
                  <div className="cell-info-section">
                    <div className="info-grid">
                      <div className="info-item">
                        <label>Tactic:</label>
                        <span>{matrixCellData.cell_info.tactic_display}</span>
                      </div>
                      <div className="info-item">
                        <label>Total TTPs:</label>
                        <span>{matrixCellData.cell_info.total_ttps_in_cell}</span>
                      </div>
                      <div className="info-item">
                        <label>Unique Techniques:</label>
                        <span>{matrixCellData.cell_info.unique_techniques}</span>
                      </div>
                      <div className="info-item">
                        <label>Threat Feeds:</label>
                        <span>{matrixCellData.cell_info.threat_feeds_count}</span>
                      </div>
                      <div className="info-item">
                        <label>Recent Activity (30d):</label>
                        <span>{matrixCellData.cell_info.recent_activity}</span>
                      </div>
                      <div className="info-item">
                        <label>With Subtechniques:</label>
                        <span>{matrixCellData.cell_info.has_subtechniques}</span>
                      </div>
                    </div>
                  </div>

                  {/* Related Techniques */}
                  {matrixCellData.related_techniques && matrixCellData.related_techniques.length > 0 && (
                    <div className="related-techniques-section">
                      <h4><i className="fas fa-sitemap"></i> Top Techniques in this Tactic</h4>
                      <div className="techniques-grid">
                        {matrixCellData.related_techniques.map((tech, index) => (
                          <div 
                            key={tech.mitre_technique_id || index}
                            className="technique-card clickable"
                            onClick={() => handleTechniqueClick(tech.mitre_technique_id)}
                          >
                            <div className="technique-id">{tech.mitre_technique_id}</div>
                            <div className="technique-count">{tech.count} TTPs</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* TTPs List */}
                  <div className="ttps-list-section">
                    <h4>
                      <i className="fas fa-list"></i>
                      TTPs ({matrixCellData.ttps.filtered_count})
                      {matrixCellData.ttps.has_next && (
                        <span className="showing-info">
                          (Showing first {matrixCellData.ttps.page_size})
                        </span>
                      )}
                    </h4>
                    
                    {matrixCellData.ttps.results.length > 0 ? (
                      <div className="ttps-list">
                        {matrixCellData.ttps.results.map(ttp => (
                          <div key={ttp.id} className="ttp-item">
                            <div className="ttp-header">
                              <div className="ttp-name">{ttp.name}</div>
                              <div className="ttp-badges">
                                {ttp.mitre_technique_id && (
                                  <span className="badge technique-badge">{ttp.mitre_technique_id}</span>
                                )}
                                {ttp.severity && (
                                  <span className={`badge severity-${ttp.severity}`}>{ttp.severity}</span>
                                )}
                                {ttp.is_anonymized && (
                                  <span className="badge anonymized-badge">Anonymized</span>
                                )}
                              </div>
                            </div>
                            
                            <div className="ttp-description">
                              {ttp.description.length > 200 
                                ? ttp.description.substring(0, 200) + '...'
                                : ttp.description
                              }
                            </div>
                            
                            <div className="ttp-meta">
                              {ttp.threat_feed && (
                                <div className="feed-info">
                                  <i className="fas fa-rss"></i>
                                  <span>{ttp.threat_feed.name}</span>
                                  {ttp.threat_feed.is_external && (
                                    <span className="external-indicator">External</span>
                                  )}
                                </div>
                              )}
                              <div className="created-date">
                                <i className="fas fa-clock"></i>
                                {new Date(ttp.created_at).toLocaleDateString()}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="empty-state">
                        <i className="fas fa-info-circle"></i>
                        <span>No TTPs found for this matrix cell</span>
                      </div>
                    )}
                  </div>

                  {/* Statistics */}
                  {matrixCellData.statistics && (
                    <div className="statistics-section">
                      <h4><i className="fas fa-chart-bar"></i> Statistics</h4>
                      <div className="stats-grid">
                        {matrixCellData.statistics.severity_distribution && (
                          <div className="stat-item">
                            <label>Severity Distribution:</label>
                            <div className="severity-bars">
                              {Object.entries(matrixCellData.statistics.severity_distribution).map(([severity, count]) => (
                                <div key={severity} className="severity-bar">
                                  <span className={`severity-label ${severity}`}>{severity}: {count}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="error-state">
                  <i className="fas fa-exclamation-triangle"></i>
                  <span>Failed to load matrix cell details</span>
                </div>
              )}
            </div>
            
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={closeMatrixCellModal}>
                Close
              </button>
              {matrixCellData && matrixCellData.ttps.has_next && (
                <button className="btn btn-primary">
                  <i className="fas fa-arrow-right"></i> View All TTPs
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Technique Details Modal */}
      {showTechniqueModal && (
        <div className="modal-overlay" onClick={closeTechniqueModal}>
          <div className="modal-content technique-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                <i className="fas fa-bullseye"></i>
                Technique Details: {selectedTechniqueId}
              </h3>
              <button className="modal-close" onClick={closeTechniqueModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <div className="modal-body">
              {techniqueLoading ? (
                <div className="loading-state">
                  <i className="fas fa-spinner fa-spin"></i>
                  <span>Loading technique details...</span>
                </div>
              ) : techniqueData ? (
                <div className="technique-details">
                  {/* Technique Information */}
                  <div className="technique-info-section">
                    <div className="info-header">
                      <div className="technique-title">
                        <h4>{techniqueData.technique_info.name || selectedTechniqueId}</h4>
                        <div className="technique-badges">
                          <span className="badge technique-badge">{selectedTechniqueId}</span>
                          <span className={`badge severity-${techniqueData.technique_info.severity}`}>
                            {techniqueData.technique_info.severity}
                          </span>
                          {techniqueData.technique_info.is_subtechnique && (
                            <span className="badge subtechnique-badge">Subtechnique</span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="technique-stats">
                      <div className="stat-item">
                        <label>Total TTPs:</label>
                        <span>{techniqueData.statistics.total_ttps}</span>
                      </div>
                      <div className="stat-item">
                        <label>Threat Feeds:</label>
                        <span>{techniqueData.statistics.unique_threat_feeds}</span>
                      </div>
                      <div className="stat-item">
                        <label>First Seen:</label>
                        <span>{techniqueData.statistics.first_seen 
                          ? new Date(techniqueData.statistics.first_seen).toLocaleDateString() 
                          : 'N/A'}</span>
                      </div>
                      <div className="stat-item">
                        <label>Last Seen:</label>
                        <span>{techniqueData.statistics.last_seen 
                          ? new Date(techniqueData.statistics.last_seen).toLocaleDateString() 
                          : 'N/A'}</span>
                      </div>
                    </div>
                  </div>

                  {/* Associated Tactics */}
                  {techniqueData.associated_tactics && techniqueData.associated_tactics.length > 0 && (
                    <div className="tactics-section">
                      <h4><i className="fas fa-layer-group"></i> Associated Tactics</h4>
                      <div className="tactics-grid">
                        {techniqueData.associated_tactics.map(tactic => (
                          <div 
                            key={tactic.tactic}
                            className="tactic-card clickable"
                            onClick={() => handleMatrixCellClick(tactic.tactic, selectedTechniqueId)}
                          >
                            <div className="tactic-name">{tactic.tactic_display}</div>
                            <div className="tactic-count">{tactic.count} TTPs</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Technique Variants */}
                  {techniqueData.variants && techniqueData.variants.length > 0 && (
                    <div className="variants-section">
                      <h4><i className="fas fa-code-branch"></i> Related Variants</h4>
                      <div className="variants-grid">
                        {techniqueData.variants.map(variant => (
                          <div 
                            key={variant.mitre_technique_id}
                            className="variant-card clickable"
                            onClick={() => handleTechniqueClick(variant.mitre_technique_id)}
                          >
                            <div className="variant-id">{variant.mitre_technique_id}</div>
                            <div className="variant-count">{variant.count} TTPs</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Recent Activity */}
                  {techniqueData.statistics.recent_activity && (
                    <div className="activity-section">
                      <h4><i className="fas fa-activity"></i> Recent Activity</h4>
                      <div className="activity-stats">
                        <div className="activity-item">
                          <label>Last 24 hours:</label>
                          <span>{techniqueData.statistics.recent_activity.last_24h}</span>
                        </div>
                        <div className="activity-item">
                          <label>Last 7 days:</label>
                          <span>{techniqueData.statistics.recent_activity.last_7d}</span>
                        </div>
                        <div className="activity-item">
                          <label>Last 30 days:</label>
                          <span>{techniqueData.statistics.recent_activity.last_30d}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TTPs using this technique */}
                  <div className="technique-ttps-section">
                    <h4>
                      <i className="fas fa-list"></i>
                      TTPs Using This Technique ({techniqueData.ttps.length})
                    </h4>
                    
                    {techniqueData.ttps.length > 0 ? (
                      <div className="technique-ttps-list">
                        {techniqueData.ttps.slice(0, 10).map(ttp => (
                          <div key={ttp.id} className="ttp-item">
                            <div className="ttp-header">
                              <div className="ttp-name">{ttp.name}</div>
                              <div className="ttp-badges">
                                {ttp.mitre_tactic && (
                                  <span className="badge tactic-badge">{ttp.mitre_tactic_display}</span>
                                )}
                                {ttp.is_anonymized && (
                                  <span className="badge anonymized-badge">Anonymized</span>
                                )}
                              </div>
                            </div>
                            
                            <div className="ttp-description">
                              {ttp.description.length > 150 
                                ? ttp.description.substring(0, 150) + '...'
                                : ttp.description
                              }
                            </div>
                            
                            <div className="ttp-meta">
                              {ttp.threat_feed && (
                                <div className="feed-info">
                                  <i className="fas fa-rss"></i>
                                  <span>{ttp.threat_feed.name}</span>
                                </div>
                              )}
                              <div className="created-date">
                                <i className="fas fa-clock"></i>
                                {new Date(ttp.created_at).toLocaleDateString()}
                              </div>
                            </div>
                          </div>
                        ))}
                        
                        {techniqueData.ttps.length > 10 && (
                          <div className="more-ttps-indicator">
                            <i className="fas fa-ellipsis-h"></i>
                            <span>and {techniqueData.ttps.length - 10} more TTPs...</span>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="empty-state">
                        <i className="fas fa-info-circle"></i>
                        <span>No TTPs found for this technique</span>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="error-state">
                  <i className="fas fa-exclamation-triangle"></i>
                  <span>Failed to load technique details</span>
                </div>
              )}
            </div>
            
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={closeTechniqueModal}>
                Close
              </button>
              {techniqueData && techniqueData.ttps.length > 10 && (
                <button className="btn btn-primary">
                  <i className="fas fa-external-link-alt"></i> View All TTPs
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

// Organisations Component


// Reports Component  
function Organisations({ active }) {
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    domain: '',
    contact_email: '',
    description: '',
    website: '',
    organization_type: 'educational',
    primary_user: {
      username: '',
      email: '',
      password: '',
      first_name: '',
      last_name: ''
    }
  });

  useEffect(() => {
    if (active) {
      fetchOrganizations();
    }
  }, [active]);

  const fetchOrganizations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/api/organizations/');
      console.log('Organizations API response:', response); // Debug log
      if (response && response.success) {
        const orgs = response.organizations || [];
        console.log('Setting organizations:', orgs); // Debug log
        setOrganizations(orgs);
      } else {
        console.error('API response unsuccessful:', response);
        setError('Failed to load institutions - API response unsuccessful');
      }
    } catch (err) {
      console.error('Error fetching organizations:', err);
      setError(`Failed to load institutions: ${err.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrganization = async (e) => {
    e.preventDefault();
    setError(null); // Clear previous errors
    try {
      const response = await api.post('/api/organizations/create/', formData);
      if (response && response.success) {
        setShowCreateModal(false);
        setFormData({
          name: '',
          domain: '',
          contact_email: '',
          description: '',
          website: '',
          organization_type: 'educational',
          primary_user: {
            username: '',
            email: '',
            password: '',
            first_name: '',
            last_name: ''
          }
        });
        fetchOrganizations();
        setError(null);
      } else if (response && response.message) {
        // Show backend error message
        setError(response.message);
      } else {
        setError('Failed to create organisation - unknown error');
      }
    } catch (err) {
      console.error('Error creating organization:', err);
      // Try to extract error message from response
      const errorMessage = err.response?.data?.message || err.message || 'Failed to create organisation';
      setError(errorMessage);
    }
  };

  if (!active) return null;

  return (
    <section id="institutions" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Organisations & Organizations</h1>
          <p className="page-subtitle">Manage connected organisations and organizations</p>
        </div>
        <div className="action-buttons">
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            <i className="fas fa-plus"></i> Add Organisation
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading institutions...</p>
        </div>
      ) : (
        <div className="institutions-grid">
          <div className="stats-row">
            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-building"></i>
              </div>
              <div className="stat-content">
                <h3>{organizations.length}</h3>
                <p>Total Organizations</p>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-users"></i>
              </div>
              <div className="stat-content">
                <h3>{organizations.reduce((sum, org) => sum + (org.member_count || 0), 0)}</h3>
                <p>Total Members</p>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-handshake"></i>
              </div>
              <div className="stat-content">
                <h3>{organizations.filter(org => org.trust_relationships_count > 0).length}</h3>
                <p>Connected Orgs</p>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-shield-alt"></i>
              </div>
              <div className="stat-content">
                <h3>{organizations.filter(org => org.is_active).length}</h3>
                <p>Active Orgs</p>
              </div>
            </div>
          </div>

          <div className="organizations-list">
            {organizations.length === 0 ? (
              <div className="empty-state">
                <i className="fas fa-building" style={{fontSize: '48px', color: '#dee2e6'}}></i>
                <h3>No institutions found</h3>
                <p>Create your first organisation to get started with threat intelligence sharing.</p>
                <button 
                  className="btn btn-primary"
                  onClick={() => setShowCreateModal(true)}
                >
                  <i className="fas fa-plus"></i> Create Organisation
                </button>
              </div>
            ) : (
              <div className="organizations-table">
                <table>
                  <thead>
                    <tr>
                      <th>Organisation</th>
                      <th>Type</th>
                      <th>Domain</th>
                      <th>Members</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {organizations.map(org => (
                      <tr key={org.id}>
                        <td>
                          <div className="org-info">
                            <div className="org-icon">
                              <i className="fas fa-building"></i>
                            </div>
                            <div>
                              <div className="org-name">{org.name}</div>
                              <div className="org-description">{org.description || 'No description'}</div>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className="org-type">{org.organization_type || 'Unknown'}</span>
                        </td>
                        <td>{org.domain || 'N/A'}</td>
                        <td>{org.member_count || 0}</td>
                        <td>
                          <span className={`status-badge ${org.is_active ? 'active' : 'inactive'}`}>
                            {org.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td>
                          <div className="actions">
                            <button 
                              className="btn btn-sm btn-outline"
                              onClick={() => setSelectedOrg(org)}
                            >
                              <i className="fas fa-eye"></i>
                            </button>
                            <button className="btn btn-sm btn-outline">
                              <i className="fas fa-edit"></i>
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Create Organization Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Organisation</h3>
              <button 
                className="close-btn"
                onClick={() => setShowCreateModal(false)}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            <form onSubmit={handleCreateOrganization}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Organisation Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label>Domain</label>
                  <input
                    type="text"
                    value={formData.domain}
                    onChange={(e) => setFormData({...formData, domain: e.target.value})}
                    placeholder="example.edu"
                  />
                </div>
                
                <div className="form-group">
                  <label>Contact Email</label>
                  <input
                    type="email"
                    value={formData.contact_email}
                    onChange={(e) => setFormData({...formData, contact_email: e.target.value})}
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label>Organization Type</label>
                  <select
                    value={formData.organization_type}
                    onChange={(e) => setFormData({...formData, organization_type: e.target.value})}
                  >
                    <option value="educational">Educational</option>
                    <option value="government">Government</option>
                    <option value="private">Private</option>
                    <option value="nonprofit">Non-profit</option>
                    <option value="healthcare">Healthcare</option>
                    <option value="financial">Financial</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    rows="3"
                  />
                </div>
                
                <div className="form-group">
                  <label>Website</label>
                  <input
                    type="url"
                    value={formData.website}
                    onChange={(e) => setFormData({...formData, website: e.target.value})}
                    placeholder="https://example.edu"
                  />
                </div>
                
                <div className="form-section">
                  <h4 style={{marginBottom: '1rem', paddingTop: '1rem', borderTop: '1px solid #ddd', color: '#333'}}>
                    Primary Administrator
                  </h4>
                  
                  <div className="form-group">
                    <label>Username *</label>
                    <input
                      type="text"
                      value={formData.primary_user.username}
                      onChange={(e) => setFormData({
                        ...formData, 
                        primary_user: {...formData.primary_user, username: e.target.value}
                      })}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Email *</label>
                    <input
                      type="email"
                      value={formData.primary_user.email}
                      onChange={(e) => setFormData({
                        ...formData, 
                        primary_user: {...formData.primary_user, email: e.target.value}
                      })}
                      required
                    />
                  </div>
                  
                  <div className="form-row">
                    <div className="form-group">
                      <label>First Name *</label>
                      <input
                        type="text"
                        value={formData.primary_user.first_name}
                        onChange={(e) => setFormData({
                          ...formData, 
                          primary_user: {...formData.primary_user, first_name: e.target.value}
                        })}
                        required
                      />
                    </div>
                    
                    <div className="form-group">
                      <label>Last Name *</label>
                      <input
                        type="text"
                        value={formData.primary_user.last_name}
                        onChange={(e) => setFormData({
                          ...formData, 
                          primary_user: {...formData.primary_user, last_name: e.target.value}
                        })}
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="form-group">
                    <label>Password *</label>
                    <input
                      type="password"
                      value={formData.primary_user.password}
                      onChange={(e) => setFormData({
                        ...formData, 
                        primary_user: {...formData.primary_user, password: e.target.value}
                      })}
                      required
                      placeholder="Minimum 8 characters"
                    />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Organisation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Organization Details Modal */}
      {selectedOrg && (
        <div className="modal-overlay" onClick={() => setSelectedOrg(null)}>
          <div className="modal large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedOrg.name}</h3>
              <button 
                className="close-btn"
                onClick={() => setSelectedOrg(null)}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <div className="org-details">
                <div className="detail-row">
                  <label>Name:</label>
                  <span>{selectedOrg.name}</span>
                </div>
                <div className="detail-row">
                  <label>Type:</label>
                  <span>{selectedOrg.organization_type || 'Not specified'}</span>
                </div>
                <div className="detail-row">
                  <label>Domain:</label>
                  <span>{selectedOrg.domain || 'Not specified'}</span>
                </div>
                <div className="detail-row">
                  <label>Contact Email:</label>
                  <span>{selectedOrg.contact_email || 'Not specified'}</span>
                </div>
                <div className="detail-row">
                  <label>Website:</label>
                  <span>
                    {selectedOrg.website ? (
                      <a href={selectedOrg.website} target="_blank" rel="noopener noreferrer">
                        {selectedOrg.website}
                      </a>
                    ) : 'Not specified'}
                  </span>
                </div>
                <div className="detail-row">
                  <label>Description:</label>
                  <span>{selectedOrg.description || 'No description provided'}</span>
                </div>
                <div className="detail-row">
                  <label>Members:</label>
                  <span>{selectedOrg.member_count || 0}</span>
                </div>
                <div className="detail-row">
                  <label>Status:</label>
                  <span className={`status-badge ${selectedOrg.is_active ? 'active' : 'inactive'}`}>
                    {selectedOrg.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setSelectedOrg(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

// Reports Component  
function Reports({ active }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);

  const sampleReports = [
    {
      id: 1,
      title: "Weekly Threat Intelligence Summary",
      type: "summary",
      date: "2025-01-08",
      status: "completed",
      description: "Comprehensive overview of threat landscape for the week"
    },
    {
      id: 2,
      title: "APT Campaign Analysis",
      type: "campaign", 
      date: "2025-01-05",
      status: "completed",
      description: "Deep dive into recent APT activities and TTPs"
    },
    {
      id: 3,
      title: "Vulnerability Trend Report",
      type: "trend",
      date: "2025-01-01",
      status: "draft",
      description: "Analysis of vulnerability trends and exploitation patterns"
    }
  ];

  useEffect(() => {
    if (active) {
      setLoading(true);
      // Simulate API call
      setTimeout(() => {
        setReports(sampleReports);
        setLoading(false);
      }, 1000);
    }
  }, [active]);

  if (!active) return null;

  return (
    <section id="reports" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Reports & Analytics</h1>
          <p className="page-subtitle">Generate and manage threat intelligence reports</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-primary">
            <i className="fas fa-plus"></i> Generate Report
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading reports...</p>
        </div>
      ) : (
        <div className="reports-grid">
          <div className="stats-row">
            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-file-alt"></i>
              </div>
              <div className="stat-content">
                <h3>{reports.length}</h3>
                <p>Total Reports</p>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-check-circle"></i>
              </div>
              <div className="stat-content">
                <h3>{reports.filter(r => r.status === 'completed').length}</h3>
                <p>Completed</p>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-edit"></i>
              </div>
              <div className="stat-content">
                <h3>{reports.filter(r => r.status === 'draft').length}</h3>
                <p>Drafts</p>
              </div>
            </div>
          </div>

          <div className="reports-list">
            <h3 style={{marginBottom: '1rem', color: '#333'}}>Recent Reports</h3>
            {reports.length === 0 ? (
              <div className="empty-state">
                <i className="fas fa-file-alt" style={{fontSize: '48px', color: '#dee2e6'}}></i>
                <h3>No reports available</h3>
                <p>Generate your first threat intelligence report.</p>
                <button className="btn btn-primary">
                  <i className="fas fa-plus"></i> Generate Report
                </button>
              </div>
            ) : (
              <div className="reports-table">
                <table>
                  <thead>
                    <tr>
                      <th>Report Title</th>
                      <th>Type</th>
                      <th>Date</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reports.map(report => (
                      <tr key={report.id}>
                        <td>
                          <div className="report-info">
                            <div className="report-title">{report.title}</div>
                            <div className="report-description">{report.description}</div>
                          </div>
                        </td>
                        <td>
                          <span className="report-type">{report.type}</span>
                        </td>
                        <td>{report.date}</td>
                        <td>
                          <span className={`status-badge ${report.status}`}>
                            {report.status}
                          </span>
                        </td>
                        <td>
                          <div className="actions">
                            <button className="btn btn-sm btn-outline">
                              <i className="fas fa-eye"></i>
                            </button>
                            <button className="btn btn-sm btn-outline">
                              <i className="fas fa-download"></i>
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}

// CSS Styles
function CSSStyles() {
  return (
    <style>
      {`
        :root {
            --primary-blue: #0056b3;
            --secondary-blue: #007bff;
            --light-blue: #e8f4ff;
            --accent-blue: #00a0e9;
            --dark-blue: #003366;
            --white: #ffffff;
            --light-gray: #f5f7fa;
            --medium-gray: #e2e8f0;
            --text-dark: #2d3748;
            --text-muted: #718096;
            --danger: #e53e3e;
            --success: #38a169;
            --warning: #f6ad55;
            --info: #4299e1;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: var(--light-gray);
            color: var(--text-dark);
            min-height: 100vh;
            overscroll-behavior: none;
        }
        
        /* Loading Screen */
        .loading-screen, .login-screen {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background: linear-gradient(135deg, #0056b3, #004494);
            color: white;
            text-align: center;
        }
        
        .login-container {
            background: rgba(255, 255, 255, 0.1);
            padding: 2rem;
            border-radius: 12px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        }
        
        .login-container h2 {
            margin-bottom: 0.5rem;
            font-size: 28px;
            font-weight: 600;
        }
        
        .login-container p {
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        
        .login-container .btn {
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 600;
        }
        
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        
        .loading-screen h2 {
            margin-bottom: 10px;
            font-size: 28px;
            font-weight: 600;
        }
        
        .loading-screen p {
            font-size: 16px;
            opacity: 0.8;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* Header */
        header {
            background-color: var(--white);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--primary-blue);
            text-decoration: none;
        }
        
        .logo-icon {
            font-size: 24px;
            background-color: var(--primary-blue);
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .logo-text {
            font-weight: 700;
            font-size: 22px;
        }
        
        .nav-actions {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .search-bar {
            position: relative;
        }
        
        .search-bar input {
            padding: 8px 12px 8px 36px;
            border-radius: 6px;
            border: 1px solid var(--medium-gray);
            width: 240px;
            background-color: white;
            font-size: 14px;
            transition: all 0.3s;
        }
        
        .search-bar input:focus {
            width: 280px;
            outline: none;
            border-color: var(--secondary-blue);
            background-color: var(--white);
        }
        
        .search-icon {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
        }
        
        .notifications {
            position: relative;
            cursor: pointer;
        }
        
        .notification-count {
            position: absolute;
            top: -5px;
            right: -5px;
            background-color: var(--danger);
            color: white;
            font-size: 10px;
            font-weight: 700;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .user-profile {
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
        }
        
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: var(--primary-blue);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 16px;
        }
        
        .user-info {
            display: flex;
            flex-direction: column;
        }
        
        .user-name {
            font-weight: 600;
            font-size: 14px;
        }
        
        .user-role {
            font-size: 12px;
            color: var(--text-muted);
        }
        
        /* Main Navigation */
        nav.main-nav {
            background-color: var(--primary-blue);
            padding: 0;
        }
        
        .nav-container {
            display: flex;
            justify-content: space-between;
        }
        
        .nav-links {
            display: flex;
            list-style: none;
        }
        
        .nav-links li {
            position: relative;
        }
        
        .nav-links a {
            color: var(--white);
            text-decoration: none;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
            transition: background-color 0.3s;
            position: relative;
            cursor: pointer;
        }
        
        .nav-links a:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        .nav-links a.active {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        .nav-links a.active::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background-color: var(--accent-blue);
        }
        
        .nav-right {
            display: flex;
            align-items: center;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 6px;
            color: var(--white);
            padding: 0 20px;
            font-size: 14px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--success);
        }
        
        /* User Profile Dropdown */
        .user-profile-container {
            position: relative;
            margin-left: 20px;
        }
        
        .user-profile {
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 25px;
            padding: 8px 15px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }
        
        .user-profile:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }
        
        .avatar {
            width: 32px;
            height: 32px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
        }
        
        .user-info {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 2px;
        }
        
        .user-name {
            font-weight: 600;
            font-size: 14px;
        }
        
        .user-role {
            font-size: 12px;
            color: var(--primary-blue);
            opacity: 0.8;
        }
        
        .user-profile i {
            font-size: 12px;
            transition: transform 0.3s ease;
        }
        
        .user-profile.open i {
            transform: rotate(180deg);
        }
        
        .user-menu-dropdown {
            position: absolute;
            top: 100%;
            right: 0;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            min-width: 280px;
            z-index: 1000;
            margin-top: 5px;
            overflow: hidden;
            animation: dropdownFadeIn 0.2s ease-out;
        }
        
        @keyframes dropdownFadeIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .dropdown-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 20px;
            background: linear-gradient(135deg, #0056b3, #004494);
            color: white;
        }
        
        .user-avatar-large {
            width: 50px;
            height: 50px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 18px;
        }
        
        .user-name-large {
            font-weight: 600;
            font-size: 16px;
            margin-bottom: 4px;
        }
        
        .user-email {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .menu-divider {
            height: 1px;
            background: #e9ecef;
        }
        
        .menu-items {
            padding: 10px 0;
        }
        
        .menu-item {
            width: 100%;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 20px;
            background: none;
            border: none;
            color: #333;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 14px;
            text-align: left;
        }
        
        .menu-item:hover {
            background: #f8f9fa;
            color: #0056b3;
        }
        
        .menu-item i {
            width: 16px;
            text-align: center;
        }
        
        .menu-item-submenu {
            position: relative;
        }
        
        .submenu-arrow {
            margin-left: auto !important;
            font-size: 12px;
            transition: transform 0.3s ease;
        }
        
        .submenu {
            background: #f8f9fa;
            border-left: 3px solid #0056b3;
        }
        
        .submenu-item {
            width: 100%;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 20px 10px 40px;
            background: none;
            border: none;
            color: #555;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 13px;
            text-align: left;
        }
        
        .submenu-item:hover {
            background: #e9ecef;
            color: #0056b3;
        }
        
        .submenu-item i {
            width: 14px;
            text-align: center;
        }
        
        .logout-item {
            color: #dc3545 !important;
        }
        
        .logout-item:hover {
            background: #f8d7da !important;
            color: #721c24 !important;
        }
        
        /* Main Content */
        .main-content {
            padding: 30px 0;
        }
        
        /* Page Section */
        .page-section {
            display: none;
        }
        
        .page-section.active {
            display: block;
        }
        
        /* Dashboard Header */
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }
        
        .page-title {
            font-size: 24px;
            font-weight: 600;
            color: var(--dark-blue);
        }
        
        .page-subtitle {
            color: var(--text-muted);
            margin-top: 4px;
            font-size: 15px;
        }
        
        .action-buttons {
            display: flex;
            gap: 12px;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 10px 16px;
            border-radius: 6px;
            font-weight: 500;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
            border: none;
        }
        
        .btn-primary {
            background-color: var(--primary-blue);
            color: white;
        }
        
        .btn-primary:hover {
            background-color: var(--dark-blue);
        }
        
        .btn-secondary {
            background-color: var(--secondary-blue);
            color: white;
        }
        
        .btn-secondary:hover {
            background-color: var(--primary-blue);
        }
        
        .btn-outline {
            background-color: transparent;
            border: 1px solid var(--primary-blue);
            color: var(--primary-blue);
        }
        
        .btn-outline:hover {
            background-color: var(--light-blue);
        }
        
        .btn-danger {
            background-color: var(--danger);
            color: white;
        }
        
        .btn-danger:hover {
            background-color: #c53030;
        }
        
        .btn-sm {
            padding: 6px 12px;
            font-size: 13px;
        }
        
        /* Stats Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background-color: var(--white);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }
        
        .stat-title {
            color: var(--text-muted);
            font-size: 14px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .stat-icon {
            width: 28px;
            height: 28px;
            background-color: var(--light-blue);
            color: var(--primary-blue);
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: 700;
            color: var(--dark-blue);
            margin-bottom: 5px;
        }
        
        .stat-change {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 14px;
        }
        
        .increase {
            color: var(--success);
        }
        
        .decrease {
            color: var(--danger);
        }
        
        /* Main Grid */
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 24px;
        }
        
        .card {
            background-color: var(--white);
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            overflow: hidden;
            margin-bottom: 24px;
        }
        
        .card:last-child {
            margin-bottom: 0;
        }
        
        .card-header {
            padding: 16px 20px;
            border-bottom: 1px solid var(--medium-gray);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .card-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--dark-blue);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card-icon {
            color: var(--primary-blue);
        }
        
        .card-actions {
            display: flex;
            gap: 12px;
        }
        
        .card-content {
            padding: 20px;
        }
        
        /* Tables */
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .data-table th, 
        .data-table td {
            padding: 12px 15px;
            text-align: left;
        }
        
        .data-table th {
            background-color: var(--light-gray);
            color: var(--text-muted);
            font-weight: 600;
            font-size: 14px;
        }
        
        .data-table tbody tr {
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .data-table tbody tr:last-child {
            border-bottom: none;
        }
        
        .data-table tbody tr:hover {
            background-color: var(--light-blue);
        }
        
        /* Badge Styles */
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .badge-high {
            background-color: rgba(229, 62, 62, 0.1);
            color: var(--danger);
        }
        
        .badge-medium {
            background-color: rgba(246, 173, 85, 0.1);
            color: var(--warning);
        }
        
        .badge-low {
            background-color: rgba(56, 161, 105, 0.1);
            color: var(--success);
        }
        
        .badge-active {
            background-color: rgba(56, 161, 105, 0.1);
            color: var(--success);
        }
        
        .badge-inactive {
            background-color: rgba(113, 128, 150, 0.1);
            color: var(--text-muted);
        }
        
        .badge-connected {
            background-color: rgba(66, 153, 225, 0.1);
            color: var(--info);
        }
        
        .badge-tags {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }
        
        /* Filter Section */
        .filters-section {
            background-color: var(--light-gray);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
        }
        
        .filters-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 16px;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .filter-label {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
        }
        
        .filter-control {
            display: flex;
            gap: 10px;
        }
        
        .filter-control select,
        .filter-control input {
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid var(--medium-gray);
            font-size: 14px;
            background-color: white;
            flex: 1;
        }
        
        .filter-control select:focus,
        .filter-control input:focus {
            outline: none;
            border-color: var(--secondary-blue);
        }
        
        /* Organisations List */
        .organisation-list {
            list-style: none;
        }
        
        .organisation-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 0;
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .organisation-item:last-child {
            border-bottom: none;
        }
        
        .organisation-logo {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            background-color: var(--light-blue);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary-blue);
            font-weight: 600;
        }
        
        .organisation-details {
            flex: 1;
        }
        
        .organisation-name {
            font-weight: 600;
            margin-bottom: 2px;
        }
        
        .organisation-meta {
            font-size: 13px;
            color: var(--text-muted);
        }
        
        .organisation-stats {
            display: flex;
            gap: 15px;
            margin-top: 5px;
        }
        
        .stat-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 13px;
        }
        
        .stat-item i {
            color: var(--primary-blue);
        }
        
        .trust-level {
            width: 80px;
            height: 6px;
            background-color: var(--medium-gray);
            border-radius: 3px;
        }
        
        .trust-fill {
            height: 100%;
            border-radius: 3px;
            background-color: var(--primary-blue);
        }
        
        /* Activity Stream */
        .activity-stream {
            list-style: none;
        }
        
        .activity-item {
            padding: 15px;
            display: flex;
            gap: 15px;
            border-bottom: 1px solid var(--medium-gray);
            background-color: white;
            border-radius: 8px;
            margin-bottom: 8px;
            transition: all 0.2s ease;
        }
        
        .activity-item:hover {
            background-color: var(--light-blue);
            transform: translateX(4px);
            box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
        }
        
        .activity-item:last-child {
            border-bottom: none;
        }
        
        .activity-icon {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background-color: var(--light-blue);
            color: var(--primary-blue);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        
        .activity-details {
            flex: 1;
        }
        
        .activity-text {
            margin-bottom: 5px;
            line-height: 1.4;
        }
        
        .activity-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .activity-time {
            font-size: 13px;
            color: var(--text-muted);
        }
        
        /* MITRE ATT&CK Matrix */
        .matrix-container {
            overflow-x: auto;
        }
        
        .mitre-matrix {
            min-width: 900px;
            border-collapse: collapse;
        }
        
        .mitre-matrix th {
            background-color: var(--primary-blue);
            color: white;
            padding: 12px;
            text-align: center;
            font-size: 14px;
        }
        
        .matrix-cell {
            width: 100px;
            height: 60px;
            border: 1px solid var(--medium-gray);
            padding: 10px;
            font-size: 12px;
            vertical-align: top;
            position: relative;
            transition: all 0.3s;
        }
        
        .matrix-cell:hover {
            background-color: var(--light-blue);
        }
        
        .matrix-cell.active {
            background-color: rgba(0, 86, 179, 0.1);
        }
        
        .technique-count {
            position: absolute;
            top: 5px;
            right: 5px;
            background-color: var(--primary-blue);
            color: white;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
        }

        .tactic-count {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.8);
            font-weight: normal;
            margin-top: 2px;
        }

        .technique-name {
            font-weight: 500;
            margin-bottom: 4px;
            line-height: 1.2;
        }

        .technique-id {
            font-size: 10px;
            color: var(--primary-blue);
            font-weight: bold;
            background-color: rgba(0, 86, 179, 0.1);
            padding: 2px 4px;
            border-radius: 3px;
            display: inline-block;
        }

        .empty-cell {
            color: #ccc;
            font-size: 18px;
            text-align: center;
        }

        .matrix-stats {
            font-size: 14px;
        }

        .matrix-stats strong {
            color: var(--primary-blue);
        }

        /* TTP Detail Modal */
        .ttp-modal {
            max-width: 900px;
            width: 90vw;
            max-height: 90vh;
            overflow-y: auto;
        }

        .ttp-detail-content {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .ttp-header-section {
            border-bottom: 1px solid var(--medium-gray);
            padding-bottom: 1rem;
        }

        .ttp-title-section {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .ttp-title {
            margin: 0;
            color: var(--primary-blue);
            font-size: 1.5rem;
        }

        .ttp-name-input {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--primary-blue);
        }

        .ttp-badges {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .ttp-details-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }

        @media (min-width: 768px) {
            .ttp-details-grid {
                grid-template-columns: 1fr 1fr;
            }
        }

        .detail-section {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
        }

        .detail-section h4 {
            margin: 0 0 1rem 0;
            color: var(--primary-blue);
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .detail-row {
            display: flex;
            flex-direction: column;
            margin-bottom: 1rem;
        }

        .detail-row:last-child {
            margin-bottom: 0;
        }

        .detail-row label {
            font-weight: 600;
            color: #555;
            margin-bottom: 0.25rem;
            font-size: 0.9rem;
        }

        .detail-value {
            color: #333;
        }

        .detail-value p {
            margin: 0;
            line-height: 1.5;
        }

        .technique-id-display {
            background: rgba(0, 86, 179, 0.1);
            color: var(--primary-blue);
            padding: 4px 8px;
            border-radius: 4px;
            font-family: monospace;
            font-weight: bold;
        }

        .feed-info {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .feed-name {
            font-weight: 600;
        }

        .feed-type {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .feed-type.external {
            background: #e3f2fd;
            color: #1976d2;
        }

        .feed-type.internal {
            background: #f3e5f5;
            color: #7b1fa2;
        }

        .no-data {
            color: #999;
            font-style: italic;
        }

        .detail-value code {
            background: #f1f3f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9rem;
        }

        /* Badge styles for TTP modal */
        .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .badge-primary {
            background: var(--primary-blue);
            color: white;
        }

        .badge-secondary {
            background: #6c757d;
            color: white;
        }

        .badge-info {
            background: #17a2b8;
            color: white;
        }

        /* TTP Creation Modal */
        .ttp-create-modal {
            max-width: 800px;
            width: 90vw;
            max-height: 85vh;
            overflow-y: auto;
        }

        /* Delete Confirmation Modal */
        .delete-modal {
            max-width: 500px;
            width: 90vw;
        }

        .delete-confirmation p {
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
            color: #333;
        }

        .warning-text {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 1rem;
            margin: 1.5rem 0;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            color: #856404;
        }

        .warning-text i {
            color: #f39c12;
            font-size: 1.1rem;
            margin-top: 0.1rem;
            flex-shrink: 0;
        }

        .feed-info {
            background: #f8f9fa;
            border-radius: 6px;
            padding: 1rem;
            margin-top: 1.5rem;
            border: 1px solid #e9ecef;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #dee2e6;
        }

        .info-row:last-child {
            border-bottom: none;
        }

        .info-row strong {
            color: #495057;
            font-weight: 600;
        }

        .create-form-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }

        @media (min-width: 768px) {
            .create-form-grid {
                grid-template-columns: 1fr 1fr;
            }
        }

        .form-section {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1.5rem;
            border: 1px solid #e9ecef;
        }

        .form-section h4 {
            margin: 0 0 1.5rem 0;
            color: var(--primary-blue);
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 0.5rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group:last-child {
            margin-bottom: 0;
        }
        
        .form-row {
            display: flex;
            gap: 1rem;
        }
        
        .form-row .form-group {
            flex: 1;
        }

        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #333;
            font-size: 0.9rem;
        }

        .required {
            color: #dc3545;
            font-weight: bold;
        }

        .form-control {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 0.9rem;
            background-color: white;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }

        .form-control:focus {
            outline: 0;
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 0.2rem rgba(0, 86, 179, 0.25);
        }

        .form-control.error {
            border-color: #dc3545;
        }

        .form-control.error:focus {
            border-color: #dc3545;
            box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
        }

        .error-text {
            display: block;
            margin-top: 0.25rem;
            font-size: 0.8rem;
            color: #dc3545;
        }

        .form-help {
            display: block;
            margin-top: 0.25rem;
            font-size: 0.8rem;
            color: #6c757d;
            font-style: italic;
        }

        .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 1rem;
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid #e9ecef;
        }

        .form-actions .btn {
            min-width: 120px;
            padding: 0.75rem 1.5rem;
        }

        /* Responsive adjustments for create modal */
        @media (max-width: 767px) {
            .create-form-grid {
                grid-template-columns: 1fr;
            }
            
            .form-actions {
                flex-direction: column;
            }
            
            .form-actions .btn {
                width: 100%;
            }
        }
        
        /* Reports Section */
        .report-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }
        
        .report-card {
            background-color: var(--white);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .report-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }
        
        .report-header {
            padding: 20px;
            background-color: var(--light-blue);
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .report-type {
            display: inline-block;
            padding: 4px 10px;
            background-color: var(--primary-blue);
            color: white;
            font-size: 12px;
            font-weight: 600;
            border-radius: 20px;
            margin-bottom: 10px;
        }
        
        .report-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--dark-blue);
        }
        
        .report-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-muted);
            font-size: 13px;
        }
        
        .report-content {
            padding: 20px;
        }
        
        .report-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .report-stat {
            text-align: center;
        }
        
        .stat-number {
            font-size: 24px;
            font-weight: 700;
            color: var(--dark-blue);
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 13px;
            color: var(--text-muted);
        }
        
        .report-actions {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
        }
        
        /* Feed Items */
        .feed-items {
            list-style: none;
        }
        
        .feed-item {
            display: flex;
            gap: 16px;
            padding: 16px 0;
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .feed-item:last-child {
            border-bottom: none;
        }
        
        .feed-icon {
            width: 48px;
            height: 48px;
            border-radius: 8px;
            background-color: var(--light-blue);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary-blue);
            font-size: 20px;
            flex-shrink: 0;
        }
        
        .feed-details {
            flex: 1;
        }
        
        .feed-name {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--dark-blue);
        }
        
        .feed-description {
            color: var(--text-muted);
            font-size: 14px;
            margin-bottom: 8px;
        }
        
        .feed-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
        }
        
        .feed-stats {
            display: flex;
            gap: 15px;
        }
        
        .feed-badges {
            display: flex;
            gap: 8px;
        }
        
        /* Pagination */
        .pagination {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 5px;
            margin-top: 20px;
        }
        
        .page-item {
            width: 32px;
            height: 32px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .page-item:hover:not(.disabled) {
            background-color: var(--light-blue);
        }
        
        .page-item.active {
            background-color: var(--primary-blue);
            color: white;
        }

        .page-item.disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .tab {
            cursor: pointer;
        }
        
        /* Chart Containers */
        .chart-container {
            height: 300px;
            position: relative;
        }
        
        /* Tabs */
        .tabs {
            display: flex;
            border-bottom: 1px solid var(--medium-gray);
            margin-bottom: 20px;
        }
        
        .tab {
            padding: 12px 20px;
            font-size: 14px;
            font-weight: 600;
            color: var(--text-muted);
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        
        .tab:hover {
            color: var(--primary-blue);
        }
        
        .tab.active {
            color: var(--primary-blue);
            border-bottom-color: var(--primary-blue);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* Helper classes */
        .text-danger {
            color: var(--danger);
        }
        
        .text-success {
            color: var(--success);
        }
        
        .text-warning {
            color: var(--warning);
        }
        
        .text-muted {
            color: var(--text-muted);
        }
        
        .mt-4 {
            margin-top: 16px;
        }
        
        .mb-4 {
            margin-bottom: 16px;
        }
        
        /* Responsive Design */
        @media (max-width: 1200px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .report-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 992px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 768px) {
            .nav-links a {
                padding: 16px 10px;
                font-size: 14px;
            }
            
            .search-bar input {
                width: 160px;
            }
            
            .search-bar input:focus {
                width: 200px;
            }
            
            .status-indicator {
                display: none;
            }
            
            .report-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 576px) {
            .header-container {
                flex-direction: column;
                gap: 15px;
            }
            
            .nav-actions {
                width: 100%;
                justify-content: center;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .page-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }
        }

        /* Modal Styles */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .modal-content {
            background: white;
            border-radius: 8px;
            width: 90%;
            max-width: 600px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        .modal-header {
            padding: 1.5rem;
            border-bottom: 1px solid var(--medium-gray);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .modal-header h2 {
            margin: 0;
            color: var(--text-dark);
            font-size: 1.25rem;
        }

        .modal-close {
            background: none;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            color: var(--text-muted);
            padding: 0.5rem;
            border-radius: 4px;
            transition: background-color 0.2s;
        }

        .modal-close:hover {
            background-color: var(--medium-gray);
        }

        .modal-body {
            padding: 1.5rem;
        }

        .form-group {
            margin-bottom: 1rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: var(--text-dark);
            font-weight: 500;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid var(--medium-gray);
            border-radius: 4px;
            font-size: 0.875rem;
            transition: border-color 0.2s;
        }

        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            outline: none;
            border-color: var(--secondary-blue);
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }

        .checkbox-label {
            display: flex !important;
            align-items: center;
            gap: 0.5rem;
            cursor: pointer;
        }

        /* Profile Styles */
        .profile-content {
            max-width: 800px;
            margin: 0 auto;
        }

        .profile-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .profile-header {
            background: linear-gradient(135deg, #0056b3, #004494);
            color: white;
            padding: 2rem;
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }

        .profile-avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
        }

        .profile-info h3 {
            margin: 0 0 0.5rem 0;
            font-size: 1.5rem;
            font-weight: 600;
        }

        .profile-role {
            margin: 0;
            opacity: 0.9;
            font-size: 1rem;
            text-transform: uppercase;
            font-weight: 500;
            letter-spacing: 0.5px;
        }

        .profile-details {
            padding: 2rem;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
        }

        .info-item {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .info-item label {
            font-weight: 600;
            color: #666;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .info-item span {
            font-size: 1rem;
            color: #333;
            padding: 0.5rem 0;
            border-bottom: 1px solid #eee;
        }

        .role-badge {
            display: inline-block;
            padding: 0.5rem 1rem !important;
            border-radius: 20px;
            font-size: 0.875rem !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: none !important;
        }

        .role-badge.bluevisionadmin {
            background: #d4edda;
            color: #155724;
        }

        .role-badge.admin {
            background: #fff3cd;
            color: #856404;
        }

        .role-badge.publisher {
            background: #cce5ff;
            color: #004085;
        }

        .role-badge.viewer {
            background: #f8f9fa;
            color: #495057;
        }

        .edit-form {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .form-actions {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #eee;
        }

        .checkbox-label input[type="checkbox"] {
            width: auto !important;
            margin: 0;
        }

        .modal-footer {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
            margin-top: 1.5rem;
        }

        /* Additional styles for Add IoC Modal */
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            color: var(--text-dark);
            font-weight: 500;
            font-size: 0.875rem;
        }

        .form-control {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid var(--medium-gray);
            border-radius: 6px;
            font-size: 0.875rem;
            background-color: white;
            transition: all 0.2s;
            box-sizing: border-box;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 3px rgba(52, 144, 220, 0.1);
        }

        .form-control.error {
            border-color: #dc3545;
        }

        .form-control.error:focus {
            border-color: #dc3545;
            box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
        }

        .form-range {
            width: 100%;
            -webkit-appearance: none;
            appearance: none;
            height: 6px;
            border-radius: 3px;
            background: var(--medium-gray);
            outline: none;
            margin: 0.5rem 0;
        }

        .form-range::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--primary-blue);
            cursor: pointer;
            transition: background 0.2s;
        }

        .form-range::-webkit-slider-thumb:hover {
            background: var(--secondary-blue);
        }

        .form-range::-moz-range-thumb {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--primary-blue);
            cursor: pointer;
            border: none;
        }

        .range-labels {
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }

        .error-text {
            color: #dc3545;
            font-size: 0.75rem;
            margin-top: 0.25rem;
            display: block;
        }

        .modal-actions {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid var(--medium-gray);
        }

        .export-info {
            margin: 1.5rem 0;
        }

        .info-card {
            display: flex;
            gap: 1rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid var(--primary-blue);
        }

        .info-card i {
            color: var(--primary-blue);
            font-size: 1.25rem;
            margin-top: 0.25rem;
        }

        .info-card p {
            margin: 0.5rem 0;
            font-size: 0.875rem;
            color: var(--text-muted);
        }

        .info-card strong {
            color: var(--text-dark);
        }

        /* Export Modal Styles */
        .export-modal {
            width: 90%;
            max-width: 800px;
            max-height: 90vh;
            overflow-y: auto;
        }

        .format-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }

        .format-option {
            cursor: pointer;
            position: relative;
        }

        .format-option input[type="radio"] {
            position: absolute;
            opacity: 0;
            pointer-events: none;
        }

        .format-card {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
            padding: 1.5rem 1rem;
            border: 2px solid var(--light-gray);
            border-radius: 8px;
            background: white;
            transition: all 0.2s ease;
            text-align: center;
        }

        .format-option:hover .format-card {
            border-color: var(--primary-blue);
            box-shadow: 0 2px 8px rgba(52, 152, 219, 0.15);
        }

        .format-option input[type="radio"]:checked + .format-card {
            border-color: var(--primary-blue);
            background: #f8f9fa;
            box-shadow: 0 2px 8px rgba(52, 152, 219, 0.2);
        }

        .format-card i {
            font-size: 2rem;
            color: var(--text-muted);
            transition: color 0.2s ease;
        }

        .format-option:hover .format-card i,
        .format-option input[type="radio"]:checked + .format-card i {
            color: var(--primary-blue);
        }

        .format-card span {
            font-weight: 600;
            color: var(--text-dark);
            font-size: 1rem;
        }

        .format-card small {
            color: var(--text-muted);
            font-size: 0.75rem;
        }

        .form-section {
            margin: 2rem 0;
            padding: 1.5rem;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid var(--primary-blue);
        }

        .form-section h4 {
            margin: 0 0 1rem 0;
            color: var(--text-dark);
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .form-section h4 i {
            color: var(--primary-blue);
        }

        .checkbox-group {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .checkbox-label {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            cursor: pointer;
            font-size: 0.875rem;
        }

        .checkbox-label input[type="checkbox"] {
            width: 16px;
            height: 16px;
            accent-color: var(--primary-blue);
        }

        .checkbox-label span {
            color: var(--text-dark);
        }

        .form-help {
            display: block;
            margin-top: 0.25rem;
            font-size: 0.75rem;
            color: var(--text-muted);
            font-style: italic;
        }

        .alert {
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .alert-error {
            background: #ffeaea;
            border: 1px solid #ffb3b3;
            color: #d8000c;
        }

        .alert-error i {
            color: #d8000c;
        }

        @media (max-width: 768px) {
            .modal-content {
                width: 95%;
                margin: 1rem;
            }
            
            .form-row {
                grid-template-columns: 1fr;
            }

            .form-grid {
                grid-template-columns: 1fr;
            }

            .modal-actions {
                flex-direction: column;
            }
        }

        /* Feed Consumption Controls */
        .feed-consumption-controls {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            margin-right: 1rem;
        }

        .feed-selection-wrapper {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            min-width: 280px;
        }

        .feed-selector {
            font-size: 0.875rem;
            padding: 0.5rem 0.75rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            background: white;
            color: var(--text-dark);
            transition: border-color 0.2s ease;
        }

        .feed-selector:focus {
            outline: none;
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 2px rgba(0, 86, 179, 0.1);
        }

        .feed-selector:disabled {
            background-color: #f5f5f5;
            cursor: not-allowed;
            opacity: 0.6;
        }

        .consumption-options {
            margin-top: 0.25rem;
        }

        .consumption-info {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-muted);
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            background: rgba(0, 86, 179, 0.05);
            border-radius: 4px;
            border: 1px solid rgba(0, 86, 179, 0.1);
        }

        .consumption-info i {
            color: var(--primary-blue);
            font-size: 0.7rem;
        }

        .consume-btn {
            align-self: flex-start;
            white-space: nowrap;
            padding: 0.5rem 1rem;
            min-height: 36px;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .consume-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        /* Feed Analysis Overview Styles */
        .feed-analysis-overview {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .overview-cards {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 1.5rem;
        }

        .feed-comparison-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }

        .feed-stat-card {
            padding: 1rem;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: white;
            transition: box-shadow 0.2s ease;
        }

        .feed-stat-card:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .feed-name {
            font-weight: 600;
            color: var(--text-dark);
            margin-bottom: 0.75rem;
            font-size: 0.95rem;
        }

        .feed-stats {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.75rem;
        }

        .feed-stats .stat-item {
            text-align: center;
        }

        .feed-stats .stat-value {
            display: block;
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary-blue);
        }

        .feed-stats .stat-label {
            display: block;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }

        .feed-type {
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .feed-type.external {
            background: rgba(255, 193, 7, 0.1);
            color: #ff8800;
            border: 1px solid rgba(255, 193, 7, 0.3);
        }

        .feed-type.internal {
            background: rgba(40, 167, 69, 0.1);
            color: #28a745;
            border: 1px solid rgba(40, 167, 69, 0.3);
        }

        /* Technique Frequency List */
        .technique-frequency-list {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .frequency-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 0.75rem;
            border: 1px solid #eee;
            border-radius: 6px;
            background: #fafafa;
        }

        .technique-rank {
            font-weight: 700;
            color: var(--primary-blue);
            min-width: 30px;
            text-align: center;
        }

        .technique-details {
            flex: 1;
        }

        .technique-id {
            font-weight: 600;
            color: var(--text-dark);
            margin-bottom: 0.25rem;
        }

        .technique-stats {
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        .frequency-bar {
            flex: 0 0 100px;
            height: 8px;
            background: #eee;
            border-radius: 4px;
            overflow: hidden;
        }

        .frequency-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-blue), #4CAF50);
            transition: width 0.3s ease;
        }

        /* Seasonal Analysis */
        .seasonal-analysis {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .seasonal-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
        }

        .seasonal-stats .stat-card {
            text-align: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #ddd;
        }

        .seasonal-stats .stat-card .stat-value {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--primary-blue);
        }

        .seasonal-stats .stat-card .stat-label {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.5rem;
        }

        .seasonal-interpretation {
            padding: 1rem;
            background: rgba(0, 86, 179, 0.05);
            border-left: 4px solid var(--primary-blue);
            border-radius: 0 8px 8px 0;
        }

        .seasonal-interpretation p {
            margin: 0;
            color: var(--text-dark);
            font-size: 0.875rem;
            line-height: 1.5;
        }

        /* Intelligence Status Badges */
        .status-badge {
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }

        .status-badge.anonymized {
            background: rgba(255, 193, 7, 0.1);
            color: #ff8800;
            border: 1px solid rgba(255, 193, 7, 0.3);
        }

        .status-badge.raw {
            background: rgba(40, 167, 69, 0.1);
            color: #28a745;
            border: 1px solid rgba(40, 167, 69, 0.3);
        }

        .technique-badge, .tactic-badge {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
            background: rgba(0, 86, 179, 0.1);
            color: var(--primary-blue);
            border: 1px solid rgba(0, 86, 179, 0.2);
        }

        /* Intelligence Summary */
        .intelligence-summary {
            padding: 1rem;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }

        .summary-stats {
            display: flex;
            gap: 2rem;
            align-items: center;
            flex-wrap: wrap;
        }

        .intelligence-summary .summary-stats .stat-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
            color: var(--text-dark);
        }

        .intelligence-summary .summary-stats .stat-item i {
            color: var(--primary-blue);
        }

        /* TTP Name Cell */
        .ttp-name-cell .ttp-title {
            font-weight: 500;
            color: var(--text-dark);
            margin-bottom: 0.25rem;
        }

        .ttp-name-cell .ttp-subtechnique {
            font-size: 0.75rem;
            color: var(--text-muted);
            font-style: italic;
        }

        /* Feed Source Cell */
        .feed-source-cell {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .feed-source-cell .feed-name {
            font-weight: 500;
            color: var(--text-dark);
            margin-bottom: 0;
        }

        /* Trends Analysis */
        .trends-analysis {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .trends-content {
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }

        .trend-charts-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 2rem;
        }

        .chart-container h3, .tactic-distribution h3 {
            margin: 0 0 1rem 0;
            color: var(--text-dark);
            font-size: 1.1rem;
        }

        .tactic-bars {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .tactic-bar-item {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .tactic-label {
            min-width: 120px;
            font-size: 0.75rem;
            font-weight: 500;
            color: var(--text-dark);
            text-transform: capitalize;
        }

        .bar-container {
            flex: 1;
            height: 20px;
            background: #eee;
            border-radius: 10px;
            overflow: hidden;
        }

        .bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-blue), #4CAF50);
            transition: width 0.3s ease;
        }

        .bar-value {
            min-width: 30px;
            text-align: right;
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-dark);
        }

        /* Trend Insights */
        .trend-insights h3 {
            margin: 0 0 1rem 0;
            color: var(--text-dark);
            font-size: 1.1rem;
        }

        .insights-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }

        .insight-card {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            padding: 1rem;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            transition: box-shadow 0.2s ease;
        }

        .insight-card:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .insight-card i {
            color: var(--primary-blue);
            font-size: 1.5rem;
            margin-top: 0.25rem;
        }

        .insight-card h4 {
            margin: 0 0 0.5rem 0;
            color: var(--text-dark);
            font-size: 0.95rem;
        }

        .insight-card p {
            margin: 0;
            color: var(--text-muted);
            font-size: 0.825rem;
            line-height: 1.4;
        }

        /* Alert improvements */
        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 0.875rem;
            line-height: 1.4;
        }

        .alert.alert-success {
            background: rgba(40, 167, 69, 0.1);
            color: #155724;
            border: 1px solid rgba(40, 167, 69, 0.2);
        }

        .alert.alert-error {
            background: rgba(220, 53, 69, 0.1);
            color: #721c24;
            border: 1px solid rgba(220, 53, 69, 0.2);
        }

        .alert i {
            font-size: 1rem;
            flex-shrink: 0;
        }

        @media (max-width: 768px) {
            .feed-consumption-controls {
                flex-direction: column;
                gap: 1rem;
            }

            .feed-selection-wrapper {
                min-width: auto;
            }

            .overview-cards {
                grid-template-columns: 1fr;
            }

            .trend-charts-grid {
                grid-template-columns: 1fr;
            }

            .summary-stats {
                gap: 1rem;
            }
        }

      `}
    </style>
  );
}

// Notifications Component
function Notifications({ active }) {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (active) {
      // Simulated notifications data
      setTimeout(() => {
        setNotifications([
          {
            id: '1',
            type: 'threat_alert',
            title: 'New High-Priority Threat Detected',
            message: 'A new malware strain has been identified in your organization\'s threat feed.',
            severity: 'high',
            read: false,
            created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          },
          {
            id: '2',
            type: 'trust_request',
            title: 'Trust Relationship Request',
            message: 'Organization "CyberSecure Inc." has requested a bilateral trust relationship.',
            severity: 'medium',
            read: false,
            created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          },
          {
            id: '3',
            type: 'feed_update',
            title: 'Threat Feed Updated',
            message: 'Your subscribed threat feed "MITRE ATT&CK" has been updated with 15 new indicators.',
            severity: 'low',
            read: true,
            created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          }
        ]);
        setLoading(false);
      }, 500);
    }
  }, [active]);

  const markAsRead = (notificationId) => {
    setNotifications(prev =>
      prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
    );
  };

  const deleteNotification = (notificationId) => {
    setNotifications(prev => prev.filter(n => n.id !== notificationId));
  };

  if (!active) return null;

  return (
    <section id="notifications" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Notifications</h1>
          <p className="page-subtitle">Stay updated with system alerts and activities</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline">
            <i className="fas fa-check-double"></i> Mark All Read
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading notifications...</p>
        </div>
      ) : (
        <div className="notifications-list">
          {notifications.length === 0 ? (
            <div className="empty-state">
              <i className="fas fa-bell-slash" style={{fontSize: '48px', color: '#dee2e6'}}></i>
              <h3>No notifications</h3>
              <p>You're all caught up! No notifications to show.</p>
            </div>
          ) : (
            notifications.map(notification => (
              <div key={notification.id} className={`notification-item ${!notification.read ? 'unread' : ''}`}>
                <div className="notification-content">
                  <div className="notification-header">
                    <div className="notification-icon">
                      <i className={
                        notification.type === 'threat_alert' ? 'fas fa-exclamation-triangle' :
                        notification.type === 'trust_request' ? 'fas fa-handshake' :
                        'fas fa-rss'
                      } style={{
                        color: notification.severity === 'high' ? '#dc3545' :
                               notification.severity === 'medium' ? '#ffc107' : '#28a745'
                      }}></i>
                    </div>
                    <div className="notification-meta">
                      <h4>{notification.title}</h4>
                      <div className="meta-info">
                        <span>{new Date(notification.created_at).toLocaleString()}</span>
                        {!notification.read && <span className="unread-dot"></span>}
                      </div>
                    </div>
                  </div>
                  <p className="notification-message">{notification.message}</p>
                </div>
                <div className="notification-actions">
                  {!notification.read && (
                    <button
                      onClick={() => markAsRead(notification.id)}
                      className="btn btn-sm btn-outline"
                    >
                      <i className="fas fa-check"></i>
                    </button>
                  )}
                  <button
                    onClick={() => deleteNotification(notification.id)}
                    className="btn btn-sm btn-danger"
                  >
                    <i className="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </section>
  );
}


// Entry point
function CRISPApp() {
  return (
    <>
      <CSSStyles />
      <App />
    </>
  );
}

export default CRISPApp;
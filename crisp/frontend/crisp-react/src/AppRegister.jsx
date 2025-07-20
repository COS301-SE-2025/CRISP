import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { useNavigate } from 'react-router-dom';
import CSSStyles from './assets/CSSStyles';
import logoImage from './assets/BlueV2.png';
import { getUserProfile, updateUserProfile, getUserStatistics, changePassword, getEmailStatistics, getSystemHealth, sendTestEmail, testGmailConnection } from './api.js';
import LoadingSpinner from './components/LoadingSpinner.jsx';
import UserManagement from './components/UserManagement.jsx';
import InstitutionManagement from './components/InstitutionManagement.jsx';
import TrustManagement from './components/TrustManagement.jsx';
import ErrorBoundary from './components/ErrorBoundary.jsx';


function AppRegister({ user, onLogout }) {
  const navigate = useNavigate();
  // State to manage the active page
  const [activePage, setActivePage] = useState('dashboard');
  const [isLoading, setIsLoading] = useState(false);

  // Function to switch between pages
  const showPage = (pageId) => {
    setIsLoading(true);
    setTimeout(() => {
      setActivePage(pageId);
      setIsLoading(false);
    }, 800);
  };

  // Function to navigate to RegisterUser page
  const navigateToRegisterUser = () => {
    setIsLoading(true);
    setTimeout(() => {
      navigate('/register-user');
      setIsLoading(false);
    }, 800);
  };

  // Add resize listener to handle chart resizing when zooming
  useEffect(() => {
    const handleResize = () => {
      // This forces a redraw of charts when window size changes (including zoom)
      if (activePage === 'dashboard') {
        const event = new Event('resize');
        window.dispatchEvent(event);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [activePage]);

  return (
    <div className="App">
      {/* Include CSS styles */}
      <CSSStyles />
      {isLoading && <LoadingSpinner fullscreen={true} />}
      
      {/* Header */}
      <Header user={user} onLogout={onLogout} navigateToRegisterUser={navigateToRegisterUser} showPage={showPage} />
      
      {/* Main Navigation */}
      <MainNav activePage={activePage} showPage={showPage} />

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {/* Dashboard */}
          <Dashboard active={activePage === 'dashboard'} />

          {/* Threat Feeds */}
          <ThreatFeeds active={activePage === 'threat-feeds'} />

          {/* IoC Management */}
          <IoCManagement active={activePage === 'ioc-management'} />

          {/* TTP Analysis */}
          <TTPAnalysis active={activePage === 'ttp-analysis'} />

          {/* Institutions */}
          <Institutions active={activePage === 'institutions'} />

          {/* Reports */}
          <Reports active={activePage === 'reports'} />

          {/* Alerts */}
          <Alerts active={activePage === 'alerts'} />

          {/* Notifications */}
          <Notifications active={activePage === 'notifications'} />

          {/* Profile */}
          <ErrorBoundary>
            <Profile active={activePage === 'profile'} user={user} />
          </ErrorBoundary>

          {/* User Management */}
          <ErrorBoundary>
            <UserManagement active={activePage === 'user-management'} />
          </ErrorBoundary>

          {/* Institution Management */}
          <ErrorBoundary>
            <InstitutionManagement active={activePage === 'institution-management'} />
          </ErrorBoundary>

          {/* Trust Management */}
          <ErrorBoundary>
            <TrustManagement active={activePage === 'trust-management'} />
          </ErrorBoundary>

          {/* Account Settings */}
          <ErrorBoundary>
            <AccountSettings active={activePage === 'account-settings'} user={user} />
          </ErrorBoundary>

          {/* Admin Settings */}
          <ErrorBoundary>
            <AdminSettings active={activePage === 'admin-settings'} onNavigate={showPage} />
          </ErrorBoundary>
        </div>
      </main>
    </div>
  );
}

// Header Component with notifications and user management
function Header({ user, onLogout, navigateToRegisterUser, showPage }) {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showManagementSubmenu, setShowManagementSubmenu] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [systemStats, setSystemStats] = useState(null);
  const [isLoadingNotifications, setIsLoadingNotifications] = useState(false);

  // Fetch notifications and system stats on component mount
  useEffect(() => {
    fetchNotifications();
    fetchSystemStats();
  }, []);

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

      // Generate notifications based on system health
      if (systemHealth) {
        if (systemHealth.status === 'healthy') {
          generatedNotifications.push({
            id: notificationId++,
            type: 'info',
            title: 'System health check passed',
            message: 'All system components are functioning normally',
            timestamp: new Date(Date.now() - 2 * 60 * 60000),
            read: true,
          });
        } else {
          generatedNotifications.push({
            id: notificationId++,
            type: 'critical',
            title: 'System health warning',
            message: `System status: ${systemHealth.status}`,
            timestamp: new Date(Date.now() - 10 * 60000),
            read: false,
          });
        }
      }

      // Add some default admin notifications if we don't have much data
      if (generatedNotifications.length < 2) {
        generatedNotifications.push(
          {
            id: notificationId++,
            type: 'warning',
            title: 'User registration pending approval',
            message: 'New user account requires admin approval',
            timestamp: new Date(Date.now() - 2 * 60 * 60000),
            read: false,
          },
          {
            id: notificationId++,
            type: 'info',
            title: 'Welcome to CRISP Admin',
            message: 'Your administrator account is now active',
            timestamp: new Date(Date.now() - 24 * 60 * 60000),
            read: true,
          }
        );
      }

      setNotifications(generatedNotifications);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
      // Fallback notifications
      setNotifications([
        {
          id: 1,
          type: 'info',
          title: 'Welcome to CRISP',
          message: 'Your administrator dashboard is ready',
          timestamp: new Date(),
          read: false,
        }
      ]);
    } finally {
      setIsLoadingNotifications(false);
    }
  };

  const fetchSystemStats = async () => {
    try {
      const stats = await getSystemHealth();
      setSystemStats(stats);
    } catch (error) {
      console.error('Failed to fetch system stats:', error);
      setSystemStats({ status: 'unknown', message: 'Unable to fetch system status' });
    }
  };

  const unreadCount = notifications.filter(n => !n.read).length;
  
  // Get first initial for avatar
  const userInitial = user && user.username ? user.username.charAt(0).toUpperCase() : 'A';
  const userName = user && user.username ? user.username.split('@')[0] : 'Admin';
  const userRole = user && user.role ? user.role : 'Administrator';

  const handleNotificationClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setShowNotifications(!showNotifications);
    setShowUserMenu(false);
    setShowManagementSubmenu(false);
  };

  const handleUserMenuClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setShowUserMenu(!showUserMenu);
    setShowNotifications(false);
  };

  const handleNotificationItemClick = (notification) => {
    console.log('Notification clicked:', notification.id);
  };

  const handleViewAllNotifications = () => {
    setShowNotifications(false);
    if (showPage) showPage('notifications');
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'critical': return 'fas fa-exclamation-triangle';
      case 'warning': return 'fas fa-exclamation-circle';
      case 'info': return 'fas fa-info-circle';
      default: return 'fas fa-bell';
    }
  };

  const formatTime = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(diff / 86400000)}d ago`;
  };

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.notifications-container') && !event.target.closest('.user-profile-container')) {
        setShowNotifications(false);
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
        <div className="logo">
          <img src={logoImage} alt="CRISP Logo" className="logo-image" />
          <span className="logo-text">CRISP</span>
        </div>
        <div className="nav-actions">
          <div className="search-bar">
            <span className="search-icon"><i className="fas fa-search"></i></span>
            <input type="text" placeholder="Search platform..." />
          </div>
          
          {/* Notifications Dropdown */}
          <div className="notifications-container">
            <button className="notifications" onClick={handleNotificationClick} type="button">
              <i className="fas fa-bell"></i>
              {unreadCount > 0 && <span className="notification-count">{unreadCount}</span>}
            </button>
            
            {showNotifications && (
              <div className="notifications-dropdown">
                <div className="dropdown-header">
                  <h3>Notifications</h3>
                  <span className="close-btn" onClick={() => setShowNotifications(false)}>
                    <i className="fas fa-times"></i>
                  </span>
                </div>
                <div className="notifications-list">
                  {isLoadingNotifications ? (
                    <div className="loading-notifications">
                      <i className="fas fa-spinner fa-spin"></i> Loading notifications...
                    </div>
                  ) : notifications.length > 0 ? (
                    notifications.slice(0, 5).map(notification => (
                      <div 
                        key={notification.id}
                        className={`notification-item ${notification.read ? 'read' : 'unread'}`}
                        onClick={() => handleNotificationItemClick(notification)}
                      >
                        <div className="notification-icon">
                          <i className={getNotificationIcon(notification.type)}></i>
                        </div>
                        <div className="notification-content">
                          <div className="notification-title">{notification.title}</div>
                          <div className="notification-message">{notification.message}</div>
                          <div className="notification-time">{formatTime(notification.timestamp)}</div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="no-notifications">No new notifications</div>
                  )}
                </div>
                <div className="dropdown-footer">
                  <button 
                    className="btn btn-sm btn-outline"
                    onClick={handleViewAllNotifications}
                    type="button"
                  >
                    View All Notifications
                  </button>
                </div>
              </div>
            )}
          </div>
          
          {/* User Profile Menu */}
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
                        <button className="submenu-item" onClick={() => {setShowUserMenu(false); setShowManagementSubmenu(false); showPage('institution-management');}} type="button">
                          <i className="fas fa-university"></i>
                          <span>Institution Management</span>
                        </button>
                        <button className="submenu-item" onClick={() => {setShowUserMenu(false); setShowManagementSubmenu(false); showPage('trust-management');}} type="button">
                          <i className="fas fa-handshake"></i>
                          <span>Trust Management</span>
                        </button>
                      </div>
                    )}
                  </div>
                  <button className="menu-item" onClick={() => {setShowUserMenu(false); showPage('admin-settings');}} type="button">
                    <i className="fas fa-shield-alt"></i>
                    <span>Admin Settings</span>
                  </button>
                  <button className="menu-item" onClick={() => {setShowUserMenu(false); navigateToRegisterUser();}} type="button">
                    <i className="fas fa-user-plus"></i>
                    <span>Register New User</span>
                  </button>
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
function MainNav({ activePage, showPage }) {
  const navItems = [
    { id: 'dashboard', icon: 'fas fa-chart-line', label: 'Dashboard' },
    { id: 'threat-feeds', icon: 'fas fa-rss', label: 'Threat Feeds' },
    { id: 'ioc-management', icon: 'fas fa-search', label: 'IoC Management' },
    { id: 'ttp-analysis', icon: 'fas fa-sitemap', label: 'TTP Analysis' },
    { id: 'institutions', icon: 'fas fa-building', label: 'Institutions' },
    { id: 'reports', icon: 'fas fa-file-alt', label: 'Reports' }
  ];

  const handleNavClick = (itemId) => {
    console.log('MainNav item clicked:', itemId);
    showPage(itemId);
  };

  return (
    <nav className="main-nav">
      <div className="container nav-container">
        <ul className="nav-links">
          {navItems.map((item) => (
            <li key={item.id}>
              <a 
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  handleNavClick(item.id);
                }} 
                className={activePage === item.id ? 'active' : ''}
                title={item.label}
              >
                <i className={item.icon}></i> {item.label}
              </a>
            </li>
          ))}
        </ul>
        <div className="nav-right">
          <div className="status-indicator">
            <span className="status-dot"></span>
            <span>System Online</span>
          </div>
        </div>
      </div>
    </nav>
  );
}

// Dashboard Component
function Dashboard({ active }) {
  // D3 Chart References
  const chartRef = useRef(null);
  
  // Set up D3 charts when component mounts or window resizes
  useEffect(() => {
    if (active && chartRef.current) {
      createThreatActivityChart();
      
      // Add resize handler for responsive charts
      const handleResize = () => {
        createThreatActivityChart();
      };
      
      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }
  }, [active]);

  const createThreatActivityChart = () => {
    // Only proceed if the chart reference exists
    if (!chartRef.current) return;
    
    // Clear previous chart if any
    d3.select(chartRef.current).selectAll("*").remove();
    
    // Sample data
    const data = [
      { date: "2025-04-20", count: 45 },
      { date: "2025-04-21", count: 52 },
      { date: "2025-04-22", count: 49 },
      { date: "2025-04-23", count: 63 },
      { date: "2025-04-24", count: 58 },
      { date: "2025-04-25", count: 72 },
      { date: "2025-04-26", count: 68 },
      { date: "2025-04-27", count: 75 },
      { date: "2025-04-28", count: 82 },
      { date: "2025-04-29", count: 78 },
      { date: "2025-04-30", count: 86 },
      { date: "2025-05-01", count: 91 },
      { date: "2025-05-02", count: 84 },
      { date: "2025-05-03", count: 76 },
      { date: "2025-05-04", count: 80 },
      { date: "2025-05-05", count: 89 },
      { date: "2025-05-06", count: 95 },
      { date: "2025-05-07", count: 101 },
      { date: "2025-05-08", count: 96 },
      { date: "2025-05-09", count: 104 },
      { date: "2025-05-10", count: 112 },
      { date: "2025-05-11", count: 108 },
      { date: "2025-05-12", count: 115 },
      { date: "2025-05-13", count: 120 },
      { date: "2025-05-14", count: 118 },
      { date: "2025-05-15", count: 125 },
      { date: "2025-05-16", count: 132 },
      { date: "2025-05-17", count: 136 },
      { date: "2025-05-18", count: 129 },
      { date: "2025-05-19", count: 138 },
    ];

    // Set dimensions based on current container size to handle zoom
    const width = chartRef.current.clientWidth || 500; // Fallback size if clientWidth is 0
    const height = 300;
    const margin = { top: 30, right: 30, bottom: 40, left: 50 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Create responsive SVG container
    const svg = d3.select(chartRef.current)
      .append("svg")
      .attr("width", "100%") // Use 100% for responsive width
      .attr("height", height)
      .attr("viewBox", `0 0 ${width} ${height}`) // Add viewBox for better scaling
      .attr("preserveAspectRatio", "xMidYMid meet") // Preserve aspect ratio
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Parse dates
    const parseDate = d3.timeParse("%Y-%m-%d");
    const formattedData = data.map(d => ({
      date: parseDate(d.date),
      count: d.count
    }));

    // Set up scales
    const x = d3.scaleTime()
      .domain(d3.extent(formattedData, d => d.date))
      .range([0, innerWidth]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(formattedData, d => d.count) * 1.1])
      .range([innerHeight, 0]);

    // Add axes
    svg.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x).ticks(7).tickFormat(d3.timeFormat("%d %b")));

    svg.append("g")
      .call(d3.axisLeft(y));

    // Add gradient for area fill
    const gradient = svg.append("defs")
      .append("linearGradient")
      .attr("id", "areaGradient")
      .attr("x1", "0%")
      .attr("y1", "0%")
      .attr("x2", "0%")
      .attr("y2", "100%");

    gradient.append("stop")
      .attr("offset", "0%")
      .attr("stop-color", "rgba(0, 86, 179, 0.8)")
      .attr("stop-opacity", 0.8);

    gradient.append("stop")
      .attr("offset", "100%")
      .attr("stop-color", "rgba(0, 160, 233, 0.2)")
      .attr("stop-opacity", 0.2);

    // Add area chart
    svg.append("path")
      .datum(formattedData)
      .attr("fill", "url(#areaGradient)")
      .attr("d", d3.area()
        .x(d => x(d.date))
        .y0(innerHeight)
        .y1(d => y(d.count))
      );

    // Add line
    svg.append("path")
      .datum(formattedData)
      .attr("fill", "none")
      .attr("stroke", "#0056b3")
      .attr("stroke-width", 2)
      .attr("d", d3.line()
        .x(d => x(d.date))
        .y(d => y(d.count))
      );

    // Add title
    svg.append("text")
      .attr("x", innerWidth / 2)
      .attr("y", -10)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "600")
      .style("fill", "#2d3748")
      .text("Threat Activity Trends");
  };

  return (
    <section id="dashboard" className={`page-section ${active ? 'active' : ''}`}>
      {/* Dashboard Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Threat Intelligence Dashboard</h1>
          <p className="page-subtitle">Overview of threat intelligence and platform activity</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline"><i className="fas fa-download"></i> Export Data</button>
          <button className="btn btn-primary"><i className="fas fa-plus"></i> Add New Feed</button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-search"></i></div>
            <span>Active IoCs</span>
          </div>
          <div className="stat-value">1,286</div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>24% from last week</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-building"></i></div>
            <span>Connected Institutions</span>
          </div>
          <div className="stat-value">42</div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>3 new this month</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-rss"></i></div>
            <span>Threat Feeds</span>
          </div>
          <div className="stat-value">18</div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>2 new feeds</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-exclamation-triangle"></i></div>
            <span>Critical Alerts</span>
          </div>
          <div className="stat-value">7</div>
          <div className="stat-change decrease">
            <span><i className="fas fa-arrow-down"></i></span>
            <span>12% from yesterday</span>
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
                <button className="btn btn-outline btn-sm"><i className="fas fa-sync-alt"></i> Refresh</button>
              </div>
            </div>
            <div className="card-content">
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
                  <tr>
                    <td>IP Address</td>
                    <td>192.168.144.32</td>
                    <td>CIRCL MISP</td>
                    <td><span className="badge badge-high">High</span></td>
                    <td>
                      <div className="badge-tags">
                        <span className="badge badge-active">Active</span>
                        <span className="badge badge-low">Verified</span>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td>Domain</td>
                    <td>malicious-ransomware.net</td>
                    <td>Internal</td>
                    <td><span className="badge badge-high">High</span></td>
                    <td>
                      <div className="badge-tags">
                        <span className="badge badge-active">Active</span>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td>File Hash</td>
                    <td>a45f3d9e7b12c04...</td>
                    <td>SANReN CSIRT</td>
                    <td><span className="badge badge-medium">Medium</span></td>
                    <td>
                      <div className="badge-tags">
                        <span className="badge badge-active">Active</span>
                        <span className="badge badge-low">Shared</span>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td>URL</td>
                    <td>https://download.malicious-file.com</td>
                    <td>SABRIC</td>
                    <td><span className="badge badge-medium">Medium</span></td>
                    <td>
                      <div className="badge-tags">
                        <span className="badge badge-active">Active</span>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td>Email</td>
                    <td>phishing@suspicious-mail.org</td>
                    <td>Internal</td>
                    <td><span className="badge badge-low">Low</span></td>
                    <td>
                      <div className="badge-tags">
                        <span className="badge badge-medium">Under Review</span>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td>TTP</td>
                    <td>T1566 - Phishing</td>
                    <td>Cyber Security Hub</td>
                    <td><span className="badge badge-high">High</span></td>
                    <td>
                      <div className="badge-tags">
                        <span className="badge badge-active">Active</span>
                        <span className="badge badge-low">Verified</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-chart-area card-icon"></i> Threat Activity Trends</h2>
              <div className="card-actions">
                <button className="btn btn-outline btn-sm"><i className="fas fa-calendar-alt"></i> Last 30 Days</button>
              </div>
            </div>
            <div className="card-content">
              <div className="chart-container" ref={chartRef}>
                {/* D3.js Chart will be rendered here */}
              </div>
            </div>
          </div>
        </div>

        {/* Side Panel */}
        <div className="side-panels">
          {/* Connected Institutions */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-building card-icon"></i> Connected Institutions</h2>
            </div>
            <div className="card-content">
              <ul className="institution-list">
                <li className="institution-item">
                  <div className="institution-logo">UP</div>
                  <div className="institution-details">
                    <div className="institution-name">University of Pretoria</div>
                    <div className="institution-stats">
                      <div className="stat-item"><i className="fas fa-exchange-alt"></i> 125 IoCs</div>
                      <div className="stat-item"><i className="fas fa-clock"></i> 5m ago</div>
                    </div>
                  </div>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '90%' }}></div>
                  </div>
                </li>
                <li className="institution-item">
                  <div className="institution-logo">CS</div>
                  <div className="institution-details">
                    <div className="institution-name">Cyber Security Hub</div>
                    <div className="institution-stats">
                      <div className="stat-item"><i className="fas fa-exchange-alt"></i> 342 IoCs</div>
                      <div className="stat-item"><i className="fas fa-clock"></i> 17m ago</div>
                    </div>
                  </div>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '85%' }}></div>
                  </div>
                </li>
                <li className="institution-item">
                  <div className="institution-logo">SR</div>
                  <div className="institution-details">
                    <div className="institution-name">SANReN CSIRT</div>
                    <div className="institution-stats">
                      <div className="stat-item"><i className="fas fa-exchange-alt"></i> 208 IoCs</div>
                      <div className="stat-item"><i className="fas fa-clock"></i> 32m ago</div>
                    </div>
                  </div>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '75%' }}></div>
                  </div>
                </li>
                <li className="institution-item">
                  <div className="institution-logo">SB</div>
                  <div className="institution-details">
                    <div className="institution-name">SABRIC</div>
                    <div className="institution-stats">
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
              <ul className="activity-stream">
                <li className="activity-item">
                  <div className="activity-icon"><i className="fas fa-share-alt"></i></div>
                  <div className="activity-details">
                    <div className="activity-text">New IoC batch shared with 4 institutions</div>
                    <div className="activity-meta">
                      <div className="activity-time">10 minutes ago</div>
                      <span className="badge badge-active">Automated</span>
                    </div>
                  </div>
                </li>
                <li className="activity-item">
                  <div className="activity-icon"><i className="fas fa-sync-alt"></i></div>
                  <div className="activity-details">
                    <div className="activity-text">CIRCL MISP feed updated with 28 new indicators</div>
                    <div className="activity-meta">
                      <div className="activity-time">25 minutes ago</div>
                      <span className="badge badge-active">Feed Update</span>
                    </div>
                  </div>
                </li>
                <li className="activity-item">
                  <div className="activity-icon"><i className="fas fa-exclamation-triangle"></i></div>
                  <div className="activity-details">
                    <div className="activity-text">High severity alert: Ransomware campaign targeting education sector</div>
                    <div className="activity-meta">
                      <div className="activity-time">1 hour ago</div>
                      <span className="badge badge-high">Alert</span>
                    </div>
                  </div>
                </li>
                <li className="activity-item">
                  <div className="activity-icon"><i className="fas fa-plus"></i></div>
                  <div className="activity-details">
                    <div className="activity-text">University of Johannesburg connected as new institution</div>
                    <div className="activity-meta">
                      <div className="activity-time">2 hours ago</div>
                      <span className="badge badge-active">New Connection</span>
                    </div>
                  </div>
                </li>
                <li className="activity-item">
                  <div className="activity-icon"><i className="fas fa-search"></i></div>
                  <div className="activity-details">
                    <div className="activity-text">TTP analysis completed for recent phishing campaign</div>
                    <div className="activity-meta">
                      <div className="activity-time">3 hours ago</div>
                      <span className="badge badge-active">Analysis</span>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// Threat Feeds Component
function ThreatFeeds({ active }) {
  return (
    <section id="threat-feeds" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Threat Feeds</h1>
          <p className="page-subtitle">Manage and monitor all threat intelligence feeds</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline"><i className="fas fa-filter"></i> Filter Feeds</button>
          <button className="btn btn-primary"><i className="fas fa-plus"></i> Add New Feed</button>
        </div>
      </div>

      <div className="filters-section">
        <div className="filters-grid">
          <div className="filter-group">
            <label className="filter-label">Feed Type</label>
            <div className="filter-control">
              <select>
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
              <select>
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
              <select>
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
              <input type="text" placeholder="Search by name or URL..." />
            </div>
          </div>
        </div>
      </div>

      <div className="tabs">
        <div className="tab active">Active Feeds (16)</div>
        <div className="tab">External (11)</div>
        <div className="tab">Internal (5)</div>
        <div className="tab">All Feeds (18)</div>
      </div>

      <div className="card">
        <div className="card-content">
          <ul className="feed-items">
            <li className="feed-item">
              <div className="feed-icon"><i className="fas fa-globe"></i></div>
              <div className="feed-details">
                <div className="feed-name">CIRCL MISP Feed</div>
                <div className="feed-description">Computer Incident Response Center Luxembourg (CIRCL) MISP feed providing indicators related to various threats.</div>
                <div className="feed-meta">
                  <div className="feed-stats">
                    <div className="stat-item"><i className="fas fa-search"></i> 1,245 IoCs</div>
                    <div className="stat-item"><i className="fas fa-sync-alt"></i> Updated 25m ago</div>
                    <div className="stat-item"><i className="fas fa-tasks"></i> 28 TTPs</div>
                  </div>
                  <div className="feed-badges">
                    <span className="badge badge-active">Active</span>
                    <span className="badge badge-connected">STIX/TAXII</span>
                  </div>
                </div>
              </div>
            </li>
            <li className="feed-item">
              <div className="feed-icon"><i className="fas fa-shield-alt"></i></div>
              <div className="feed-details">
                <div className="feed-name">SANReN CSIRT Feed</div>
                <div className="feed-description">South African National Research Network Computer Security Incident Response Team feed focused on academic sector threats.</div>
                <div className="feed-meta">
                  <div className="feed-stats">
                    <div className="stat-item"><i className="fas fa-search"></i> 862 IoCs</div>
                    <div className="stat-item"><i className="fas fa-sync-alt"></i> Updated 1h ago</div>
                    <div className="stat-item"><i className="fas fa-tasks"></i> 19 TTPs</div>
                  </div>
                  <div className="feed-badges">
                    <span className="badge badge-active">Active</span>
                    <span className="badge badge-connected">TAXII</span>
                  </div>
                </div>
              </div>
            </li>
            <li className="feed-item">
              <div className="feed-icon"><i className="fas fa-university"></i></div>
              <div className="feed-details">
                <div className="feed-name">SABRIC Intelligence Feed</div>
                <div className="feed-description">South African Banking Risk Information Centre feed with financial sector threat intelligence.</div>
                <div className="feed-meta">
                  <div className="feed-stats">
                    <div className="stat-item"><i className="fas fa-search"></i> 635 IoCs</div>
                    <div className="stat-item"><i className="fas fa-sync-alt"></i> Updated 3h ago</div>
                    <div className="stat-item"><i className="fas fa-tasks"></i> 14 TTPs</div>
                  </div>
                  <div className="feed-badges">
                    <span className="badge badge-active">Active</span>
                    <span className="badge badge-connected">STIX/TAXII</span>
                  </div>
                </div>
              </div>
            </li>
            <li className="feed-item">
              <div className="feed-icon"><i className="fas fa-lock"></i></div>
              <div className="feed-details">
                <div className="feed-name">Cyber Security Hub</div>
                <div className="feed-description">National CSIRT of South Africa providing threat intelligence focused on critical infrastructure.</div>
                <div className="feed-meta">
                  <div className="feed-stats">
                    <div className="stat-item"><i className="fas fa-search"></i> 978 IoCs</div>
                    <div className="stat-item"><i className="fas fa-sync-alt"></i> Updated 2h ago</div>
                    <div className="stat-item"><i className="fas fa-tasks"></i> 32 TTPs</div>
                  </div>
                  <div className="feed-badges">
                    <span className="badge badge-active">Active</span>
                    <span className="badge badge-connected">MISP</span>
                  </div>
                </div>
              </div>
            </li>
            <li className="feed-item">
              <div className="feed-icon"><i className="fas fa-server"></i></div>
              <div className="feed-details">
                <div className="feed-name">Internal Threat Feed</div>
                <div className="feed-description">BlueVision ITM internal threat intelligence gathered from incident response activities.</div>
                <div className="feed-meta">
                  <div className="feed-stats">
                    <div className="stat-item"><i className="fas fa-search"></i> 527 IoCs</div>
                    <div className="stat-item"><i className="fas fa-sync-alt"></i> Updated 30m ago</div>
                    <div className="stat-item"><i className="fas fa-tasks"></i> 23 TTPs</div>
                  </div>
                  <div className="feed-badges">
                    <span className="badge badge-active">Active</span>
                    <span className="badge badge-connected">Internal</span>
                  </div>
                </div>
              </div>
            </li>
            <li className="feed-item">
              <div className="feed-icon"><i className="fas fa-bug"></i></div>
              <div className="feed-details">
                <div className="feed-name">AlienVault OTX</div>
                <div className="feed-description">Open Threat Exchange provides community-powered threat intelligence.</div>
                <div className="feed-meta">
                  <div className="feed-stats">
                    <div className="stat-item"><i className="fas fa-search"></i> 1,892 IoCs</div>
                    <div className="stat-item"><i className="fas fa-sync-alt"></i> Updated 45m ago</div>
                    <div className="stat-item"><i className="fas fa-tasks"></i> 46 TTPs</div>
                  </div>
                  <div className="feed-badges">
                    <span className="badge badge-active">Active</span>
                    <span className="badge badge-connected">API</span>
                  </div>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <div className="pagination">
        <div className="page-item"><i className="fas fa-chevron-left"></i></div>
        <div className="page-item active">1</div>
        <div className="page-item">2</div>
        <div className="page-item">3</div>
        <div className="page-item"><i className="fas fa-chevron-right"></i></div>
      </div>
    </section>
  );
}

// IoC Management Component
function IoCManagement({ active }) {
  return (
    <section id="ioc-management" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">IoC Management</h1>
          <p className="page-subtitle">Manage and analyze indicators of compromise</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline"><i className="fas fa-file-export"></i> Export IoCs</button>
          <button className="btn btn-outline"><i className="fas fa-file-import"></i> Import IoCs</button>
          <button className="btn btn-primary"><i className="fas fa-plus"></i> Add New IoC</button>
        </div>
      </div>

      <div className="filters-section">
        <div className="filters-grid">
          <div className="filter-group">
            <label className="filter-label">IoC Type</label>
            <div className="filter-control">
              <select>
                <option value="">All Types</option>
                <option value="ip">IP Address</option>
                <option value="domain">Domain</option>
                <option value="url">URL</option>
                <option value="hash">File Hash</option>
                <option value="email">Email</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Severity</label>
            <div className="filter-control">
              <select>
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
              <select>
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="review">Under Review</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Source</label>
            <div className="filter-control">
              <select>
                <option value="">All Sources</option>
                <option value="circl">CIRCL MISP</option>
                <option value="sanren">SANReN CSIRT</option>
                <option value="sabric">SABRIC</option>
                <option value="internal">Internal</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title"><i className="fas fa-search card-icon"></i> Indicators of Compromise</h2>
          <div className="card-actions">
            <button className="btn btn-outline btn-sm"><i className="fas fa-sync-alt"></i> Refresh</button>
          </div>
        </div>
        <div className="card-content">
          <table className="data-table">
            <thead>
              <tr>
                <th><input type="checkbox" /></th>
                <th>Type</th>
                <th>Value</th>
                <th>Severity</th>
                <th>Source</th>
                <th>Date Added</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><input type="checkbox" /></td>
                <td>IP Address</td>
                <td>192.168.144.32</td>
                <td><span className="badge badge-high">High</span></td>
                <td>CIRCL MISP</td>
                <td>2025-05-18</td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
                </td>
              </tr>
              <tr>
                <td><input type="checkbox" /></td>
                <td>Domain</td>
                <td>malicious-ransomware.net</td>
                <td><span className="badge badge-high">High</span></td>
                <td>Internal</td>
                <td>2025-05-17</td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
                </td>
              </tr>
              <tr>
                <td><input type="checkbox" /></td>
                <td>File Hash</td>
                <td>a45f3d9e7b12c04e8572630a21ba8f61</td>
                <td><span className="badge badge-medium">Medium</span></td>
                <td>SANReN CSIRT</td>
                <td>2025-05-16</td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
                </td>
              </tr>
              <tr>
                <td><input type="checkbox" /></td>
                <td>URL</td>
                <td>https://download.malicious-file.com/payload</td>
                <td><span className="badge badge-medium">Medium</span></td>
                <td>SABRIC</td>
                <td>2025-05-15</td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
                </td>
              </tr>
              <tr>
                <td><input type="checkbox" /></td>
                <td>Email</td>
                <td>phishing@suspicious-mail.org</td>
                <td><span className="badge badge-low">Low</span></td>
                <td>Internal</td>
                <td>2025-05-14</td>
                <td><span className="badge badge-medium">Under Review</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
                </td>
              </tr>
              <tr>
                <td><input type="checkbox" /></td>
                <td>IP Address</td>
                <td>45.195.33.12</td>
                <td><span className="badge badge-high">High</span></td>
                <td>Cyber Security Hub</td>
                <td>2025-05-13</td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
                </td>
              </tr>
              <tr>
                <td><input type="checkbox" /></td>
                <td>File Hash</td>
                <td>5a8f1c9b2e3d647a8c9f1b5d3e7a2c4d</td>
                <td><span className="badge badge-high">High</span></td>
                <td>AlienVault OTX</td>
                <td>2025-05-12</td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
                </td>
              </tr>
              <tr>
                <td><input type="checkbox" /></td>
                <td>Domain</td>
                <td>fake-university-portal.com</td>
                <td><span className="badge badge-high">High</span></td>
                <td>Internal</td>
                <td>2025-05-11</td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="pagination">
        <div className="page-item"><i className="fas fa-chevron-left"></i></div>
        <div className="page-item active">1</div>
        <div className="page-item">2</div>
        <div className="page-item">3</div>
        <div className="page-item">4</div>
        <div className="page-item">5</div>
        <div className="page-item"><i className="fas fa-chevron-right"></i></div>
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
                <span>Total IoCs</span>
              </div>
              <div className="stat-value">1,286</div>
              <div className="stat-change increase">
                <span><i className="fas fa-arrow-up"></i></span>
                <span>24% from last week</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-title">
                <div className="stat-icon"><i className="fas fa-exclamation-triangle"></i></div>
                <span>High Severity</span>
              </div>
              <div className="stat-value">412</div>
              <div className="stat-change increase">
                <span><i className="fas fa-arrow-up"></i></span>
                <span>18% from last week</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-title">
                <div className="stat-icon"><i className="fas fa-share-alt"></i></div>
                <span>Shared IoCs</span>
              </div>
              <div className="stat-value">854</div>
              <div className="stat-change increase">
                <span><i className="fas fa-arrow-up"></i></span>
                <span>32% from last week</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-title">
                <div className="stat-icon"><i className="fas fa-check-circle"></i></div>
                <span>Verified IoCs</span>
              </div>
              <div className="stat-value">593</div>
              <div className="stat-change increase">
                <span><i className="fas fa-arrow-up"></i></span>
                <span>12% from last week</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// TTP Analysis Component
function TTPAnalysis({ active }) {
  const ttpChartRef = useRef(null);
  
  useEffect(() => {
    if (active && ttpChartRef.current) {
      createTTPTrendsChart();
      
      // Add resize handler for responsive charts
      const handleResize = () => {
        createTTPTrendsChart();
      };
      
      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }
  }, [active]);

  const createTTPTrendsChart = () => {
    // Clear previous chart if any
    d3.select(ttpChartRef.current).selectAll("*").remove();
    
    // Sample data - TTP observations over time by category
    const data = [
      { date: "2025-02", initialAccess: 12, execution: 8, persistence: 5, defenseEvasion: 7, impact: 10 },
      { date: "2025-03", initialAccess: 15, execution: 10, persistence: 6, defenseEvasion: 9, impact: 12 },
      { date: "2025-04", initialAccess: 18, execution: 14, persistence: 8, defenseEvasion: 13, impact: 16 },
      { date: "2025-05", initialAccess: 22, execution: 17, persistence: 11, defenseEvasion: 15, impact: 19 }
    ];

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
      .domain([0, d3.max(data, d => Math.max(d.initialAccess, d.execution, d.persistence, d.defenseEvasion, d.impact)) * 1.1])
      .range([innerHeight, 0]);

    // Define line generator
    const line = d3.line()
      .x(d => x(d.date))
      .y(d => y(d.value))
      .curve(d3.curveMonotoneX);

    // Define colors for different TTP categories
    const colors = {
      initialAccess: "#0056b3",
      execution: "#00a0e9",
      persistence: "#38a169",
      defenseEvasion: "#e53e3e",
      impact: "#f6ad55"
    };

    // Create line for each category
    const categories = ['initialAccess', 'execution', 'persistence', 'defenseEvasion', 'impact'];
    const categoryLabels = {
      initialAccess: "Initial Access",
      execution: "Execution",
      persistence: "Persistence",
      defenseEvasion: "Defense Evasion",
      impact: "Impact"
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
  };

  return (
    <section id="ttp-analysis" className={`page-section ${active ? 'active' : ''}`}>
      {/* Content for TTP Analysis section */}
      <div className="page-header">
        <div>
          <h1 className="page-title">TTP Analysis</h1>
          <p className="page-subtitle">Track and analyze tactics, techniques, and procedures</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline"><i className="fas fa-download"></i> Export Analysis</button>
          <button className="btn btn-primary"><i className="fas fa-plus"></i> New TTP</button>
        </div>
      </div>
      
      <div className="card mt-4">
        <div className="card-header">
          <h2 className="card-title"><i className="fas fa-chart-line card-icon"></i> TTP Trends</h2>
        </div>
        <div className="card-content">
          <div className="chart-container" ref={ttpChartRef}>
            {/* D3.js Chart will be rendered here */}
          </div>
        </div>
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h2 className="card-title"><i className="fas fa-tasks card-icon"></i> Recent TTP Analyses</h2>
        </div>
        <div className="card-content">
          <table className="data-table">
            <thead>
              <tr>
                <th>TTP ID</th>
                <th>Name</th>
                <th>Category</th>
                <th>MITRE ID</th>
                <th>Associated Threat Actor</th>
                <th>Last Observed</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>TTP-2025-0042</td>
                <td>Phishing with Malicious Attachments</td>
                <td>Initial Access</td>
                <td>T1566.001</td>
                <td>APT-EDU-01</td>
                <td>2025-05-19</td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-eye"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
                </td>
              </tr>
              <tr>
                <td>TTP-2025-0041</td>
                <td>PowerShell Script Execution</td>
                <td>Execution</td>
                <td>T1059.001</td>
                <td>APT-EDU-01, CyberCrim-12</td>
                <td>2025-05-18</td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-eye"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
                </td>
              </tr>
              <tr>
                <td>TTP-2025-0039</td>
                <td>Data Encryption for Impact</td>
                <td>Impact</td>
                <td>T1486</td>
                <td>RansomGroup-X</td>
                <td>2025-05-17</td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-eye"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
                </td>
              </tr>
              <tr>
                <td>TTP-2025-0038</td>
                <td>Credential Dumping</td>
                <td>Credential Access</td>
                <td>T1003</td>
                <td>APT-EDU-01, RansomGroup-X</td>
                <td>2025-05-15</td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-eye"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
                </td>
              </tr>
              <tr>
                <td>TTP-2025-0035</td>
                <td>Network Service Discovery</td>
                <td>Discovery</td>
                <td>T1046</td>
                <td>CyberCrim-12</td>
                <td>2025-05-12</td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-eye"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

// Institutions Component
function Institutions({ active }) {
  const mapRef = useRef(null);
  
  useEffect(() => {
    if (active && mapRef.current) {
      createInstitutionMap();
      
      // Add resize handler to handle map resizing
      const handleResize = () => {
        createInstitutionMap();
      };
      
      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }
  }, [active]);

  const createInstitutionMap = () => {
    // Clear previous chart if any
    d3.select(mapRef.current).selectAll("*").remove();
    
    // Set dimensions and margins for the chart
    const width = mapRef.current.clientWidth;
    const height = 300;
    
    // Create the SVG container
    const svg = d3.select(mapRef.current)
      .append("svg")
      .attr("width", width)
      .attr("height", height);
    
    // Sample data for institutions
    const institutions = [
      { name: "University of Pretoria", location: [28.2, -25.7], type: "Education", size: 90 },
      { name: "Cyber Security Hub", location: [28.0, -26.2], type: "Government", size: 85 },
      { name: "SANReN CSIRT", location: [18.4, -33.9], type: "Security", size: 75 },
      { name: "SABRIC", location: [28.05, -26.1], type: "Financial", size: 70 },
      { name: "University of Johannesburg", location: [28.0, -26.1], type: "Education", size: 65 },
      { name: "Tshwane University of Technology", location: [28.16, -25.73], type: "Education", size: 60 },
      { name: "Oxford University", location: [-1.25, 51.75], type: "Education", size: 55 },
      { name: "CERT-EU", location: [4.35, 50.85], type: "Security", size: 50 },
      { name: "Stanford University", location: [-122.17, 37.43], type: "Education", size: 60 },
      { name: "MIT", location: [-71.09, 42.36], type: "Education", size: 65 }
    ];
    
    // Define a projection
    // This is a simple mercator projection - for a real app, you would use a proper world map
    const projection = d3.geoMercator()
      .scale(100)
      .center([0, 0])
      .translate([width / 2, height / 2]);
    
    // Define colors for institution types
    const typeColors = {
      "Education": "#0056b3",
      "Government": "#38a169",
      "Security": "#e53e3e",
      "Financial": "#f6ad55"
    };
    
    // Add institutions as circles
    svg.selectAll("circle")
      .data(institutions)
      .enter()
      .append("circle")
      .attr("cx", d => projection(d.location)[0])
      .attr("cy", d => projection(d.location)[1])
      .attr("r", d => Math.sqrt(d.size) * 0.8)
      .attr("fill", d => typeColors[d.type])
      .attr("opacity", 0.7)
      .attr("stroke", "#fff")
      .attr("stroke-width", 1)
      .append("title")
      .text(d => `${d.name} (${d.type})`);
    
    // Add connections between institutions
    // For simplicity, connecting the first institution with others
    svg.selectAll(".connection")
      .data(institutions.slice(1, 6))
      .enter()
      .append("line")
      .attr("class", "connection")
      .attr("x1", projection(institutions[0].location)[0])
      .attr("y1", projection(institutions[0].location)[1])
      .attr("x2", d => projection(d.location)[0])
      .attr("y2", d => projection(d.location)[1])
      .attr("stroke", "#0056b3")
      .attr("stroke-width", 1)
      .attr("stroke-opacity", 0.3);
    
    // Add a simple title
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", 20)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "600")
      .style("fill", "#2d3748")
      .text("Global Institution Network");
    
    // Add a simple legend
    const legend = svg.append("g")
      .attr("transform", `translate(20, 40)`);
    
    const legendData = Object.entries(typeColors);
    
    legendData.forEach((item, i) => {
      const [type, color] = item;
      
      legend.append("circle")
        .attr("cx", 10)
        .attr("cy", i * 20)
        .attr("r", 6)
        .attr("fill", color);
        
      legend.append("text")
        .attr("x", 25)
        .attr("y", i * 20 + 5)
        .text(type)
        .style("font-size", "12px");
    });
  };

  return (
    <section id="institutions" className={`page-section ${active ? 'active' : ''}`}>
      {/* Content for Institutions section */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Connected Institutions</h1>
          <p className="page-subtitle">Manage sharing partners and trust relationships</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline"><i className="fas fa-filter"></i> Filter</button>
          <button className="btn btn-primary"><i className="fas fa-plus"></i> Add Institution</button>
        </div>
      </div>
      
      <div className="card mt-4">
        <div className="card-header">
          <h2 className="card-title"><i className="fas fa-chart-area card-icon"></i> Institution Activity Map</h2>
        </div>
        <div className="card-content">
          <div className="chart-container" ref={mapRef}>
            {/* D3.js Map will be rendered here */}
          </div>
        </div>
      </div>
    </section>
  );
}

// Reports Component
function Reports({ active }) {
  return (
    <section id="reports" className={`page-section ${active ? 'active' : ''}`}>
      {/* Content for Reports section */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Threat Intelligence Reports</h1>
          <p className="page-subtitle">Access and manage comprehensive threat reports</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline"><i className="fas fa-filter"></i> Filter</button>
          <button className="btn btn-primary"><i className="fas fa-plus"></i> Create New Report</button>
        </div>
      </div>

      <div className="report-grid">
        {/* Report Card 1 */}
        <div className="report-card">
          <div className="report-header">
            <div className="report-type">Campaign Analysis</div>
            <h3 className="report-title">Education Sector Ransomware Campaign</h3>
            <div className="report-meta">
              <span>May 19, 2025</span>
              <span><i className="fas fa-eye"></i> 148</span>
            </div>
          </div>
          <div className="report-content">
            <div className="report-stats">
              <div className="report-stat">
                <div className="stat-number">18</div>
                <div className="stat-label">Institutions Targeted</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">42</div>
                <div className="stat-label">Related IoCs</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">8</div>
                <div className="stat-label">TTPs Identified</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">High</div>
                <div className="stat-label">Severity</div>
              </div>
            </div>
            <p>Analysis of ongoing ransomware campaign targeting education institutions in South Africa and neighboring countries.</p>
            <div className="report-actions">
              <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i> Share</button>
              <button className="btn btn-primary btn-sm"><i className="fas fa-eye"></i> View Report</button>
            </div>
          </div>
        </div>

        {/* Report Card 2 */}
        <div className="report-card">
          <div className="report-header">
            <div className="report-type">Weekly Summary</div>
            <h3 className="report-title">Threat Intelligence Digest: Week 20</h3>
            <div className="report-meta">
              <span>May 17, 2025</span>
              <span><i className="fas fa-eye"></i> 127</span>
            </div>
          </div>
          <div className="report-content">
            <div className="report-stats">
              <div className="report-stat">
                <div className="stat-number">86</div>
                <div className="stat-label">New IoCs</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">12</div>
                <div className="stat-label">TTPs Observed</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">4</div>
                <div className="stat-label">Critical Alerts</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">3</div>
                <div className="stat-label">Threat Actors</div>
              </div>
            </div>
            <p>Weekly summary of significant threat intelligence findings and trends for the week ending May 17, 2025.</p>
            <div className="report-actions">
              <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i> Share</button>
              <button className="btn btn-primary btn-sm"><i className="fas fa-eye"></i> View Report</button>
            </div>
          </div>
        </div>

        {/* Report Card 3 */}
        <div className="report-card">
          <div className="report-header">
            <div className="report-type">Incident Analysis</div>
            <h3 className="report-title">University Data Breach Investigation</h3>
            <div className="report-meta">
              <span>May 15, 2025</span>
              <span><i className="fas fa-eye"></i> 215</span>
            </div>
          </div>
          <div className="report-content">
            <div className="report-stats">
              <div className="report-stat">
                <div className="stat-number">28</div>
                <div className="stat-label">IoCs Discovered</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">6</div>
                <div className="stat-label">TTPs Identified</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">APT-EDU-01</div>
                <div className="stat-label">Threat Actor</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">Medium</div>
                <div className="stat-label">Severity</div>
              </div>
            </div>
            <p>Detailed analysis of recent data breach affecting a major university, including timeline, attack vectors, and remediation steps.</p>
            <div className="report-actions">
              <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i> Share</button>
              <button className="btn btn-primary btn-sm"><i className="fas fa-eye"></i> View Report</button>
            </div>
          </div>
        </div>

        {/* Report Card 4 */}
        <div className="report-card">
          <div className="report-header">
            <div className="report-type">Trend Analysis</div>
            <h3 className="report-title">Emerging Phishing Techniques in 2025</h3>
            <div className="report-meta">
              <span>May 10, 2025</span>
              <span><i className="fas fa-eye"></i> 342</span>
            </div>
          </div>
          <div className="report-content">
            <div className="report-stats">
              <div className="report-stat">
                <div className="stat-number">53</div>
                <div className="stat-label">IoCs Analyzed</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">7</div>
                <div className="stat-label">New Techniques</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">14</div>
                <div className="stat-label">Organizations</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">High</div>
                <div className="stat-label">Relevance</div>
              </div>
            </div>
            <p>Analysis of evolving phishing techniques observed across multiple sectors, with focus on AI-generated content and deep fakes.</p>
            <div className="report-actions">
              <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i> Share</button>
              <button className="btn btn-primary btn-sm"><i className="fas fa-eye"></i> View Report</button>
            </div>
          </div>
        </div>

        {/* Report Card 5 */}
        <div className="report-card">
          <div className="report-header">
            <div className="report-type">Sector Analysis</div>
            <h3 className="report-title">Financial Sector Threat Landscape</h3>
            <div className="report-meta">
              <span>May 5, 2025</span>
              <span><i className="fas fa-eye"></i> 198</span>
            </div>
          </div>
          <div className="report-content">
            <div className="report-stats">
              <div className="report-stat">
                <div className="stat-number">94</div>
                <div className="stat-label">IoCs Analyzed</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">16</div>
                <div className="stat-label">TTPs Identified</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">5</div>
                <div className="stat-label">Threat Actors</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">High</div>
                <div className="stat-label">Severity</div>
              </div>
            </div>
            <p>Comprehensive overview of current threats targeting financial institutions in Southern Africa, with focus on banking trojans and ATM malware.</p>
            <div className="report-actions">
              <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i> Share</button>
              <button className="btn btn-primary btn-sm"><i className="fas fa-eye"></i> View Report</button>
            </div>
          </div>
        </div>

        {/* Report Card 6 */}
        <div className="report-card">
          <div className="report-header">
            <div className="report-type">Technical Analysis</div>
            <h3 className="report-title">EDU-Ransom Malware Analysis</h3>
            <div className="report-meta">
              <span>May 2, 2025</span>
              <span><i className="fas fa-eye"></i> 276</span>
            </div>
          </div>
          <div className="report-content">
            <div className="report-stats">
              <div className="report-stat">
                <div className="stat-number">37</div>
                <div className="stat-label">IoCs Generated</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">9</div>
                <div className="stat-label">TTPs Mapped</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">RansomGroup-X</div>
                <div className="stat-label">Attribution</div>
              </div>
              <div className="report-stat">
                <div className="stat-number">Critical</div>
                <div className="stat-label">Severity</div>
              </div>
            </div>
            <p>Technical deep-dive into the EDU-Ransom malware strain targeting educational institutions, including code analysis and IOC extraction.</p>
            <div className="report-actions">
              <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i> Share</button>
              <button className="btn btn-primary btn-sm"><i className="fas fa-eye"></i> View Report</button>
            </div>
          </div>
        </div>
      </div>

      <div className="pagination">
        <div className="page-item"><i className="fas fa-chevron-left"></i></div>
        <div className="page-item active">1</div>
        <div className="page-item">2</div>
        <div className="page-item">3</div>
        <div className="page-item">4</div>
        <div className="page-item"><i className="fas fa-chevron-right"></i></div>
      </div>
    </section>
  );
}

// Alerts Component
function Alerts({ active }) {
  if (!active) return null;

  return (
    <section className="page-section active">
      <div className="page-header">
        <div>
          <h1 className="page-title">Security Alerts</h1>
          <p className="page-subtitle">Monitor and manage security alerts across your network</p>
        </div>
      </div>
      
      <div className="alerts-grid">
        <div className="alert-card critical">
          <div className="alert-header">
            <i className="fas fa-exclamation-triangle"></i>
            <div>
              <h3>Critical Security Breach</h3>
              <span className="alert-time">2 minutes ago</span>
            </div>
          </div>
          <p>Unauthorized access detected from IP 192.168.144.32</p>
          <div className="alert-actions">
            <button className="btn btn-sm btn-primary">Investigate</button>
            <button className="btn btn-sm btn-outline">Dismiss</button>
          </div>
        </div>
        
        <div className="alert-card warning">
          <div className="alert-header">
            <i className="fas fa-exclamation-circle"></i>
            <div>
              <h3>Suspicious Activity</h3>
              <span className="alert-time">15 minutes ago</span>
            </div>
          </div>
          <p>Multiple failed login attempts detected</p>
          <div className="alert-actions">
            <button className="btn btn-sm btn-primary">Review</button>
            <button className="btn btn-sm btn-outline">Dismiss</button>
          </div>
        </div>
      </div>
    </section>
  );
}

// Notifications Component  
function Notifications({ active }) {
  if (!active) return null;

  return (
    <section className="page-section active">
      <div className="page-header">
        <div>
          <h1 className="page-title">All Notifications</h1>
          <p className="page-subtitle">View and manage all your notifications</p>
        </div>
      </div>
      
      <div className="notifications-page-list">
        <div className="notification-page-item unread">
          <div className="notification-icon">
            <i className="fas fa-exclamation-triangle"></i>
          </div>
          <div className="notification-content">
            <div className="notification-title">New malware detected in network traffic</div>
            <div className="notification-message">Suspicious activity detected from IP 192.168.144.32</div>
            <div className="notification-time">30 minutes ago</div>
          </div>
        </div>
        
        <div className="notification-page-item unread">
          <div className="notification-icon">
            <i className="fas fa-exclamation-circle"></i>
          </div>
          <div className="notification-content">
            <div className="notification-title">User registration pending approval</div>
            <div className="notification-message">New user account requires admin approval</div>
            <div className="notification-time">2 hours ago</div>
          </div>
        </div>
        
        <div className="notification-page-item read">
          <div className="notification-icon">
            <i className="fas fa-info-circle"></i>
          </div>
          <div className="notification-content">
            <div className="notification-title">System maintenance completed</div>
            <div className="notification-message">All systems are fully operational</div>
            <div className="notification-time">6 hours ago</div>
          </div>
        </div>
      </div>
    </section>
  );
}

// Profile Component with full backend integration
function Profile({ active, user }) {
  const [profileData, setProfileData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editFormData, setEditFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    organization: '',
    phone: '',
    job_title: ''
  });
  const [userStats, setUserStats] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('profile');
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  // Fetch profile data on component mount
  useEffect(() => {
    if (active) {
      fetchProfileData();
      fetchUserStatistics();
    }
  }, [active]);

  if (!active) return null;

  const fetchProfileData = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await getUserProfile();
      
      // Handle admin users with empty names
      let firstName = data.first_name || '';
      let lastName = data.last_name || '';
      
      if (!firstName && !lastName && (data.is_admin || data.is_staff || data.username === 'admin')) {
        firstName = 'System';
        lastName = 'Administrator';
        // Update the data object too for display
        data.first_name = firstName;
        data.last_name = lastName;
      }
      
      setProfileData(data);
      setEditFormData({
        first_name: firstName,
        last_name: lastName,
        email: data.email || '',
        organization: data.organization || '',
        phone: data.phone || '',
        job_title: data.job_title || ''
      });
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      setError('Failed to load profile data: ' + error);
      // Fallback to user data from props
      if (user) {
        // Provide better defaults for admin users
        let firstName = user.first_name || '';
        let lastName = user.last_name || '';
        
        // If no name is set and user appears to be admin, provide defaults
        if (!firstName && !lastName && (user.is_staff || user.is_superuser || user.username === 'admin')) {
          firstName = 'System';
          lastName = 'Administrator';
        }
        
        const fallbackData = {
          username: user.username,
          email: user.email || user.username,
          first_name: firstName,
          last_name: lastName,
          organization: user.organization || '',
          is_staff: user.is_staff || false,
          is_admin: user.is_admin || false,
          last_login: user.last_login || new Date().toISOString()
        };
        setProfileData(fallbackData);
        setEditFormData({
          first_name: fallbackData.first_name,
          last_name: fallbackData.last_name,
          email: fallbackData.email,
          organization: fallbackData.organization,
          phone: '',
          job_title: ''
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const fetchUserStatistics = async () => {
    try {
      const stats = await getUserStatistics();
      setUserStats(stats);
    } catch (error) {
      console.error('Failed to fetch user statistics:', error);
      // Set fallback stats
      setUserStats({
        login_count: 1,
        last_login: new Date().toISOString(),
        account_created: new Date().toISOString(),
        is_active: true
      });
    }
  };

  const handleEditToggle = () => {
    setIsEditing(!isEditing);
    setError('');
    setSuccess('');
  };

  const handleFormChange = (field, value) => {
    setEditFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSaveProfile = async () => {
    setIsLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const updatedData = await updateUserProfile(editFormData);
      setProfileData(updatedData);
      setIsEditing(false);
      setSuccess('Profile updated successfully!');
    } catch (error) {
      console.error('Failed to update profile:', error);
      setError('Failed to update profile: ' + error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordChange = (field, value) => {
    setPasswordForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    if (passwordForm.newPassword.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setIsLoading(true);
    try {
      await changePassword(passwordForm.currentPassword, passwordForm.newPassword);
      setSuccess('Password changed successfully!');
      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (error) {
      console.error('Failed to change password:', error);
      setError('Failed to change password: ' + error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Invalid date';
    }
  };

  return (
    <section className="page-section active">
      <div className="page-header">
        <div>
          <h1 className="page-title">User Profile</h1>
          <p className="page-subtitle">Manage your account settings and view your information</p>
        </div>
        <div className="action-buttons">
          {!isEditing ? (
            <button className="btn btn-primary" onClick={handleEditToggle} disabled={isLoading}>
              <i className="fas fa-edit"></i> Edit Profile
            </button>
          ) : (
            <>
              <button className="btn btn-outline" onClick={handleEditToggle} disabled={isLoading}>
                <i className="fas fa-times"></i> Cancel
              </button>
              <button className="btn btn-primary" onClick={handleSaveProfile} disabled={isLoading}>
                <i className="fas fa-save"></i> {isLoading ? 'Saving...' : 'Save Changes'}
              </button>
            </>
          )}
        </div>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="alert alert-error">
          <i className="fas fa-exclamation-circle"></i> {error}
        </div>
      )}
      {success && (
        <div className="alert alert-success">
          <i className="fas fa-check-circle"></i> {success}
        </div>
      )}

      {/* Profile Tabs */}
      <div className="profile-tabs">
        <button 
          className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          <i className="fas fa-user"></i> Profile Information
        </button>
        <button 
          className={`tab-button ${activeTab === 'security' ? 'active' : ''}`}
          onClick={() => setActiveTab('security')}
        >
          <i className="fas fa-shield-alt"></i> Security Settings
        </button>
      </div>

      {/* Profile Information Tab */}
      {activeTab === 'profile' && (
        <div className="profile-content">
          <div className="profile-grid">
            <div className="profile-main">
              <div className="card">
                <div className="card-header">
                  <h2 className="card-title">
                    <i className="fas fa-user card-icon"></i> Personal Information
                  </h2>
                </div>
                <div className="card-content">
                  {isLoading && !profileData ? (
                    <div className="loading-spinner">
                      <i className="fas fa-spinner fa-spin"></i> Loading profile...
                    </div>
                  ) : (
                    <div className="profile-form">
                      <div className="form-row">
                        <div className="form-group">
                          <label>Username</label>
                          <input 
                            type="text" 
                            value={profileData?.username || ''} 
                            disabled 
                          />
                        </div>
                        <div className="form-group">
                          <label>Email</label>
                          <input 
                            type="email" 
                            value={isEditing ? editFormData.email : (profileData?.email || '')}
                            onChange={(e) => handleFormChange('email', e.target.value)}
                            disabled={!isEditing}
                          />
                        </div>
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label>First Name</label>
                          <input 
                            type="text" 
                            value={isEditing ? editFormData.first_name : (profileData?.first_name || '')}
                            onChange={(e) => handleFormChange('first_name', e.target.value)}
                            disabled={!isEditing}
                          />
                        </div>
                        <div className="form-group">
                          <label>Last Name</label>
                          <input 
                            type="text" 
                            value={isEditing ? editFormData.last_name : (profileData?.last_name || '')}
                            onChange={(e) => handleFormChange('last_name', e.target.value)}
                            disabled={!isEditing}
                          />
                        </div>
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Organization</label>
                          <input 
                            type="text" 
                            value={isEditing ? editFormData.organization : (profileData?.organization || '')}
                            onChange={(e) => handleFormChange('organization', e.target.value)}
                            disabled={!isEditing}
                          />
                        </div>
                        <div className="form-group">
                          <label>Job Title</label>
                          <input 
                            type="text" 
                            value={isEditing ? editFormData.job_title : (profileData?.job_title || '')}
                            onChange={(e) => handleFormChange('job_title', e.target.value)}
                            disabled={!isEditing}
                          />
                        </div>
                      </div>
                      <div className="form-group">
                        <label>Phone</label>
                        <input 
                          type="tel" 
                          value={isEditing ? editFormData.phone : (profileData?.phone || '')}
                          onChange={(e) => handleFormChange('phone', e.target.value)}
                          disabled={!isEditing}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            <div className="profile-sidebar">
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Account Statistics</h3>
                </div>
                <div className="card-content">
                  <div className="stats-list">
                    <div className="stat-item">
                      <div className="stat-value">
                        {profileData?.is_admin || profileData?.is_staff ? 'Administrator' : 'User'}
                      </div>
                      <div className="stat-label">Account Type</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value">
                        {userStats?.is_active ? 'Active' : 'Inactive'}
                      </div>
                      <div className="stat-label">Status</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value">{formatDate(userStats?.last_login)}</div>
                      <div className="stat-label">Last Login</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value">{userStats?.login_count || 0}</div>
                      <div className="stat-label">Total Logins</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value">{formatDate(userStats?.account_created)}</div>
                      <div className="stat-label">Account Created</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Security Settings Tab */}
      {activeTab === 'security' && (
        <div className="profile-content">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">
                <i className="fas fa-shield-alt card-icon"></i> Change Password
              </h2>
            </div>
            <div className="card-content">
              <form onSubmit={handleChangePassword}>
                <div className="form-group">
                  <label>Current Password</label>
                  <input 
                    type="password" 
                    value={passwordForm.currentPassword}
                    onChange={(e) => handlePasswordChange('currentPassword', e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>New Password</label>
                  <input 
                    type="password" 
                    value={passwordForm.newPassword}
                    onChange={(e) => handlePasswordChange('newPassword', e.target.value)}
                    required
                    minLength={8}
                  />
                </div>
                <div className="form-group">
                  <label>Confirm New Password</label>
                  <input 
                    type="password" 
                    value={passwordForm.confirmPassword}
                    onChange={(e) => handlePasswordChange('confirmPassword', e.target.value)}
                    required
                    minLength={8}
                  />
                </div>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={isLoading}
                >
                  <i className="fas fa-key"></i> {isLoading ? 'Changing...' : 'Change Password'}
                </button>
              </form>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}


// Account Settings Component
function AccountSettings({ active, user }) {
  const [formData, setFormData] = useState({
    username: user?.username || '',
    fullName: user?.full_name || '',
    email: user?.email || user?.username || '',
    organization: user?.organization || '',
    role: user?.role || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  if (!active) return null;

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      const profileData = {
        full_name: formData.fullName,
        organization: formData.organization,
        role: formData.role
      };
      
      await updateUserProfile(profileData);
      setMessage('Profile updated successfully!');
      
      // Refresh the page after a short delay to show updated data
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (error) {
      setMessage(`Error updating profile: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (formData.newPassword !== formData.confirmPassword) {
      setMessage('New passwords do not match!');
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      await changePassword(formData.currentPassword, formData.newPassword);
      setMessage('Password changed successfully!');
      setFormData(prev => ({
        ...prev,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }));
    } catch (error) {
      setMessage(`Error changing password: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="page-section active">
      <div className="page-header">
        <h1><i className="fas fa-cog"></i> Account Settings</h1>
        <p>Manage your account preferences and security settings</p>
      </div>

      <div className="settings-container">
        {message && (
          <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`}>
            {message}
          </div>
        )}

        <div className="settings-grid">
          {/* Profile Information */}
          <div className="settings-card">
            <h3><i className="fas fa-user"></i> Profile Information</h3>
            <form onSubmit={handleProfileUpdate}>
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  disabled
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label htmlFor="fullName">Full Name</label>
                <input
                  type="text"
                  id="fullName"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleInputChange}
                  className="form-control"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="form-control"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="organization">Organization</label>
                <input
                  type="text"
                  id="organization"
                  name="organization"
                  value={formData.organization}
                  onChange={handleInputChange}
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label htmlFor="role">Role</label>
                <input
                  type="text"
                  id="role"
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  className="form-control"
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={isLoading}>
                {isLoading ? 'Updating...' : 'Update Profile'}
              </button>
            </form>
          </div>

          {/* Password Change */}
          <div className="settings-card">
            <h3><i className="fas fa-lock"></i> Change Password</h3>
            <form onSubmit={handlePasswordChange}>
              <div className="form-group">
                <label htmlFor="currentPassword">Current Password</label>
                <input
                  type="password"
                  id="currentPassword"
                  name="currentPassword"
                  value={formData.currentPassword}
                  onChange={handleInputChange}
                  className="form-control"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="newPassword">New Password</label>
                <input
                  type="password"
                  id="newPassword"
                  name="newPassword"
                  value={formData.newPassword}
                  onChange={handleInputChange}
                  className="form-control"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm New Password</label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="form-control"
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={isLoading}>
                {isLoading ? 'Changing...' : 'Change Password'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}

// Admin Settings Component
function AdminSettings({ active, onNavigate }) {
  const [systemHealth, setSystemHealth] = useState(null);
  const [emailStats, setEmailStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (active) {
      fetchSystemData();
    }
  }, [active]);

  if (!active) return null;

  const fetchSystemData = async () => {
    setIsLoading(true);
    try {
      const [healthResponse, statsResponse] = await Promise.all([
        getSystemHealth().catch(() => null),
        getEmailStatistics().catch(() => null)
      ]);
      
      // Extract data from API response structure
      const healthData = healthResponse?.success ? healthResponse.data : healthResponse;
      const statsData = statsResponse?.success ? statsResponse.data : statsResponse;
      
      setSystemHealth(healthData);
      setEmailStats(statsData);
    } catch (error) {
      console.error('Error fetching system data:', error);
      setSystemHealth(null);
      setEmailStats(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestEmail = async () => {
    const email = prompt('Enter email address to send test email:');
    if (!email) return;

    setIsLoading(true);
    setMessage('');
    
    try {
      const response = await sendTestEmail(email);
      if (response?.success) {
        setMessage('✅ Test email sent successfully!');
      } else {
        setMessage(`❌ Error sending test email: ${response?.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Test email error:', error);
      setMessage(`❌ Error sending test email: ${error?.message || error}`);
    } finally {
      setIsLoading(false);
      // Clear message after 5 seconds
      setTimeout(() => setMessage(''), 5000);
    }
  };

  const handleTestConnection = async () => {
    setIsLoading(true);
    setMessage('');
    
    try {
      const response = await testGmailConnection();
      if (response?.success) {
        setMessage('✅ Gmail connection test successful!');
      } else {
        setMessage(`❌ Gmail connection test failed: ${response?.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Gmail connection test error:', error);
      setMessage(`❌ Gmail connection test failed: ${error?.message || error}`);
    } finally {
      setIsLoading(false);
      // Clear message after 5 seconds
      setTimeout(() => setMessage(''), 5000);
    }
  };

  const handleNavigation = (pageId) => {
    if (onNavigate) {
      onNavigate(pageId);
    }
  };

  return (
    <section className="page-section active">
      <div className="page-header">
        <h1><i className="fas fa-shield-alt"></i> Admin Settings</h1>
        <p>System administration and configuration</p>
      </div>

      <div className="admin-settings-container">
        {message && (
          <div className={`alert ${message.includes('Error') || message.includes('failed') ? 'alert-error' : 'alert-success'}`}>
            {message}
          </div>
        )}

        <div className="admin-grid">
          {/* System Health */}
          <div className="admin-card system-health-card">
            <div className="card-header">
              <h3><i className="fas fa-heartbeat"></i> System Health</h3>
              <button onClick={fetchSystemData} className="btn btn-sm btn-outline refresh-btn">
                <i className="fas fa-sync-alt"></i>
              </button>
            </div>
            {isLoading ? (
              <div className="loading">
                <div className="loading-animation">
                  <div className="pulse-ring"></div>
                  <div className="pulse-ring"></div>
                  <div className="pulse-ring"></div>
                  <div className="pulse-core"></div>
                </div>
                <p>Loading system health...</p>
              </div>
            ) : systemHealth ? (
              <div className="health-dashboard">
                {/* Overall Status */}
                <div className="health-overview">
                  <div className={`status-badge ${systemHealth.database?.status === 'healthy' ? 'status-healthy' : 'status-warning'}`}>
                    <i className={`fas ${systemHealth.database?.status === 'healthy' ? 'fa-check-circle' : 'fa-exclamation-triangle'}`}></i>
                    <span>{systemHealth.database?.status === 'healthy' ? 'System Healthy' : 'Needs Attention'}</span>
                  </div>
                </div>

                {/* Key Metrics Grid */}
                <div className="metrics-grid">
                  {/* Database Metrics */}
                  <div className="metric-group">
                    <h4><i className="fas fa-database"></i> Database</h4>
                    <div className="metric-stats">
                      <div className="metric-item">
                        <span className="metric-label">Total Users</span>
                        <span className="metric-value">{systemHealth.database?.total_users?.toLocaleString() || '0'}</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Active Users</span>
                        <span className="metric-value active">{systemHealth.database?.active_users?.toLocaleString() || '0'}</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Organizations</span>
                        <span className="metric-value">{systemHealth.database?.total_organizations?.toLocaleString() || '0'}</span>
                      </div>
                    </div>
                  </div>

                  {/* Authentication Metrics */}
                  <div className="metric-group">
                    <h4><i className="fas fa-shield-alt"></i> Authentication</h4>
                    <div className="metric-stats">
                      <div className="metric-item">
                        <span className="metric-label">Active Sessions</span>
                        <span className="metric-value session">{systemHealth.authentication?.active_sessions || '0'}</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Failed Logins (24h)</span>
                        <span className={`metric-value ${systemHealth.authentication?.failed_logins_24h > 0 ? 'warning' : 'success'}`}>
                          {systemHealth.authentication?.failed_logins_24h || '0'}
                        </span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Locked Accounts</span>
                        <span className={`metric-value ${systemHealth.authentication?.locked_accounts > 0 ? 'error' : 'success'}`}>
                          {systemHealth.authentication?.locked_accounts || '0'}
                        </span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Avg Session Duration</span>
                        <span className="metric-value">{systemHealth.authentication?.average_session_duration || '0'} min</span>
                      </div>
                    </div>
                  </div>

                  {/* Trust System Metrics */}
                  <div className="metric-group">
                    <h4><i className="fas fa-handshake"></i> Trust System</h4>
                    <div className="metric-stats">
                      <div className="metric-item">
                        <span className="metric-label">Total Relationships</span>
                        <span className="metric-value">{systemHealth.trust_system?.total_relationships || '0'}</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Active Relationships</span>
                        <span className="metric-value active">{systemHealth.trust_system?.active_relationships || '0'}</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Pending Approvals</span>
                        <span className={`metric-value ${systemHealth.trust_system?.pending_approvals > 50 ? 'warning' : 'normal'}`}>
                          {systemHealth.trust_system?.pending_approvals || '0'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* System Status Indicators */}
                <div className="status-indicators">
                  <div className="indicator">
                    <div className="indicator-icon healthy">
                      <i className="fas fa-server"></i>
                    </div>
                    <div className="indicator-info">
                      <span className="indicator-label">Database</span>
                      <span className="indicator-status">Online</span>
                    </div>
                  </div>
                  <div className="indicator">
                    <div className="indicator-icon healthy">
                      <i className="fas fa-network-wired"></i>
                    </div>
                    <div className="indicator-info">
                      <span className="indicator-label">API Services</span>
                      <span className="indicator-status">Operational</span>
                    </div>
                  </div>
                  <div className="indicator">
                    <div className="indicator-icon healthy">
                      <i className="fas fa-lock"></i>
                    </div>
                    <div className="indicator-info">
                      <span className="indicator-label">Security</span>
                      <span className="indicator-status">Protected</span>
                    </div>
                  </div>
                </div>

                <div className="health-actions">
                  <button onClick={fetchSystemData} className="btn btn-primary" disabled={isLoading}>
                    <i className={`fas fa-sync-alt ${isLoading ? 'fa-spin' : ''}`}></i> 
                    {isLoading ? 'Refreshing...' : 'Refresh Data'}
                  </button>
                  <button className="btn btn-outline" onClick={() => console.log('System logs viewed')}>
                    <i className="fas fa-file-alt"></i> View Logs
                  </button>
                </div>
              </div>
            ) : (
              <div className="no-data">
                <div className="no-data-icon">
                  <i className="fas fa-exclamation-triangle"></i>
                </div>
                <h4>Unable to fetch system health data</h4>
                <p>There was an issue connecting to the monitoring service</p>
                <button onClick={fetchSystemData} className="btn btn-primary">
                  <i className="fas fa-sync-alt"></i> Retry Connection
                </button>
              </div>
            )}
          </div>

          {/* Email System */}
          <div className="admin-card">
            <h3><i className="fas fa-envelope"></i> Email System</h3>
            {emailStats ? (
              <div className="email-stats">
                <div className="stat-item">
                  <span className="stat-label">Total Sent:</span>
                  <span className="stat-value">{emailStats.total_emails_sent || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Threat Alerts:</span>
                  <span className="stat-value">{emailStats.threat_alerts_sent || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Feed Notifications:</span>
                  <span className="stat-value">{emailStats.feed_notifications_sent || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Connection Status:</span>
                  <span className={`stat-value ${emailStats.gmail_connection_status === 'online' ? 'success' : emailStats.gmail_connection_status === 'offline' ? 'error' : 'warning'}`}>
                    {emailStats.gmail_connection_status || 'Unknown'}
                  </span>
                </div>
                <div className="email-actions">
                  <button onClick={handleTestConnection} className="btn btn-outline" disabled={isLoading}>
                    <i className="fas fa-plug"></i>
                    <span>{isLoading ? 'Testing...' : 'Test Connection'}</span>
                  </button>
                  <button onClick={handleTestEmail} className="btn btn-primary" disabled={isLoading}>
                    <i className="fas fa-paper-plane"></i>
                    <span>{isLoading ? 'Sending...' : 'Send Test Email'}</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="no-data">
                <p>Email statistics not available</p>
                <button onClick={fetchSystemData} className="btn btn-outline">
                  <i className="fas fa-sync-alt"></i> Reload
                </button>
              </div>
            )}
          </div>

          {/* User Management */}
          <div className="admin-card">
            <h3><i className="fas fa-users"></i> User Management</h3>
            <div className="management-actions">
              <button onClick={() => handleNavigation('user-management')} className="btn btn-primary">
                <i className="fas fa-user-plus"></i>
                <span>Create New User</span>
              </button>
              <button onClick={() => handleNavigation('user-management')} className="btn btn-outline">
                <i className="fas fa-users-cog"></i>
                <span>Manage User Roles</span>
              </button>
              <button onClick={() => handleNavigation('user-management')} className="btn btn-outline">
                <i className="fas fa-key"></i>
                <span>Reset User Passwords</span>
              </button>
            </div>
          </div>

          {/* Trust System */}
          <div className="admin-card">
            <h3><i className="fas fa-handshake"></i> Trust System</h3>
            <div className="trust-actions">
              <button onClick={() => handleNavigation('trust-management')} className="btn btn-primary">
                <i className="fas fa-network-wired"></i>
                <span>Manage Trust Relationships</span>
              </button>
              <button onClick={() => handleNavigation('trust-management')} className="btn btn-outline">
                <i className="fas fa-chart-line"></i>
                <span>View Trust Metrics</span>
              </button>
              <button onClick={() => handleNavigation('trust-management')} className="btn btn-outline">
                <i className="fas fa-cogs"></i>
                <span>System Configuration</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default AppRegister;


import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import CSSStyles from './assets/CSSStyles'; // Import the separate CSS file
import './assets/trust-management.css'; // Import Trust Management CSS
import logoImage from './assets/BlueV2.png';
import * as api from './api.js';
import UserManagementComponent from './components/UserManagement';
import TrustManagement from './components/TrustManagement';
import LoadingSpinner from './components/LoadingSpinner';


function App({ user, onLogout, isAdmin }) { // Updated props to match what AuthWrapper passes
  // State to manage the active page with URL synchronization
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
  
  // Notification state shared across components - fetch from API
  const [notifications, setNotifications] = useState([]);

  // Fetch notifications from API
  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const notificationData = await api.getAlerts();
        setNotifications(notificationData.data || notificationData || []);
      } catch (error) {
        console.warn('Failed to fetch notifications:', error);
        // Keep empty array if API fails
        setNotifications([]);
      }
    };

    if (user) {
      fetchNotifications();
    }
  }, [user]);

  // Function to mark notification as read
  const markNotificationAsRead = async (notificationId) => {
    try {
      await api.markAlertAsRead(notificationId);
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === notificationId 
            ? { ...notif, read: true }
            : notif
        )
      );
    } catch (error) {
      console.warn('Failed to mark notification as read:', error);
      // Still update UI even if API call fails
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === notificationId 
            ? { ...notif, read: true }
            : notif
        )
      );
    }
  };

  // Function to get user-specific notifications
  const getUserNotifications = () => {
    return notifications.filter(notif => 
      notif.userId === user?.id || notif.userId === 1
    );
  };

  // Function to get unread count
  const getUnreadCount = () => {
    return getUserNotifications().filter(notif => !notif.read).length;
  };
  
  // Function to switch between pages with loading state and URL synchronization
  const showPage = (pageId, options = {}) => {
    try {
      console.log('App: Switching to page:', pageId, 'with options:', options);
      
      if (!pageId) {
        console.error('App: No pageId provided to showPage');
        return;
      }
      
      setIsLoading(true);
      
      // Update URL with page and options
      const params = new URLSearchParams(window.location.search);
      params.set('page', pageId);
      
      // Add any additional options as URL parameters
      if (options.tab) {
        params.set('tab', options.tab);
      } else {
        params.delete('tab');
      }
      
      if (options.section) {
        params.set('section', options.section);
      } else {
        params.delete('section');
      }
      
      // Update URL without page reload
      const newUrl = `${window.location.pathname}?${params.toString()}`;
      window.history.pushState({ pageId, options }, '', newUrl);
      
      // Update our internal state
      const newUrlParams = {
        page: pageId,
        tab: options.tab || null,
        section: options.section || null
      };
      console.log('App: Updating URL params to:', newUrlParams);
      setUrlParams(newUrlParams);
      
      // Add delay to show loading spinner
      setTimeout(() => {
        setActivePage(pageId);
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('App: Error in showPage:', error);
      setIsLoading(false);
    }
  };

  // Handle browser back/forward navigation
  useEffect(() => {
    const handlePopState = (event) => {
      const params = new URLSearchParams(window.location.search);
      const pageFromUrl = params.get('page') || 'dashboard';
      const newUrlParams = {
        page: pageFromUrl,
        tab: params.get('tab') || null,
        section: params.get('section') || null
      };
      
      console.log('App: PopState detected, updating to:', newUrlParams);
      setUrlParams(newUrlParams);
      if (pageFromUrl !== activePage) {
        setActivePage(pageFromUrl);
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, [activePage]);

  // Add resize listener to handle chart resizing when zooming
  useEffect(() => {
    const handleResize = () => {
      // This forces a redraw of charts when window size changes (including zoom)
      if (activePage === 'dashboard') {
        // Force chart redraw by triggering a state change instead of dispatching resize event
        setIsLoading(prev => prev); // Trigger re-render without causing infinite loop
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
      
      {/* Header */}
      <Header 
        user={user} 
        onLogout={onLogout} 
        isAdmin={hasAdminAccess}
        isBlueVisionAdmin={isBlueVisionAdmin}
        isPublisher={isPublisher}
        userRole={userRole}
        notifications={getUserNotifications()}
        unreadCount={getUnreadCount()}
        onNotificationRead={markNotificationAsRead}
        showPage={showPage}
      /> {/* Pass notification data and showPage to header */}
      
      {/* Main Navigation */}
      <MainNav activePage={activePage} showPage={showPage} isAdmin={hasAdminAccess} userRole={userRole} isPublisher={isPublisher} />

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {isLoading && (
            <div className="loading-overlay">
              <LoadingSpinner />
            </div>
          )}
          
          {/* Dashboard */}
          <Dashboard active={activePage === 'dashboard'} userRole={userRole} userOrganization={userOrganization} />

          {/* Threat Feeds */}
          <ThreatFeeds active={activePage === 'threat-feeds'} userRole={userRole} userOrganization={userOrganization} />

          {/* IoC Management - All users can view, publishers can manage */}
          <IoCManagement active={activePage === 'ioc-management'} userRole={userRole} isPublisher={isPublisher} userOrganization={userOrganization} />

          {/* TTP Analysis - Publishers and BlueVision Admins only */}
          {(isPublisher || isBlueVisionAdmin) && <TTPAnalysis active={activePage === 'ttp-analysis'} userRole={userRole} userOrganization={userOrganization} />}

          {/* Institutions - Publishers and BlueVision Admins only */}
          {(isPublisher || isBlueVisionAdmin) && <Institutions active={activePage === 'institutions'} userRole={userRole} userOrganization={userOrganization} />}

          {/* Reports */}
          <Reports active={activePage === 'reports'} userRole={userRole} userOrganization={userOrganization} />

          {/* User Profile */}
          <UserProfile 
            active={activePage === 'profile'} 
            user={user} 
            userRole={userRole}
            userOrganization={userOrganization}
            notifications={getUserNotifications()}
            onNotificationRead={markNotificationAsRead}
          />

          {/* Trust Management - Publishers and BlueVision Admins only */}
          {(isPublisher || isBlueVisionAdmin) && <TrustManagement 
            active={activePage === 'trust-management'} 
            initialTab={getUrlParams().tab}
          />}

          {/* User Management - Publishers and BlueVision Admins only */}
          {(isPublisher || isBlueVisionAdmin || userRole === 'admin') && <UserManagementComponent 
            active={activePage === 'user-management'} 
            initialSection={getUrlParams().section}
          />}

          {/* Alerts System */}
          <AlertsSystem 
            active={activePage === 'alerts'} 
            notifications={notifications}
            onNotificationRead={markNotificationAsRead}
            userRole={userRole}
            userOrganization={userOrganization}
          />

          {/* Account Settings */}
          <AccountSettings active={activePage === 'account-settings'} user={user} userRole={userRole} userOrganization={userOrganization} />

          {/* Admin Settings - BlueVision Admins only */}
          {isBlueVisionAdmin && <AdminSettings active={activePage === 'admin-settings'} />}

          {/* Export Data */}
          <ExportData active={activePage === 'export-data'} />

          {/* Add Feed */}
          <AddFeed active={activePage === 'add-feed'} />

          {/* Edit User */}
          <EditUser active={activePage === 'edit-user'} />

          {/* Register User - BlueVision Admins only */}
          {isBlueVisionAdmin && <RegisterUser active={activePage === 'register-user'} />}
        </div>
      </main>
    </div>
  );
}

// Header Component with notifications and user management
function Header({ user, onLogout, isAdmin, isBlueVisionAdmin, isPublisher, userRole, notifications, unreadCount, onNotificationRead, showPage }) {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  // Get first initial for avatar
  const userInitial = user && user.username ? user.username.charAt(0).toUpperCase() : 'A';
  const userName = user && user.username ? user.username.split('@')[0] : 'User';
  
  // Display proper role name
  const getRoleDisplayName = (role) => {
    switch(role) {
      case 'BlueVisionAdmin': return 'BlueVision Administrator';
      case 'publisher': return 'Publisher';
      case 'viewer': return 'Viewer';
      default: return 'User';
    }
  };
  
  const displayRole = getRoleDisplayName(userRole);

  const handleNotificationClick = () => {
    setShowNotifications(!showNotifications);
    setShowUserMenu(false); // Close user menu when opening notifications
  };

  const handleUserMenuClick = () => {
    setShowUserMenu(!showUserMenu);
    setShowNotifications(false); // Close notifications when opening user menu
  };

  const handleNotificationItemClick = (notification) => {
    if (!notification.read) {
      onNotificationRead(notification.id);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'critical': return 'fas fa-exclamation-triangle';
      case 'warning': return 'fas fa-exclamation-circle';
      case 'info': return 'fas fa-info-circle';
      case 'update': return 'fas fa-sync-alt';
      case 'alert': return 'fas fa-bell';
      default: return 'fas fa-bell';
    }
  };

  const formatTime = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  const handleViewAllNotifications = () => {
    setShowNotifications(false);
    showPage('alerts');
  };

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.notifications-container') && !event.target.closest('.user-profile-container')) {
        setShowNotifications(false);
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

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
                  {notifications.length > 0 ? (
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
                    <div className="no-notifications">No notifications</div>
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
                <div className="user-role">{displayRole}</div>
              </div>
              <i className="fas fa-chevron-down"></i>
            </button>
            
            {showUserMenu && (
              <div className="user-menu-dropdown">
                <div className="dropdown-header">
                  <div className="user-avatar-large">{userInitial}</div>
                  <div>
                    <div className="user-name-large">{userName}</div>
                    <div className="user-email">{user?.username || 'user@example.com'}</div>
                  </div>
                </div>
                <div className="menu-divider"></div>
                <div className="menu-items">
                  <button className="menu-item" onClick={() => {setShowUserMenu(false); showPage('profile');}}>
                    <i className="fas fa-user"></i>
                    <span>My Profile</span>
                  </button>
                  <button className="menu-item" onClick={() => {setShowUserMenu(false); showPage('alerts');}}>
                    <i className="fas fa-bell"></i>
                    <span>Alerts & Notifications</span>
                    {unreadCount > 0 && <span className="menu-badge">{unreadCount}</span>}
                  </button>
                  <button className="menu-item" onClick={() => {setShowUserMenu(false); showPage('account-settings');}}>
                    <i className="fas fa-cog"></i>
                    <span>Account Settings</span>
                  </button>
                  
                  {/* Show management options for publishers and BlueVision admins */}
                  {(isPublisher || isBlueVisionAdmin || userRole === 'admin') && (
                    <>
                      <div className="menu-divider"></div>
                      <button className="menu-item" onClick={() => {setShowUserMenu(false); window.location.href = '/user-management';}}>
                        <i className="fas fa-users"></i>
                        <span>User Management</span>
                      </button>
                      <button className="menu-item" onClick={() => {setShowUserMenu(false); window.location.href = '/trust-management';}}>
                        <i className="fas fa-handshake"></i>
                        <span>Trust Management</span>
                      </button>
                    </>
                  )}
                  
                  {/* Show admin settings only for BlueVision admins */}
                  {isBlueVisionAdmin && (
                    <>
                      <button className="menu-item" onClick={() => {setShowUserMenu(false); showPage('admin-settings');}}>
                        <i className="fas fa-shield-alt"></i>
                        <span>Admin Settings</span>
                      </button>
                      <button className="menu-item" onClick={() => {setShowUserMenu(false); showPage('register-user');}}>
                        <i className="fas fa-user-plus"></i>
                        <span>Register New User</span>
                      </button>
                    </>
                  )}
                </div>
                <div className="menu-divider"></div>
                <button className="menu-item logout-item" onClick={() => {setShowUserMenu(false); onLogout()}}>
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
function MainNav({ activePage, showPage, isAdmin, userRole, isPublisher }) {
  // Base navigation items for all users
  const baseNavItems = [
    { id: 'dashboard', icon: 'fas fa-chart-line', label: 'Dashboard' },
    { id: 'threat-feeds', icon: 'fas fa-rss', label: 'Threat Feeds' },
    { id: 'ioc-management', icon: 'fas fa-search', label: 'IoC Management' },
    { id: 'reports', icon: 'fas fa-file-alt', label: 'Reports' }
  ];
  
  // Additional items for publishers and admins
  const publisherNavItems = [
    { id: 'ttp-analysis', icon: 'fas fa-sitemap', label: 'TTP Analysis' },
    { id: 'institutions', icon: 'fas fa-building', label: 'Institutions' },
    { id: 'trust-management', icon: 'fas fa-handshake', label: 'Trust Management' }
  ];
  
  // Build navigation based on user role
  let navItems = [...baseNavItems];
  
  // Add publisher/admin items if user has appropriate permissions
  if (isPublisher || userRole === 'BlueVisionAdmin') {
    navItems = [...navItems, ...publisherNavItems];
  }
  
  // Viewers only see basic items - no additional logic needed

  const handleNavClick = (itemId) => {
    console.log('MainNav item clicked:', itemId);
    if (itemId === 'alerts') {
      console.log('Switching to alerts page');
    } else if (itemId === 'profile') {
      console.log('Switching to profile page');
    }
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
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Fetch dashboard data when component becomes active
  useEffect(() => {
    if (active) {
      fetchDashboardData();
    }
  }, [active]);
  
  // Set up D3 charts when component mounts or data changes
  useEffect(() => {
    if (active && chartRef.current && chartData.length > 0) {
      createThreatActivityChart();
      
      // Add resize handler for responsive charts
      const handleResize = () => {
        createThreatActivityChart();
      };
      
      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }
  }, [active, chartData]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const dashboardData = await api.getDashboard();
      // Extract chart data from response or use empty array
      const threatData = dashboardData?.threat_activity || [];
      setChartData(threatData);
    } catch (error) {
      console.warn('Failed to fetch dashboard data:', error);
      setChartData([]); // Empty data if API fails
    } finally {
      setLoading(false);
    }
  };

  const createThreatActivityChart = () => {
    // Only proceed if the chart reference exists
    if (!chartRef.current) return;
    
    // Clear previous chart if any
    d3.select(chartRef.current).selectAll("*").remove();
    
    // Use real data from API, fallback to empty array if no data
    const data = chartData.length > 0 ? chartData : [
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
          <p className="page-subtitle">Real-time overview of threat intelligence and platform activity</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline" onClick={() => showPage('export-data')}>
            <i className="fas fa-download"></i> Export Data
          </button>
          <button className="btn btn-primary" onClick={() => showPage('add-feed')}>
            <i className="fas fa-plus"></i> Add New Feed
          </button>
        </div>
      </div>

      {/* Stats Cards - Always visible and prominent */}
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
      
      // Add resize handler for responsive map
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

        {/* Report Cards 3-6 would go here, similar to the original code */}
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

// User Profile Component - Enhanced with notifications
function UserProfile({ active, user, userRole, userOrganization, notifications, onNotificationRead }) {
  const [activeTab, setActiveTab] = useState('profile');
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: user?.username || '',
    fullName: user?.full_name || `${user?.first_name || ''} ${user?.last_name || ''}`.trim(),
    email: user?.email || user?.username || '',
    organization: userOrganization?.name || '',
    role: userRole || 'viewer',
    phone: user?.phone_number || '',
    department: user?.department || ''
  });

  // Update form data when user prop changes
  React.useEffect(() => {
    setFormData({
      username: user?.username || '',
      fullName: user?.full_name || `${user?.first_name || ''} ${user?.last_name || ''}`.trim(),
      email: user?.email || user?.username || '',
      organization: userOrganization?.name || '',
      role: userRole || 'viewer',
      phone: user?.phone_number || '',
      department: user?.department || ''
    });
  }, [user, userOrganization, userRole]);

  if (!active) return null;

  const handleSave = async () => {
    try {
      // Prepare profile data for API call
      const profileData = {
        first_name: formData.fullName.split(' ')[0] || '',
        last_name: formData.fullName.split(' ').slice(1).join(' ') || '',
        email: formData.email,
        phone_number: formData.phone,
        department: formData.department
      };

      // Call the API to update profile
      const result = await api.updateUserProfile(profileData);
      
      if (result.success) {
        alert('Profile updated successfully!');
        setEditing(false);
        // Optionally update the local user data if passed as prop
        // onUserUpdate && onUserUpdate(result.data.profile);
      } else {
        alert('Failed to update profile: ' + (result.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Profile update error:', error);
      alert('Failed to update profile: ' + error.message);
    }
  };

  const handleNotificationClick = (notification) => {
    if (!notification.read) {
      onNotificationRead(notification.id);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'critical': return 'fas fa-exclamation-triangle';
      case 'warning': return 'fas fa-exclamation-circle';
      case 'info': return 'fas fa-info-circle';
      case 'update': return 'fas fa-sync-alt';
      case 'alert': return 'fas fa-bell';
      default: return 'fas fa-bell';
    }
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleString();
  };

  return (
    <section id="profile" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">User Profile</h1>
          <p className="page-subtitle">Manage your account settings and view your notifications</p>
        </div>
        <div className="action-buttons">
          {!editing ? (
            <button className="btn btn-primary" onClick={() => setEditing(true)}>
              <i className="fas fa-edit"></i> Edit Profile
            </button>
          ) : (
            <>
              <button className="btn btn-outline" onClick={() => setEditing(false)}>
                <i className="fas fa-times"></i> Cancel
              </button>
              <button className="btn btn-primary" onClick={handleSave}>
                <i className="fas fa-save"></i> Save Changes
              </button>
            </>
          )}
        </div>
      </div>

      {/* Profile Tabs */}
      <div className="profile-tabs">
        <button 
          className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          <i className="fas fa-user"></i> Profile Information
        </button>
        <button 
          className={`tab-button ${activeTab === 'notifications' ? 'active' : ''}`}
          onClick={() => setActiveTab('notifications')}
        >
          <i className="fas fa-bell"></i> My Notifications ({notifications?.filter(n => !n.read).length || 0})
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
                  <div className="profile-form">
                    <div className="form-row">
                      <div className="form-group">
                        <label>Username</label>
                        <input 
                          type="text" 
                          value={formData.username} 
                          disabled={!editing}
                          onChange={(e) => setFormData({...formData, username: e.target.value})}
                        />
                      </div>
                      <div className="form-group">
                        <label>Full Name</label>
                        <input 
                          type="text" 
                          value={formData.fullName} 
                          disabled={!editing}
                          onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="form-row">
                      <div className="form-group">
                        <label>Email</label>
                        <input 
                          type="email" 
                          value={formData.email} 
                          disabled={!editing}
                          onChange={(e) => setFormData({...formData, email: e.target.value})}
                        />
                      </div>
                      <div className="form-group">
                        <label>Phone</label>
                        <input 
                          type="tel" 
                          value={formData.phone} 
                          disabled={!editing}
                          placeholder="Enter phone number"
                          onChange={(e) => setFormData({...formData, phone: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="form-row">
                      <div className="form-group">
                        <label>Organization</label>
                        <input 
                          type="text" 
                          value={formData.organization} 
                          disabled={!editing}
                          placeholder="Enter organization"
                          onChange={(e) => setFormData({...formData, organization: e.target.value})}
                        />
                      </div>
                      <div className="form-group">
                        <label>Department</label>
                        <input 
                          type="text" 
                          value={formData.department} 
                          disabled={!editing}
                          placeholder="Enter department"
                          onChange={(e) => setFormData({...formData, department: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="form-group">
                      <label>Role</label>
                      <input 
                        type="text" 
                        value={formData.role} 
                        disabled
                      />
                      <small className="form-hint">Role is managed by administrators</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="profile-sidebar">
              <div className="card">
                <div className="card-header">
                  <h2 className="card-title">
                    <i className="fas fa-chart-bar card-icon"></i> Account Summary
                  </h2>
                </div>
                <div className="card-content">
                  <div className="account-stats">
                    <div className="stat-item">
                      <div className="stat-label">Account Status</div>
                      <div className="stat-value">
                        <span className={`badge ${user?.is_active ? 'badge-active' : 'badge-inactive'}`}>
                          {user?.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-label">Last Login</div>
                      <div className="stat-value">
                        {user?.last_login ? new Date(user.last_login).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        }) : 'Never'}
                      </div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-label">Notifications</div>
                      <div className="stat-value">{notifications?.filter(n => !n.read).length || 0} unread</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-label">Member Since</div>
                      <div className="stat-value">
                        {user?.date_joined ? new Date(user.date_joined).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long'
                        }) : 'Unknown'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <div className="profile-content">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">
                <i className="fas fa-bell card-icon"></i> My Notifications
              </h2>
              <div className="card-actions">
                <button className="btn btn-outline btn-sm">Mark All Read</button>
              </div>
            </div>
            <div className="card-content">
              {notifications && notifications.length > 0 ? (
                <div className="notifications-list-profile">
                  {notifications.map(notification => (
                    <div 
                      key={notification.id}
                      className={`notification-item-profile ${notification.read ? 'read' : 'unread'}`}
                      onClick={() => handleNotificationClick(notification)}
                    >
                      <div className="notification-icon-profile">
                        <i className={getNotificationIcon(notification.type)}></i>
                      </div>
                      <div className="notification-content-profile">
                        <div className="notification-header">
                          <div className="notification-title">{notification.title}</div>
                          <div className="notification-time">{formatTime(notification.timestamp)}</div>
                        </div>
                        <div className="notification-message">{notification.message}</div>
                        {!notification.read && <div className="unread-indicator"></div>}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-notifications-profile">
                  <i className="fas fa-bell-slash"></i>
                  <p>No notifications yet</p>
                </div>
              )}
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
                <i className="fas fa-shield-alt card-icon"></i> Security Settings
              </h2>
            </div>
            <div className="card-content">
              <div className="security-section">
                <h3>Password</h3>
                <button className="btn btn-outline">
                  <i className="fas fa-key"></i> Change Password
                </button>
              </div>
              <div className="security-section">
                <h3>Two-Factor Authentication</h3>
                <p className="text-muted">Add an extra layer of security to your account</p>
                <button className="btn btn-primary">
                  <i className="fas fa-mobile-alt"></i> Setup 2FA
                </button>
              </div>
              <div className="security-section">
                <h3>Active Sessions</h3>
                <p className="text-muted">Manage your active login sessions</p>
                <div className="session-item">
                  <div className="session-info">
                    <div className="session-device">Current Session</div>
                    <div className="session-details">Windows • Chrome • Just now</div>
                  </div>
                  <span className="badge badge-active">Active</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

// Original Complex UserProfile Component - will restore later
function UserProfileDetailed({ active, user }) {
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({});
  const [sessions, setSessions] = useState([]);
  const [showChangePassword, setShowChangePassword] = useState(false);

  useEffect(() => {
    if (active) {
      try {
        fetchProfileData();
        fetchSessions();
      } catch (error) {
        console.error('Error in UserProfile useEffect:', error);
      }
    }
  }, [active]);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      const data = await api.getUserProfile();
      setProfileData(data);
      setFormData(data);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      // Set some default data to prevent crashes
      setProfileData({ username: user?.username || 'Unknown', full_name: 'Loading...', email: 'Loading...', organization: 'Loading...', role: 'User' });
    } finally {
      setLoading(false);
    }
  };

  const fetchSessions = async () => {
    try {
      const data = await api.getUserSessions();
      setSessions(data);
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      await api.updateUserProfile(formData);
      setProfileData(formData);
      setEditing(false);
    } catch (error) {
      console.error('Failed to update profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRevokeSession = async (sessionId) => {
    try {
      await api.revokeSession(sessionId);
      fetchSessions();
    } catch (error) {
      console.error('Failed to revoke session:', error);
    }
  };

  if (!active) return null;

  return (
    <section id="profile" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">User Profile</h1>
          <p className="page-subtitle">Manage your account settings and preferences</p>
        </div>
        <div className="action-buttons">
          {!editing ? (
            <button className="btn btn-primary" onClick={() => setEditing(true)}>
              <i className="fas fa-edit"></i> Edit Profile
            </button>
          ) : (
            <>
              <button className="btn btn-outline" onClick={() => setEditing(false)}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleSave} disabled={loading}>
                <i className="fas fa-save"></i> Save Changes
              </button>
            </>
          )}
        </div>
      </div>

      <div className="profile-grid">
        <div className="profile-main">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-user card-icon"></i> Profile Information</h2>
            </div>
            <div className="card-content">
              {loading ? (
                <LoadingSpinner size="small" />
              ) : (
                <div className="profile-form">
                  <div className="form-group">
                    <label>Username</label>
                    <input
                      type="text"
                      value={profileData?.username || ''}
                      disabled={true}
                    />
                  </div>
                  <div className="form-group">
                    <label>Full Name</label>
                    <input
                      type="text"
                      value={editing ? formData.full_name || '' : profileData?.full_name || ''}
                      onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                      disabled={!editing}
                    />
                  </div>
                  <div className="form-group">
                    <label>Email</label>
                    <input
                      type="email"
                      value={editing ? formData.email || '' : profileData?.email || ''}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      disabled={!editing}
                    />
                  </div>
                  <div className="form-group">
                    <label>Organization</label>
                    <input
                      type="text"
                      value={editing ? formData.organization || '' : profileData?.organization || ''}
                      onChange={(e) => setFormData({...formData, organization: e.target.value})}
                      disabled={!editing}
                    />
                  </div>
                  <div className="form-group">
                    <label>Role</label>
                    <input
                      type="text"
                      value={profileData?.role || ''}
                      disabled={true}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-shield-alt card-icon"></i> Security Settings</h2>
            </div>
            <div className="card-content">
              <div className="security-actions">
                <button 
                  className="btn btn-outline"
                  onClick={() => setShowChangePassword(!showChangePassword)}
                >
                  <i className="fas fa-key"></i> Change Password
                </button>
              </div>
              
              {showChangePassword && (
                <ChangePasswordForm onClose={() => setShowChangePassword(false)} />
              )}
            </div>
          </div>
        </div>

        <div className="profile-sidebar">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-clock card-icon"></i> Active Sessions</h2>
            </div>
            <div className="card-content">
              <div className="sessions-list">
                {sessions.map((session, index) => (
                  <div key={index} className="session-item">
                    <div className="session-info">
                      <div className="session-device">{session.device || 'Unknown Device'}</div>
                      <div className="session-ip">{session.ip_address}</div>
                      <div className="session-time">{session.created_at}</div>
                    </div>
                    <button 
                      className="btn btn-outline btn-sm"
                      onClick={() => handleRevokeSession(session.id)}
                    >
                      <i className="fas fa-times"></i> Revoke
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-chart-bar card-icon"></i> Activity Summary</h2>
            </div>
            <div className="card-content">
              <div className="activity-stats">
                <div className="stat-item">
                  <div className="stat-value">{profileData?.login_count || 0}</div>
                  <div className="stat-label">Total Logins</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{profileData?.last_login || 'Never'}</div>
                  <div className="stat-label">Last Login</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{profileData?.is_active ? 'Active' : 'Inactive'}</div>
                  <div className="stat-label">Account Status</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// Change Password Component
function ChangePasswordForm({ onClose }) {
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    try {
      setLoading(true);
      setError('');
      console.log('Sending password change request with data:', {
        currentPassword: passwordData.currentPassword ? '***filled***' : 'empty',
        newPassword: passwordData.newPassword ? '***filled***' : 'empty', 
        confirmPassword: passwordData.confirmPassword ? '***filled***' : 'empty'
      });
      await api.changePassword(passwordData.currentPassword, passwordData.newPassword, passwordData.confirmPassword);
      onClose();
    } catch (error) {
      setError(error.toString());
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="change-password-form">
      <form onSubmit={handleSubmit}>
        {error && <div className="error-message">{error}</div>}
        <div className="form-group">
          <label>Current Password</label>
          <input
            type="password"
            value={passwordData.currentPassword}
            onChange={(e) => setPasswordData({...passwordData, currentPassword: e.target.value})}
            required
          />
        </div>
        <div className="form-group">
          <label>New Password</label>
          <input
            type="password"
            value={passwordData.newPassword}
            onChange={(e) => setPasswordData({...passwordData, newPassword: e.target.value})}
            required
          />
        </div>
        <div className="form-group">
          <label>Confirm New Password</label>
          <input
            type="password"
            value={passwordData.confirmPassword}
            onChange={(e) => setPasswordData({...passwordData, confirmPassword: e.target.value})}
            required
          />
        </div>
        <div className="form-actions">
          <button type="button" className="btn btn-outline" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Changing...' : 'Change Password'}
          </button>
        </div>
      </form>
    </div>
  );
}

// Trust Management Component is now imported from separate file - old components below are kept for reference
function TrustManagementOld({ active }) {
  const [trustRelationships, setTrustRelationships] = useState([]);
  const [trustMetrics, setTrustMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (active) {
      fetchTrustData();
    }
  }, [active]);

  const fetchTrustData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [relationships, metrics] = await Promise.all([
        api.getTrustRelationships().catch(() => ({ data: [] })),
        api.getTrustMetrics().catch(() => ({ data: {} }))
      ]);
      setTrustRelationships(relationships.data || relationships || []);
      setTrustMetrics(metrics.data || metrics || {});
    } catch (err) {
      console.error('Failed to fetch trust data:', err);
      setError('Failed to load trust data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!active) return null;

  return (
    <section id="trust-management" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Trust Management</h1>
          <p className="page-subtitle">Manage trust relationships and groups</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline" onClick={fetchTrustData}>
            <i className="fas fa-sync-alt"></i> Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <i className="fas fa-exclamation-triangle"></i>
          {error}
        </div>
      )}
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title"><i className="fas fa-handshake card-icon"></i> Trust Relationships</h2>
        </div>
        <div className="card-content">
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading trust relationships...</p>
            </div>
          ) : trustRelationships.length === 0 ? (
            <div className="empty-state">
              <i className="fas fa-handshake"></i>
              <h3>No Trust Relationships</h3>
              <p>No trust relationships have been established yet.</p>
            </div>
          ) : (
            <div className="trust-relationships-list">
              {trustRelationships.map((relationship, index) => (
                <div key={relationship.id || index} className="trust-relationship-card">
                  <div className="relationship-info">
                    <h4>{relationship.target_organization?.name || 'Unknown Organization'}</h4>
                    <span className={`trust-level ${relationship.trust_level?.name?.toLowerCase() || 'unknown'}`}>
                      {relationship.trust_level?.name || 'Unknown Level'}
                    </span>
                  </div>
                  <div className="relationship-status">
                    <span className={`status-badge ${relationship.status?.toLowerCase() || 'unknown'}`}>
                      {relationship.status || 'Unknown'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {trustMetrics && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title"><i className="fas fa-chart-bar card-icon"></i> Trust Metrics</h2>
          </div>
          <div className="card-content">
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-value">{trustMetrics.total_relationships || 0}</div>
                <div className="metric-label">Total Relationships</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{trustMetrics.active_relationships || 0}</div>
                <div className="metric-label">Active Relationships</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{trustMetrics.trust_score || 'N/A'}</div>
                <div className="metric-label">Average Trust Score</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

// Original Complex TrustManagement Component - will restore later
function TrustManagementDetailed({ active }) {
  const [trustRelationships, setTrustRelationships] = useState([]);
  const [trustGroups, setTrustGroups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showNewRelationship, setShowNewRelationship] = useState(false);
  const [showNewGroup, setShowNewGroup] = useState(false);

  useEffect(() => {
    if (active) {
      fetchTrustData();
    }
  }, [active]);

  const fetchTrustData = async () => {
    try {
      setLoading(true);
      const [relationships, groups] = await Promise.all([
        api.getTrustRelationships().catch(() => []),
        api.getTrustGroups().catch(() => [])
      ]);
      setTrustRelationships(relationships || []);
      setTrustGroups(groups || []);
    } catch (error) {
      console.error('Failed to fetch trust data:', error);
      setTrustRelationships([]);
      setTrustGroups([]);
    } finally {
      setLoading(false);
    }
  };

  if (!active) return null;

  return (
    <section id="trust-management" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Trust Management</h1>
          <p className="page-subtitle">Manage trust relationships and groups</p>
        </div>
        <div className="action-buttons">
          <button 
            className="btn btn-outline"
            onClick={() => setShowNewGroup(true)}
          >
            <i className="fas fa-plus"></i> New Trust Group
          </button>
          <button 
            className="btn btn-primary"
            onClick={() => setShowNewRelationship(true)}
          >
            <i className="fas fa-handshake"></i> New Trust Relationship
          </button>
        </div>
      </div>

      <div className="trust-grid">
        <div className="trust-main">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-handshake card-icon"></i> Trust Relationships</h2>
              <div className="card-actions">
                <button className="btn btn-outline btn-sm" onClick={fetchTrustData}>
                  <i className="fas fa-sync-alt"></i> Refresh
                </button>
              </div>
            </div>
            <div className="card-content">
              {loading ? (
                <LoadingSpinner size="small" />
              ) : (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Partner Organization</th>
                      <th>Trust Level</th>
                      <th>Relationship Type</th>
                      <th>Status</th>
                      <th>Created Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {trustRelationships.map((relationship, index) => (
                      <tr key={index}>
                        <td>{relationship.partner_organization}</td>
                        <td>
                          <div className="trust-level-bar">
                            <div 
                              className="trust-fill" 
                              style={{width: `${relationship.trust_level}%`}}
                            ></div>
                            <span className="trust-percentage">{relationship.trust_level}%</span>
                          </div>
                        </td>
                        <td>
                          <span className={`badge badge-${relationship.relationship_type.toLowerCase()}`}>
                            {relationship.relationship_type}
                          </span>
                        </td>
                        <td>
                          <span className={`badge badge-${relationship.status.toLowerCase()}`}>
                            {relationship.status}
                          </span>
                        </td>
                        <td>{relationship.created_at}</td>
                        <td>
                          <button className="btn btn-outline btn-sm">
                            <i className="fas fa-edit"></i>
                          </button>
                          <button className="btn btn-outline btn-sm">
                            <i className="fas fa-eye"></i>
                          </button>
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
              <h2 className="card-title"><i className="fas fa-users card-icon"></i> Trust Groups</h2>
            </div>
            <div className="card-content">
              <div className="trust-groups-grid">
                {trustGroups.map((group, index) => (
                  <div key={index} className="trust-group-card">
                    <div className="group-header">
                      <h3>{group.name}</h3>
                      <span className={`badge badge-${group.status.toLowerCase()}`}>
                        {group.status}
                      </span>
                    </div>
                    <div className="group-description">
                      {group.description}
                    </div>
                    <div className="group-stats">
                      <div className="stat-item">
                        <span className="stat-value">{group.member_count}</span>
                        <span className="stat-label">Members</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-value">{group.avg_trust_level}%</span>
                        <span className="stat-label">Avg Trust</span>
                      </div>
                    </div>
                    <div className="group-actions">
                      <button className="btn btn-outline btn-sm">
                        <i className="fas fa-eye"></i> View
                      </button>
                      <button className="btn btn-outline btn-sm">
                        <i className="fas fa-edit"></i> Edit
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="trust-sidebar">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-chart-pie card-icon"></i> Trust Analytics</h2>
            </div>
            <div className="card-content">
              <div className="trust-stats">
                <div className="stat-card">
                  <div className="stat-value">{trustRelationships.length}</div>
                  <div className="stat-label">Active Relationships</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{trustGroups.length}</div>
                  <div className="stat-label">Trust Groups</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">
                    {trustRelationships.length > 0 
                      ? Math.round(trustRelationships.reduce((sum, rel) => sum + rel.trust_level, 0) / trustRelationships.length)
                      : 0
                    }%
                  </div>
                  <div className="stat-label">Average Trust Level</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {showNewRelationship && (
        <NewTrustRelationshipModal 
          onClose={() => setShowNewRelationship(false)}
          onSave={fetchTrustData}
        />
      )}

      {showNewGroup && (
        <NewTrustGroupModal 
          onClose={() => setShowNewGroup(false)}
          onSave={fetchTrustData}
        />
      )}
    </section>
  );
}

// User Management Component - Enhanced for admins only
function UserManagement({ active, isAdmin, currentUser, showPage }) {
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [showNewUserModal, setShowNewUserModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch users from API when component becomes active
  useEffect(() => {
    if (active && isAdmin) {
      fetchUsers();
    }
  }, [active, isAdmin]);

  // Filter users based on search and filters - moved BEFORE early returns
  useEffect(() => {
    let filtered = users.filter(user => {
      const matchesSearch = (user.full_name || user.username || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (user.organization?.name || '').toLowerCase().includes(searchTerm.toLowerCase());
      const matchesRole = selectedRole === 'all' || user.role === selectedRole;
      const matchesStatus = selectedStatus === 'all' || (user.is_active ? 'Active' : 'Inactive') === selectedStatus;
      
      return matchesSearch && matchesRole && matchesStatus;
    });
    
    setFilteredUsers(filtered);
  }, [searchTerm, selectedRole, selectedStatus, users]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const userData = await api.getUsers();
      const usersArray = userData.data || userData || [];
      setUsers(Array.isArray(usersArray) ? usersArray : []);
    } catch (err) {
      console.error('Failed to fetch users:', err);
      setError('Failed to load users. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!active) return null;
  
  // Access control - only admins can access user management
  if (!isAdmin) {
    return (
      <section id="user-management" className={`page-section ${active ? 'active' : ''}`}>
        <div className="access-denied">
          <div className="access-denied-content">
            <i className="fas fa-shield-alt"></i>
            <h2>Access Denied</h2>
            <p>You don't have permission to access this page.</p>
            <p>Only administrators can manage users.</p>
          </div>
        </div>
      </section>
    );
  }

  const handleUserAction = async (action, userId) => {
    try {
      switch (action) {
        case 'edit':
          // Navigate to edit user page or open edit modal
          showPage('edit-user');
          break;
        case 'delete':
          if (confirm('Are you sure you want to delete this user?')) {
            setLoading(true);
            // await api.deleteUser(userId); // Uncomment when backend supports this
            // For now, remove from local state
            setUsers(prev => prev.filter(user => user.id !== userId));
            alert('User deleted successfully!');
          }
          break;
        case 'activate':
        case 'deactivate':
          setLoading(true);
          const isActivating = action === 'activate';
          // await api.updateUser(userId, { is_active: isActivating }); // Uncomment when backend supports this
          // For now, update local state
          setUsers(prev => prev.map(user => 
            user.id === userId ? { ...user, is_active: isActivating } : user
          ));
          alert(`User ${isActivating ? 'activated' : 'deactivated'} successfully!`);
          break;
        default:
          break;
      }
    } catch (err) {
      console.error('User action failed:', err);
      alert('Action failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="user-management" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">User Management</h1>
          <p className="page-subtitle">Manage system users, roles, and permissions</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline">
            <i className="fas fa-download"></i> Export Users
          </button>
          <button 
            className="btn btn-primary"
            onClick={() => setShowNewUserModal(true)}
          >
            <i className="fas fa-user-plus"></i> Add New User
          </button>
        </div>
      </div>

      {/* User Statistics */}
      <div className="user-stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-users"></i>
          </div>
          <div className="stat-content">
            <div className="stat-value">{users.length}</div>
            <div className="stat-label">Total Users</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-user-check"></i>
          </div>
          <div className="stat-content">
            <div className="stat-value">{users.filter(u => u.status === 'Active').length}</div>
            <div className="stat-label">Active Users</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-shield-alt"></i>
          </div>
          <div className="stat-content">
            <div className="stat-value">{users.filter(u => u.role === 'Administrator').length}</div>
            <div className="stat-label">Administrators</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-building"></i>
          </div>
          <div className="stat-content">
            <div className="stat-value">{new Set(users.map(u => u.organization)).size}</div>
            <div className="stat-label">Organizations</div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="card">
        <div className="card-content">
          <div className="user-filters">
            <div className="filter-group">
              <input
                type="text"
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
            <div className="filter-group">
              <select 
                value={selectedRole} 
                onChange={(e) => setSelectedRole(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Roles</option>
                <option value="Administrator">Administrator</option>
                <option value="Analyst">Analyst</option>
                <option value="User">User</option>
              </select>
            </div>
            <div className="filter-group">
              <select 
                value={selectedStatus} 
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Status</option>
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
              </select>
            </div>
            <button className="btn btn-outline" onClick={() => {
              setSearchTerm('');
              setSelectedRole('all');
              setSelectedStatus('all');
            }}>
              <i className="fas fa-times"></i> Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <i className="fas fa-users card-icon"></i> 
            System Users ({filteredUsers.length})
          </h2>
        </div>
        <div className="card-content">
          {filteredUsers.length > 0 ? (
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Organization</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Last Login</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan="6" className="text-center">
                        <div className="loading-spinner"></div>
                        <p>Loading users...</p>
                      </td>
                    </tr>
                  ) : error ? (
                    <tr>
                      <td colSpan="6" className="text-center">
                        <div className="error-message">
                          <i className="fas fa-exclamation-triangle"></i>
                          <p>{error}</p>
                          <button className="btn btn-outline btn-sm" onClick={fetchUsers}>
                            <i className="fas fa-refresh"></i> Try Again
                          </button>
                        </div>
                      </td>
                    </tr>
                  ) : filteredUsers.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="text-center">
                        <p>No users found</p>
                      </td>
                    </tr>
                  ) : (
                    filteredUsers.map(user => {
                      const fullName = user.full_name || `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username;
                      const organization = user.organization?.name || 'Unknown';
                      const status = user.is_active ? 'Active' : 'Inactive';
                      const lastLogin = user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never';
                      
                      return (
                        <tr key={user.id}>
                          <td>
                            <div className="user-cell">
                              <div className="user-avatar">{fullName.charAt(0).toUpperCase()}</div>
                              <div className="user-details">
                                <div className="user-name">{fullName}</div>
                                <div className="user-email">{user.username}</div>
                              </div>
                            </div>
                          </td>
                          <td>{organization}</td>
                          <td>
                            <span className={`role-badge role-${(user.role || 'viewer').toLowerCase()}`}>
                              {user.role || 'viewer'}
                            </span>
                          </td>
                          <td>
                            <span className={`badge ${status === 'Active' ? 'badge-active' : 'badge-inactive'}`}>
                              {status}
                            </span>
                          </td>
                          <td>{lastLogin}</td>
                          <td>
                            <div className="action-buttons-table">
                              <button 
                                className="btn-icon" 
                                title="Edit User"
                                onClick={() => handleUserAction('edit', user.id)}
                                disabled={loading}
                              >
                                <i className="fas fa-edit"></i>
                              </button>
                              {status === 'Active' ? (
                                <button 
                                  className="btn-icon btn-warning" 
                                  title="Deactivate User"
                                  onClick={() => handleUserAction('deactivate', user.id)}
                                  disabled={loading}
                                >
                                  <i className="fas fa-user-slash"></i>
                                </button>
                              ) : (
                                <button 
                                  className="btn-icon btn-success" 
                                  title="Activate User"
                                  onClick={() => handleUserAction('activate', user.id)}
                                  disabled={loading}
                                >
                                  <i className="fas fa-user-check"></i>
                                </button>
                              )}
                              <button 
                                className="btn-icon btn-danger" 
                                title="Delete User"
                                onClick={() => handleUserAction('delete', user.id)}
                                disabled={loading}
                              >
                                <i className="fas fa-trash"></i>
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="no-users">
              <i className="fas fa-users"></i>
              <p>No users found matching your criteria</p>
            </div>
          )}
        </div>
      </div>

      {/* New User Modal Placeholder */}
      {showNewUserModal && (
        <div className="modal-overlay" onClick={() => setShowNewUserModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Add New User</h3>
              <button className="close-btn" onClick={() => setShowNewUserModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <p>Click below to navigate to the user registration page:</p>
              <button className="btn btn-primary" onClick={() => {setShowNewUserModal(false); showPage('register-user');}}>Go to Registration</button>
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setShowNewUserModal(false)}>
                Cancel
              </button>
              <button className="btn btn-primary">
                Create User
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

// Original Complex UserManagement Component - will restore later
function UserManagementDetailed({ active }) {
  const [users, setUsers] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('');
  const [showNewUser, setShowNewUser] = useState(false);

  useEffect(() => {
    if (active) {
      fetchUsersData();
    }
  }, [active]);

  const fetchUsersData = async () => {
    try {
      setLoading(true);
      const [usersData, orgsData] = await Promise.all([
        api.getUsersList(),
        api.getOrganizations()
      ]);
      setUsers(usersData);
      setOrganizations(orgsData);
    } catch (error) {
      console.error('Failed to fetch users data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter(user => 
    user.username.toLowerCase().includes(filter.toLowerCase()) ||
    user.full_name.toLowerCase().includes(filter.toLowerCase()) ||
    user.organization.toLowerCase().includes(filter.toLowerCase())
  );

  if (!active) return null;

  return (
    <section id="user-management" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">User Management</h1>
          <p className="page-subtitle">Manage system users and permissions</p>
        </div>
        <div className="action-buttons">
          <button 
            className="btn btn-outline"
            onClick={fetchUsersData}
          >
            <i className="fas fa-sync-alt"></i> Refresh
          </button>
          <button 
            className="btn btn-primary"
            onClick={() => setShowNewUser(true)}
          >
            <i className="fas fa-user-plus"></i> Add User
          </button>
        </div>
      </div>

      <div className="filters-section">
        <div className="filter-group">
          <label className="filter-label">Search Users</label>
          <div className="filter-control">
            <input
              type="text"
              placeholder="Search by username, name, or organization..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title"><i className="fas fa-users card-icon"></i> System Users</h2>
        </div>
        <div className="card-content">
          {loading ? (
            <LoadingSpinner size="small" />
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Full Name</th>
                  <th>Organization</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Last Login</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((user, index) => (
                  <tr key={index}>
                    <td>{user.username}</td>
                    <td>{user.full_name}</td>
                    <td>{user.organization}</td>
                    <td>
                      <span className={`badge badge-${user.role.toLowerCase()}`}>
                        {user.role}
                      </span>
                    </td>
                    <td>
                      <span className={`badge badge-${user.is_active ? 'active' : 'inactive'}`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>{user.last_login || 'Never'}</td>
                    <td>
                      <button className="btn btn-outline btn-sm">
                        <i className="fas fa-edit"></i>
                      </button>
                      <button className="btn btn-outline btn-sm">
                        <i className="fas fa-eye"></i>
                      </button>
                      {user.is_locked && (
                        <button className="btn btn-outline btn-sm">
                          <i className="fas fa-unlock"></i>
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <div className="user-stats-grid">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title"><i className="fas fa-chart-bar card-icon"></i> User Statistics</h2>
          </div>
          <div className="card-content">
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-value">{users.length}</div>
                <div className="stat-label">Total Users</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{users.filter(u => u.is_active).length}</div>
                <div className="stat-label">Active Users</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{organizations.length}</div>
                <div className="stat-label">Organizations</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{users.filter(u => u.role === 'Admin').length}</div>
                <div className="stat-label">Administrators</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {showNewUser && (
        <NewUserModal 
          onClose={() => setShowNewUser(false)}
          onSave={fetchUsersData}
          organizations={organizations}
        />
      )}
    </section>
  );
}

// Alerts System Component - Simplified for now
function AlertsSystem({ active, notifications, onNotificationRead, userRole, userOrganization }) {
  if (!active) return null;

  const handleNotificationClick = (notification) => {
    if (!notification.read) {
      onNotificationRead(notification.id);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'critical': return 'fas fa-exclamation-triangle';
      case 'warning': return 'fas fa-exclamation-circle';
      case 'info': return 'fas fa-info-circle';
      case 'update': return 'fas fa-sync-alt';
      case 'alert': return 'fas fa-bell';
      default: return 'fas fa-bell';
    }
  };

  const formatTime = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  return (
    <section id="alerts" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Alerts & Notifications</h1>
          <p className="page-subtitle">View and manage your notifications</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline">
            <i className="fas fa-filter"></i> Filter
          </button>
          <button className="btn btn-primary">
            <i className="fas fa-bell"></i> Mark All Read
          </button>
        </div>
      </div>
      
      <div className="notifications-grid">
        {notifications && notifications.length > 0 ? (
          notifications.map(notification => (
            <div 
              key={notification.id}
              className={`notification-card ${notification.read ? 'read' : 'unread'}`}
              onClick={() => handleNotificationClick(notification)}
            >
              <div className="notification-header">
                <div className="notification-icon">
                  <i className={getNotificationIcon(notification.type)}></i>
                </div>
                <div className="notification-meta">
                  <span className={`notification-type ${notification.type}`}>
                    {notification.type.toUpperCase()}
                  </span>
                  <span className="notification-time">
                    {formatTime(notification.timestamp)}
                  </span>
                </div>
              </div>
              <div className="notification-content">
                <h3 className="notification-title">{notification.title}</h3>
                <p className="notification-message">{notification.message}</p>
              </div>
              {!notification.read && (
                <div className="notification-badge">
                  <span className="unread-indicator"></span>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="no-notifications">
            <div className="no-notifications-content">
              <i className="fas fa-bell-slash"></i>
              <h3>No notifications</h3>
              <p>You're all caught up! No new notifications at this time.</p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

// Original Complex AlertsSystem Component - will restore later
function AlertsSystemDetailed({ active }) {
  const [alertStats, setAlertStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [testEmail, setTestEmail] = useState('');
  const [connectionStatus, setConnectionStatus] = useState(null);

  useEffect(() => {
    if (active) {
      fetchAlertsData();
      testConnection();
    }
  }, [active]);

  const fetchAlertsData = async () => {
    try {
      setLoading(true);
      const stats = await api.getEmailStatistics();
      setAlertStats(stats);
    } catch (error) {
      console.error('Failed to fetch alerts data:', error);
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async () => {
    try {
      const result = await api.testGmailConnection();
      setConnectionStatus(result.status);
    } catch (error) {
      setConnectionStatus('error');
      console.error('Connection test failed:', error);
    }
  };

  const sendTestEmail = async () => {
    if (!testEmail) return;
    
    try {
      await api.sendTestEmail(testEmail);
      alert('Test email sent successfully!');
      setTestEmail('');
    } catch (error) {
      alert('Failed to send test email: ' + error);
    }
  };

  if (!active) return null;

  return (
    <section id="alerts" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Alerts System</h1>
          <p className="page-subtitle">Manage email notifications and alerts</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline" onClick={testConnection}>
            <i className="fas fa-plug"></i> Test Connection
          </button>
          <button className="btn btn-primary" onClick={fetchAlertsData}>
            <i className="fas fa-sync-alt"></i> Refresh
          </button>
        </div>
      </div>

      <div className="alerts-grid">
        <div className="alerts-main">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">
                <i className="fas fa-envelope card-icon"></i> Email Service Status
              </h2>
              <div className="card-actions">
                <span className={`status-badge ${connectionStatus === 'connected' ? 'success' : 'error'}`}>
                  {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
            <div className="card-content">
              <div className="service-info">
                <div className="info-item">
                  <label>Service Provider</label>
                  <span>Gmail SMTP</span>
                </div>
                <div className="info-item">
                  <label>Connection Status</label>
                  <span className={connectionStatus === 'connected' ? 'text-success' : 'text-error'}>
                    {connectionStatus === 'connected' ? 'Active' : 'Error'}
                  </span>
                </div>
                <div className="info-item">
                  <label>Last Tested</label>
                  <span>{new Date().toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-paper-plane card-icon"></i> Send Test Email</h2>
            </div>
            <div className="card-content">
              <div className="test-email-form">
                <div className="form-group">
                  <label>Recipient Email</label>
                  <input
                    type="email"
                    value={testEmail}
                    onChange={(e) => setTestEmail(e.target.value)}
                    placeholder="Enter email address..."
                  />
                </div>
                <button 
                  className="btn btn-primary"
                  onClick={sendTestEmail}
                  disabled={!testEmail}
                >
                  <i className="fas fa-paper-plane"></i> Send Test Email
                </button>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-bell card-icon"></i> Alert Configuration</h2>
            </div>
            <div className="card-content">
              <div className="alert-settings">
                <div className="setting-item">
                  <div className="setting-info">
                    <h4>Threat Alerts</h4>
                    <p>High-priority security threat notifications</p>
                  </div>
                  <div className="setting-control">
                    <input type="checkbox" defaultChecked />
                    <span>Enabled</span>
                  </div>
                </div>
                <div className="setting-item">
                  <div className="setting-info">
                    <h4>Feed Notifications</h4>
                    <p>Updates when threat feeds are refreshed</p>
                  </div>
                  <div className="setting-control">
                    <input type="checkbox" defaultChecked />
                    <span>Enabled</span>
                  </div>
                </div>
                <div className="setting-item">
                  <div className="setting-info">
                    <h4>System Alerts</h4>
                    <p>System maintenance and security notifications</p>
                  </div>
                  <div className="setting-control">
                    <input type="checkbox" defaultChecked />
                    <span>Enabled</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="alerts-sidebar">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-chart-bar card-icon"></i> Email Statistics</h2>
            </div>
            <div className="card-content">
              {loading ? (
                <LoadingSpinner size="small" />
              ) : (
                <div className="email-stats">
                  <div className="stat-card">
                    <div className="stat-value">{alertStats.total_sent || 0}</div>
                    <div className="stat-label">Total Emails Sent</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{alertStats.sent_today || 0}</div>
                    <div className="stat-label">Sent Today</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{alertStats.failed_count || 0}</div>
                    <div className="stat-label">Failed Deliveries</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{alertStats.success_rate || '100'}%</div>
                    <div className="stat-label">Success Rate</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-history card-icon"></i> Recent Alerts</h2>
            </div>
            <div className="card-content">
              <div className="recent-alerts">
                <div className="alert-item">
                  <div className="alert-icon">
                    <i className="fas fa-exclamation-triangle"></i>
                  </div>
                  <div className="alert-info">
                    <div className="alert-text">High severity threat detected</div>
                    <div className="alert-time">2 hours ago</div>
                  </div>
                </div>
                <div className="alert-item">
                  <div className="alert-icon">
                    <i className="fas fa-sync-alt"></i>
                  </div>
                  <div className="alert-info">
                    <div className="alert-text">Feed update notification sent</div>
                    <div className="alert-time">4 hours ago</div>
                  </div>
                </div>
                <div className="alert-item">
                  <div className="alert-icon">
                    <i className="fas fa-shield-alt"></i>
                  </div>
                  <div className="alert-info">
                    <div className="alert-text">Security alert dispatched</div>
                    <div className="alert-time">1 day ago</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// Modal Components (Placeholder implementations)
function NewTrustRelationshipModal({ onClose, onSave }) {
  const [formData, setFormData] = useState({
    partner_organization: '',
    relationship_type: 'Partner',
    trust_level: 50,
    description: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.createTrustRelationship(formData);
      onSave();
      onClose();
    } catch (error) {
      console.error('Failed to create trust relationship:', error);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h3>New Trust Relationship</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label>Partner Organization</label>
              <input
                type="text"
                value={formData.partner_organization}
                onChange={(e) => setFormData({...formData, partner_organization: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label>Relationship Type</label>
              <select
                value={formData.relationship_type}
                onChange={(e) => setFormData({...formData, relationship_type: e.target.value})}
              >
                <option value="Partner">Partner</option>
                <option value="Vendor">Vendor</option>
                <option value="Customer">Customer</option>
              </select>
            </div>
            <div className="form-group">
              <label>Trust Level</label>
              <input
                type="range"
                min="0"
                max="100"
                value={formData.trust_level}
                onChange={(e) => setFormData({...formData, trust_level: parseInt(e.target.value)})}
              />
              <span>{formData.trust_level}%</span>
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
              />
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-outline" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Create Relationship
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function NewTrustGroupModal({ onClose, onSave }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    min_trust_level: 50
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.createTrustGroup(formData);
      onSave();
      onClose();
    } catch (error) {
      console.error('Failed to create trust group:', error);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h3>New Trust Group</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label>Group Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label>Minimum Trust Level</label>
              <input
                type="range"
                min="0"
                max="100"
                value={formData.min_trust_level}
                onChange={(e) => setFormData({...formData, min_trust_level: parseInt(e.target.value)})}
              />
              <span>{formData.min_trust_level}%</span>
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-outline" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Create Group
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function NewUserModal({ onClose, onSave, organizations }) {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    full_name: '',
    email: '',
    organization: '',
    role: 'User'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.registerUser(
        formData.username, 
        formData.password, 
        formData.full_name, 
        formData.organization, 
        formData.role
      );
      onSave();
      onClose();
    } catch (error) {
      console.error('Failed to create user:', error);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h3>New User</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label>Organization</label>
              <select
                value={formData.organization}
                onChange={(e) => setFormData({...formData, organization: e.target.value})}
                required
              >
                <option value="">Select Organization</option>
                {organizations.map((org, index) => (
                  <option key={index} value={org.name}>{org.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Role</label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({...formData, role: e.target.value})}
              >
                <option value="User">User</option>
                <option value="Admin">Admin</option>
                <option value="Moderator">Moderator</option>
              </select>
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-outline" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Create User
            </button>
          </div>
        </form>
      </div>
    </div>
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
      
      await api.updateUserProfile(profileData);
      setMessage('Profile updated successfully!');
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
      await api.changePassword(formData.currentPassword, formData.newPassword, formData.confirmPassword);
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
    <section className={`page-section ${active ? 'active' : ''}`}>
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
              <button type="submit" className="btn btn-primary" disabled={isLoading}>
                {isLoading ? 'Updating...' : 'Update Profile'}
              </button>
            </form>
          </div>

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
function AdminSettings({ active }) {
  const [systemHealth, setSystemHealth] = useState(null);
  const [emailStats, setEmailStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const fetchSystemData = async () => {
    setIsLoading(true);
    try {
      const [healthData, statsData] = await Promise.all([
        api.getSystemHealth().catch(() => null),
        api.getEmailStatistics().catch(() => null)
      ]);
      
      setSystemHealth(healthData);
      setEmailStats(statsData);
    } catch (error) {
      console.error('Error fetching system data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (active) {
      fetchSystemData();
    }
  }, [active]);

  if (!active) return null;

  return (
    <section className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <h1><i className="fas fa-shield-alt"></i> Admin Settings</h1>
        <p>System administration and configuration</p>
      </div>

      <div className="admin-settings-container">
        {message && (
          <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`}>
            {message}
          </div>
        )}

        <div className="admin-grid">
          <div className="admin-card">
            <h3><i className="fas fa-heartbeat"></i> System Health</h3>
            {isLoading ? (
              <div className="loading-state">
                <div className="loading-spinner"></div>
                <p>Loading system health...</p>
              </div>
            ) : systemHealth ? (
              <div className="health-info">
                <div className="health-status">
                  <span className={`status-indicator ${systemHealth.status === 'healthy' ? 'healthy' : 'warning'}`}>
                    {systemHealth.status || 'Unknown'}
                  </span>
                </div>
                <p>{systemHealth.message || 'System status available'}</p>
              </div>
            ) : (
              <div className="error-state">
                <i className="fas fa-exclamation-triangle"></i>
                <p>System health data unavailable</p>
                <button className="btn btn-outline btn-sm" onClick={fetchSystemData}>
                  <i className="fas fa-refresh"></i> Retry
                </button>
              </div>
            )}
          </div>

          <div className="admin-card">
            <h3><i className="fas fa-envelope"></i> Email System</h3>
            {isLoading ? (
              <div className="loading-state">
                <div className="loading-spinner"></div>
                <p>Loading email statistics...</p>
              </div>
            ) : emailStats ? (
              <div className="email-stats">
                <div className="stat-item">
                  <span className="stat-label">Total Sent:</span>
                  <span className="stat-value">{emailStats.total_sent || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Failed:</span>
                  <span className="stat-value error">{emailStats.failed_emails || 0}</span>
                </div>
              </div>
            ) : (
              <div className="error-state">
                <i className="fas fa-exclamation-triangle"></i>
                <p>Email statistics unavailable</p>
                <button className="btn btn-outline btn-sm" onClick={fetchSystemData}>
                  <i className="fas fa-refresh"></i> Retry
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

// Export Data Component
function ExportData({ active }) {
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState('json');

  if (!active) return null;

  const handleExport = async () => {
    setIsExporting(true);
    try {
      // Simulate export functionality
      await new Promise(resolve => setTimeout(resolve, 2000));
      alert(`Data exported successfully as ${exportFormat.toUpperCase()}!`);
    } catch (error) {
      alert('Export failed: ' + error.message);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <section className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <h1><i className="fas fa-download"></i> Export Data</h1>
        <p>Download your platform data in various formats</p>
      </div>

      <div className="export-container">
        <div className="export-options">
          <div className="form-group">
            <label htmlFor="format">Export Format</label>
            <select 
              id="format" 
              value={exportFormat} 
              onChange={(e) => setExportFormat(e.target.value)}
              className="form-control"
            >
              <option value="json">JSON</option>
              <option value="csv">CSV</option>
              <option value="xml">XML</option>
              <option value="pdf">PDF Report</option>
            </select>
          </div>
          
          <button 
            onClick={handleExport} 
            disabled={isExporting}
            className="btn btn-primary"
          >
            {isExporting ? 'Exporting...' : 'Export Data'}
          </button>
        </div>
      </div>
    </section>
  );
}

// Add Feed Component
function AddFeed({ active }) {
  const [feedData, setFeedData] = useState({
    name: '',
    url: '',
    type: 'misp',
    description: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!active) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Simulate feed creation
      await new Promise(resolve => setTimeout(resolve, 1500));
      alert('Threat feed added successfully!');
      setFeedData({ name: '', url: '', type: 'misp', description: '' });
    } catch (error) {
      alert('Failed to add feed: ' + error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <h1><i className="fas fa-plus"></i> Add New Feed</h1>
        <p>Configure a new threat intelligence feed</p>
      </div>

      <div className="add-feed-container">
        <form onSubmit={handleSubmit} className="feed-form">
          <div className="form-group">
            <label htmlFor="name">Feed Name</label>
            <input
              type="text"
              id="name"
              value={feedData.name}
              onChange={(e) => setFeedData(prev => ({...prev, name: e.target.value}))}
              className="form-control"
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="url">Feed URL</label>
            <input
              type="url"
              id="url"
              value={feedData.url}
              onChange={(e) => setFeedData(prev => ({...prev, url: e.target.value}))}
              className="form-control"
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="type">Feed Type</label>
            <select
              id="type"
              value={feedData.type}
              onChange={(e) => setFeedData(prev => ({...prev, type: e.target.value}))}
              className="form-control"
            >
              <option value="misp">MISP</option>
              <option value="stix">STIX/TAXII</option>
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              value={feedData.description}
              onChange={(e) => setFeedData(prev => ({...prev, description: e.target.value}))}
              className="form-control"
              rows="3"
            />
          </div>
          
          <button type="submit" disabled={isSubmitting} className="btn btn-primary">
            {isSubmitting ? 'Adding Feed...' : 'Add Feed'}
          </button>
        </form>
      </div>
    </section>
  );
}

// Edit User Component
function EditUser({ active }) {
  if (!active) return null;

  return (
    <section className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <h1><i className="fas fa-user-edit"></i> Edit User</h1>
        <p>Modify user account details and permissions</p>
      </div>

      <div className="edit-user-container">
        <p>User editing functionality will be implemented here.</p>
        <p>This will allow administrators to modify user accounts, roles, and permissions.</p>
      </div>
    </section>
  );
}

// Register User Component
function RegisterUser({ active }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    role: 'viewer',
    organization: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!active) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const userData = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        first_name: formData.firstName,
        last_name: formData.lastName,
        role: formData.role,
        organization_id: formData.organization
      };
      
      const result = await api.createUser(userData);
      
      if (result.success) {
        alert('User created successfully!');
        setFormData({
          username: '',
          email: '',
          password: '',
          confirmPassword: '',
          firstName: '',
          lastName: '',
          role: 'viewer',
          organization: ''
        });
      } else {
        alert('Failed to create user: ' + (result.message || 'Unknown error'));
      }
    } catch (error) {
      alert('Failed to create user: ' + error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <h1><i className="fas fa-user-plus"></i> Register New User</h1>
        <p>Create a new user account in the system</p>
      </div>

      <div className="register-user-container">
        <div className="card">
          <div className="card-content">
            <form onSubmit={handleSubmit} className="register-form">
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="firstName">First Name</label>
                  <input
                    type="text"
                    id="firstName"
                    value={formData.firstName}
                    onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="lastName">Last Name</label>
                  <input
                    type="text"
                    id="lastName"
                    value={formData.lastName}
                    onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="username">Username</label>
                  <input
                    type="text"
                    id="username"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="email">Email</label>
                  <input
                    type="email"
                    id="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="password">Password</label>
                  <input
                    type="password"
                    id="password"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="confirmPassword">Confirm Password</label>
                  <input
                    type="password"
                    id="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="role">Role</label>
                  <select
                    id="role"
                    value={formData.role}
                    onChange={(e) => setFormData({...formData, role: e.target.value})}
                    required
                  >
                    <option value="viewer">Viewer</option>
                    <option value="publisher">Publisher</option>
                    <option value="BlueVisionAdmin">BlueVision Admin</option>
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="organization">Organization</label>
                  <input
                    type="text"
                    id="organization"
                    value={formData.organization}
                    onChange={(e) => setFormData({...formData, organization: e.target.value})}
                    placeholder="Organization ID or name"
                  />
                </div>
              </div>

              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                  {isSubmitting ? 'Creating User...' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}

export default App;
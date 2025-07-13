import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import CSSStyles from './assets/CSSStyles'; // Import the separate CSS file
import logoImage from './assets/BlueV2.png';
import { getDashboard, getAdminDashboard, getUsers, getOrganizations, getTrustMetrics } from './api';


function App({ user, onLogout, isAdmin }) { // Updated props to match what AuthWrapper passes
  // State to manage the active page
  const [activePage, setActivePage] = useState('dashboard');

  // Function to switch between pages
  const showPage = (pageId) => {
    setActivePage(pageId);
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
      
      {/* Header */}
      <Header user={user} onLogout={onLogout} isAdmin={isAdmin} /> {/* Pass user and isAdmin to header */}
      
      {/* Main Navigation */}
      <MainNav activePage={activePage} showPage={showPage} />

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {/* Dashboard */}
          <Dashboard active={activePage === 'dashboard'} />

          {/* User Management */}
          <UserManagement active={activePage === 'users'} />

          {/* Organization Management */}
          <OrganizationManagement active={activePage === 'organizations'} />

          {/* Trust Relationships */}
          <TrustRelationships active={activePage === 'trust-relationships'} />

          {/* Threat Feeds */}
          <ThreatFeeds active={activePage === 'threat-feeds'} />

          {/* IoC Management */}
          <IoCManagement active={activePage === 'ioc-management'} />

          {/* TTP Analysis */}
          <TTPAnalysis active={activePage === 'ttp-analysis'} />
        </div>
      </main>
    </div>
  );
}

// Header Component with Logout Button and Register User button for admins
function Header({ user, onLogout, isAdmin }) {
  // Get first initial for avatar
  const userInitial = user && user.username ? user.username.charAt(0).toUpperCase() : 'A';
  const userName = user && user.username ? user.username.split('@')[0] : 'User';
  const userRole = user && user.role ? user.role : (isAdmin ? 'Administrator' : 'User');

  return (
    <header>
      <div className="container header-container">
        <a href="#" className="logo">
                <img src={logoImage} alt="CRISP Logo" className="logo-image" />      </a>
        <div className="nav-actions">
          <div className="search-bar">
            <span className="search-icon"><i className="fas fa-search"></i></span>
            <input type="text" placeholder="Search platform..." />
          </div>
          <div className="notifications">
            <i className="fas fa-bell"></i>
            <span className="notification-count">3</span>
          </div>
          <div className="user-profile">
            <div className="avatar">{userInitial}</div>
            <div className="user-info">
              <div className="user-name">{userName}</div>
              <div className="user-role">{userRole}</div>
            </div>
            {/* Show Register User button only if user is admin */}
            {isAdmin && (
              <div className="register-button" onClick={() => window.location.href = '/register'}>
                <i className="fas fa-user-plus"></i>
                <span>Register User</span>
              </div>
            )}
            {/* Add logout button */}
            <div className="logout-button" onClick={onLogout}>
              <i className="fas fa-sign-out-alt"></i>
              <span>Logout</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

// Main Navigation Component
function MainNav({ activePage, showPage }) {
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
              onClick={() => showPage('users')} 
              className={activePage === 'users' ? 'active' : ''}
            >
              <i className="fas fa-users"></i> User Management
            </a>
          </li>
          <li>
            <a 
              onClick={() => showPage('organizations')} 
              className={activePage === 'organizations' ? 'active' : ''}
            >
              <i className="fas fa-building"></i> Organizations
            </a>
          </li>
          <li>
            <a 
              onClick={() => showPage('trust-relationships')} 
              className={activePage === 'trust-relationships' ? 'active' : ''}
            >
              <i className="fas fa-handshake"></i> Trust Relationships
            </a>
          </li>
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
  
  // State for UserTrust data
  const [dashboardData, setDashboardData] = useState(null);
  const [adminData, setAdminData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Load UserTrust data when component becomes active
  useEffect(() => {
    if (active) {
      loadDashboardData();
    }
  }, [active]);
  
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load dashboard data
      const dashResponse = await getDashboard();
      if (dashResponse.success) {
        setDashboardData(dashResponse.data);
      }
      
      // Try to load admin data if user has permissions
      try {
        const adminResponse = await getAdminDashboard();
        if (adminResponse.success) {
          setAdminData(adminResponse.data);
        }
      } catch (adminError) {
        // User doesn't have admin permissions, that's okay
        console.log('Admin data not available:', adminError);
      }
      
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data');
      console.error('Dashboard data loading error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // Set up D3 charts when component mounts or window resizes
  useEffect(() => {
    if (active && chartRef.current && dashboardData) {
      createUserActivityChart();
      
      // Add resize handler for responsive charts
      const handleResize = () => {
        createUserActivityChart();
      };
      
      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }
  }, [active, dashboardData]);

  const createUserActivityChart = () => {
    // Only proceed if the chart reference exists and we have data
    if (!chartRef.current || !adminData) return;
    
    // Clear previous chart if any
    d3.select(chartRef.current).selectAll("*").remove();
    
    // Generate sample activity data based on recent activities
    const activities = adminData.recent_activities || [];
    
    // Create data for the last 14 days
    const data = [];
    const today = new Date();
    
    for (let i = 13; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      // Count activities for this date
      const dayActivities = activities.filter(activity => {
        const activityDate = new Date(activity.timestamp);
        return activityDate.toDateString() === date.toDateString();
      });
      
      data.push({
        date: date.toISOString().split('T')[0],
        count: dayActivities.length + Math.floor(Math.random() * 20) + 5 // Add some baseline activity
      });
    }

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

  if (loading) {
    return (
      <section id="dashboard" className={`page-section ${active ? 'active' : ''}`}>
        <div className="page-header">
          <div>
            <h1 className="page-title">Trust Management Dashboard</h1>
            <p className="page-subtitle">Loading dashboard data...</p>
          </div>
        </div>
        <div style={{ padding: '60px', textAlign: 'center' }}>
          <i className="fas fa-spinner fa-spin" style={{ fontSize: '48px', color: '#0056b3' }}></i>
          <p style={{ marginTop: '20px', fontSize: '16px', color: '#718096' }}>Loading UserTrust data...</p>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section id="dashboard" className={`page-section ${active ? 'active' : ''}`}>
        <div className="page-header">
          <div>
            <h1 className="page-title">Trust Management Dashboard</h1>
            <p className="page-subtitle">Error loading dashboard data</p>
          </div>
        </div>
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <i className="fas fa-exclamation-triangle" style={{ fontSize: '48px', color: '#e53e3e' }}></i>
          <p style={{ marginTop: '20px', fontSize: '16px', color: '#e53e3e' }}>{error}</p>
          <button className="btn btn-primary" onClick={loadDashboardData} style={{ marginTop: '20px' }}>
            <i className="fas fa-refresh"></i> Retry
          </button>
        </div>
      </section>
    );
  }

  const userStats = adminData?.user_statistics || {};
  const orgStats = adminData?.organization_statistics || {};
  const systemHealth = adminData?.system_health || {};
  const accessibleOrgs = dashboardData?.accessible_organizations || [];

  return (
    <section id="dashboard" className={`page-section ${active ? 'active' : ''}`}>
      {/* Dashboard Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Trust Management Dashboard</h1>
          <p className="page-subtitle">UserTrust platform overview and analytics</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline" onClick={loadDashboardData}>
            <i className="fas fa-refresh"></i> Refresh Data
          </button>
          <button className="btn btn-primary"><i className="fas fa-plus"></i> Add Organization</button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-users"></i></div>
            <span>Total Users</span>
          </div>
          <div className="stat-value">{userStats.total_users || 0}</div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>{userStats.active_users || 0} active</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-building"></i></div>
            <span>Organizations</span>
          </div>
          <div className="stat-value">{orgStats.total_organizations || 0}</div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>{accessibleOrgs.length} accessible</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-shield-alt"></i></div>
            <span>Trust Relationships</span>
          </div>
          <div className="stat-value">{orgStats.trust_metrics?.total_relationships || 0}</div>
          <div className="stat-change">
            <span><i className="fas fa-link"></i></span>
            <span>{orgStats.trust_metrics?.active_relationships || 0} active</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-heartbeat"></i></div>
            <span>Active Sessions</span>
          </div>
          <div className="stat-value">{systemHealth.total_active_sessions || 0}</div>
          <div className="stat-change">
            <span><i className="fas fa-check-circle"></i></span>
            <span>System healthy</span>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="main-grid">
        {/* Recent Activity */}
        <div>
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-history card-icon"></i> Recent System Activity</h2>
              <div className="card-actions">
                <button className="btn btn-outline btn-sm" onClick={loadDashboardData}>
                  <i className="fas fa-sync-alt"></i> Refresh
                </button>
              </div>
            </div>
            <div className="card-content">
              {adminData?.recent_activities?.length > 0 ? (
                <ul className="activity-stream">
                  {adminData.recent_activities.slice(0, 10).map((activity, index) => (
                    <li key={activity.id || index} className="activity-item">
                      <div className="activity-icon">
                        <i className={`fas ${
                          activity.action === 'login_success' ? 'fa-sign-in-alt' :
                          activity.action === 'login_attempt' ? 'fa-exclamation-triangle' :
                          activity.action === 'api_request' ? 'fa-exchange-alt' :
                          'fa-info-circle'
                        }`}></i>
                      </div>
                      <div className="activity-details">
                        <div className="activity-text">
                          {activity.action === 'login_success' ? 'Successful login' :
                           activity.action === 'login_attempt' ? 'Failed login attempt' :
                           activity.action === 'api_request' ? `API request to ${activity.additional_data?.path}` :
                           activity.action || 'System activity'}
                        </div>
                        <div className="activity-meta">
                          <div className="activity-time">
                            {new Date(activity.timestamp).toLocaleString()}
                          </div>
                          <span className={`badge ${activity.success ? 'badge-active' : 'badge-medium'}`}>
                            {activity.success ? 'Success' : 'Failed'}
                          </span>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <p style={{ textAlign: 'center', color: '#718096', padding: '40px' }}>
                  No recent activities to display
                </p>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-chart-area card-icon"></i> User Activity Trends</h2>
              <div className="card-actions">
                <button className="btn btn-outline btn-sm"><i className="fas fa-calendar-alt"></i> Last 14 Days</button>
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
          {/* Connected Organizations */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-building card-icon"></i> Connected Organizations</h2>
            </div>
            <div className="card-content">
              {accessibleOrgs.length > 0 ? (
                <ul className="institution-list">
                  {accessibleOrgs.slice(0, 6).map((org, index) => {
                    const initials = org.name.split(' ').map(word => word.charAt(0)).join('').substring(0, 2);
                    const trustLevel = org.access_level === 'full' ? 95 : 
                                     org.access_level === 'administrative' ? 85 : 
                                     org.access_level === 'limited' ? 60 : 70;
                    
                    return (
                      <li key={org.id} className="institution-item">
                        <div className="institution-logo">{initials}</div>
                        <div className="institution-details">
                          <div className="institution-name">{org.name}</div>
                          <div className="institution-stats">
                            <div className="stat-item">
                              <i className="fas fa-link"></i> {org.access_level}
                            </div>
                            <div className="stat-item">
                              <i className="fas fa-shield-alt"></i> {org.is_own ? 'Own' : 'Partner'}
                            </div>
                          </div>
                        </div>
                        <div className="trust-level">
                          <div className="trust-fill" style={{ width: `${trustLevel}%` }}></div>
                        </div>
                      </li>
                    );
                  })}
                </ul>
              ) : (
                <p style={{ textAlign: 'center', color: '#718096', padding: '40px' }}>
                  No organizations available
                </p>
              )}
            </div>
          </div>

          {/* User Statistics */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-users card-icon"></i> User Statistics</h2>
            </div>
            <div className="card-content">
              {userStats && Object.keys(userStats).length > 0 ? (
                <div>
                  <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px', marginBottom: '20px' }}>
                    <div className="stat-card" style={{ padding: '15px' }}>
                      <div className="stat-title">
                        <div className="stat-icon"><i className="fas fa-user-check"></i></div>
                        <span>Active Users</span>
                      </div>
                      <div className="stat-value" style={{ fontSize: '20px' }}>{userStats.active_users}</div>
                    </div>
                    <div className="stat-card" style={{ padding: '15px' }}>
                      <div className="stat-title">
                        <div className="stat-icon"><i className="fas fa-shield-alt"></i></div>
                        <span>Publishers</span>
                      </div>
                      <div className="stat-value" style={{ fontSize: '20px' }}>{userStats.publishers}</div>
                    </div>
                  </div>
                  
                  <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '15px', color: '#2d3748' }}>
                    Users by Role
                  </h4>
                  <div className="role-breakdown">
                    {userStats.by_role && Object.entries(userStats.by_role).map(([role, count]) => (
                      <div key={role} className="stat-item" style={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        alignItems: 'center',
                        padding: '8px 0',
                        borderBottom: '1px solid #e2e8f0',
                        fontSize: '14px'
                      }}>
                        <span style={{ textTransform: 'capitalize' }}>{role.replace('BlueVision', '')}</span>
                        <span style={{ fontWeight: '600', color: '#0056b3' }}>{count}</span>
                      </div>
                    ))}
                  </div>
                  
                  {userStats.recent_registrations && userStats.recent_registrations.length > 0 && (
                    <div style={{ marginTop: '20px' }}>
                      <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '15px', color: '#2d3748' }}>
                        Recent Registrations
                      </h4>
                      <ul className="activity-stream">
                        {userStats.recent_registrations.slice(0, 3).map(user => (
                          <li key={user.id} className="activity-item" style={{ padding: '10px 0' }}>
                            <div className="activity-icon" style={{ width: '24px', height: '24px' }}>
                              <i className="fas fa-user-plus"></i>
                            </div>
                            <div className="activity-details">
                              <div className="activity-text" style={{ fontSize: '13px' }}>
                                {user.username} ({user.role})
                              </div>
                              <div className="activity-time" style={{ fontSize: '12px' }}>
                                {new Date(user.date_joined).toLocaleDateString()}
                              </div>
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <p style={{ textAlign: 'center', color: '#718096', padding: '40px' }}>
                  No user statistics available
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// User Management Component
function UserManagement({ active }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    if (active) {
      loadUsers();
    }
  }, [active]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await getUsers();
      if (response.success && response.data && response.data.users) {
        setUsers(response.data.users);
      }
    } catch (err) {
      setError(err.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (userData) => {
    try {
      const response = await createUser(userData);
      if (response.success) {
        setShowCreateForm(false);
        loadUsers(); // Reload the user list
      }
    } catch (err) {
      alert('Failed to create user: ' + err.message);
    }
  };

  return (
    <section id="user-management" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">User Management</h1>
          <p className="page-subtitle">Manage users and their access permissions</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline" onClick={loadUsers}>
            <i className="fas fa-refresh"></i> Refresh
          </button>
          <button className="btn btn-primary" onClick={() => setShowCreateForm(true)}>
            <i className="fas fa-plus"></i> Add User
          </button>
        </div>
      </div>

      {showCreateForm && (
        <div className="card mb-4">
          <div className="card-header">
            <h2 className="card-title">Create New User</h2>
            <button className="btn btn-outline btn-sm" onClick={() => setShowCreateForm(false)}>
              <i className="fas fa-times"></i> Cancel
            </button>
          </div>
          <div className="card-content">
            <CreateUserForm onSubmit={handleCreateUser} />
          </div>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px' }}>
          <i className="fas fa-spinner fa-spin" style={{ fontSize: '48px', color: '#0056b3' }}></i>
          <p style={{ marginTop: '20px' }}>Loading users...</p>
        </div>
      ) : error ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <i className="fas fa-exclamation-triangle" style={{ fontSize: '48px', color: '#e53e3e' }}></i>
          <p style={{ marginTop: '20px', color: '#e53e3e' }}>{error}</p>
        </div>
      ) : (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title"><i className="fas fa-users card-icon"></i> Platform Users</h2>
          </div>
          <div className="card-content">
            {users.length > 0 ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Organization</th>
                    <th>Status</th>
                    <th>Last Login</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(user => (
                    <tr key={user.id}>
                      <td>{user.username}</td>
                      <td>{user.first_name} {user.last_name}</td>
                      <td>{user.email}</td>
                      <td>
                        <span className="badge badge-active">
                          {user.role?.replace('BlueVision', '') || 'User'}
                        </span>
                      </td>
                      <td>{user.organization?.name || 'N/A'}</td>
                      <td>
                        <span className={`badge ${user.is_active ? 'badge-active' : 'badge-inactive'}`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>{user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
                      <td>
                        <button className="btn btn-outline btn-sm">
                          <i className="fas fa-edit"></i>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p style={{ textAlign: 'center', color: '#718096', padding: '40px' }}>
                No users found
              </p>
            )}
          </div>
        </div>
      )}
    </section>
  );
}

// Create User Form Component
function CreateUserForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'viewer',
    organization_id: ''
  });
  const [organizations, setOrganizations] = useState([]);
  const [loadingOrgs, setLoadingOrgs] = useState(true);

  useEffect(() => {
    loadOrganizations();
  }, []);

  const loadOrganizations = async () => {
    try {
      setLoadingOrgs(true);
      const response = await getOrganizations();
      if (response.success && response.data && response.data.organizations) {
        setOrganizations(response.data.organizations);
      }
    } catch (err) {
      console.error('Failed to load organizations:', err);
    } finally {
      setLoadingOrgs(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Username</label>
        <input
          type="text"
          name="username"
          value={formData.username}
          onChange={handleChange}
          required
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Email</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>First Name</label>
        <input
          type="text"
          name="first_name"
          value={formData.first_name}
          onChange={handleChange}
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Last Name</label>
        <input
          type="text"
          name="last_name"
          value={formData.last_name}
          onChange={handleChange}
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Password</label>
        <input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          required
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Role</label>
        <select
          name="role"
          value={formData.role}
          onChange={handleChange}
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        >
          <option value="viewer">Viewer</option>
          <option value="publisher">Publisher</option>
          <option value="BlueVisionAdmin">Administrator</option>
        </select>
      </div>
      <div style={{ gridColumn: 'span 2' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Organization</label>
        <select
          name="organization_id"
          value={formData.organization_id}
          onChange={handleChange}
          required
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        >
          <option value="">Select an organization...</option>
          {loadingOrgs ? (
            <option disabled>Loading organizations...</option>
          ) : (
            organizations.map(org => (
              <option key={org.id} value={org.id}>
                {org.name} ({org.domain})
              </option>
            ))
          )}
        </select>
      </div>
      <div style={{ gridColumn: 'span 2', textAlign: 'right' }}>
        <button type="submit" className="btn btn-primary" disabled={!formData.organization_id}>
          <i className="fas fa-plus"></i> Create User
        </button>
      </div>
    </form>
  );
}

// Create Organization Form Component
function CreateOrganizationForm({ onSubmit }) {
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

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('primary_user.')) {
      const field = name.split('.')[1];
      setFormData({ 
        ...formData, 
        primary_user: { ...formData.primary_user, [field]: value }
      });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
      <div style={{ gridColumn: 'span 2' }}>
        <h3 style={{ margin: '0 0 15px 0', color: '#2d3748', borderBottom: '2px solid #e2e8f0', paddingBottom: '8px' }}>Organization Details</h3>
      </div>
      
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Organization Name</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Domain</label>
        <input
          type="text"
          name="domain"
          value={formData.domain}
          onChange={handleChange}
          required
          placeholder="example.edu"
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Contact Email</label>
        <input
          type="email"
          name="contact_email"
          value={formData.contact_email}
          onChange={handleChange}
          required
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Organization Type</label>
        <select
          name="organization_type"
          value={formData.organization_type}
          onChange={handleChange}
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        >
          <option value="educational">Educational</option>
          <option value="government">Government</option>
          <option value="private">Private</option>
        </select>
      </div>
      <div style={{ gridColumn: 'span 2' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Website</label>
        <input
          type="url"
          name="website"
          value={formData.website}
          onChange={handleChange}
          placeholder="https://example.edu"
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        />
      </div>
      <div style={{ gridColumn: 'span 2' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Description</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows="3"
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px', resize: 'vertical' }}
        />
      </div>

      <div style={{ gridColumn: 'span 2', marginTop: '20px' }}>
        <h3 style={{ margin: '0 0 15px 0', color: '#2d3748', borderBottom: '2px solid #e2e8f0', paddingBottom: '8px' }}>Primary User (Administrator)</h3>
      </div>
      
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Username</label>
        <input
          type="text"
          name="primary_user.username"
          value={formData.primary_user.username}
          onChange={handleChange}
          required
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Email</label>
        <input
          type="email"
          name="primary_user.email"
          value={formData.primary_user.email}
          onChange={handleChange}
          required
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>First Name</label>
        <input
          type="text"
          name="primary_user.first_name"
          value={formData.primary_user.first_name}
          onChange={handleChange}
          required
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        />
      </div>
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Last Name</label>
        <input
          type="text"
          name="primary_user.last_name"
          value={formData.primary_user.last_name}
          onChange={handleChange}
          required
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        />
      </div>
      <div style={{ gridColumn: 'span 2' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>Password</label>
        <input
          type="password"
          name="primary_user.password"
          value={formData.primary_user.password}
          onChange={handleChange}
          required
          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
        />
      </div>
      
      <div style={{ gridColumn: 'span 2', textAlign: 'right', marginTop: '20px' }}>
        <button type="submit" className="btn btn-primary">
          <i className="fas fa-plus"></i> Create Organization
        </button>
      </div>
    </form>
  );
}

// Organization Management Component
function OrganizationManagement({ active }) {
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    if (active) {
      loadOrganizations();
    }
  }, [active]);

  const loadOrganizations = async () => {
    try {
      setLoading(true);
      const response = await getOrganizations();
      if (response.success && response.data && response.data.organizations) {
        setOrganizations(response.data.organizations);
      }
    } catch (err) {
      setError(err.message || 'Failed to load organizations');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrganization = async (orgData) => {
    try {
      const response = await createOrganization(orgData);
      if (response.success) {
        setShowCreateForm(false);
        loadOrganizations(); // Reload the organization list
      }
    } catch (err) {
      alert('Failed to create organization: ' + err.message);
    }
  };

  return (
    <section id="organization-management" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Organization Management</h1>
          <p className="page-subtitle">Manage organizations and trust relationships</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline" onClick={loadOrganizations}>
            <i className="fas fa-refresh"></i> Refresh
          </button>
          <button className="btn btn-primary" onClick={() => setShowCreateForm(true)}>
            <i className="fas fa-plus"></i> Add Organization
          </button>
        </div>
      </div>

      {showCreateForm && (
        <div className="card mb-4">
          <div className="card-header">
            <h2 className="card-title">Create New Organization</h2>
            <button className="btn btn-outline btn-sm" onClick={() => setShowCreateForm(false)}>
              <i className="fas fa-times"></i> Cancel
            </button>
          </div>
          <div className="card-content">
            <CreateOrganizationForm onSubmit={handleCreateOrganization} />
          </div>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px' }}>
          <i className="fas fa-spinner fa-spin" style={{ fontSize: '48px', color: '#0056b3' }}></i>
          <p style={{ marginTop: '20px' }}>Loading organizations...</p>
        </div>
      ) : error ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <i className="fas fa-exclamation-triangle" style={{ fontSize: '48px', color: '#e53e3e' }}></i>
          <p style={{ marginTop: '20px', color: '#e53e3e' }}>{error}</p>
        </div>
      ) : (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title"><i className="fas fa-building card-icon"></i> Organizations</h2>
          </div>
          <div className="card-content">
            {organizations.length > 0 ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Domain</th>
                    <th>Type</th>
                    <th>Users</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {organizations.map(org => (
                    <tr key={org.id}>
                      <td>{org.name}</td>
                      <td>{org.domain}</td>
                      <td>
                        <span className="badge badge-active">
                          {org.organization_type || 'N/A'}
                        </span>
                      </td>
                      <td>{org.user_count || 0}</td>
                      <td>
                        <span className={`badge ${org.is_active ? 'badge-active' : 'badge-inactive'}`}>
                          {org.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>{new Date(org.created_at).toLocaleDateString()}</td>
                      <td>
                        <button className="btn btn-outline btn-sm">
                          <i className="fas fa-edit"></i>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p style={{ textAlign: 'center', color: '#718096', padding: '40px' }}>
                No organizations found
              </p>
            )}
          </div>
        </div>
      )}
    </section>
  );
}

// Trust Relationships Component
function TrustRelationships({ active }) {
  return (
    <section id="trust-relationships" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Trust Relationships</h1>
          <p className="page-subtitle">Manage trust relationships between organizations</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline"><i className="fas fa-refresh"></i> Refresh</button>
          <button className="btn btn-primary"><i className="fas fa-plus"></i> Create Relationship</button>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title"><i className="fas fa-handshake card-icon"></i> Trust Network</h2>
        </div>
        <div className="card-content">
          <p style={{ textAlign: 'center', color: '#718096', padding: '40px' }}>
            Trust relationship management coming soon...
          </p>
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

export default App;
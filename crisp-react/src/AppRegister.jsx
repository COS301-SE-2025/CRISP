import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { useNavigate } from 'react-router-dom';
import CSSStyles from './CSSStyles';
import logoImage from './BlueV2.png';


function AppRegister({ user, onLogout }) {
  const navigate = useNavigate();
  // State to manage the active page
  const [activePage, setActivePage] = useState('dashboard');

  // Function to switch between pages
  const showPage = (pageId) => {
    setActivePage(pageId);
  };

  // Function to navigate to RegisterUser page
  const navigateToRegisterUser = () => {
    navigate('/register-user');
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
      <Header user={user} onLogout={onLogout} navigateToRegisterUser={navigateToRegisterUser} />
      
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
        </div>
      </main>
    </div>
  );
}

// Header Component with Logout Button and Register User button
function Header({ user, onLogout, navigateToRegisterUser }) {
  // Get first initial for avatar
  const userInitial = user && user.username ? user.username.charAt(0).toUpperCase() : 'A';
  const userName = user && user.username ? user.username.split('@')[0] : 'Admin';
  const userRole = user && user.role ? user.role : 'Administrator';

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
            {/* Add Register User button for admins */}
            <div className="register-button" onClick={navigateToRegisterUser}>
              <i className="fas fa-user-plus"></i>
              <span>Register User</span>
            </div>
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

export default AppRegister;


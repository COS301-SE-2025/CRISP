import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// API Helper Functions
const api = {
  get: async (endpoint) => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`API Error: ${endpoint}`, error);
      return null;
    }
  }
};

function App() {
  // State to manage the active page
  const [activePage, setActivePage] = useState('dashboard');

  // Function to switch between pages
  const showPage = (pageId) => {
    setActivePage(pageId);
  };

  return (
    <div className="App">
      {/* Header */}
      <Header />
      
      {/* Main Navigation */}
      <MainNav activePage={activePage} showPage={showPage} />

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {/* Dashboard */}
          <Dashboard active={activePage === 'dashboard'} showPage={showPage} />

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

// Header Component
function Header() {
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
          <div className="notifications">
            <i className="fas fa-bell"></i>
            <span className="notification-count">3</span>
          </div>
          <div className="user-profile">
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
function Dashboard({ active, showPage }) {
  // State for dashboard data
  const [dashboardStats, setDashboardStats] = useState({
    threat_feeds: 0,
    indicators: 0,
    ttps: 0,
    status: 'loading'
  });
  
  // D3 Chart References
  const chartRef = useRef(null);
  
  // Fetch dashboard data from backend
  useEffect(() => {
    if (active) {
      fetchDashboardData();
    }
  }, [active]);
  
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
            totalIndicators += feedStatus.indicators_count || 0;
            totalTTPs += feedStatus.ttps_count || 0;
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
  
  // Set up D3 charts when component mounts
  useEffect(() => {
    if (active && chartRef.current) {
      createThreatActivityChart();
    }
  }, [active]);

  const createThreatActivityChart = () => {
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

    // Set dimensions and margins for the chart
    const width = chartRef.current.clientWidth;
    const height = 300;
    const margin = { top: 30, right: 30, bottom: 40, left: 50 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Create the SVG container
    const svg = d3.select(chartRef.current)
      .append("svg")
      .attr("width", width)
      .attr("height", height)
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
          <button className="btn btn-primary" onClick={() => showPage('threat-feeds')}><i className="fas fa-plus"></i> Add New Feed</button>
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
  
  // Fetch threat feeds from backend
  useEffect(() => {
    if (active) {
      fetchThreatFeeds();
    }
  }, [active]);
  
  const fetchThreatFeeds = async () => {
    setLoading(true);
    const data = await api.get('/api/threat-feeds/');
    if (data && data.results) {
      setThreatFeeds(data.results);
    }
    setLoading(false);
  };
  
  const handleConsumeFeed = async (feedId) => {
    const result = await api.post(`/api/threat-feeds/${feedId}/consume/`);
    if (result) {
      console.log('Feed consumption started:', result);
      // Refresh feeds after consumption
      fetchThreatFeeds();
    }
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
                        >
                          <i className="fas fa-download"></i> Consume
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
    </section>
  );
}

// IoC Management Component
function IoCManagement({ active }) {
  const [indicators, setIndicators] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newIoC, setNewIoC] = useState({
    type: '',
    value: '',
    severity: 'Medium',
    description: '',
    source: '',
    confidence: 50
  });
  const [formErrors, setFormErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  
  // Fetch indicators from backend
  useEffect(() => {
    if (active) {
      fetchIndicators();
    }
  }, [active]);

  
  const fetchIndicators = async () => {
    setLoading(true);
    // Get real indicator data from feeds
    const feedData = await api.get('/api/threat-feeds/');
    if (feedData && feedData.results) {
      let allIndicators = [];
      
      for (const feed of feedData.results) {
        const feedStatus = await api.get(`/api/threat-feeds/${feed.id}/status/`);
        if (feedStatus && feedStatus.indicator_count > 0) {
          // Get real indicators from this feed
          const indicatorsData = await api.get(`/api/threat-feeds/${feed.id}/indicators/?page_size=20`);
          if (indicatorsData && indicatorsData.results) {
            const realIndicators = indicatorsData.results.map(indicator => ({
              id: indicator.id,
              type: indicator.type === 'ip' ? 'IP Address' : 
                    indicator.type === 'domain' ? 'Domain' :
                    indicator.type === 'url' ? 'URL' :
                    indicator.type === 'file_hash' ? 'File Hash' :
                    indicator.type === 'email' ? 'Email' : indicator.type,
              value: indicator.value,
              severity: indicator.confidence >= 75 ? 'High' : 
                       indicator.confidence >= 50 ? 'Medium' : 'Low',
              source: indicator.source || 'Unknown',
              created: new Date(indicator.created_at).toISOString().split('T')[0],
              status: indicator.is_anonymized ? 'Anonymized' : 'Active'
            }));
            allIndicators.push(...realIndicators);
          }
        }
      }
      
      setIndicators(allIndicators);
    }
    setLoading(false);
  };
  
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
          <button className="btn btn-primary" onClick={() => setShowAddModal(true)}><i className="fas fa-plus"></i> Add New IoC</button>
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
            <button className="btn btn-outline btn-sm" onClick={handleRefresh} disabled={loading}>
              <i className={`fas fa-sync-alt ${loading ? 'fa-spin' : ''}`}></i> 
              {loading ? 'Refreshing...' : 'Refresh'}
            </button>
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
              {loading ? (
                <tr>
                  <td colSpan="8" style={{textAlign: 'center', padding: '2rem'}}>
                    <i className="fas fa-spinner fa-spin"></i> Loading indicators...
                  </td>
                </tr>
              ) : indicators.length > 0 ? (
                indicators.map((indicator) => (
                  <tr key={indicator.id}>
                    <td><input type="checkbox" /></td>
                    <td>{indicator.type}</td>
                    <td>{indicator.value}</td>
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
                      <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                      <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" style={{textAlign: 'center', padding: '2rem'}}>
                    No indicators found
                  </td>
                </tr>
              )}
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
      confidence: 50
    });
    setFormErrors({});
  }

  function handleRefresh() {
    fetchIndicators();
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
      // For now, we'll simulate API call and add to local state
      // TODO: Replace with actual API call when backend endpoint is ready
      const newIndicator = {
        id: Date.now(), // Temporary ID
        type: newIoC.type === 'ip' ? 'IP Address' : 
              newIoC.type === 'domain' ? 'Domain' :
              newIoC.type === 'url' ? 'URL' :
              newIoC.type === 'file_hash' ? 'File Hash' :
              newIoC.type === 'email' ? 'Email' : newIoC.type,
        value: newIoC.value.trim(),
        severity: newIoC.severity,
        source: newIoC.source || 'Manual Entry',
        created: new Date().toISOString().split('T')[0],
        status: 'Active'
      };
      
      // Add to indicators list
      setIndicators(prev => [newIndicator, ...prev]);
      
      // Close modal
      closeAddModal();
      
      // Show success message (you can implement a toast notification here)
      console.log('IoC added successfully:', newIndicator);
      
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
  const [ttpData, setTtpData] = useState([]);
  const [loading, setLoading] = useState(false);
  const ttpChartRef = useRef(null);
  
  // Fetch TTP data from backend
  useEffect(() => {
    if (active) {
      fetchTTPData();
    }
  }, [active]);
  
  const fetchTTPData = async () => {
    setLoading(true);
    // Get TTP data from feeds
    const feedData = await api.get('/api/threat-feeds/');
    if (feedData && feedData.length > 0) {
      // Get TTP status from the first feed
      const feedStatus = await api.get(`/api/threat-feeds/${feedData[0].id}/status/`);
      if (feedStatus) {
        // Create mock TTP data based on feed data
        const mockTTPs = Array.from({length: Math.min(feedStatus.ttp_count, 10)}, (_, i) => ({
          id: `T${1000 + i}`,
          name: `TTP-${i + 1}`,
          tactic: ['Initial Access', 'Execution', 'Persistence', 'Defense Evasion', 'Impact'][i % 5],
          technique: `Technique ${i + 1}`,
          source: feedData[0].name || 'Unknown',
          severity: ['High', 'Medium', 'Low'][i % 3],
          frequency: Math.floor(Math.random() * 50) + 1
        }));
        setTtpData(mockTTPs);
      }
    }
    setLoading(false);
  };
  
  useEffect(() => {
    if (active && ttpChartRef.current) {
      createTTPTrendsChart();
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

      <div className="tabs">
        <div className="tab active">MITRE ATT&CK Matrix</div>
        <div className="tab">TTP List</div>
        <div className="tab">Threat Actors</div>
        <div className="tab">Campaigns</div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title"><i className="fas fa-sitemap card-icon"></i> MITRE ATT&CK Enterprise Matrix</h2>
          <div className="card-actions">
            <button className="btn btn-outline btn-sm"><i className="fas fa-filter"></i> Filter</button>
          </div>
        </div>
        <div className="card-content">
          <div className="matrix-container">
            <table className="mitre-matrix">
              <thead>
                <tr>
                  <th>Initial Access</th>
                  <th>Execution</th>
                  <th>Persistence</th>
                  <th>Privilege Escalation</th>
                  <th>Defense Evasion</th>
                  <th>Credential Access</th>
                  <th>Discovery</th>
                  <th>Lateral Movement</th>
                  <th>Collection</th>
                  <th>Exfiltration</th>
                  <th>Impact</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="matrix-cell active">
                    Phishing
                    <div className="technique-count">8</div>
                  </td>
                  <td className="matrix-cell active">
                    Command & Scripting
                    <div className="technique-count">6</div>
                  </td>
                  <td className="matrix-cell">
                    Boot/Logon Autostart
                    <div className="technique-count">2</div>
                  </td>
                  <td className="matrix-cell">
                    Access Token Manipulation
                    <div className="technique-count">1</div>
                  </td>
                  <td className="matrix-cell active">
                    Obfuscated Files
                    <div className="technique-count">5</div>
                  </td>
                  <td className="matrix-cell active">
                    Brute Force
                    <div className="technique-count">4</div>
                  </td>
                  <td className="matrix-cell">
                    Account Discovery
                    <div className="technique-count">3</div>
                  </td>
                  <td className="matrix-cell">
                    Remote Services
                    <div className="technique-count">2</div>
                  </td>
                  <td className="matrix-cell">
                    Data from Local System
                    <div className="technique-count">2</div>
                  </td>
                  <td className="matrix-cell">
                    Exfiltration Over Web
                    <div className="technique-count">3</div>
                  </td>
                  <td className="matrix-cell active">
                    Data Encryption
                    <div className="technique-count">7</div>
                  </td>
                </tr>
                <tr>
                  <td className="matrix-cell active">
                    Valid Accounts
                    <div className="technique-count">5</div>
                  </td>
                  <td className="matrix-cell">
                    Native API
                    <div className="technique-count">2</div>
                  </td>
                  <td className="matrix-cell active">
                    Create Account
                    <div className="technique-count">4</div>
                  </td>
                  <td className="matrix-cell">
                    Bypass UAC
                    <div className="technique-count">1</div>
                  </td>
                  <td className="matrix-cell">
                    Indicator Removal
                    <div className="technique-count">2</div>
                  </td>
                  <td className="matrix-cell active">
                    Credentials from Browser
                    <div className="technique-count">4</div>
                  </td>
                  <td className="matrix-cell active">
                    Network Service Scanning
                    <div className="technique-count">5</div>
                  </td>
                  <td className="matrix-cell active">
                    Exploitation of Remote Services
                    <div className="technique-count">4</div>
                  </td>
                  <td className="matrix-cell">
                    Screen Capture
                    <div className="technique-count">3</div>
                  </td>
                  <td className="matrix-cell active">
                    Exfiltration Over C2
                    <div className="technique-count">5</div>
                  </td>
                  <td className="matrix-cell active">
                    Service Stop
                    <div className="technique-count">6</div>
                  </td>
                </tr>
                <tr>
                  <td className="matrix-cell">
                    External Remote Services
                    <div className="technique-count">3</div>
                  </td>
                  <td className="matrix-cell active">
                    Windows Management Instrumentation
                    <div className="technique-count">4</div>
                  </td>
                  <td className="matrix-cell">
                    Scheduled Task
                    <div className="technique-count">3</div>
                  </td>
                  <td className="matrix-cell active">
                    Scheduled Task
                    <div className="technique-count">4</div>
                  </td>
                  <td className="matrix-cell active">
                    Process Injection
                    <div className="technique-count">4</div>
                  </td>
                  <td className="matrix-cell">
                    Input Capture
                    <div className="technique-count">2</div>
                  </td>
                  <td className="matrix-cell">
                    System Information Discovery
                    <div className="technique-count">3</div>
                  </td>
                  <td className="matrix-cell">
                    Internal Spearphishing
                    <div className="technique-count">2</div>
                  </td>
                  <td className="matrix-cell active">
                    Data from Network
                    <div className="technique-count">4</div>
                  </td>
                  <td className="matrix-cell">
                    Scheduled Transfer
                    <div className="technique-count">1</div>
                  </td>
                  <td className="matrix-cell">
                    Resource Hijacking
                    <div className="technique-count">2</div>
                  </td>
                </tr>
              </tbody>
            </table>
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
                    <td>{ttp.tactic}</td>
                    <td>{ttp.id}</td>
                    <td>{ttp.source}</td>
                    <td>{new Date().toISOString().split('T')[0]}</td>
                    <td>
                      <span className={`badge badge-${ttp.severity.toLowerCase()}`}>
                        {ttp.severity}
                      </span>
                    </td>
                    <td>
                      <button className="btn btn-outline btn-sm"><i className="fas fa-eye"></i></button>
                      <button className="btn btn-outline btn-sm"><i className="fas fa-share-alt"></i></button>
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
    </section>
  );
}

// Institutions Component
function Institutions({ active }) {
  const mapRef = useRef(null);
  
  useEffect(() => {
    if (active && mapRef.current) {
      createInstitutionMap();
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

      <div className="filters-section">
        <div className="filters-grid">
          <div className="filter-group">
            <label className="filter-label">Organization Type</label>
            <div className="filter-control">
              <select>
                <option value="">All Types</option>
                <option value="education">Education</option>
                <option value="government">Government</option>
                <option value="finance">Financial</option>
                <option value="security">Security</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Trust Level</label>
            <div className="filter-control">
              <select>
                <option value="">All Levels</option>
                <option value="high">High (80-100%)</option>
                <option value="medium">Medium (50-79%)</option>
                <option value="low">Low (0-49%)</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Connection Status</label>
            <div className="filter-control">
              <select>
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="pending">Pending</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Search</label>
            <div className="filter-control">
              <input type="text" placeholder="Search by name or location..." />
            </div>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-building"></i></div>
            <span>Total Institutions</span>
          </div>
          <div className="stat-value">42</div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>3 new this month</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-university"></i></div>
            <span>Education Sector</span>
          </div>
          <div className="stat-value">18</div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>2 new this month</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-exchange-alt"></i></div>
            <span>Active Sharing</span>
          </div>
          <div className="stat-value">35</div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>5 more than last month</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-handshake"></i></div>
            <span>Avg. Trust Level</span>
          </div>
          <div className="stat-value">78%</div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>4% from last month</span>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title"><i className="fas fa-building card-icon"></i> Connected Institutions</h2>
        </div>
        <div className="card-content">
          <table className="data-table">
            <thead>
              <tr>
                <th>Institution</th>
                <th>Type</th>
                <th>Location</th>
                <th>IoCs Shared</th>
                <th>IoCs Received</th>
                <th>Trust Level</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div className="institution-logo">UP</div>
                    <span>University of Pretoria</span>
                  </div>
                </td>
                <td>Education</td>
                <td>Pretoria, South Africa</td>
                <td>125</td>
                <td>189</td>
                <td>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '90%' }}></div>
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '12px' }}>90%</div>
                </td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-eye"></i></button>
                </td>
              </tr>
              <tr>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div className="institution-logo">CS</div>
                    <span>Cyber Security Hub</span>
                  </div>
                </td>
                <td>Government</td>
                <td>Johannesburg, South Africa</td>
                <td>342</td>
                <td>215</td>
                <td>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '85%' }}></div>
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '12px' }}>85%</div>
                </td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-eye"></i></button>
                </td>
              </tr>
              <tr>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div className="institution-logo">SR</div>
                    <span>SANReN CSIRT</span>
                  </div>
                </td>
                <td>Security</td>
                <td>Cape Town, South Africa</td>
                <td>208</td>
                <td>176</td>
                <td>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '75%' }}></div>
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '12px' }}>75%</div>
                </td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-eye"></i></button>
                </td>
              </tr>
              <tr>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div className="institution-logo">SB</div>
                    <span>SABRIC</span>
                  </div>
                </td>
                <td>Financial</td>
                <td>Johannesburg, South Africa</td>
                <td>156</td>
                <td>143</td>
                <td>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '70%' }}></div>
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '12px' }}>70%</div>
                </td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-eye"></i></button>
                </td>
              </tr>
              <tr>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div className="institution-logo">UJ</div>
                    <span>University of Johannesburg</span>
                  </div>
                </td>
                <td>Education</td>
                <td>Johannesburg, South Africa</td>
                <td>87</td>
                <td>104</td>
                <td>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '65%' }}></div>
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '12px' }}>65%</div>
                </td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-eye"></i></button>
                </td>
              </tr>
              <tr>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div className="institution-logo">TU</div>
                    <span>Tshwane University of Technology</span>
                  </div>
                </td>
                <td>Education</td>
                <td>Pretoria, South Africa</td>
                <td>62</td>
                <td>98</td>
                <td>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '60%' }}></div>
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '12px' }}>60%</div>
                </td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-eye"></i></button>
                </td>
              </tr>
              <tr>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div className="institution-logo">OX</div>
                    <span>Oxford University</span>
                  </div>
                </td>
                <td>Education</td>
                <td>Oxford, United Kingdom</td>
                <td>43</td>
                <td>92</td>
                <td>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '55%' }}></div>
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '12px' }}>55%</div>
                </td>
                <td><span className="badge badge-active">Active</span></td>
                <td>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-edit"></i></button>
                  <button className="btn btn-outline btn-sm"><i className="fas fa-eye"></i></button>
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
        <div className="page-item"><i className="fas fa-chevron-right"></i></div>
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

      <div className="filters-section">
        <div className="filters-grid">
          <div className="filter-group">
            <label className="filter-label">Report Type</label>
            <div className="filter-control">
              <select>
                <option value="">All Types</option>
                <option value="incident">Incident</option>
                <option value="campaign">Campaign</option>
                <option value="trend">Trend Analysis</option>
                <option value="summary">Weekly Summary</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Sector Focus</label>
            <div className="filter-control">
              <select>
                <option value="">All Sectors</option>
                <option value="education">Education</option>
                <option value="financial">Financial</option>
                <option value="government">Government</option>
                <option value="healthcare">Healthcare</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Date Range</label>
            <div className="filter-control">
              <select>
                <option value="">All Time</option>
                <option value="week">Last Week</option>
                <option value="month">Last Month</option>
                <option value="quarter">Last Quarter</option>
                <option value="year">Last Year</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Search</label>
            <div className="filter-control">
              <input type="text" placeholder="Search reports..." />
            </div>
          </div>
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
            background-color: var(--light-gray);
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
            flex: 1;
        }
        
        .filter-control select:focus,
        .filter-control input:focus {
            outline: none;
            border-color: var(--secondary-blue);
        }
        
        /* Institutions List */
        .institution-list {
            list-style: none;
        }
        
        .institution-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 0;
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .institution-item:last-child {
            border-bottom: none;
        }
        
        .institution-logo {
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
        
        .institution-details {
            flex: 1;
        }
        
        .institution-name {
            font-weight: 600;
            margin-bottom: 2px;
        }
        
        .institution-meta {
            font-size: 13px;
            color: var(--text-muted);
        }
        
        .institution-stats {
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
            padding: 15px 0;
            display: flex;
            gap: 15px;
            border-bottom: 1px solid var(--medium-gray);
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
      `}
    </style>
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
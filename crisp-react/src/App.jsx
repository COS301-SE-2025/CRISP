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
  },
  
  put: async (endpoint, data) => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
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
        headers: { 'Content-Type': 'application/json' }
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
  // State to manage the active page and navigation parameters
  const [activePage, setActivePage] = useState('dashboard');
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
          <ThreatFeeds active={activePage === 'threat-feeds'} navigationState={navigationState} setNavigationState={setNavigationState} />

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
    if (active) {
      fetchDashboardData();
      fetchRecentIoCs();
      fetchChartData();
      fetchSystemHealth();
      fetchRecentActivities();
    }
  }, [active]);

  // Refetch chart data when filters change
  useEffect(() => {
    if (active) {
      fetchChartData();
    }
  }, [chartFilters, active]);

  // Auto-refresh system health every 30 seconds
  useEffect(() => {
    if (!active) return;
    
    const interval = setInterval(() => {
      fetchSystemHealth();
    }, 30000);
    
    return () => clearInterval(interval);
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
    institutions: [],
    anonymizationLevel: 'medium',
    shareMethod: 'taxii'
  });
  const [sharing, setSharing] = useState(false);
  const [institutionSearch, setInstitutionSearch] = useState('');
  const [showInstitutionDropdown, setShowInstitutionDropdown] = useState(false);
  const [selectedInstitutionIndex, setSelectedInstitutionIndex] = useState(-1);
  const [shareInstitutionMode, setShareInstitutionMode] = useState('existing');
  const [institutionDropdownSearch, setInstitutionDropdownSearch] = useState('');
  const [showInstitutionSelectDropdown, setShowInstitutionSelectDropdown] = useState(false);
  
  // Threat feeds for Add IoC modal
  const [threatFeeds, setThreatFeeds] = useState([]);
  
  // Mock institutions list - in real app, this would come from API
  const availableInstitutions = [
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
      if (showInstitutionDropdown && !event.target.closest('.institution-search-container')) {
        setShowInstitutionDropdown(false);
        setSelectedInstitutionIndex(-1);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showInstitutionDropdown]);
  
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

    // Filter by search term (searches in value and description)
    if (filters.searchTerm) {
      const searchTerm = filters.searchTerm.toLowerCase();
      filtered = filtered.filter(indicator => 
        indicator.value.toLowerCase().includes(searchTerm) ||
        indicator.description.toLowerCase().includes(searchTerm)
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
              ) : getPaginatedIndicators().length > 0 ? (
                getPaginatedIndicators().map((indicator) => (
                  <tr key={indicator.id}>
                    <td><input type="checkbox" /></td>
                    <td>
                      <span className={`type-badge type-${indicator.rawType}`}>
                        {indicator.type}
                      </span>
                    </td>
                    <td className="indicator-value" title={indicator.value}>
                      {indicator.value.length > 50 ? 
                        `${indicator.value.substring(0, 50)}...` : 
                        indicator.value
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
                  <td colSpan="8" style={{textAlign: 'center', padding: '2rem'}}>
                    <i className="fas fa-filter"></i> No indicators match the current filters.
                    <br />
                    <button className="btn btn-outline btn-sm mt-2" onClick={resetFilters}>
                      <i className="fas fa-times"></i> Clear Filters
                    </button>
                  </td>
                </tr>
              ) : (
                <tr>
                  <td colSpan="8" style={{textAlign: 'center', padding: '2rem'}}>
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
                          <th>Value</th>
                          <th>Severity</th>
                          <th>Source</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {importPreview.slice(0, 10).map((indicator, index) => (
                          <tr key={index}>
                            <td>{indicator.type}</td>
                            <td className="truncate">{indicator.value}</td>
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
                    Select trusted institutions to share this threat intelligence with
                  </p>
                  
                  {/* Sleek Organization Selector */}
                  <div className="sleek-org-selector">
                    {/* Search Input */}
                    <div className="search-field">
                      <input
                        type="text"
                        className="sleek-search-input"
                        value={institutionDropdownSearch}
                        onChange={(e) => {
                          setInstitutionDropdownSearch(e.target.value);
                          setShowInstitutionSelectDropdown(true);
                        }}
                        onFocus={() => setShowInstitutionSelectDropdown(true)}
                        onBlur={(e) => {
                          setTimeout(() => {
                            if (!e.relatedTarget || !e.relatedTarget.closest('.results-list')) {
                              setShowInstitutionSelectDropdown(false);
                            }
                          }, 200);
                        }}
                        placeholder="Type to search organizations..."
                      />
                      <i className="fas fa-search search-icon"></i>
                    </div>
                    
                    {/* Results List */}
                    {showInstitutionSelectDropdown && institutionDropdownSearch && (
                      <div className="results-list">
                        {availableInstitutions
                          .filter(institution => 
                            !shareFormData.institutions.includes(institution) &&
                            institution.toLowerCase().includes(institutionDropdownSearch.toLowerCase())
                          )
                          .slice(0, 5)
                          .map(institution => (
                            <div
                              key={institution}
                              className="result-item"
                              onClick={() => {
                                addInstitution(institution);
                                setInstitutionDropdownSearch('');
                                setShowInstitutionSelectDropdown(false);
                              }}
                            >
                              <span className="result-name">{institution}</span>
                              <i className="fas fa-plus add-icon"></i>
                            </div>
                          ))
                        }
                        {availableInstitutions
                          .filter(institution => 
                            !shareFormData.institutions.includes(institution) &&
                            institution.toLowerCase().includes(institutionDropdownSearch.toLowerCase())
                          ).length === 0 && (
                            <div className="no-results">
                              No organizations found
                            </div>
                          )
                        }
                      </div>
                    )}
                    
                    {/* Selected Organizations */}
                    {shareFormData.institutions.length > 0 && (
                      <div className="selected-orgs">
                        <div className="selected-label">
                          Selected ({shareFormData.institutions.length})
                        </div>
                        <div className="org-tags">
                          {shareFormData.institutions.map(institution => (
                            <div key={institution} className="org-tag">
                              <span>{institution}</span>
                              <button 
                                type="button" 
                                className="remove-tag"
                                onClick={() => removeInstitution(institution)}
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
                  <button type="submit" className="btn btn-primary" disabled={sharing || shareFormData.institutions.length === 0}>
                    {sharing ? (
                      <><i className="fas fa-spinner fa-spin"></i> Sharing...</>
                    ) : (
                      <><i className="fas fa-share-alt"></i> Share with {shareFormData.institutions.length} Institution(s)</>
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
        severity: ind.severity || 'Medium',
        source: ind.source || 'Import',
        status: ind.status || 'Active'
      }));
    }
    
    if (Array.isArray(data)) {
      return data.map(ind => ({
        type: ind.type || 'Unknown',
        value: ind.value || '',
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
      institutions: [],
      anonymizationLevel: 'medium',
      shareMethod: 'taxii'
    });
    setShowShareModal(true);
  }

  function closeShareModal() {
    setShowShareModal(false);
    setSharingIndicator(null);
    setShareFormData({
      institutions: [],
      anonymizationLevel: 'medium',
      shareMethod: 'taxii'
    });
    setInstitutionSearch('');
    setShowInstitutionDropdown(false);
    setSelectedInstitutionIndex(-1);
  }

  // Institution search helper functions
  function getFilteredInstitutions() {
    return availableInstitutions.filter(institution =>
      institution.toLowerCase().includes(institutionSearch.toLowerCase()) &&
      !shareFormData.institutions.includes(institution)
    );
  }

  function addInstitution(institution) {
    setShareFormData(prev => ({
      ...prev,
      institutions: [...prev.institutions, institution]
    }));
    setInstitutionSearch('');
    setShowInstitutionDropdown(false);
    setSelectedInstitutionIndex(-1);
  }

  function handleKeyDown(e) {
    const filteredInstitutions = getFilteredInstitutions().slice(0, 10);
    
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedInstitutionIndex(prev => 
        prev < filteredInstitutions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedInstitutionIndex(prev => prev > 0 ? prev - 1 : -1);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedInstitutionIndex >= 0 && selectedInstitutionIndex < filteredInstitutions.length) {
        addInstitution(filteredInstitutions[selectedInstitutionIndex]);
      }
    } else if (e.key === 'Escape') {
      setShowInstitutionDropdown(false);
      setSelectedInstitutionIndex(-1);
    }
  }

  function removeInstitution(institution) {
    setShareFormData(prev => ({
      ...prev,
      institutions: prev.institutions.filter(inst => inst !== institution)
    }));
  }

  async function handleShareIndicatorSubmit(e) {
    e.preventDefault();
    
    if (!sharingIndicator || shareFormData.institutions.length === 0) {
      alert('Please select at least one institution to share with.');
      return;
    }
    
    setSharing(true);
    
    try {
      const shareData = {
        institutions: shareFormData.institutions,
        anonymization_level: shareFormData.anonymizationLevel,
        share_method: shareFormData.shareMethod
      };
      
      const response = await api.post(`/api/indicators/${sharingIndicator.id}/share/`, shareData);
      
      if (response && response.success) {
        closeShareModal();
        alert(`Indicator shared with ${response.shared_with} institution(s) successfully!`);
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
  const [ttpData, setTtpData] = useState([]);
  const [trendsData, setTrendsData] = useState([]);
  const [matrixData, setMatrixData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [trendsLoading, setTrendsLoading] = useState(false);
  const [matrixLoading, setMatrixLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('matrix');
  
  // TTP Detail Modal state
  const [showTTPModal, setShowTTPModal] = useState(false);
  const [selectedTTP, setSelectedTTP] = useState(null);
  const [ttpDetailLoading, setTtpDetailLoading] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [editFormData, setEditFormData] = useState({});
  
  const ttpChartRef = useRef(null);
  
  // Fetch TTP data from backend
  useEffect(() => {
    if (active) {
      fetchTTPData();
      fetchTTPTrendsData();
      fetchMatrixData();
    }
  }, [active]);
  
  const fetchTTPData = async () => {
    setLoading(true);
    try {
      // Get TTP data from the API
      const response = await api.get('/api/ttps/');
      if (response && response.results) {
        setTtpData(response.results);
      } else {
        setTtpData([]);
      }
    } catch (error) {
      console.error('Error fetching TTP data:', error);
      setTtpData([]);
    }
    setLoading(false);
  };

  const fetchTTPTrendsData = async () => {
    setTrendsLoading(true);
    try {
      // Get TTP trends data from the API
      const response = await api.get('/api/ttps/trends/?days=120&granularity=month&group_by=tactic');
      if (response && response.data) {
        setTrendsData(response.data);
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
      } else {
        alert('Failed to update TTP');
      }
    } catch (error) {
      console.error('Error updating TTP:', error);
      alert('Error updating TTP: ' + (error.message || 'Unknown error'));
    }
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
              <th key={tactic.code} title={`${count} techniques in ${tactic.name}`}>
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
            {row.map((cell, cellIndex) => (
              <td 
                key={cellIndex} 
                className={`matrix-cell ${cell.isActive ? 'active' : ''}`}
                title={cell.technique ? `${cell.technique.name} (${cell.technique.technique_id})` : ''}
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
                  <div className="empty-cell">-</div>
                )}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    );
  };

  const transformTrendsDataForChart = (apiData) => {
    // Group data by date and aggregate by tactic
    const dateMap = new Map();
    
    apiData.forEach(item => {
      const date = item.date;
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
      
      const tactic = item.tactic ? item.tactic.toLowerCase().replace(/\s+/g, '-') : 'unknown';
      const dateEntry = dateMap.get(date);
      if (dateEntry.hasOwnProperty(tactic)) {
        dateEntry[tactic] = item.count || 0;
      }
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
    // Clear previous chart if any
    d3.select(ttpChartRef.current).selectAll("*").remove();
    
    // Return early if no trends data
    if (!trendsData || trendsData.length === 0) {
      return;
    }
    
    // Transform API data to chart format
    const data = transformTrendsDataForChart(trendsData);

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
          TTP List
        </div>
        <div 
          className={`tab ${activeTab === 'actors' ? 'active' : ''}`}
          onClick={() => handleTabChange('actors')}
        >
          Threat Actors
        </div>
        <div 
          className={`tab ${activeTab === 'campaigns' ? 'active' : ''}`}
          onClick={() => handleTabChange('campaigns')}
        >
          Campaigns
        </div>
      </div>

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
            <h2 className="card-title"><i className="fas fa-list card-icon"></i> TTP List</h2>
            <div className="card-actions">
              <button className="btn btn-outline btn-sm"><i className="fas fa-filter"></i> Filter</button>
              <button className="btn btn-outline btn-sm"><i className="fas fa-download"></i> Export</button>
            </div>
          </div>
          <div className="card-content">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>MITRE ID</th>
                  <th>Tactic</th>
                  <th>Source Feed</th>
                  <th>Confidence</th>
                  <th>Created</th>
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
                      <td>{ttp.confidence || 'N/A'}%</td>
                      <td>{ttp.created_at ? new Date(ttp.created_at).toLocaleDateString() : 'N/A'}</td>
                      <td>
                        <button 
                          className="btn btn-outline btn-sm" 
                          onClick={() => openTTPModal(ttp.id)}
                          title="View TTP Details"
                          style={{marginRight: '5px'}}
                        >
                          <i className="fas fa-eye"></i>
                        </button>
                        <button 
                          className="btn btn-outline btn-sm text-danger" 
                          onClick={() => deleteTTP(ttp.id)}
                          title="Delete TTP"
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
      {activeTab === 'actors' && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title"><i className="fas fa-user-secret card-icon"></i> Threat Actors</h2>
            <div className="card-actions">
              <button className="btn btn-outline btn-sm"><i className="fas fa-filter"></i> Filter</button>
              <button className="btn btn-primary btn-sm"><i className="fas fa-plus"></i> Add Actor</button>
            </div>
          </div>
          <div className="card-content">
            <div style={{textAlign: 'center', padding: '4rem'}}>
              <i className="fas fa-user-secret" style={{fontSize: '3rem', color: '#ccc'}}></i>
              <h3 style={{marginTop: '1rem', color: '#666'}}>Threat Actors Management</h3>
              <p style={{color: '#888', fontSize: '0.9rem'}}>Track and analyze threat actor profiles, campaigns, and TTPs</p>
              <div style={{marginTop: '2rem'}}>
                <button className="btn btn-primary">
                  <i className="fas fa-plus"></i> Add First Threat Actor
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Campaigns Tab */}
      {activeTab === 'campaigns' && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title"><i className="fas fa-project-diagram card-icon"></i> Campaigns</h2>
            <div className="card-actions">
              <button className="btn btn-outline btn-sm"><i className="fas fa-filter"></i> Filter</button>
              <button className="btn btn-primary btn-sm"><i className="fas fa-plus"></i> Add Campaign</button>
            </div>
          </div>
          <div className="card-content">
            <div style={{textAlign: 'center', padding: '4rem'}}>
              <i className="fas fa-project-diagram" style={{fontSize: '3rem', color: '#ccc'}}></i>
              <h3 style={{marginTop: '1rem', color: '#666'}}>Campaign Management</h3>
              <p style={{color: '#888', fontSize: '0.9rem'}}>Monitor threat campaigns, their TTPs, and associated indicators</p>
              <div style={{marginTop: '2rem'}}>
                <button className="btn btn-primary">
                  <i className="fas fa-plus"></i> Add First Campaign
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent TTP Analyses (only shown on matrix and list tabs) */}
      {(activeTab === 'matrix' || activeTab === 'list') && (
        <div className="card mt-4">
          <div className="card-header">
            <h2 className="card-title"><i className="fas fa-tasks card-icon"></i> Recent TTP Analyses</h2>
        </div>
        <div className="card-content">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>MITRE Technique</th>
                <th>Tactic</th>
                <th>Threat Feed</th>
                <th>Created</th>
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
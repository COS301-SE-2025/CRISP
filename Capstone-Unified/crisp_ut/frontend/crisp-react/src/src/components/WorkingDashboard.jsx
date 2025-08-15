import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';

// Enhanced API Configuration
const API_BASE_URL = 'http://localhost:8000';

const enhancedApi = {
  get: async (endpoint) => {
    try {
      const token = localStorage.getItem('crisp_auth_token');
      const headers = { 'Content-Type': 'application/json' };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: headers
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`API Error: ${endpoint}`, error);
      return null;
    }
  }
};

function WorkingDashboard({ active, showPage }) {
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

  // Set up polling for real-time updates
  useEffect(() => {
    if (!active) return;
    
    const interval = setInterval(() => {
      fetchDashboardData();
      fetchSystemHealth();
      fetchRecentActivities();
    }, 30000); // Poll every 30 seconds

    return () => clearInterval(interval);
  }, [active]);
  
  const fetchDashboardData = async () => {
    const feedsData = await enhancedApi.get('/api/threat-feeds/');
    if (feedsData) {
      let totalIndicators = 0;
      let totalTTPs = 0;
      
      // Get indicator and TTP counts from each feed
      if (feedsData.results) {
        for (const feed of feedsData.results) {
          const feedStatus = await enhancedApi.get(`/api/threat-feeds/${feed.id}/status/`);
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

  const fetchRecentIoCs = async () => {
    setIocLoading(true);
    setIocError(null);
    
    try {
      const indicatorsData = await enhancedApi.get('/api/indicators/?limit=6');
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
      setIocError('Failed to load recent indicators');
      setRecentIoCs([]);
    } finally {
      setIocLoading(false);
    }
  };

  // Transform IoC data for dashboard display
  const transformIoCForDashboard = (indicator) => {
    // Map indicator types to display names
    const typeMapping = {
      'ip': 'IP Address',
      'domain': 'Domain',
      'url': 'URL',
      'hash': 'File Hash',
      'email': 'Email',
      'file': 'File',
      'mutex': 'Mutex',
      'registry': 'Registry Key'
    };

    // Calculate confidence level
    const getConfidenceLevel = (confidence) => {
      if (confidence >= 80) return 'High';
      if (confidence >= 60) return 'Medium';
      if (confidence >= 40) return 'Low';
      return 'Unknown';
    };

    return {
      id: indicator.id,
      value: indicator.value || 'N/A',
      type: typeMapping[indicator.type] || indicator.type || 'Unknown',
      confidence: getConfidenceLevel(indicator.confidence || 0),
      severity: indicator.severity || 'medium',
      source: indicator.feed_name || 'Unknown',
      created: indicator.created_at ? new Date(indicator.created_at) : new Date(),
      createdDate: indicator.created_at ? new Date(indicator.created_at) : new Date()
    };
  };

  // Chart data fetching and processing
  const fetchChartData = async () => {
    setChartLoading(true);
    setChartError(null);

    try {
      const queryParams = new URLSearchParams({
        days: chartFilters.days.toString(),
        ...(chartFilters.type && { type: chartFilters.type }),
        ...(chartFilters.feed_id && { feed_id: chartFilters.feed_id.toString() })
      });

      const response = await enhancedApi.get(`/api/threat-activity-chart/?${queryParams}`);
      
      if (response && response.chart_data) {
        setChartData(response.chart_data);
        setChartSummary(response.summary || {});
        
        // Create D3 chart after data is loaded
        setTimeout(createD3Chart, 100);
      } else {
        setChartError('No chart data available');
        setChartData([]);
      }
    } catch (error) {
      console.error('Error fetching chart data:', error);
      setChartError('Failed to load chart data');
      setChartData([]);
    } finally {
      setChartLoading(false);
    }
  };

  const fetchSystemHealth = async () => {
    setHealthLoading(true);
    setHealthError(null);

    try {
      const response = await enhancedApi.get('/api/system-health/');
      if (response) {
        setSystemHealth(response);
      }
    } catch (error) {
      console.error('Error fetching system health:', error);
      setHealthError('Failed to load system health');
    } finally {
      setHealthLoading(false);
    }
  };

  const fetchRecentActivities = async () => {
    setActivitiesLoading(true);
    setActivitiesError(null);

    try {
      const response = await enhancedApi.get('/api/recent-activities/?limit=10');
      if (response && response.activities) {
        setRecentActivities(response.activities);
      } else {
        setRecentActivities([]);
      }
    } catch (error) {
      console.error('Error fetching recent activities:', error);
      setActivitiesError('Failed to load recent activities');
      setRecentActivities([]);
    } finally {
      setActivitiesLoading(false);
    }
  };

  // D3 Chart Creation
  const createD3Chart = () => {
    if (!chartRef.current || chartData.length === 0) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 40 };
    const container = chartRef.current.getBoundingClientRect();
    const width = container.width - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const svg = d3.select(chartRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom);

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Parse and format dates
    const parseDate = d3.timeParse("%Y-%m-%d");
    const formatDate = d3.timeFormat("%b %d");

    const data = chartData.map(d => ({
      ...d,
      date: parseDate(d.date),
      count: +d.count
    })).sort((a, b) => a.date - b.date);

    // Scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(data, d => d.date))
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.count) * 1.1])
      .range([height, 0]);

    // Line generator
    const line = d3.line()
      .x(d => xScale(d.date))
      .y(d => yScale(d.count))
      .curve(d3.curveMonotoneX);

    // Add axes
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale).tickFormat(formatDate));

    g.append("g")
      .call(d3.axisLeft(yScale));

    // Add the line
    g.append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", "#0056b3")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Add dots
    g.selectAll(".dot")
      .data(data)
      .enter().append("circle")
      .attr("class", "dot")
      .attr("cx", d => xScale(d.date))
      .attr("cy", d => yScale(d.count))
      .attr("r", 4)
      .attr("fill", "#0056b3")
      .on("mouseover", function(event, d) {
        // Tooltip logic here if needed
      });
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
          <button className="btn btn-outline" onClick={() => setShowDashboardExportModal(true)}>
            <i className="fas fa-download"></i> Export Data
          </button>
          <button className="btn btn-primary" onClick={() => showPage('threat-feeds', 'addFeed')}>
            <i className="fas fa-plus"></i> Add New Feed
          </button>
        </div>
      </div>

      {/* Dashboard Grid */}
      <div className="dashboard-grid">
        {/* Statistics Cards */}
        <div className="stats-row">
          <div className="stat-card">
            <div className="stat-header">
              <div className="stat-icon"><i className="fas fa-rss"></i></div>
              <span>Active Feeds</span>
            </div>
            <div className="stat-value">{dashboardStats.threat_feeds}</div>
            <div className="stat-description">Threat intelligence sources</div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <div className="stat-icon"><i className="fas fa-search"></i></div>
              <span>Total IoCs</span>
            </div>
            <div className="stat-value">{dashboardStats.indicators}</div>
            <div className="stat-description">Indicators of compromise</div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <div className="stat-icon"><i className="fas fa-shield-alt"></i></div>
              <span>TTPs</span>
            </div>
            <div className="stat-value">{dashboardStats.ttps}</div>
            <div className="stat-description">Tactics, techniques & procedures</div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <div className="stat-icon"><i className="fas fa-heartbeat"></i></div>
              <span>System Status</span>
            </div>
            <div className="stat-value">
              <span><i className="fas fa-circle" style={{color: dashboardStats.status === 'active' ? '#28a745' : '#dc3545'}}></i></span>
            </div>
            <div className="stat-description">Platform operational status</div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="main-dashboard-content">
          {/* Threat Activity Chart */}
          <div className="card chart-card">
            <div className="card-header">
              <h3 className="card-title">
                <i className="fas fa-chart-line card-icon"></i>
                Threat Activity Trends
              </h3>
              <div className="chart-filters">
                <select 
                  value={chartFilters.days} 
                  onChange={(e) => setChartFilters({...chartFilters, days: parseInt(e.target.value)})}
                  style={{marginRight: '10px'}}
                >
                  <option value={7}>Last 7 days</option>
                  <option value={30}>Last 30 days</option>
                  <option value={90}>Last 90 days</option>
                </select>
                <button 
                  className="btn btn-sm btn-outline" 
                  onClick={fetchChartData}
                  disabled={chartLoading}
                  style={{marginRight: '10px'}}
                >
                  <i className="fas fa-sync-alt"></i> Refresh
                </button>
              </div>
            </div>
            <div className="card-body">
              <div className="card-status-bar" style={{
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                fontSize: '0.9rem',
                color: '#666',
                marginBottom: '15px'
              }}>
                <span>Indicators: {chartSummary.total_indicators || 0}</span>
                <span style={{margin: '0 15px'}}>|</span>
                <span>Daily Avg: {chartSummary.avg_daily || 0}</span>
                <span style={{margin: '0 15px'}}>|</span>
                <span>Period: {chartFilters.days} days</span>
              </div>
              
              {chartLoading ? (
                <div className="alert alert-info" style={{
                  textAlign: 'center',
                  padding: '2rem',
                  margin: '1rem 0'
                }}>
                  <i className="fas fa-spinner fa-spin" style={{fontSize: '24px', color: '#0056b3'}}></i>
                  <p style={{marginTop: '10px', color: '#666'}}>Loading chart data...</p>
                </div>
              ) : chartError ? (
                <div className="alert alert-error" style={{
                  textAlign: 'center',
                  padding: '2rem',
                  margin: '1rem 0'
                }}>
                  <i className="fas fa-exclamation-triangle" style={{fontSize: '24px', color: '#dc3545'}}></i>
                  <p style={{marginTop: '10px', color: '#dc3545'}}>{chartError}</p>
                </div>
              ) : (
                <div style={{position: 'relative', minHeight: '350px'}}>
                  <div 
                    ref={chartRef}
                    className="chart-container" 
                    style={{
                      width: '100%',
                      height: '350px',
                      border: '1px solid #e9ecef',
                      borderRadius: '4px',
                      background: '#fff'
                    }}
                  />
                </div>
              )}
            </div>
          </div>

          {/* Recent IoCs */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">
                <i className="fas fa-clock card-icon"></i>
                Recent Indicators
              </h3>
              <button 
                className="btn btn-sm btn-outline" 
                onClick={fetchRecentIoCs}
                disabled={iocLoading}
              >
                <i className="fas fa-sync-alt"></i> Refresh
              </button>
            </div>
            <div className="card-body">
              {iocLoading ? (
                <div className="loading-indicator">
                  <i className="fas fa-spinner fa-spin"></i> Loading recent indicators...
                </div>
              ) : iocError ? (
                <div className="alert alert-error">
                  <i className="fas fa-exclamation-triangle"></i>
                  {iocError}
                </div>
              ) : recentIoCs.length > 0 ? (
                <div className="recent-iocs-list">
                  {recentIoCs.map((ioc, index) => (
                    <div key={index} className="ioc-item">
                      <div className="ioc-header">
                        <span className="ioc-type">{ioc.type}</span>
                        <span className="ioc-time">
                          {ioc.createdDate ? ioc.createdDate.toLocaleDateString() : 'Unknown'}
                        </span>
                      </div>
                      <div className="ioc-value">{ioc.value}</div>
                      <div className="ioc-meta">
                        <span className={`badge badge-${ioc.severity}`}>{ioc.severity}</span>
                        <span className="ioc-source">{ioc.source}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <i className="fas fa-info-circle"></i>
                  <p>No recent indicators available</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default WorkingDashboard;
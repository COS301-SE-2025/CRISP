import React, { useState, useEffect } from 'react';
import ReportDetailModal from './ReportDetailModal';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const [viewMode, setViewMode] = useState('grid');

  useEffect(() => {
    fetchReports();
    fetchDashboardStats();
    fetchRecentActivity();
  }, [filter]);

  const fetchDashboardStats = async () => {
    try {
      const token = localStorage.getItem('crisp_auth_token');
      if (!token) return;

      const response = await fetch('http://localhost:8000/api/reports/status/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setDashboardStats(data.status);
        }
      }
    } catch (error) {
      console.warn('Failed to fetch dashboard stats:', error);
    }
  };

  const fetchRecentActivity = async () => {
    try {
      const token = localStorage.getItem('crisp_auth_token');
      if (!token) return;

      // Mock recent activity for now - could be replaced with real API
      const mockActivity = [
        {
          id: 1,
          action: 'Report Generated',
          report: 'Education Sector Analysis',
          timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
          user: 'System',
          severity: 'info'
        },
        {
          id: 2,
          action: 'Threat Detected',
          report: 'Financial Sector Monitor',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
          user: 'Auto-Scanner',
          severity: 'warning'
        },
        {
          id: 3,
          action: 'Report Exported',
          report: 'Government Infrastructure',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
          user: 'Admin',
          severity: 'success'
        }
      ];
      setRecentActivity(mockActivity);
    } catch (error) {
      console.warn('Failed to fetch recent activity:', error);
    }
  };

  const fetchReports = async () => {
    try {
      setLoading(true);
      
      // Fetch real reports from API
      const token = localStorage.getItem('crisp_auth_token');
      console.log('Auth token check:', { 
        token: token ? 'Present' : 'Missing', 
        tokenLength: token ? token.length : 0,
        allKeys: Object.keys(localStorage).filter(k => k.includes('auth') || k.includes('token') || k.includes('crisp'))
      });
      
      if (!token) {
        throw new Error('Authentication required');
      }

      const reportsToFetch = [
        { endpoint: '/api/reports/education-sector-analysis/', type: 'Sector Analysis' },
        { endpoint: '/api/reports/financial-sector-analysis/', type: 'Sector Analysis' },
        { endpoint: '/api/reports/government-sector-analysis/', type: 'Sector Analysis' }
      ];

      const fetchedReports = [];

      for (const reportConfig of reportsToFetch) {
        try {
          const response = await fetch(`http://localhost:8000${reportConfig.endpoint}`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            const data = await response.json();
            if (data.success && data.report) {
              // Transform API response to match frontend format with enhanced data
              const severity = data.report.statistics?.find(s => s.label === 'Severity')?.value || 'Medium';
              const iocCount = parseInt(data.report.statistics?.find(s => s.label.includes('IoC'))?.value || '0');
              const orgCount = parseInt(data.report.statistics?.find(s => s.label.includes('Institutions') || s.label.includes('Organizations'))?.value || '0');
              
              const transformedReport = {
                id: data.report.id,
                title: data.report.title,
                type: reportConfig.type,
                date: data.report.date,
                views: data.report.views,
                description: data.report.description,
                stats: data.report.statistics || [],
                severity: severity,
                threatLevel: iocCount > 40 ? 'High' : iocCount > 20 ? 'Medium' : 'Low',
                organizationsAnalyzed: orgCount,
                lastUpdated: new Date().toISOString(),
                sector: data.report.sector_focus || 'general',
                status: 'Active',
                confidence: iocCount > 30 ? 'High' : iocCount > 15 ? 'Medium' : 'Low'
              };
              fetchedReports.push(transformedReport);
            }
          }
        } catch (apiError) {
          console.warn(`Failed to fetch ${reportConfig.endpoint}:`, apiError.message);
        }
      }

      // If no real reports were fetched, fall back to mock data
      if (fetchedReports.length === 0) {
        console.log('Using fallback mock data');
        const mockReports = [
          {
            id: '1',
            title: 'Education Sector Threat Analysis',
            type: 'Sector Analysis',
            date: 'August 19, 2025',
            views: 148,
            description: 'No real data available. Please ensure the backend is running and demo data is populated.',
            stats: [
              { label: 'Status', value: 'Demo Mode' },
              { label: 'Data Source', value: 'Mock' },
              { label: 'Backend', value: 'Offline' },
              { label: 'Action Required', value: 'Check API' }
            ]
          }
        ];
        setReports(mockReports);
      } else {
        // Apply filters to real data
        let filteredReports = fetchedReports;
        if (filter !== 'all') {
          filteredReports = fetchedReports.filter(r => {
            return r.type.toLowerCase().replace(' ', '_') === filter;
          });
        }
        setReports(filteredReports);
      }
    } catch (err) {
      console.error('Error fetching reports:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // No need for formatting functions since stats are already formatted in the data

  const viewReport = (report) => {
    setSelectedReport(report);
    setShowDetailModal(true);
  };

  const closeDetailModal = () => {
    setShowDetailModal(false);
    setSelectedReport(null);
  };

  // Create API helper for the modal
  const api = {
    get: async (endpoint) => {
      const token = localStorage.getItem('crisp_auth_token');
      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`http://localhost:8000${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    }
  };

  const shareReport = (report) => {
    console.log(`Sharing report: ${report.title}`);
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return '#dc3545';
      case 'high': return '#fd7e14';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'fas fa-exclamation-triangle';
      case 'high': return 'fas fa-exclamation-circle';
      case 'medium': return 'fas fa-info-circle';
      case 'low': return 'fas fa-check-circle';
      default: return 'fas fa-minus-circle';
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'Active': { color: '#28a745', icon: 'fas fa-play-circle' },
      'Processing': { color: '#ffc107', icon: 'fas fa-sync fa-spin' },
      'Completed': { color: '#17a2b8', icon: 'fas fa-check-circle' },
      'Error': { color: '#dc3545', icon: 'fas fa-times-circle' }
    };
    return statusConfig[status] || statusConfig['Active'];
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const filteredAndSortedReports = reports
    .filter(report => 
      report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.description.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.lastUpdated) - new Date(a.lastUpdated);
        case 'severity':
          const severityOrder = { 'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1 };
          return (severityOrder[b.severity] || 0) - (severityOrder[a.severity] || 0);
        case 'views':
          return b.views - a.views;
        case 'title':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    });

  if (loading) {
    return (
      <div className="reports">
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading reports...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="reports">
        <div className="error-state">
          <i className="fas fa-exclamation-triangle"></i>
          <p>Error loading reports: {error}</p>
          <button onClick={fetchReports} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="reports-section">
      {/* Enhanced Header with Dashboard */}
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <i className="fas fa-chart-line"></i>
            Threat Intelligence Reports
          </h1>
          <p className="page-subtitle">Real-time cybersecurity threat analysis and intelligence</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline">
            <i className="fas fa-download"></i> Export All
          </button>
          <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
            <i className="fas fa-plus"></i> Generate Report
          </button>
        </div>
      </div>

      {/* Dashboard Statistics Section */}
      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-icon primary-icon">
            <i className="fas fa-file-alt"></i>
          </div>
          <div className="stat-content">
            <div className="stat-number">{filteredAndSortedReports.length}</div>
            <div className="stat-label">Active Reports</div>
            <div className="stat-trend positive">
              <i className="fas fa-arrow-up"></i> 12% from last month
            </div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon threat-icon">
            <i className="fas fa-shield-alt"></i>
          </div>
          <div className="stat-content">
            <div className="stat-number">{filteredAndSortedReports.reduce((acc, r) => acc + parseInt(r.stats?.find(s => s.label.includes('IoC'))?.value || 0), 0)}</div>
            <div className="stat-label">IoCs Analyzed</div>
            <div className="stat-trend positive">
              <i className="fas fa-arrow-up"></i> 8% this week
            </div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon warning-icon">
            <i className="fas fa-exclamation-triangle"></i>
          </div>
          <div className="stat-content">
            <div className="stat-number">{filteredAndSortedReports.filter(r => r.severity === 'High' || r.severity === 'Critical').length}</div>
            <div className="stat-label">High Priority</div>
            <div className="stat-trend negative">
              <i className="fas fa-arrow-down"></i> 3% improvement
            </div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon success-icon">
            <i className="fas fa-building"></i>
          </div>
          <div className="stat-content">
            <div className="stat-number">{filteredAndSortedReports.reduce((acc, r) => acc + (r.organizationsAnalyzed || 0), 0)}</div>
            <div className="stat-label">Organizations</div>
            <div className="stat-trend neutral">
              <i className="fas fa-minus"></i> No change
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Controls Section */}
      <div className="controls-section">
        <div className="left-controls">
          <div className="search-box">
            <i className="fas fa-search"></i>
            <input
              type="text"
              placeholder="Search reports..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          
          <div className="filter-controls">
            <select 
              value={filter} 
              onChange={(e) => setFilter(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Sectors</option>
              <option value="sector_analysis">Sector Analysis</option>
              <option value="trend_analysis">Trend Analysis</option>
              <option value="incident_analysis">Incident Analysis</option>
            </select>
            
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="sort-select"
            >
              <option value="date">Sort by Date</option>
              <option value="severity">Sort by Severity</option>
              <option value="views">Sort by Views</option>
              <option value="title">Sort by Title</option>
            </select>
          </div>
        </div>
        
        <div className="right-controls">
          <div className="view-toggle">
            <button 
              className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => setViewMode('grid')}
              title="Grid View"
            >
              <i className="fas fa-th-large"></i>
            </button>
            <button 
              className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
              title="List View"
            >
              <i className="fas fa-list"></i>
            </button>
          </div>
          
          <div className="quick-filters">
            <span className="filter-tag active" title="All Reports">All</span>
            <span className="filter-tag" title="High Priority Only">Critical</span>
            <span className="filter-tag" title="Recent Reports">Recent</span>
          </div>
        </div>
      </div>

      {/* Reports Grid/List Section */}
      <div className={`reports-container ${viewMode}`}>
        {filteredAndSortedReports.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              <i className="fas fa-file-alt"></i>
            </div>
            <h3>No reports found</h3>
            <p>No reports match your current filters. Try adjusting your search criteria.</p>
            <button 
              className="btn btn-primary"
              onClick={() => setShowCreateModal(true)}
            >
              <i className="fas fa-plus"></i>
              Generate New Report
            </button>
          </div>
        ) : (
          filteredAndSortedReports.map(report => (
            <div key={report.id} className="enhanced-report-card">
              {/* Status and Severity Indicators */}
              <div className="card-header">
                <div className="status-indicators">
                  <div 
                    className="severity-badge"
                    style={{ 
                      backgroundColor: getSeverityColor(report.severity),
                      color: 'white' 
                    }}
                  >
                    <i className={getSeverityIcon(report.severity)}></i>
                    {report.severity || 'Medium'}
                  </div>
                  <div 
                    className="status-badge"
                    style={{ 
                      backgroundColor: getStatusBadge(report.status).color,
                      color: 'white' 
                    }}
                  >
                    <i className={getStatusBadge(report.status).icon}></i>
                    {report.status || 'Active'}
                  </div>
                </div>
                <div className="card-menu">
                  <button className="menu-btn">
                    <i className="fas fa-ellipsis-v"></i>
                  </button>
                </div>
              </div>

              {/* Report Content */}
              <div className="card-content">
                <div className="report-type-tag">{report.type}</div>
                <h3 className="report-title">{report.title}</h3>
                <p className="report-description">{report.description}</p>
                
                {/* Enhanced Metadata */}
                <div className="report-metadata">
                  <div className="meta-item">
                    <i className="fas fa-calendar"></i>
                    <span>{report.date}</span>
                  </div>
                  <div className="meta-item">
                    <i className="fas fa-eye"></i>
                    <span>{report.views} views</span>
                  </div>
                  <div className="meta-item">
                    <i className="fas fa-clock"></i>
                    <span>{formatTimeAgo(report.lastUpdated)}</span>
                  </div>
                  <div className="meta-item">
                    <i className="fas fa-building"></i>
                    <span>{report.organizationsAnalyzed || 0} orgs</span>
                  </div>
                </div>

                {/* Key Statistics */}
                <div className="key-stats">
                  {(report.stats || report.statistics || []).slice(0, 3).map((stat, index) => (
                    <div key={index} className="key-stat">
                      <div className="stat-value">{stat.value}</div>
                      <div className="stat-label">{stat.label}</div>
                    </div>
                  ))}
                </div>

                {/* Threat Level Indicator */}
                <div className="threat-level-bar">
                  <div className="threat-level-label">Threat Level</div>
                  <div className="threat-level-indicator">
                    <div 
                      className={`threat-level-fill ${report.threatLevel?.toLowerCase() || 'medium'}`}
                      style={{ 
                        width: report.threatLevel === 'High' ? '80%' : 
                               report.threatLevel === 'Medium' ? '60%' : '40%' 
                      }}
                    ></div>
                  </div>
                  <div className="threat-level-text">{report.threatLevel || 'Medium'}</div>
                </div>

                {/* Confidence Indicator */}
                <div className="confidence-indicator">
                  <span className="confidence-label">Confidence:</span>
                  <div className="confidence-dots">
                    {[1, 2, 3, 4, 5].map(dot => (
                      <div 
                        key={dot}
                        className={`confidence-dot ${
                          (report.confidence === 'High' && dot <= 5) ||
                          (report.confidence === 'Medium' && dot <= 3) ||
                          (report.confidence === 'Low' && dot <= 2) ? 'active' : ''
                        }`}
                      ></div>
                    ))}
                  </div>
                  <span className="confidence-text">{report.confidence || 'Medium'}</span>
                </div>
              </div>

              {/* Enhanced Actions */}
              <div className="card-actions">
                <div className="action-buttons">
                  <button 
                    className="action-btn secondary"
                    onClick={() => shareReport(report)}
                    title="Share Report"
                  >
                    <i className="fas fa-share-alt"></i>
                    Share
                  </button>
                  <button 
                    className="action-btn secondary"
                    title="Download Report"
                  >
                    <i className="fas fa-download"></i>
                    Export
                  </button>
                  <button 
                    className="action-btn primary"
                    onClick={() => viewReport(report)}
                    title="View Full Report"
                  >
                    <i className="fas fa-eye"></i>
                    View Details
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Generate New Report</h3>
              <button 
                className="close-btn"
                onClick={() => setShowCreateModal(false)}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <div className="report-types">
                <h4>Select Report Type</h4>
                <div className="type-options">
                  <div className="type-option">
                    <i className="fas fa-shield-alt"></i>
                    <h5>Threat Summary</h5>
                    <p>Comprehensive threat intelligence analysis</p>
                  </div>
                  <div className="type-option">
                    <i className="fas fa-handshake"></i>
                    <h5>Trust Analysis</h5>
                    <p>Organization trust relationships report</p>
                  </div>
                  <div className="type-option">
                    <i className="fas fa-rss"></i>
                    <h5>Feed Analysis</h5>
                    <p>STIX/TAXII feed consumption metrics</p>
                  </div>
                  <div className="type-option">
                    <i className="fas fa-chart-bar"></i>
                    <h5>Security Metrics</h5>
                    <p>KPIs and security performance indicators</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowCreateModal(false)}
              >
                Cancel
              </button>
              <button className="btn btn-primary">
                Generate Report
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Report Detail Modal */}
      {selectedReport && (
        <ReportDetailModal
          report={selectedReport}
          isOpen={showDetailModal}
          onClose={closeDetailModal}
          api={api}
        />
      )}

      <style jsx>{`
        :root {
          --primary-blue: #1e3d59;
          --secondary-blue: #5a9fd4;
          --light-blue: #f0f8ff;
          --dark-blue: #0f2a3f;
          --white: #ffffff;
          --light-gray: #f5f5f5;
          --medium-gray: #d0d0d0;
          --text-muted: #666666;
          --success: #28a745;
          --warning: #ffc107;
          --danger: #dc3545;
          --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          --hover-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
          --border-radius: 12px;
          --transition: all 0.3s ease;
          --warning: #ffc107;
          --danger: #dc3545;
        }

        .reports-section {
          padding: 24px;
          background: #f8f9fa;
          min-height: 100vh;
        }

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
          margin: 0;
        }

        .page-subtitle {
          color: var(--text-muted);
          margin-top: 4px;
          font-size: 15px;
          margin-bottom: 0;
        }

        .action-buttons {
          display: flex;
          align-items: center;
          gap: 12px;
        }

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
          background: var(--white);
        }

        .filter-control select:focus,
        .filter-control input:focus {
          outline: none;
          border-color: var(--secondary-blue);
        }

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
          margin-top: 0;
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

        .report-content p {
          margin-bottom: 15px;
          line-height: 1.5;
          color: #495057;
          font-size: 14px;
        }

        .report-actions {
          display: flex;
          justify-content: space-between;
          margin-top: 15px;
        }

        .btn {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          display: inline-flex;
          align-items: center;
          gap: 6px;
          transition: all 0.2s;
          text-decoration: none;
        }

        .btn-primary {
          background: var(--primary-blue);
          color: white;
        }

        .btn-primary:hover {
          background: var(--dark-blue);
        }

        .btn-outline {
          background: transparent;
          border: 1px solid var(--medium-gray);
          color: #495057;
        }

        .btn-outline:hover {
          background: #f8f9fa;
        }

        .btn-sm {
          padding: 6px 12px;
          font-size: 12px;
        }

        .empty-state {
          grid-column: 1 / -1;
          text-align: center;
          padding: 60px 20px;
          color: var(--text-muted);
        }

        .empty-state i {
          font-size: 64px;
          margin-bottom: 20px;
          opacity: 0.3;
        }

        .empty-state h3 {
          margin: 0 0 10px 0;
          color: #495057;
        }

        .loading-state,
        .error-state {
          text-align: center;
          padding: 60px 20px;
        }

        .loading-state i {
          font-size: 32px;
          color: var(--primary-blue);
          margin-bottom: 15px;
        }

        .error-state i {
          font-size: 32px;
          color: var(--danger);
          margin-bottom: 15px;
        }

        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal {
          background: white;
          border-radius: 8px;
          width: 90%;
          max-width: 600px;
          max-height: 80vh;
          overflow-y: auto;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .modal-header {
          padding: 20px;
          border-bottom: 1px solid #dee2e6;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .modal-header h3 {
          margin: 0;
          color: #333;
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 18px;
          color: #6c757d;
          cursor: pointer;
        }

        .modal-body {
          padding: 20px;
        }

        .modal-footer {
          padding: 20px;
          border-top: 1px solid #dee2e6;
          display: flex;
          justify-content: flex-end;
          gap: 10px;
        }

        .report-types h4 {
          margin: 0 0 20px 0;
          color: #333;
        }

        .type-options {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
        }

        .type-option {
          padding: 20px;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          text-align: center;
          cursor: pointer;
          transition: all 0.2s;
        }

        .type-option:hover {
          border-color: var(--primary-blue);
          background: #f8f9ff;
        }

        .type-option i {
          font-size: 24px;
          color: var(--primary-blue);
          margin-bottom: 10px;
        }

        .type-option h5 {
          margin: 0 0 8px 0;
          color: #333;
        }

        .type-option p {
          margin: 0;
          color: #6c757d;
          font-size: 14px;
        }

        @media (max-width: 1200px) {
          .report-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }

        /* Dashboard Statistics */
        .dashboard-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 24px;
          margin-bottom: 32px;
          padding: 0 4px;
        }

        .stat-card {
          background: white;
          border-radius: var(--border-radius);
          padding: 24px;
          box-shadow: var(--card-shadow);
          display: flex;
          align-items: center;
          gap: 20px;
          transition: var(--transition);
          position: relative;
          overflow: hidden;
        }

        .stat-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 4px;
          background: linear-gradient(90deg, var(--primary-blue), var(--secondary-blue));
        }

        .stat-card:hover {
          box-shadow: var(--hover-shadow);
          transform: translateY(-2px);
        }

        .stat-icon {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          color: white;
          flex-shrink: 0;
        }

        .primary-icon { background: linear-gradient(135deg, var(--primary-blue), var(--secondary-blue)); }
        .threat-icon { background: linear-gradient(135deg, #6f42c1, #9561e2); }
        .warning-icon { background: linear-gradient(135deg, #fd7e14, #ffb347); }
        .success-icon { background: linear-gradient(135deg, var(--success), #5cbf60); }

        .stat-content {
          flex: 1;
        }

        .stat-number {
          font-size: 32px;
          font-weight: 700;
          color: var(--dark-blue);
          margin-bottom: 4px;
          line-height: 1;
        }

        .stat-label {
          font-size: 14px;
          color: var(--text-muted);
          font-weight: 500;
          margin-bottom: 8px;
        }

        .stat-trend {
          font-size: 12px;
          display: flex;
          align-items: center;
          gap: 4px;
          font-weight: 500;
        }

        .stat-trend.positive { color: var(--success); }
        .stat-trend.negative { color: var(--success); }
        .stat-trend.neutral { color: var(--text-muted); }

        /* Enhanced Controls */
        .controls-section {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 32px;
          padding: 20px;
          background: white;
          border-radius: var(--border-radius);
          box-shadow: var(--card-shadow);
          flex-wrap: wrap;
          gap: 16px;
        }

        .left-controls {
          display: flex;
          align-items: center;
          gap: 16px;
          flex-wrap: wrap;
        }

        .search-box {
          position: relative;
          min-width: 300px;
        }

        .search-box i {
          position: absolute;
          left: 12px;
          top: 50%;
          transform: translateY(-50%);
          color: var(--text-muted);
          font-size: 16px;
        }

        .search-input {
          width: 100%;
          padding: 12px 12px 12px 40px;
          border: 2px solid #e9ecef;
          border-radius: 8px;
          font-size: 14px;
          transition: var(--transition);
        }

        .search-input:focus {
          outline: none;
          border-color: var(--secondary-blue);
          box-shadow: 0 0 0 3px rgba(90, 159, 212, 0.1);
        }

        .filter-controls {
          display: flex;
          gap: 12px;
        }

        .filter-select, .sort-select {
          padding: 8px 16px;
          border: 2px solid #e9ecef;
          border-radius: 6px;
          background: white;
          font-size: 14px;
          cursor: pointer;
          transition: var(--transition);
        }

        .filter-select:focus, .sort-select:focus {
          outline: none;
          border-color: var(--secondary-blue);
        }

        .right-controls {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .view-toggle {
          display: flex;
          background: #f8f9fa;
          border-radius: 6px;
          padding: 2px;
        }

        .view-btn {
          padding: 8px 12px;
          border: none;
          background: transparent;
          border-radius: 4px;
          cursor: pointer;
          color: var(--text-muted);
          transition: var(--transition);
        }

        .view-btn.active {
          background: white;
          color: var(--primary-blue);
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .quick-filters {
          display: flex;
          gap: 8px;
        }

        .filter-tag {
          padding: 6px 12px;
          background: #f8f9fa;
          border-radius: 20px;
          font-size: 12px;
          color: var(--text-muted);
          cursor: pointer;
          transition: var(--transition);
          border: 1px solid #e9ecef;
        }

        .filter-tag.active {
          background: var(--primary-blue);
          color: white;
          border-color: var(--primary-blue);
        }

        /* Enhanced Report Cards */
        .reports-container.grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
          gap: 24px;
        }

        .reports-container.list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .enhanced-report-card {
          background: white;
          border-radius: var(--border-radius);
          box-shadow: var(--card-shadow);
          transition: var(--transition);
          overflow: hidden;
          border: 1px solid #f1f3f4;
          position: relative;
        }

        .enhanced-report-card:hover {
          box-shadow: var(--hover-shadow);
          transform: translateY(-4px);
          border-color: var(--secondary-blue);
        }

        .card-header {
          padding: 16px 20px;
          background: linear-gradient(135deg, #f8f9fa 0%, #f1f3f4 100%);
          border-bottom: 1px solid #e9ecef;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .status-indicators {
          display: flex;
          gap: 8px;
        }

        .severity-badge, .status-badge {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 4px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .menu-btn {
          background: none;
          border: none;
          color: var(--text-muted);
          cursor: pointer;
          padding: 4px;
          border-radius: 4px;
          transition: var(--transition);
        }

        .menu-btn:hover {
          background: #f8f9fa;
          color: var(--dark-blue);
        }

        .card-content {
          padding: 20px;
        }

        .report-type-tag {
          display: inline-block;
          padding: 4px 12px;
          background: var(--light-blue);
          color: var(--primary-blue);
          border-radius: 16px;
          font-size: 12px;
          font-weight: 500;
          margin-bottom: 12px;
          border: 1px solid #e1f3ff;
        }

        .report-title {
          font-size: 18px;
          font-weight: 600;
          color: var(--dark-blue);
          margin-bottom: 8px;
          line-height: 1.4;
        }

        .report-description {
          color: var(--text-muted);
          font-size: 14px;
          line-height: 1.5;
          margin-bottom: 16px;
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        .report-metadata {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin-bottom: 16px;
        }

        .meta-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: var(--text-muted);
        }

        .meta-item i {
          width: 14px;
          color: var(--secondary-blue);
        }

        .key-stats {
          display: flex;
          justify-content: space-between;
          margin-bottom: 16px;
          padding: 12px;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .key-stat {
          text-align: center;
          flex: 1;
        }

        .key-stat .stat-value {
          font-size: 20px;
          font-weight: 700;
          color: var(--primary-blue);
          margin-bottom: 4px;
        }

        .key-stat .stat-label {
          font-size: 11px;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .threat-level-bar {
          margin-bottom: 16px;
        }

        .threat-level-label {
          font-size: 12px;
          font-weight: 500;
          color: var(--dark-blue);
          margin-bottom: 6px;
        }

        .threat-level-indicator {
          height: 6px;
          background: #e9ecef;
          border-radius: 3px;
          overflow: hidden;
          position: relative;
        }

        .threat-level-fill {
          height: 100%;
          border-radius: 3px;
          transition: var(--transition);
        }

        .threat-level-fill.low { background: var(--success); }
        .threat-level-fill.medium { background: var(--warning); }
        .threat-level-fill.high { background: var(--danger); }

        .threat-level-text {
          font-size: 11px;
          color: var(--text-muted);
          margin-top: 4px;
          text-align: right;
          font-weight: 500;
        }

        .confidence-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 16px;
          font-size: 12px;
        }

        .confidence-label {
          color: var(--dark-blue);
          font-weight: 500;
        }

        .confidence-dots {
          display: flex;
          gap: 3px;
        }

        .confidence-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #e9ecef;
          transition: var(--transition);
        }

        .confidence-dot.active {
          background: var(--secondary-blue);
        }

        .confidence-text {
          color: var(--text-muted);
          font-weight: 500;
        }

        .card-actions {
          padding: 16px 20px;
          background: #fafbfc;
          border-top: 1px solid #f1f3f4;
        }

        .action-buttons {
          display: flex;
          gap: 8px;
          justify-content: flex-end;
        }

        .action-btn {
          padding: 8px 16px;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 12px;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 6px;
          transition: var(--transition);
          text-decoration: none;
        }

        .action-btn.primary {
          background: var(--primary-blue);
          color: white;
        }

        .action-btn.primary:hover {
          background: var(--dark-blue);
          transform: translateY(-1px);
        }

        .action-btn.secondary {
          background: white;
          color: var(--text-muted);
          border: 1px solid #e9ecef;
        }

        .action-btn.secondary:hover {
          background: #f8f9fa;
          color: var(--dark-blue);
          border-color: #d1d9e0;
        }

        /* Enhanced Empty State */
        .empty-state {
          text-align: center;
          padding: 80px 20px;
          background: white;
          border-radius: var(--border-radius);
          box-shadow: var(--card-shadow);
        }

        .empty-icon {
          width: 80px;
          height: 80px;
          margin: 0 auto 20px;
          background: var(--light-blue);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--secondary-blue);
          font-size: 32px;
        }

        @media (max-width: 768px) {
          .page-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 15px;
          }

          .dashboard-stats {
            grid-template-columns: 1fr 1fr;
            gap: 16px;
          }

          .controls-section {
            flex-direction: column;
            align-items: stretch;
          }

          .left-controls, .right-controls {
            justify-content: space-between;
          }

          .search-box {
            min-width: 100%;
          }

          .reports-container.grid {
            grid-template-columns: 1fr;
          }

          .enhanced-report-card {
            margin-bottom: 16px;
          }

          .report-metadata {
            grid-template-columns: 1fr;
          }

          .key-stats {
            flex-direction: column;
            gap: 12px;
          }

          .quick-filters {
            justify-content: center;
          }

          .report-grid {
            grid-template-columns: 1fr;
          }

          .filters-grid {
            grid-template-columns: 1fr;
          }

          .stat-card {
            padding: 16px;
          }

          .stat-number {
            font-size: 24px;
          }
        }

        @media (max-width: 480px) {
          .dashboard-stats {
            grid-template-columns: 1fr;
          }

          .action-buttons {
            flex-direction: column;
            gap: 8px;
          }

          .filter-controls {
            flex-direction: column;
            gap: 8px;
            width: 100%;
          }

          .filter-select, .sort-select {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default Reports;
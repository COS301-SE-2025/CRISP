import React, { useState, useEffect } from 'react';
import ReportDetailModal from './ReportDetailModal';

const Reports = ({ active = true }) => {

  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [sectorFilter, setSectorFilter] = useState('all');
  const [dateRangeFilter, setDateRangeFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const [viewMode, setViewMode] = useState('grid');
  const [savingReportId, setSavingReportId] = useState(null);
  const [exportingReportId, setExportingReportId] = useState(null);

  useEffect(() => {
    fetchReports();
    fetchDashboardStats();
    fetchRecentActivity();
  }, [filter, sectorFilter, dateRangeFilter]);

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
    // Recent activity functionality removed for production
    // Can be implemented later with real API endpoint
    setRecentActivity([]);
  };

  const fetchReports = async () => {
    try {
      setLoading(true);

      const token = localStorage.getItem('crisp_auth_token');
      if (!token) {
        throw new Error('Authentication required');
      }

      // Fetch persistent reports from database
      const response = await fetch('http://localhost:8000/api/reports/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });


      if (response.ok) {
        const data = await response.json();

        if (data.success && data.reports) {

          // Transform persistent reports to match frontend format
          const transformedReports = data.reports.map(report => {
            // Extract stats from report data
            const reportData = report.report_data || {};
            const statistics = reportData.statistics || [];


            // Get key metrics from real data
            const threatTypes = parseInt(statistics.find(s => s.label === 'Threat Types')?.value || '0');
            const iocCount = parseInt(statistics.find(s => s.label.includes('IoC'))?.value || '0');
            const orgCount = parseInt(statistics.find(s =>
              s.label.includes('Organizations') ||
              s.label.includes('Institutions') ||
              s.label.includes('Affected') ||
              s.label.includes('Targeted')
            )?.value || '0');
            const ttpCount = parseInt(statistics.find(s => s.label.includes('TTP'))?.value || '0');

            // Use ONLY real statistics from database - no mock data for production
            const reportStats = statistics;

            return {
              id: report.id,
              title: report.title,
              type: report.report_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) + ' Analysis',
              created_at: report.created_at,
              date: new Date(report.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              }),
              views: report.view_count,
              view_count: report.view_count,
              description: report.description || `Analysis report for ${report.report_type.replace('_', ' ')} sector`,
              stats: reportStats,
              threatTypes: threatTypes,
              threatLevel: iocCount > 40 ? 'High' : iocCount > 20 ? 'Medium' : 'Low',
              organizationsAnalyzed: orgCount,
              lastUpdated: report.updated_at,
              sector: report.report_type.includes('education') ? 'education' :
                     report.report_type.includes('financial') ? 'financial' :
                     report.report_type.includes('government') ? 'government' : 'general',
              status: report.status === 'completed' ? 'Active' : 'Processing',
              confidence: iocCount > 30 ? 'High' : iocCount > 15 ? 'Medium' : 'Low',
              generated_by: report.generated_by,
              organization: report.organization,
              age_days: report.age_days,
              isPersistent: true, // Mark as persistent report
              isSaved: true, // Already saved to database
              isTemporary: false,
              reportData: reportData // Include full report data for detail view
            };
          });

          // Apply filters
          let filteredReports = transformedReports;

          // Report type filter
          if (filter !== 'all') {
            filteredReports = filteredReports.filter(r => {
              const reportType = r.type.toLowerCase();
              return reportType.includes(filter.toLowerCase()) ||
                     r.report_type?.toLowerCase().includes(filter.toLowerCase());
            });
          }

          // Sector filter
          if (sectorFilter !== 'all') {
            filteredReports = filteredReports.filter(r => {
              const reportSector = r.sector || 'general';
              return reportSector === sectorFilter;
            });
          }

          // Date range filter
          if (dateRangeFilter !== 'all') {
            const now = new Date();
            let cutoffDate;

            switch (dateRangeFilter) {
              case 'week':
                cutoffDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                break;
              case 'month':
                cutoffDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                break;
              case 'quarter':
                cutoffDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
                break;
              case 'year':
                cutoffDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
                break;
              default:
                cutoffDate = null;
            }

            if (cutoffDate) {
              filteredReports = filteredReports.filter(r => {
                const reportDate = new Date(r.lastUpdated || r.created_at);
                return reportDate >= cutoffDate;
              });
            }
          }

          setReports(filteredReports);
        } else {
          console.warn('No reports returned from API');
          setReports([]);
        }
      } else {
        const errorText = await response.text();
        console.error('❌ API Error Response:', {
          status: response.status,
          statusText: response.statusText,
          body: errorText
        });
        throw new Error(`Failed to fetch reports: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error fetching persistent reports:', error);
      setError(error.message);

      // Fallback to empty state with helpful message
      setReports([]);
    } finally {
      setLoading(false);
    }
  };

  // New function to generate fresh reports (moved from fetchReports)
  const generateNewReport = async (reportType) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('crisp_auth_token');

      if (!token) {
        throw new Error('Authentication required');
      }

      const endpoints = {
        'education': '/api/reports/education-sector-analysis/',
        'financial': '/api/reports/financial-sector-analysis/',
        'government': '/api/reports/government-sector-analysis/'
      };

      const endpoint = endpoints[reportType];
      if (!endpoint) {
        throw new Error('Invalid report type');
      }


      const response = await fetch(`http://localhost:8000${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Since persistence is disabled, create a temporary report object
          const reportData = data.report;
          const statistics = reportData.statistics || [];

          // Extract stats like the persistent reports do
          const threatTypes = parseInt(statistics.find(s => s.label === 'Threat Types')?.value || '0');
          const iocCount = parseInt(statistics.find(s => s.label.includes('IoC'))?.value || '0');
          const orgCount = parseInt(statistics.find(s =>
            s.label.includes('Organizations') ||
            s.label.includes('Institutions') ||
            s.label.includes('Affected') ||
            s.label.includes('Targeted')
          )?.value || '0');
          const ttpCount = parseInt(statistics.find(s => s.label.includes('TTP'))?.value || '0');

          const tempReport = {
            id: `temp-${Date.now()}`,
            title: reportData.title,
            type: reportData.type,
            created_at: new Date().toISOString(),
            date: new Date().toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            }),
            views: reportData.views || 0,
            view_count: reportData.views || 0,
            description: reportData.description,
            stats: statistics,
            threatTypes: threatTypes,
            threatLevel: iocCount > 40 ? 'High' : iocCount > 20 ? 'Medium' : 'Low',
            organizationsAnalyzed: orgCount,
            lastUpdated: new Date().toISOString(),
            sector: reportData.sector_focus || 'general',
            generated_by: { username: 'current-user', first_name: 'Current', last_name: 'User' },
            fullData: reportData,
            isSaved: false,
            isTemporary: true,
            reportType: reportType
          };

          // Add the temp report to the current reports list
          setReports(prevReports => [tempReport, ...prevReports]);
          return data;
        }
      }

      throw new Error('Failed to generate report');
    } catch (error) {
      console.error('Error generating report:', error);
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Handle report generation from modal
  const handleGenerateReport = async (reportType) => {
    try {
      await generateNewReport(reportType);
      setShowCreateModal(false);

      // Show success message (optional)
    } catch (error) {
      console.error('Failed to generate report:', error);
      // Error handling is already done in generateNewReport
    }
  };

  // Save a temporary report to the database
  const saveReport = async (report) => {
    try {
      setSavingReportId(report.id);
      const token = localStorage.getItem('crisp_auth_token');

      if (!token) {
        throw new Error('Authentication required');
      }

      const endpoints = {
        'education': '/api/reports/education-sector-analysis/',
        'financial': '/api/reports/financial-sector-analysis/',
        'government': '/api/reports/government-sector-analysis/'
      };

      const endpoint = endpoints[report.reportType];
      if (!endpoint) {
        throw new Error('Invalid report type');
      }

      // Make API call with persist=True by adding query parameter
      const response = await fetch(`http://localhost:8000${endpoint}?persist=true`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Update the report in the list to mark it as saved
          setReports(prevReports =>
            prevReports.map(r =>
              r.id === report.id
                ? { ...r, isSaved: true, isTemporary: false, id: data.report.id || r.id }
                : r
            )
          );

          // Refresh reports list to include the newly saved report from database
          await fetchReports();
          return data;
        }
      }

      throw new Error('Failed to save report');
    } catch (error) {
      console.error('Error saving report:', error);
      setError(error.message);
      throw error;
    } finally {
      setSavingReportId(null);
    }
  };

  // Export report as PDF
  const exportReportPDF = async (report) => {
    try {
      setExportingReportId(report.id);

      // Generate a clean PDF-ready view of the report
      const printWindow = window.open('', '_blank');

      // Create PDF-optimized HTML content
      const pdfContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <title>${report.title}</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              margin: 40px;
              background: white;
              color: black;
              line-height: 1.6;
            }
            .report-header {
              border-bottom: 2px solid #333;
              padding-bottom: 20px;
              margin-bottom: 30px;
            }
            .report-title {
              font-size: 24px;
              font-weight: bold;
              margin: 0 0 10px 0;
              color: #333;
            }
            .report-meta {
              color: #666;
              font-size: 14px;
            }
            .stats-grid {
              display: grid;
              grid-template-columns: repeat(2, 1fr);
              gap: 20px;
              margin: 30px 0;
            }
            .stat-card {
              border: 1px solid #ddd;
              padding: 15px;
              border-radius: 8px;
              text-align: center;
            }
            .stat-number {
              font-size: 24px;
              font-weight: bold;
              color: #333;
            }
            .stat-label {
              font-size: 12px;
              color: #666;
              text-transform: uppercase;
            }
            .description {
              background: #f8f9fa;
              padding: 20px;
              border-radius: 8px;
              margin: 20px 0;
            }
            .footer {
              margin-top: 40px;
              padding-top: 20px;
              border-top: 1px solid #ddd;
              text-align: center;
              color: #666;
              font-size: 12px;
            }
            @media print {
              body { margin: 20px; }
              .stats-grid { page-break-inside: avoid; }
            }
          </style>
        </head>
        <body>
          <div class="report-header">
            <div class="report-title">${report.title}</div>
            <div class="report-meta">
              Generated: ${report.date} |
              Created by: ${typeof report.generated_by === 'object' && report.generated_by
                ? `${report.generated_by.first_name} ${report.generated_by.last_name}`
                : report.generated_by || 'System'}
            </div>
          </div>

          <div class="stats-grid">
            ${(report.stats || []).map(stat => `
              <div class="stat-card">
                <div class="stat-number">${stat.value}</div>
                <div class="stat-label">${stat.label}</div>
              </div>
            `).join('')}
          </div>

          <div class="description">
            <h3>Summary</h3>
            <p>${report.description}</p>
          </div>

          <div class="footer">
            <p>CRISP - Cyber Threat Intelligence Report</p>
            <p>Generated on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}</p>
          </div>
        </body>
        </html>
      `;

      printWindow.document.write(pdfContent);
      printWindow.document.close();

      // Wait a bit for content to load, then trigger print
      setTimeout(() => {
        printWindow.focus();
        printWindow.print();
      }, 500);

    } catch (error) {
      console.error('Error exporting PDF:', error);
    } finally {
      setTimeout(() => setExportingReportId(null), 1000);
    }
  };

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
      report.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.sector?.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.lastUpdated || b.created_at) - new Date(a.lastUpdated || a.created_at);
        case 'severity':
          const severityOrder = { 'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1 };
          return (severityOrder[b.severity] || 0) - (severityOrder[a.severity] || 0);
        case 'views':
          return (b.views || b.view_count || 0) - (a.views || a.view_count || 0);
        case 'title':
          return a.title.localeCompare(b.title);
        case 'type':
          return a.type.localeCompare(b.type);
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

  if (!active) return null;

  return (
    <section id="reports" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Threat Intelligence Reports</h1>
          <p className="page-subtitle">Access and manage comprehensive threat reports</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline">
            <i className="fas fa-filter"></i> Filter
          </button>
          <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
            <i className="fas fa-plus"></i> Create New Report
          </button>
        </div>
      </div>

      <div className="filters-section">
        <div className="filters-grid">
          <div className="filter-group">
            <label className="filter-label">Report Type</label>
            <div className="filter-control">
              <select value={filter} onChange={(e) => setFilter(e.target.value)}>
                <option value="all">All Types</option>
                <option value="sector">Sector Analysis</option>
                <option value="education">Education Analysis</option>
                <option value="financial">Financial Analysis</option>
                <option value="government">Government Analysis</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Sector Focus</label>
            <div className="filter-control">
              <select value={sectorFilter} onChange={(e) => setSectorFilter(e.target.value)}>
                <option value="all">All Sectors</option>
                <option value="education">Education</option>
                <option value="financial">Financial</option>
                <option value="government">Government</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Date Range</label>
            <div className="filter-control">
              <select value={dateRangeFilter} onChange={(e) => setDateRangeFilter(e.target.value)}>
                <option value="all">All Time</option>
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
              <input
                type="text"
                placeholder="Search reports..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Sort By</label>
            <div className="filter-control">
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="date">Date Created</option>
                <option value="title">Report Title</option>
                <option value="severity">Severity Level</option>
                <option value="views">View Count</option>
                <option value="type">Report Type</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading reports...</p>
        </div>
      ) : (
        <div className="report-grid">
          {filteredAndSortedReports.length === 0 ? (
            <div className="empty-state">
              <i className="fas fa-file-alt"></i>
              <h3>No reports found</h3>
              <p>Generate your first report to see analytics and insights.</p>
              <button className="btn btn-primary btn-sm empty-state-btn" onClick={() => setShowCreateModal(true)}>
                Generate Report
              </button>
            </div>
          ) : (
            filteredAndSortedReports.map(report => (
              <div key={report.id} className="report-card">
                <div className="report-header">
                  <div className="report-type">{report.report_type || report.type}</div>
                  <h3 className="report-title">{report.title}</h3>
                  <div className="report-meta">
                    <div className="meta-left">
                      <span><i className="fas fa-calendar"></i> {new Date(report.created_at || report.lastUpdated).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}</span>
                      <span><i className="fas fa-user"></i> {
                        typeof report.generated_by === 'object' && report.generated_by
                          ? `${report.generated_by.first_name} ${report.generated_by.last_name}`
                          : report.generated_by || 'System'
                      }</span>
                    </div>
                  </div>
                </div>
                <div className="report-content">
                  <div className="report-stats">
                    {(report.stats || []).map((stat, index) => (
                      <div key={index} className="report-stat">
                        <div className="stat-number">{stat.value}</div>
                        <div className="stat-label">{stat.label}</div>
                      </div>
                    ))}
                  </div>
                  <p>{report.description}</p>
                  <div className="report-actions">
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => viewReport(report)}
                    >
                      <i className="fas fa-eye"></i> View Report
                    </button>
                    {report.isTemporary && !report.isSaved && (
                      <button
                        className="btn btn-success btn-sm"
                        onClick={() => saveReport(report)}
                        disabled={savingReportId === report.id}
                      >
                        {savingReportId === report.id ? (
                          <>
                            <i className="fas fa-spinner fa-spin"></i> Saving...
                          </>
                        ) : (
                          <>
                            <i className="fas fa-save"></i> Save Report
                          </>
                        )}
                      </button>
                    )}
                    <button
                      className="btn btn-outline btn-sm"
                      onClick={() => exportReportPDF(report)}
                      disabled={exportingReportId === report.id}
                    >
                      {exportingReportId === report.id ? (
                        <>
                          <i className="fas fa-spinner fa-spin"></i> Exporting...
                        </>
                      ) : (
                        <>
                          <i className="fas fa-file-pdf"></i> Export PDF
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

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
                <h4>Select Sector Analysis Report</h4>
                <p className="modal-description">Generate comprehensive threat intelligence reports for specific sectors. New reports will be saved and accessible in your reports history.</p>
                <div className="type-options">
                  <div
                    className="type-option"
                    onClick={() => handleGenerateReport('education')}
                    style={{ cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.6 : 1 }}
                  >
                    <i className="fas fa-graduation-cap"></i>
                    <h5>Education Sector</h5>
                    <p>Universities, schools, and educational institutions</p>
                  </div>
                  <div
                    className="type-option"
                    onClick={() => handleGenerateReport('financial')}
                    style={{ cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.6 : 1 }}
                  >
                    <i className="fas fa-university"></i>
                    <h5>Financial Sector</h5>
                    <p>Banks, financial institutions, and fintech companies</p>
                  </div>
                  <div
                    className="type-option"
                    onClick={() => handleGenerateReport('government')}
                    style={{ cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.6 : 1 }}
                  >
                    <i className="fas fa-building"></i>
                    <h5>Government Sector</h5>
                    <p>Government agencies and public institutions</p>
                  </div>
                </div>
                {loading && (
                  <div className="generation-status">
                    <div className="loading-spinner"></div>
                    <p>Generating report... This may take a few moments.</p>
                  </div>
                )}
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={() => setShowCreateModal(false)}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Cancel'}
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

      <style>{`
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
          align-items: flex-start;
          color: var(--text-muted);
          font-size: 13px;
          gap: 10px;
        }

        .meta-left {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .report-meta span {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .report-meta i {
          width: 12px;
          font-size: 10px;
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

        .btn-success {
          background: #28a745;
          border: 1px solid #28a745;
          color: white;
        }

        .btn-success:hover {
          background: #218838;
          border-color: #1e7e34;
        }

        .btn-success:disabled {
          background: #6c757d;
          border-color: #6c757d;
          cursor: not-allowed;
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

        .empty-state-btn {
          padding: 3px 8px !important;
          font-size: 10px !important;
          margin-top: 16px;
          min-width: auto !important;
          text-align: center;
          display: inline-block;
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

        .modal-description {
          color: #6c757d;
          font-size: 14px;
          margin-bottom: 20px;
          line-height: 1.4;
        }

        .generation-status {
          margin-top: 20px;
          padding: 20px;
          background: #f8f9fa;
          border-radius: 8px;
          text-align: center;
        }

        .loading-spinner {
          width: 24px;
          height: 24px;
          border: 3px solid #f3f3f3;
          border-top: 3px solid var(--primary-blue);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 10px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
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

        /* Controls */
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

        /* Report Cards */
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

        .report-card {
          background: white;
          border-radius: var(--border-radius);
          box-shadow: var(--card-shadow);
          transition: var(--transition);
          overflow: hidden;
          border: 1px solid #f1f3f4;
          position: relative;
        }

        .report-card:hover {
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

        .persistent-badge {
          background: #28a745;
          color: white;
          font-size: 11px;
          font-weight: 600;
          padding: 4px 8px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .persistent-badge i {
          font-size: 10px;
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

        /* Empty State */
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

          .report-card {
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
    </section>
  );
};

export default Reports;
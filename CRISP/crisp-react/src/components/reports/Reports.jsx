import React, { useState, useEffect } from 'react';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchReports();
  }, [filter]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      // Simulated API call - replace with actual endpoint
      const mockReports = [
        {
          id: '1',
          name: 'Monthly Threat Intelligence Summary',
          type: 'threat_summary',
          status: 'completed',
          created_at: '2025-01-10T08:00:00Z',
          generated_by: 'System',
          file_size: '2.5 MB',
          format: 'PDF',
          description: 'Comprehensive analysis of threat indicators and TTPs identified during January 2025.',
          download_count: 15
        },
        {
          id: '2',
          name: 'Organization Trust Relationships',
          type: 'trust_analysis',
          status: 'completed',
          created_at: '2025-01-08T14:30:00Z',
          generated_by: 'Admin User',
          file_size: '1.2 MB',
          format: 'PDF',
          description: 'Analysis of bilateral and community trust relationships across partner organizations.',
          download_count: 8
        },
        {
          id: '3',
          name: 'STIX Feed Consumption Report',
          type: 'feed_analysis',
          status: 'processing',
          created_at: '2025-01-13T10:15:00Z',
          generated_by: 'System',
          file_size: null,
          format: 'PDF',
          description: 'Weekly report on STIX/TAXII feed consumption and indicator processing.',
          download_count: 0
        },
        {
          id: '4',
          name: 'Security Metrics Dashboard',
          type: 'metrics',
          status: 'failed',
          created_at: '2025-01-12T16:45:00Z',
          generated_by: 'Security Team',
          file_size: null,
          format: 'Excel',
          description: 'Key performance indicators and security metrics for Q4 2024.',
          download_count: 0
        }
      ];

      let filteredReports = mockReports;
      if (filter !== 'all') {
        filteredReports = mockReports.filter(r => {
          if (filter === 'completed') return r.status === 'completed';
          if (filter === 'processing') return r.status === 'processing';
          if (filter === 'failed') return r.status === 'failed';
          return r.type === filter;
        });
      }

      setReports(filteredReports);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getReportTypeIcon = (type) => {
    const icons = {
      threat_summary: 'fas fa-shield-alt',
      trust_analysis: 'fas fa-handshake',
      feed_analysis: 'fas fa-rss',
      metrics: 'fas fa-chart-bar',
      audit: 'fas fa-clipboard-check'
    };
    return icons[type] || 'fas fa-file-alt';
  };

  const getStatusIcon = (status) => {
    const icons = {
      completed: 'fas fa-check-circle',
      processing: 'fas fa-spinner fa-spin',
      failed: 'fas fa-exclamation-circle'
    };
    return icons[status] || 'fas fa-question-circle';
  };

  const getStatusColor = (status) => {
    const colors = {
      completed: '#28a745',
      processing: '#ffc107',
      failed: '#dc3545'
    };
    return colors[status] || '#6c757d';
  };

  const downloadReport = (report) => {
    // Simulate download
    console.log(`Downloading report: ${report.name}`);
  };

  const deleteReport = (reportId) => {
    setReports(prev => prev.filter(r => r.id !== reportId));
  };

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
    <div className="reports">
      <div className="header">
        <h2>Reports & Analytics</h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          <i className="fas fa-plus"></i>
          Generate Report
        </button>
      </div>

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
            <i className="fas fa-check-circle" style={{color: '#28a745'}}></i>
          </div>
          <div className="stat-content">
            <h3>{reports.filter(r => r.status === 'completed').length}</h3>
            <p>Completed</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-spinner" style={{color: '#ffc107'}}></i>
          </div>
          <div className="stat-content">
            <h3>{reports.filter(r => r.status === 'processing').length}</h3>
            <p>Processing</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-download"></i>
          </div>
          <div className="stat-content">
            <h3>{reports.reduce((sum, r) => sum + (r.download_count || 0), 0)}</h3>
            <p>Downloads</p>
          </div>
        </div>
      </div>

      <div className="filters">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All Reports
        </button>
        <button
          className={`filter-btn ${filter === 'completed' ? 'active' : ''}`}
          onClick={() => setFilter('completed')}
        >
          Completed
        </button>
        <button
          className={`filter-btn ${filter === 'processing' ? 'active' : ''}`}
          onClick={() => setFilter('processing')}
        >
          Processing
        </button>
        <button
          className={`filter-btn ${filter === 'threat_summary' ? 'active' : ''}`}
          onClick={() => setFilter('threat_summary')}
        >
          Threat Reports
        </button>
        <button
          className={`filter-btn ${filter === 'trust_analysis' ? 'active' : ''}`}
          onClick={() => setFilter('trust_analysis')}
        >
          Trust Analysis
        </button>
      </div>

      <div className="reports-list">
        {reports.length === 0 ? (
          <div className="empty-state">
            <i className="fas fa-file-alt"></i>
            <h3>No reports found</h3>
            <p>Generate your first report to see analytics and insights.</p>
            <button 
              className="btn btn-primary"
              onClick={() => setShowCreateModal(true)}
            >
              <i className="fas fa-plus"></i>
              Generate Report
            </button>
          </div>
        ) : (
          reports.map(report => (
            <div key={report.id} className="report-card">
              <div className="report-header">
                <div className="report-icon">
                  <i className={getReportTypeIcon(report.type)}></i>
                </div>
                <div className="report-meta">
                  <h3>{report.name}</h3>
                  <p className="report-description">{report.description}</p>
                  <div className="report-details">
                    <span className="detail-item">
                      <i className="fas fa-user"></i>
                      {report.generated_by}
                    </span>
                    <span className="detail-item">
                      <i className="fas fa-calendar"></i>
                      {new Date(report.created_at).toLocaleDateString()}
                    </span>
                    {report.file_size && (
                      <span className="detail-item">
                        <i className="fas fa-file"></i>
                        {report.file_size} ({report.format})
                      </span>
                    )}
                    <span className="detail-item">
                      <i className="fas fa-download"></i>
                      {report.download_count} downloads
                    </span>
                  </div>
                </div>
                <div className="report-status">
                  <span 
                    className="status-indicator"
                    style={{ color: getStatusColor(report.status) }}
                  >
                    <i className={getStatusIcon(report.status)}></i>
                    {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
                  </span>
                </div>
              </div>
              
              <div className="report-actions">
                {report.status === 'completed' && (
                  <button 
                    className="btn btn-sm btn-primary"
                    onClick={() => downloadReport(report)}
                  >
                    <i className="fas fa-download"></i>
                    Download
                  </button>
                )}
                <button className="btn btn-sm btn-outline">
                  <i className="fas fa-eye"></i>
                  View Details
                </button>
                <button className="btn btn-sm btn-outline">
                  <i className="fas fa-share"></i>
                  Share
                </button>
                <button 
                  className="btn btn-sm btn-danger"
                  onClick={() => deleteReport(report.id)}
                >
                  <i className="fas fa-trash"></i>
                  Delete
                </button>
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

      <style jsx>{`
        .reports {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
        }

        .header h2 {
          margin: 0;
          color: #333;
        }

        .stats-row {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }

        .stat-card {
          background: white;
          border-radius: 8px;
          padding: 20px;
          display: flex;
          align-items: center;
          gap: 15px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .stat-icon {
          width: 50px;
          height: 50px;
          background: #f8f9fa;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          color: #0056b3;
        }

        .stat-content h3 {
          margin: 0 0 5px 0;
          font-size: 24px;
          font-weight: 700;
          color: #333;
        }

        .stat-content p {
          margin: 0;
          color: #6c757d;
          font-size: 14px;
        }

        .filters {
          display: flex;
          gap: 8px;
          margin-bottom: 20px;
          padding-bottom: 15px;
          border-bottom: 1px solid #dee2e6;
        }

        .filter-btn {
          padding: 8px 16px;
          background: none;
          border: 1px solid #dee2e6;
          border-radius: 20px;
          cursor: pointer;
          font-size: 14px;
          color: #6c757d;
          transition: all 0.2s;
        }

        .filter-btn:hover {
          background: #f8f9fa;
          color: #495057;
        }

        .filter-btn.active {
          background: #0056b3;
          color: white;
          border-color: #0056b3;
        }

        .reports-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .report-card {
          background: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          transition: box-shadow 0.2s;
        }

        .report-card:hover {
          box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        .report-header {
          display: flex;
          align-items: flex-start;
          gap: 16px;
          margin-bottom: 15px;
        }

        .report-icon {
          width: 50px;
          height: 50px;
          background: #f8f9fa;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          color: #0056b3;
          flex-shrink: 0;
        }

        .report-meta {
          flex: 1;
        }

        .report-meta h3 {
          margin: 0 0 8px 0;
          color: #333;
          font-size: 18px;
        }

        .report-description {
          margin: 0 0 12px 0;
          color: #6c757d;
          line-height: 1.4;
        }

        .report-details {
          display: flex;
          flex-wrap: wrap;
          gap: 16px;
        }

        .detail-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;
          color: #6c757d;
        }

        .detail-item i {
          width: 14px;
          text-align: center;
        }

        .report-status {
          flex-shrink: 0;
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;
          font-weight: 500;
        }

        .report-actions {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
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
          transition: background-color 0.2s;
          text-decoration: none;
        }

        .btn-primary {
          background: #0056b3;
          color: white;
        }

        .btn-primary:hover {
          background: #004494;
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-outline {
          background: transparent;
          border: 1px solid #dee2e6;
          color: #495057;
        }

        .btn-outline:hover {
          background: #f8f9fa;
        }

        .btn-sm {
          padding: 6px 12px;
          font-size: 12px;
        }

        .btn-danger {
          background: #dc3545;
          color: white;
        }

        .btn-danger:hover {
          background: #c82333;
        }

        .empty-state {
          text-align: center;
          padding: 60px 20px;
          color: #6c757d;
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
          border-color: #0056b3;
          background: #f8f9ff;
        }

        .type-option i {
          font-size: 24px;
          color: #0056b3;
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

        .loading-state,
        .error-state {
          text-align: center;
          padding: 60px 20px;
        }

        .loading-state i {
          font-size: 32px;
          color: #0056b3;
          margin-bottom: 15px;
        }

        .error-state i {
          font-size: 32px;
          color: #dc3545;
          margin-bottom: 15px;
        }
      `}</style>
    </div>
  );
};

export default Reports;
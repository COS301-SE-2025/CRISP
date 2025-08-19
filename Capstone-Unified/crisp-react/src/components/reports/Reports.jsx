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
      // Mock data matching EXACT prototype structure
      const mockReports = [
        {
          id: '1',
          title: 'Education Sector Ransomware Campaign',
          type: 'Campaign Analysis',
          date: 'May 19, 2025',
          views: 148,
          description: 'Analysis of ongoing ransomware campaign targeting education institutions in South Africa and neighboring countries.',
          stats: [
            { label: 'Institutions Targeted', value: '18' },
            { label: 'Related IoCs', value: '42' },
            { label: 'TTPs Identified', value: '8' },
            { label: 'Severity', value: 'High' }
          ]
        },
        {
          id: '2',
          title: 'Threat Intelligence Digest: Week 20',
          type: 'Weekly Summary',
          date: 'May 17, 2025',
          views: 127,
          description: 'Weekly summary of significant threat intelligence findings and trends for the week ending May 17, 2025.',
          stats: [
            { label: 'New IoCs', value: '86' },
            { label: 'TTPs Observed', value: '12' },
            { label: 'Critical Alerts', value: '4' },
            { label: 'Threat Actors', value: '3' }
          ]
        },
        {
          id: '3',
          title: 'University Data Breach Investigation',
          type: 'Incident Analysis',
          date: 'May 15, 2025',
          views: 215,
          description: 'Detailed analysis of recent data breach affecting a major university, including timeline, attack vectors, and remediation steps.',
          stats: [
            { label: 'IoCs Discovered', value: '28' },
            { label: 'TTPs Identified', value: '6' },
            { label: 'Threat Actor', value: 'APT-EDU-01' },
            { label: 'Severity', value: 'Medium' }
          ]
        },
        {
          id: '4',
          title: 'Emerging Phishing Techniques in 2025',
          type: 'Trend Analysis',
          date: 'May 10, 2025',
          views: 342,
          description: 'Analysis of evolving phishing techniques observed across multiple sectors, with focus on AI-generated content and deep fakes.',
          stats: [
            { label: 'IoCs Analyzed', value: '53' },
            { label: 'New Techniques', value: '7' },
            { label: 'Organizations', value: '14' },
            { label: 'Relevance', value: 'High' }
          ]
        },
        {
          id: '5',
          title: 'Financial Sector Threat Landscape',
          type: 'Sector Analysis',
          date: 'May 5, 2025',
          views: 198,
          description: 'Comprehensive overview of current threats targeting financial institutions in Southern Africa, with focus on banking trojans and ATM malware.',
          stats: [
            { label: 'IoCs Analyzed', value: '94' },
            { label: 'TTPs Identified', value: '16' },
            { label: 'Threat Actors', value: '5' },
            { label: 'Severity', value: 'High' }
          ]
        },
        {
          id: '6',
          title: 'EDU-Ransom Malware Analysis',
          type: 'Technical Analysis',
          date: 'May 2, 2025',
          views: 276,
          description: 'Technical deep-dive into the EDU-Ransom malware strain targeting educational institutions, including code analysis and IOC extraction.',
          stats: [
            { label: 'IoCs Generated', value: '37' },
            { label: 'TTPs Mapped', value: '9' },
            { label: 'Attribution', value: 'RansomGroup-X' },
            { label: 'Severity', value: 'Critical' }
          ]
        }
      ];

      let filteredReports = mockReports;
      if (filter !== 'all') {
        filteredReports = mockReports.filter(r => {
          return r.type.toLowerCase().replace(' ', '_') === filter;
        });
      }

      setReports(filteredReports);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // No need for formatting functions since stats are already formatted in the data

  const viewReport = (report) => {
    console.log(`Viewing report: ${report.title}`);
  };

  const shareReport = (report) => {
    console.log(`Sharing report: ${report.title}`);
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
    <div className="reports-section">
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
                <div className="report-type">{report.type}</div>
                <h3 className="report-title">{report.title}</h3>
                <div className="report-meta">
                  <span>{report.date}</span>
                  <span><i className="fas fa-eye"></i> {report.views}</span>
                </div>
              </div>
              <div className="report-content">
                <div className="report-stats">
                  {report.stats.map((stat, index) => (
                    <div key={index} className="report-stat">
                      <div className="stat-number">{stat.value}</div>
                      <div className="stat-label">{stat.label}</div>
                    </div>
                  ))}
                </div>
                <p>{report.description}</p>
                <div className="report-actions">
                  <button 
                    className="btn btn-outline btn-sm"
                    onClick={() => shareReport(report)}
                  >
                    <i className="fas fa-share-alt"></i> Share
                  </button>
                  <button 
                    className="btn btn-primary btn-sm"
                    onClick={() => viewReport(report)}
                  >
                    <i className="fas fa-eye"></i> View Report
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

        @media (max-width: 768px) {
          .page-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 15px;
          }

          .report-grid {
            grid-template-columns: 1fr;
          }

          .filters-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default Reports;
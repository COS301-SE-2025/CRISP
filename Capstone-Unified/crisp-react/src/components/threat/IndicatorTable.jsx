import React, { useState, useEffect } from 'react';

const IndicatorTable = () => {
  const [indicators, setIndicators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  useEffect(() => {
    fetchIndicators();
  }, [filter, searchTerm]);

  const fetchIndicators = async () => {
    try {
      setLoading(true);
      // Mock indicator data - replace with actual API call
      const mockIndicators = [
        {
          id: '1',
          type: 'IP Address',
          value: '192.168.1.100',
          threat_type: 'Command & Control',
          confidence: 'high',
          severity: 'critical',
          source: 'AlienVault OTX',
          created_at: '2025-01-15T14:30:00Z',
          first_seen: '2025-01-14T10:15:00Z',
          last_seen: '2025-01-15T13:45:00Z',
          tags: ['botnet', 'c2', 'malware'],
          description: 'Known command and control server for banking trojan',
          ttps: ['T1071.001', 'T1105'],
          false_positive_score: 0.1
        },
        {
          id: '2',
          type: 'Domain',
          value: 'malicious-site.example.com',
          threat_type: 'Phishing',
          confidence: 'medium',
          severity: 'high',
          source: 'Internal Feed',
          created_at: '2025-01-15T12:20:00Z',
          first_seen: '2025-01-15T08:30:00Z',
          last_seen: '2025-01-15T12:15:00Z',
          tags: ['phishing', 'credential-theft', 'social-engineering'],
          description: 'Phishing domain impersonating major bank login page',
          ttps: ['T1566.002', 'T1539'],
          false_positive_score: 0.2
        },
        {
          id: '3',
          type: 'File Hash',
          value: 'a1b2c3d4e5f6789012345678901234567890abcd',
          threat_type: 'Malware',
          confidence: 'high',
          severity: 'critical',
          source: 'MISP Feed',
          created_at: '2025-01-15T10:10:00Z',
          first_seen: '2025-01-12T14:20:00Z',
          last_seen: '2025-01-15T09:55:00Z',
          tags: ['ransomware', 'encryption', 'persistence'],
          description: 'Ransomware payload with advanced evasion techniques',
          ttps: ['T1486', 'T1027', 'T1547.001'],
          false_positive_score: 0.05
        },
        {
          id: '4',
          type: 'URL',
          value: 'https://suspicious-download.net/payload.exe',
          threat_type: 'Malware Distribution',
          confidence: 'medium',
          severity: 'high',
          source: 'Emerging Threats',
          created_at: '2025-01-15T09:45:00Z',
          first_seen: '2025-01-15T06:30:00Z',
          last_seen: '2025-01-15T09:40:00Z',
          tags: ['dropper', 'payload', 'infection-vector'],
          description: 'Malware distribution site hosting multiple payloads',
          ttps: ['T1105', 'T1027'],
          false_positive_score: 0.15
        },
        {
          id: '5',
          type: 'Email',
          value: 'admin@phishing-bank.com',
          threat_type: 'Phishing',
          confidence: 'high',
          severity: 'medium',
          source: 'Internal Feed',
          created_at: '2025-01-14T16:20:00Z',
          first_seen: '2025-01-14T12:10:00Z',
          last_seen: '2025-01-14T16:15:00Z',
          tags: ['spear-phishing', 'business-email-compromise'],
          description: 'Email address used in targeted phishing campaign',
          ttps: ['T1566.001', 'T1078'],
          false_positive_score: 0.1
        }
      ];

      let filteredIndicators = mockIndicators;
      
      // Apply type filter
      if (filter !== 'all') {
        filteredIndicators = mockIndicators.filter(i => 
          i.type === filter || i.threat_type === filter || i.confidence === filter || i.severity === filter
        );
      }

      // Apply search filter
      if (searchTerm) {
        filteredIndicators = filteredIndicators.filter(i =>
          i.value.toLowerCase().includes(searchTerm.toLowerCase()) ||
          i.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          i.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
        );
      }

      setIndicators(filteredIndicators);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getTypeIcon = (type) => {
    const icons = {
      'IP Address': 'fas fa-globe',
      'Domain': 'fas fa-link',
      'File Hash': 'fas fa-file-alt',
      'URL': 'fas fa-external-link-alt',
      'Email': 'fas fa-envelope'
    };
    return icons[type] || 'fas fa-shield-alt';
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: '#dc3545',
      high: '#fd7e14',
      medium: '#ffc107',
      low: '#28a745'
    };
    return colors[severity] || '#6c757d';
  };

  const getConfidenceColor = (confidence) => {
    const colors = {
      high: '#28a745',
      medium: '#ffc107',
      low: '#fd7e14'
    };
    return colors[confidence] || '#6c757d';
  };

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
    
    const sortedIndicators = [...indicators].sort((a, b) => {
      if (a[key] < b[key]) return direction === 'asc' ? -1 : 1;
      if (a[key] > b[key]) return direction === 'asc' ? 1 : -1;
      return 0;
    });
    
    setIndicators(sortedIndicators);
  };

  // Pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = indicators.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(indicators.length / itemsPerPage);

  if (loading) {
    return (
      <div className="indicator-table">
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading threat indicators...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="indicator-table">
        <div className="error-state">
          <i className="fas fa-exclamation-triangle"></i>
          <p>Error loading indicators: {error}</p>
          <button onClick={fetchIndicators} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="indicator-table">
      <div className="header">
        <h2>Threat Indicators</h2>
        <div className="header-actions">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search indicators..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <i className="fas fa-search"></i>
          </div>
          <button className="btn btn-primary">
            <i className="fas fa-download"></i>
            Export
          </button>
        </div>
      </div>

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-shield-alt"></i>
          </div>
          <div className="stat-content">
            <h3>{indicators.length.toLocaleString()}</h3>
            <p>Total Indicators</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-exclamation-triangle" style={{color: '#dc3545'}}></i>
          </div>
          <div className="stat-content">
            <h3>{indicators.filter(i => i.severity === 'critical').length}</h3>
            <p>Critical Threats</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-eye" style={{color: '#28a745'}}></i>
          </div>
          <div className="stat-content">
            <h3>{indicators.filter(i => i.confidence === 'high').length}</h3>
            <p>High Confidence</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-clock" style={{color: '#ffc107'}}></i>
          </div>
          <div className="stat-content">
            <h3>{indicators.filter(i => {
              const dayAgo = new Date();
              dayAgo.setDate(dayAgo.getDate() - 1);
              return new Date(i.created_at) > dayAgo;
            }).length}</h3>
            <p>Last 24h</p>
          </div>
        </div>
      </div>

      <div className="filters">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All Types
        </button>
        <button
          className={`filter-btn ${filter === 'IP Address' ? 'active' : ''}`}
          onClick={() => setFilter('IP Address')}
        >
          IP Addresses
        </button>
        <button
          className={`filter-btn ${filter === 'Domain' ? 'active' : ''}`}
          onClick={() => setFilter('Domain')}
        >
          Domains
        </button>
        <button
          className={`filter-btn ${filter === 'File Hash' ? 'active' : ''}`}
          onClick={() => setFilter('File Hash')}
        >
          File Hashes
        </button>
        <button
          className={`filter-btn ${filter === 'critical' ? 'active' : ''}`}
          onClick={() => setFilter('critical')}
        >
          Critical Only
        </button>
        <button
          className={`filter-btn ${filter === 'high' ? 'active' : ''}`}
          onClick={() => setFilter('high')}
        >
          High Confidence
        </button>
      </div>

      <div className="table-container">
        <table className="indicators-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('type')}>
                Type
                {sortConfig.key === 'type' && (
                  <i className={`fas fa-sort-${sortConfig.direction === 'asc' ? 'up' : 'down'}`}></i>
                )}
              </th>
              <th onClick={() => handleSort('value')}>
                Indicator Value
                {sortConfig.key === 'value' && (
                  <i className={`fas fa-sort-${sortConfig.direction === 'asc' ? 'up' : 'down'}`}></i>
                )}
              </th>
              <th onClick={() => handleSort('threat_type')}>
                Threat Type
                {sortConfig.key === 'threat_type' && (
                  <i className={`fas fa-sort-${sortConfig.direction === 'asc' ? 'up' : 'down'}`}></i>
                )}
              </th>
              <th onClick={() => handleSort('severity')}>
                Severity
                {sortConfig.key === 'severity' && (
                  <i className={`fas fa-sort-${sortConfig.direction === 'asc' ? 'up' : 'down'}`}></i>
                )}
              </th>
              <th onClick={() => handleSort('confidence')}>
                Confidence
                {sortConfig.key === 'confidence' && (
                  <i className={`fas fa-sort-${sortConfig.direction === 'asc' ? 'up' : 'down'}`}></i>
                )}
              </th>
              <th onClick={() => handleSort('source')}>
                Source
                {sortConfig.key === 'source' && (
                  <i className={`fas fa-sort-${sortConfig.direction === 'asc' ? 'up' : 'down'}`}></i>
                )}
              </th>
              <th onClick={() => handleSort('created_at')}>
                Created
                {sortConfig.key === 'created_at' && (
                  <i className={`fas fa-sort-${sortConfig.direction === 'asc' ? 'up' : 'down'}`}></i>
                )}
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {currentItems.map(indicator => (
              <tr key={indicator.id}>
                <td>
                  <div className="type-cell">
                    <i className={getTypeIcon(indicator.type)}></i>
                    {indicator.type}
                  </div>
                </td>
                <td>
                  <div className="value-cell">
                    <span className="value">{indicator.value}</span>
                    <div className="tags">
                      {indicator.tags.slice(0, 2).map(tag => (
                        <span key={tag} className="tag">{tag}</span>
                      ))}
                      {indicator.tags.length > 2 && (
                        <span className="tag">+{indicator.tags.length - 2}</span>
                      )}
                    </div>
                  </div>
                </td>
                <td>
                  <span className="threat-type">{indicator.threat_type}</span>
                </td>
                <td>
                  <span 
                    className="severity-badge"
                    style={{ backgroundColor: getSeverityColor(indicator.severity) }}
                  >
                    {indicator.severity}
                  </span>
                </td>
                <td>
                  <span 
                    className="confidence-badge"
                    style={{ backgroundColor: getConfidenceColor(indicator.confidence) }}
                  >
                    {indicator.confidence}
                  </span>
                </td>
                <td>
                  <span className="source">{indicator.source}</span>
                </td>
                <td>
                  <span className="date">
                    {new Date(indicator.created_at).toLocaleDateString()}
                  </span>
                  <div className="time">
                    {new Date(indicator.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </div>
                </td>
                <td>
                  <div className="actions">
                    <button className="btn-icon" title="View Details">
                      <i className="fas fa-eye"></i>
                    </button>
                    <button className="btn-icon" title="Block">
                      <i className="fas fa-ban"></i>
                    </button>
                    <button className="btn-icon" title="Export">
                      <i className="fas fa-download"></i>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button 
            className="btn btn-sm btn-outline"
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            <i className="fas fa-chevron-left"></i>
            Previous
          </button>
          
          <div className="page-numbers">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
              <button
                key={page}
                className={`page-btn ${currentPage === page ? 'active' : ''}`}
                onClick={() => setCurrentPage(page)}
              >
                {page}
              </button>
            ))}
          </div>
          
          <button 
            className="btn btn-sm btn-outline"
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            Next
            <i className="fas fa-chevron-right"></i>
          </button>
        </div>
      )}

      <style jsx>{`
        .indicator-table {
          padding: 20px;
          max-width: 1400px;
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

        .header-actions {
          display: flex;
          gap: 15px;
          align-items: center;
        }

        .search-box {
          position: relative;
          display: flex;
          align-items: center;
        }

        .search-input {
          padding: 8px 35px 8px 12px;
          border: 1px solid #dee2e6;
          border-radius: 20px;
          width: 250px;
          font-size: 14px;
        }

        .search-box i {
          position: absolute;
          right: 12px;
          color: #6c757d;
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

        .table-container {
          background: white;
          border-radius: 8px;
          overflow-x: auto;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          margin-bottom: 20px;
        }

        .indicators-table {
          width: 100%;
          border-collapse: collapse;
        }

        .indicators-table th,
        .indicators-table td {
          padding: 12px;
          text-align: left;
          border-bottom: 1px solid #f8f9fa;
        }

        .indicators-table th {
          background: #f8f9fa;
          font-weight: 600;
          color: #495057;
          cursor: pointer;
          user-select: none;
          position: sticky;
          top: 0;
          z-index: 10;
        }

        .indicators-table th:hover {
          background: #e9ecef;
        }

        .indicators-table th i {
          margin-left: 5px;
          opacity: 0.6;
        }

        .type-cell {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .type-cell i {
          color: #0056b3;
        }

        .value-cell .value {
          display: block;
          font-family: monospace;
          font-size: 13px;
          margin-bottom: 4px;
          word-break: break-all;
        }

        .tags {
          display: flex;
          gap: 4px;
          flex-wrap: wrap;
        }

        .tag {
          background: #e3f2fd;
          color: #0056b3;
          padding: 2px 6px;
          border-radius: 10px;
          font-size: 10px;
          font-weight: 500;
        }

        .threat-type {
          font-weight: 500;
          color: #495057;
        }

        .severity-badge,
        .confidence-badge {
          padding: 4px 8px;
          border-radius: 12px;
          color: white;
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
        }

        .source {
          color: #6c757d;
          font-size: 13px;
        }

        .date {
          display: block;
          font-weight: 500;
        }

        .time {
          font-size: 12px;
          color: #6c757d;
        }

        .actions {
          display: flex;
          gap: 5px;
        }

        .btn-icon {
          width: 32px;
          height: 32px;
          border: none;
          background: #f8f9fa;
          color: #6c757d;
          border-radius: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-icon:hover {
          background: #e9ecef;
          color: #495057;
        }

        .pagination {
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 15px;
        }

        .page-numbers {
          display: flex;
          gap: 5px;
        }

        .page-btn {
          width: 36px;
          height: 36px;
          border: 1px solid #dee2e6;
          background: white;
          color: #6c757d;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .page-btn:hover {
          background: #f8f9fa;
        }

        .page-btn.active {
          background: #0056b3;
          color: white;
          border-color: #0056b3;
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
        }

        .btn-primary {
          background: #0056b3;
          color: white;
        }

        .btn-outline {
          background: transparent;
          border: 1px solid #dee2e6;
          color: #495057;
        }

        .btn-outline:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn-sm {
          padding: 6px 12px;
          font-size: 12px;
        }

        .empty-state,
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

export default IndicatorTable;
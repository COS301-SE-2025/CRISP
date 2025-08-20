import React, { useState, useEffect } from 'react';

const UnifiedDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    fetchDashboardData();
  }, [timeRange]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // Mock unified dashboard data - replace with actual API calls
      const mockData = {
        user_stats: {
          total_users: 247,
          active_users: 189,
          new_users_today: 12,
          organizations: 23,
          trust_relationships: 45
        },
        threat_stats: {
          total_indicators: 15432,
          new_indicators_today: 324,
          active_feeds: 8,
          blocked_threats: 156,
          critical_alerts: 3
        },
        recent_threats: [
          {
            id: '1',
            type: 'IP Address',
            value: '192.168.1.100',
            threat_type: 'Command & Control',
            severity: 'critical',
            source: 'AlienVault OTX',
            detected_at: '2025-01-15T14:30:00Z'
          },
          {
            id: '2',
            type: 'Domain',
            value: 'malicious-site.example.com',
            threat_type: 'Phishing',
            severity: 'high',
            source: 'Internal Feed',
            detected_at: '2025-01-15T13:45:00Z'
          },
          {
            id: '3',
            type: 'File Hash',
            value: 'a1b2c3d4e5f6789012345678901234567890abcd',
            threat_type: 'Malware',
            severity: 'critical',
            source: 'MISP Feed',
            detected_at: '2025-01-15T12:20:00Z'
          }
        ],
        recent_activities: [
          {
            id: '1',
            type: 'user_login',
            user: 'john.doe@company.com',
            action: 'logged in from 203.0.113.45',
            timestamp: '2025-01-15T14:35:00Z',
            status: 'success'
          },
          {
            id: '2',
            type: 'feed_update',
            user: 'system',
            action: 'AlienVault OTX feed updated with 156 new indicators',
            timestamp: '2025-01-15T14:30:00Z',
            status: 'success'
          },
          {
            id: '3',
            type: 'trust_relationship',
            user: 'admin@bluevision.com',
            action: 'approved trust relationship with University XYZ',
            timestamp: '2025-01-15T14:15:00Z',
            status: 'success'
          },
          {
            id: '4',
            type: 'security_alert',
            user: 'security-system',
            action: 'blocked access attempt from suspicious IP 198.51.100.33',
            timestamp: '2025-01-15T14:00:00Z',
            status: 'blocked'
          }
        ],
        feed_status: [
          { name: 'AlienVault OTX', status: 'active', last_update: '5 min ago', indicators: 15432 },
          { name: 'MISP Feed', status: 'active', last_update: '12 min ago', indicators: 8921 },
          { name: 'Internal Feed', status: 'active', last_update: '2 min ago', indicators: 2145 },
          { name: 'Emerging Threats', status: 'pending', last_update: '2 hours ago', indicators: 0 }
        ],
        organization_metrics: {
          top_organizations: [
            { name: 'BlueVision Corp', users: 45, indicators_shared: 234, trust_score: 98 },
            { name: 'University ABC', users: 23, indicators_shared: 156, trust_score: 87 },
            { name: 'TechSecure Ltd', users: 18, indicators_shared: 89, trust_score: 92 },
            { name: 'CyberDefense Inc', users: 31, indicators_shared: 145, trust_score: 85 }
          ]
        },
        system_health: {
          api_response_time: 245,
          database_connections: 23,
          active_sessions: 156,
          memory_usage: 67,
          cpu_usage: 34
        }
      };

      setDashboardData(mockData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type) => {
    const icons = {
      user_login: 'fas fa-sign-in-alt',
      feed_update: 'fas fa-rss',
      trust_relationship: 'fas fa-handshake',
      security_alert: 'fas fa-shield-alt',
      system_event: 'fas fa-cog'
    };
    return icons[type] || 'fas fa-info-circle';
  };

  const getActivityColor = (status) => {
    const colors = {
      success: '#28a745',
      warning: '#ffc107',
      error: '#dc3545',
      blocked: '#fd7e14',
      pending: '#6c757d'
    };
    return colors[status] || '#6c757d';
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

  const getHealthStatus = (value, type) => {
    if (type === 'response_time') {
      if (value < 200) return { color: '#28a745', status: 'excellent' };
      if (value < 500) return { color: '#ffc107', status: 'good' };
      return { color: '#dc3545', status: 'poor' };
    }
    if (type === 'usage') {
      if (value < 50) return { color: '#28a745', status: 'low' };
      if (value < 80) return { color: '#ffc107', status: 'moderate' };
      return { color: '#dc3545', status: 'high' };
    }
    return { color: '#6c757d', status: 'unknown' };
  };

  if (loading) {
    return (
      <div className="unified-dashboard">
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="unified-dashboard">
        <div className="error-state">
          <i className="fas fa-exclamation-triangle"></i>
          <p>Error loading dashboard: {error}</p>
          <button onClick={fetchDashboardData} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="unified-dashboard">
      <div className="dashboard-header">
        <div className="header-info">
          <h1>CRISP Dashboard</h1>
          <p>Cyber Risk Information Sharing Platform - Unified View</p>
        </div>
        <div className="time-range-selector">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-select"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
        </div>
      </div>

      {/* Key Metrics Row */}
      <div className="metrics-grid">
        <div className="metric-card user-metrics">
          <div className="metric-header">
            <h3>User Management</h3>
            <i className="fas fa-users"></i>
          </div>
          <div className="metric-stats">
            <div className="stat">
              <span className="stat-value">{dashboardData.user_stats.total_users}</span>
              <span className="stat-label">Total Users</span>
            </div>
            <div className="stat">
              <span className="stat-value">{dashboardData.user_stats.active_users}</span>
              <span className="stat-label">Active Users</span>
            </div>
            <div className="stat">
              <span className="stat-value">{dashboardData.user_stats.organizations}</span>
              <span className="stat-label">Organizations</span>
            </div>
            <div className="stat">
              <span className="stat-value">{dashboardData.user_stats.trust_relationships}</span>
              <span className="stat-label">Trust Links</span>
            </div>
          </div>
        </div>

        <div className="metric-card threat-metrics">
          <div className="metric-header">
            <h3>Threat Intelligence</h3>
            <i className="fas fa-shield-alt"></i>
          </div>
          <div className="metric-stats">
            <div className="stat">
              <span className="stat-value">{dashboardData.threat_stats.total_indicators.toLocaleString()}</span>
              <span className="stat-label">Total Indicators</span>
            </div>
            <div className="stat">
              <span className="stat-value">{dashboardData.threat_stats.new_indicators_today}</span>
              <span className="stat-label">New Today</span>
            </div>
            <div className="stat">
              <span className="stat-value">{dashboardData.threat_stats.active_feeds}</span>
              <span className="stat-label">Active Feeds</span>
            </div>
            <div className="stat">
              <span className="stat-value critical">{dashboardData.threat_stats.critical_alerts}</span>
              <span className="stat-label">Critical Alerts</span>
            </div>
          </div>
        </div>

        <div className="metric-card system-health">
          <div className="metric-header">
            <h3>System Health</h3>
            <i className="fas fa-heartbeat"></i>
          </div>
          <div className="health-indicators">
            <div className="health-item">
              <span className="health-label">API Response</span>
              <span 
                className="health-value"
                style={{ color: getHealthStatus(dashboardData.system_health.api_response_time, 'response_time').color }}
              >
                {dashboardData.system_health.api_response_time}ms
              </span>
            </div>
            <div className="health-item">
              <span className="health-label">Memory Usage</span>
              <span 
                className="health-value"
                style={{ color: getHealthStatus(dashboardData.system_health.memory_usage, 'usage').color }}
              >
                {dashboardData.system_health.memory_usage}%
              </span>
            </div>
            <div className="health-item">
              <span className="health-label">Active Sessions</span>
              <span className="health-value">{dashboardData.system_health.active_sessions}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="content-grid">
        {/* Recent Threats */}
        <div className="dashboard-card recent-threats">
          <div className="card-header">
            <h3>Recent Threats</h3>
            <button className="btn btn-sm btn-outline">View All</button>
          </div>
          <div className="threats-list">
            {dashboardData.recent_threats.map(threat => (
              <div key={threat.id} className="threat-item">
                <div className="threat-info">
                  <span className="threat-value">{threat.value}</span>
                  <span className="threat-type">{threat.threat_type}</span>
                </div>
                <div className="threat-meta">
                  <span 
                    className="severity-badge"
                    style={{ backgroundColor: getSeverityColor(threat.severity) }}
                  >
                    {threat.severity}
                  </span>
                  <span className="threat-source">{threat.source}</span>
                  <span className="threat-time">
                    {new Date(threat.detected_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Feed Status */}
        <div className="dashboard-card feed-status">
          <div className="card-header">
            <h3>Threat Feeds Status</h3>
            <button className="btn btn-sm btn-outline">Manage Feeds</button>
          </div>
          <div className="feeds-list">
            {dashboardData.feed_status.map((feed, index) => (
              <div key={index} className="feed-item">
                <div className="feed-info">
                  <span className="feed-name">{feed.name}</span>
                  <span className="feed-indicators">{feed.indicators.toLocaleString()} indicators</span>
                </div>
                <div className="feed-meta">
                  <span 
                    className="feed-status-badge"
                    style={{ 
                      backgroundColor: feed.status === 'active' ? '#28a745' : 
                                     feed.status === 'pending' ? '#ffc107' : '#dc3545' 
                    }}
                  >
                    {feed.status}
                  </span>
                  <span className="feed-update">{feed.last_update}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activities */}
        <div className="dashboard-card recent-activities">
          <div className="card-header">
            <h3>Recent Activities</h3>
            <button className="btn btn-sm btn-outline">View Logs</button>
          </div>
          <div className="activities-list">
            {dashboardData.recent_activities.map(activity => (
              <div key={activity.id} className="activity-item">
                <div className="activity-icon">
                  <i 
                    className={getActivityIcon(activity.type)}
                    style={{ color: getActivityColor(activity.status) }}
                  ></i>
                </div>
                <div className="activity-content">
                  <div className="activity-user">{activity.user}</div>
                  <div className="activity-action">{activity.action}</div>
                  <div className="activity-time">
                    {new Date(activity.timestamp).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Organizations */}
        <div className="dashboard-card top-organizations">
          <div className="card-header">
            <h3>Top Organizations</h3>
            <button className="btn btn-sm btn-outline">View All</button>
          </div>
          <div className="organizations-list">
            {dashboardData.organization_metrics.top_organizations.map((org, index) => (
              <div key={index} className="org-item">
                <div className="org-rank">#{index + 1}</div>
                <div className="org-info">
                  <div className="org-name">{org.name}</div>
                  <div className="org-stats">
                    {org.users} users • {org.indicators_shared} indicators shared
                  </div>
                </div>
                <div className="org-trust-score">
                  <div className="trust-score">{org.trust_score}</div>
                  <div className="trust-label">Trust Score</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <style jsx>{`
        .unified-dashboard {
          padding: 20px;
          max-width: 1400px;
          margin: 0 auto;
          background: #f8f9fa;
          min-height: 100vh;
        }

        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
          background: white;
          padding: 20px;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .header-info h1 {
          margin: 0 0 5px 0;
          color: #333;
          font-size: 28px;
        }

        .header-info p {
          margin: 0;
          color: #6c757d;
          font-size: 16px;
        }

        .time-select {
          padding: 8px 12px;
          border: 1px solid #dee2e6;
          border-radius: 6px;
          background: white;
          font-size: 14px;
          cursor: pointer;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }

        .metric-card {
          background: white;
          border-radius: 12px;
          padding: 24px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .metric-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .metric-header h3 {
          margin: 0;
          color: #333;
          font-size: 18px;
        }

        .metric-header i {
          font-size: 24px;
          opacity: 0.3;
        }

        .user-metrics .metric-header i { color: #007bff; }
        .threat-metrics .metric-header i { color: #dc3545; }
        .system-health .metric-header i { color: #28a745; }

        .metric-stats {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 15px;
        }

        .stat {
          text-align: center;
        }

        .stat-value {
          display: block;
          font-size: 24px;
          font-weight: 700;
          color: #333;
          margin-bottom: 5px;
        }

        .stat-value.critical {
          color: #dc3545;
        }

        .stat-label {
          font-size: 12px;
          color: #6c757d;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .health-indicators {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .health-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .health-label {
          font-size: 14px;
          color: #6c757d;
        }

        .health-value {
          font-weight: 600;
          font-size: 14px;
        }

        .content-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 20px;
        }

        .dashboard-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          overflow: hidden;
        }

        .card-header {
          padding: 20px;
          border-bottom: 1px solid #f8f9fa;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .card-header h3 {
          margin: 0;
          color: #333;
          font-size: 18px;
        }

        .threats-list,
        .feeds-list,
        .activities-list,
        .organizations-list {
          padding: 0;
        }

        .threat-item,
        .feed-item,
        .activity-item,
        .org-item {
          padding: 16px 20px;
          border-bottom: 1px solid #f8f9fa;
          transition: background-color 0.2s;
        }

        .threat-item:hover,
        .feed-item:hover,
        .activity-item:hover,
        .org-item:hover {
          background: #f8f9fa;
        }

        .threat-item:last-child,
        .feed-item:last-child,
        .activity-item:last-child,
        .org-item:last-child {
          border-bottom: none;
        }

        .threat-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .threat-value {
          font-family: monospace;
          font-weight: 600;
          color: #333;
          display: block;
          margin-bottom: 4px;
        }

        .threat-type {
          font-size: 13px;
          color: #6c757d;
        }

        .threat-meta {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .severity-badge,
        .feed-status-badge {
          padding: 2px 8px;
          border-radius: 10px;
          color: white;
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
        }

        .threat-source,
        .threat-time {
          font-size: 12px;
          color: #6c757d;
        }

        .feed-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .feed-name {
          font-weight: 600;
          color: #333;
          display: block;
          margin-bottom: 4px;
        }

        .feed-indicators {
          font-size: 13px;
          color: #6c757d;
        }

        .feed-meta {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .feed-update {
          font-size: 12px;
          color: #6c757d;
        }

        .activity-item {
          display: flex;
          align-items: flex-start;
          gap: 15px;
        }

        .activity-icon {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: #f8f9fa;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .activity-user {
          font-weight: 600;
          color: #333;
          font-size: 14px;
          margin-bottom: 4px;
        }

        .activity-action {
          color: #495057;
          font-size: 14px;
          line-height: 1.4;
          margin-bottom: 4px;
        }

        .activity-time {
          font-size: 12px;
          color: #6c757d;
        }

        .org-item {
          display: flex;
          align-items: center;
          gap: 15px;
        }

        .org-rank {
          width: 32px;
          height: 32px;
          background: #0056b3;
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 14px;
        }

        .org-info {
          flex: 1;
        }

        .org-name {
          font-weight: 600;
          color: #333;
          margin-bottom: 4px;
        }

        .org-stats {
          font-size: 13px;
          color: #6c757d;
        }

        .org-trust-score {
          text-align: center;
        }

        .trust-score {
          font-size: 20px;
          font-weight: 700;
          color: #28a745;
        }

        .trust-label {
          font-size: 11px;
          color: #6c757d;
          text-transform: uppercase;
        }

        .btn {
          padding: 6px 12px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          text-decoration: none;
          transition: all 0.2s;
        }

        .btn-primary {
          background: #0056b3;
          color: white;
        }

        .btn-outline {
          background: transparent;
          border: 1px solid #dee2e6;
          color: #6c757d;
        }

        .btn-outline:hover {
          background: #f8f9fa;
        }

        .btn-sm {
          padding: 4px 8px;
          font-size: 11px;
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

export default UnifiedDashboard;
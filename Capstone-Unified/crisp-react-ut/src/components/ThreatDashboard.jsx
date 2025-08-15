import React, { useState, useEffect, useMemo } from 'react';
import LoadingSpinner from './LoadingSpinner.jsx';

const ThreatDashboard = ({ active = true, userRole, userOrganization, onNavigate }) => {
  console.log('ThreatDashboard rendered with props:', { active, userRole, userOrganization });
  
  // States following existing patterns
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [recentIndicators, setRecentIndicators] = useState([]);
  const [activeThreatFeeds, setActiveThreatFeeds] = useState([]);

  // Permission checks following existing patterns
  const isAdmin = userRole === 'admin' || userRole === 'BlueVisionAdmin';
  const isPublisher = userRole === 'publisher' || isAdmin;
  const isViewer = userRole === 'viewer';

  // Time range options
  const timeRangeOptions = [
    { value: '24h', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' }
  ];

  useEffect(() => {
    if (active) {
      loadDashboardData();
    }
  }, [active, selectedTimeRange]);

  const loadDashboardData = async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError(null);
    
    try {
      const token = localStorage.getItem('crisp_auth_token');
      
      // Load dashboard overview data
      const dashboardResponse = await fetch(`http://localhost:8000/api/v1/dashboard/overview/?timerange=${selectedTimeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!dashboardResponse.ok) {
        throw new Error(`HTTP ${dashboardResponse.status}: Failed to fetch dashboard data`);
      }

      const dashboardResult = await dashboardResponse.json();
      console.log('Dashboard data loaded:', dashboardResult);
      
      // Handle response format from unified API
      const data = dashboardResult.data || dashboardResult;
      setDashboardData(data);

      // Load recent indicators
      if (data.threat_intelligence?.recent_indicators) {
        setRecentIndicators(data.threat_intelligence.recent_indicators.slice(0, 10));
      }

      // Load active threat feeds
      if (data.threat_intelligence?.active_feeds) {
        setActiveThreatFeeds(data.threat_intelligence.active_feeds.slice(0, 5));
      }

    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError(err.message || 'Failed to load dashboard data');
      
      // Set fallback data for demonstration
      setDashboardData({
        threat_intelligence: {
          total_feeds: 0,
          active_feeds: 0,
          total_indicators: 0,
          total_ttps: 0,
          recent_indicators: 0
        },
        organization: userOrganization ? {
          has_organization: true,
          name: userOrganization.name,
          id: userOrganization.id
        } : { has_organization: false },
        user_info: {
          role: userRole,
          permissions: {
            can_view_feeds: true,
            can_manage_feeds: isPublisher,
            can_admin: isAdmin
          }
        }
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    loadDashboardData(true);
  };

  const getTimeRangeLabel = () => {
    const option = timeRangeOptions.find(opt => opt.value === selectedTimeRange);
    return option ? option.label : 'Last 7 Days';
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  // Don't render if not active
  if (!active) return null;

  if (loading) {
    return <LoadingSpinner message="Loading threat intelligence dashboard..." />;
  }

  const threatIntel = dashboardData?.threat_intelligence || {};
  const orgInfo = dashboardData?.organization || {};
  const userInfo = dashboardData?.user_info || {};

  return (
    <div className="threat-dashboard-container">
      {/* Header */}
      <div className="page-header">
        <div className="page-title-section">
          <h1 className="page-title">
            <i className="fas fa-chart-line"></i>
            Threat Intelligence Dashboard
          </h1>
          <p className="page-subtitle">
            Overview of threat intelligence data and recent activity
            {orgInfo.has_organization && ` for ${orgInfo.name}`}
          </p>
        </div>
        
        <div className="page-actions">
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="time-range-select"
          >
            {timeRangeOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          
          <button 
            className="btn btn-outline"
            onClick={handleRefresh}
            disabled={refreshing}
            title="Refresh data"
          >
            <i className={`fas fa-sync-alt ${refreshing ? 'fa-spin' : ''}`}></i>
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <i className="fas fa-exclamation-triangle"></i>
          <span>Some dashboard data may be unavailable: {error}</span>
          <button className="btn btn-small" onClick={handleRefresh}>
            Retry
          </button>
        </div>
      )}

      {/* Statistics Overview */}
      <div className="dashboard-stats">
        <div className="stat-card primary">
          <div className="stat-icon">
            <i className="fas fa-rss"></i>
          </div>
          <div className="stat-content">
            <h3>{formatNumber(threatIntel.total_feeds)}</h3>
            <p>Total Threat Feeds</p>
            <span className="stat-detail">
              {threatIntel.active_feeds || 0} active
            </span>
          </div>
          <div className="stat-action">
            <button 
              className="btn btn-icon"
              onClick={() => onNavigate && onNavigate('threat-feeds')}
              title="View all feeds"
            >
              <i className="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>

        <div className="stat-card success">
          <div className="stat-icon">
            <i className="fas fa-search"></i>
          </div>
          <div className="stat-content">
            <h3>{formatNumber(threatIntel.total_indicators)}</h3>
            <p>Threat Indicators</p>
            <span className="stat-detail">
              {getTimeRangeLabel()}
            </span>
          </div>
          <div className="stat-action">
            <button 
              className="btn btn-icon"
              onClick={() => onNavigate && onNavigate('ioc-management')}
              title="View indicators"
            >
              <i className="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>

        <div className="stat-card warning">
          <div className="stat-icon">
            <i className="fas fa-sitemap"></i>
          </div>
          <div className="stat-content">
            <h3>{formatNumber(threatIntel.total_ttps)}</h3>
            <p>TTPs</p>
            <span className="stat-detail">
              Tactics, Techniques & Procedures
            </span>
          </div>
          <div className="stat-action">
            <button 
              className="btn btn-icon"
              onClick={() => onNavigate && onNavigate('ttp-analysis')}
              title="View TTPs"
            >
              <i className="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>

        <div className="stat-card info">
          <div className="stat-icon">
            <i className="fas fa-clock"></i>
          </div>
          <div className="stat-content">
            <h3>{formatNumber(threatIntel.recent_indicators)}</h3>
            <p>Recent Activity</p>
            <span className="stat-detail">
              New indicators today
            </span>
          </div>
        </div>
      </div>

      {/* Main Dashboard Content */}
      <div className="dashboard-content">
        {/* Recent Indicators */}
        <div className="dashboard-section">
          <div className="section-header">
            <h2>
              <i className="fas fa-clock"></i>
              Recent Indicators
            </h2>
            <button 
              className="btn btn-outline btn-small"
              onClick={() => onNavigate && onNavigate('ioc-management')}
            >
              View All
            </button>
          </div>
          
          <div className="indicators-list">
            {recentIndicators.length > 0 ? (
              recentIndicators.map((indicator, index) => (
                <div key={index} className="indicator-item">
                  <div className="indicator-icon">
                    <i className="fas fa-exclamation-triangle"></i>
                  </div>
                  <div className="indicator-content">
                    <div className="indicator-pattern">
                      {indicator.pattern || 'Unknown pattern'}
                    </div>
                    <div className="indicator-meta">
                      <span className="indicator-type">
                        {indicator.indicator_type?.replace(/-/g, ' ') || 'Unknown'}
                      </span>
                      <span className="indicator-time">
                        {indicator.created ? new Date(indicator.created).toLocaleDateString() : 'Unknown date'}
                      </span>
                    </div>
                  </div>
                  <div className={`confidence-badge ${
                    indicator.confidence >= 75 ? 'high' : 
                    indicator.confidence >= 50 ? 'medium' : 'low'
                  }`}>
                    {indicator.confidence || 0}%
                  </div>
                </div>
              ))
            ) : (
              <div className="no-data">
                <i className="fas fa-info-circle"></i>
                <p>No recent indicators available</p>
              </div>
            )}
          </div>
        </div>

        {/* Active Threat Feeds */}
        <div className="dashboard-section">
          <div className="section-header">
            <h2>
              <i className="fas fa-rss"></i>
              Active Threat Feeds
            </h2>
            <button 
              className="btn btn-outline btn-small"
              onClick={() => onNavigate && onNavigate('threat-feeds')}
            >
              Manage Feeds
            </button>
          </div>
          
          <div className="feeds-list">
            {activeThreatFeeds.length > 0 ? (
              activeThreatFeeds.map((feed, index) => (
                <div key={index} className="feed-item">
                  <div className="feed-icon">
                    <i className="fas fa-rss"></i>
                  </div>
                  <div className="feed-content">
                    <div className="feed-name">
                      {feed.name || 'Unnamed Feed'}
                    </div>
                    <div className="feed-meta">
                      <span className="feed-type">
                        {feed.is_external ? 'External' : 'Internal'}
                      </span>
                      <span className="feed-sync">
                        Last sync: {feed.last_sync ? 
                          new Date(feed.last_sync).toLocaleDateString() : 
                          'Never'
                        }
                      </span>
                    </div>
                  </div>
                  <div className="feed-stats">
                    <span className="indicator-count">
                      {feed.indicator_count || 0} indicators
                    </span>
                  </div>
                  <div className="feed-status">
                    <span className={`status-badge ${feed.is_active ? 'active' : 'inactive'}`}>
                      {feed.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-data">
                <i className="fas fa-info-circle"></i>
                <p>No active threat feeds</p>
                {isPublisher && (
                  <button 
                    className="btn btn-primary btn-small"
                    onClick={() => onNavigate && onNavigate('threat-feeds')}
                  >
                    Add Feed
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="dashboard-actions">
        <div className="actions-header">
          <h2>
            <i className="fas fa-bolt"></i>
            Quick Actions
          </h2>
        </div>
        
        <div className="actions-grid">
          <button 
            className="action-card"
            onClick={() => onNavigate && onNavigate('threat-feeds')}
          >
            <i className="fas fa-rss"></i>
            <span>Browse Threat Feeds</span>
          </button>
          
          <button 
            className="action-card"
            onClick={() => onNavigate && onNavigate('ioc-management')}
          >
            <i className="fas fa-search"></i>
            <span>Search Indicators</span>
          </button>
          
          {isPublisher && (
            <>
              <button 
                className="action-card"
                onClick={() => onNavigate && onNavigate('add-threat-feed')}
              >
                <i className="fas fa-plus"></i>
                <span>Add New Feed</span>
              </button>
              
              <button 
                className="action-card"
                onClick={() => onNavigate && onNavigate('reports')}
              >
                <i className="fas fa-file-alt"></i>
                <span>Generate Report</span>
              </button>
            </>
          )}
          
          <button 
            className="action-card"
            onClick={() => onNavigate && onNavigate('ttp-analysis')}
          >
            <i className="fas fa-sitemap"></i>
            <span>Analyze TTPs</span>
          </button>
          
          {isAdmin && (
            <button 
              className="action-card"
              onClick={() => onNavigate && onNavigate('admin-settings')}
            >
              <i className="fas fa-cog"></i>
              <span>System Settings</span>
            </button>
          )}
        </div>
      </div>

      {/* Organization Info */}
      {orgInfo.has_organization && (
        <div className="organization-info">
          <div className="org-header">
            <i className="fas fa-building"></i>
            <h3>{orgInfo.name}</h3>
          </div>
          <div className="org-details">
            <span className="org-role">Your role: <strong>{userRole}</strong></span>
            {orgInfo.domain && (
              <span className="org-domain">Domain: {orgInfo.domain}</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ThreatDashboard;
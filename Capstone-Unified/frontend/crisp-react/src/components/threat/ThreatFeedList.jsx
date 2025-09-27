import React, { useState, useEffect, useCallback } from 'react';
import { getThreatFeeds, consumeThreatFeed } from '../../api.js';
import refreshManager from '../../utils/RefreshManager.js';

const ThreatFeedList = () => {
  const [feeds, setFeeds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [showSubscribeModal, setShowSubscribeModal] = useState(false);
  const [consumingFeeds, setConsumingFeeds] = useState(new Set());
  const [pollIntervalId, setPollIntervalId] = useState(null);
  const [previousFeedStates, setPreviousFeedStates] = useState(new Map());

  // Memoize fetchFeeds to prevent infinite re-renders
  const fetchFeeds = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getThreatFeeds();
      const threatFeeds = response.results || response || [];

      // Apply filters to the real data
      let filteredFeeds = threatFeeds;
      if (filter !== 'all') {
        filteredFeeds = threatFeeds.filter(f => {
          if (filter === 'subscribed') return f.is_external;
          if (filter === 'available') return !f.is_external;
          return f.consumption_status === filter || f.taxii_server_url?.includes(filter);
        });
      }

      setFeeds(filteredFeeds);

      // Check for status changes and show notifications
      filteredFeeds.forEach(feed => {
        const previousState = previousFeedStates.get(feed.id);
        const currentStatus = feed.consumption_status || 'idle';

        if (previousState && previousState !== currentStatus) {
          if (previousState === 'running' && (currentStatus === 'completed' || currentStatus === 'idle')) {
            // Feed completed successfully
            showCompletionNotification(feed);
          } else if (previousState === 'running' && currentStatus === 'error') {
            // Feed failed
            showErrorNotification(feed);
          }
        }
      });

      // Update previous states for next comparison
      const newStates = new Map();
      filteredFeeds.forEach(feed => {
        newStates.set(feed.id, feed.consumption_status || 'idle');
      });
      setPreviousFeedStates(newStates);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filter, previousFeedStates]);

  useEffect(() => {
    fetchFeeds();
  }, [fetchFeeds]);

  // Subscribe to RefreshManager for automatic updates
  useEffect(() => {
    refreshManager.subscribe('threat-feeds', fetchFeeds, {
      backgroundRefresh: true,
      isVisible: () => true // This component is visible when mounted
    });

    console.log('🔄 ThreatFeedList: Subscribed to RefreshManager');

    return () => {
      refreshManager.unsubscribe('threat-feeds');
      console.log('🔄 ThreatFeedList: Unsubscribed from RefreshManager');
    };
  }, [fetchFeeds]);

  // Smart polling only when needed - much less aggressive
  useEffect(() => {
    if (consumingFeeds.size > 0) {
      // Only poll while we have locally tracked consuming feeds
      const intervalId = setInterval(() => {
        console.log('🔄 Checking status for locally tracked consuming feeds');
        fetchFeeds();
      }, 30000); // Reduce to 30 seconds to prevent performance issues

      setPollIntervalId(intervalId);

      return () => {
        clearInterval(intervalId);
        setPollIntervalId(null);
      };
    } else if (pollIntervalId) {
      // Stop polling when no local feeds are consuming
      clearInterval(pollIntervalId);
      setPollIntervalId(null);
    }
  }, [consumingFeeds, fetchFeeds]); // Removed feeds dependency to prevent constant polling

  // Notification functions
  const showCompletionNotification = (feed) => {
    console.log(`✅ Feed consumption completed: ${feed.name}`);

    // Create a browser notification if possible
    if (Notification.permission === 'granted') {
      new Notification('Threat Feed Consumption Complete', {
        body: `Feed "${feed.name}" has finished consuming`,
        icon: '/favicon.ico'
      });
    }

    // Also show an in-page notification (you can customize this)
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed; top: 20px; right: 20px; z-index: 10000;
      background: #28a745; color: white; padding: 15px 20px;
      border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      max-width: 300px; animation: slideIn 0.3s ease-out;
    `;
    notification.innerHTML = `
      <div style="display: flex; align-items: center; gap: 10px;">
        <i class="fas fa-check-circle" style="font-size: 18px;"></i>
        <div>
          <strong>Feed Consumption Complete</strong><br>
          <small>${feed.name}</small>
        </div>
      </div>
    `;

    document.body.appendChild(notification);
    setTimeout(() => {
      notification.remove();
    }, 5000);
  };

  const showErrorNotification = (feed) => {
    console.log(`❌ Feed consumption failed: ${feed.name}`);

    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed; top: 20px; right: 20px; z-index: 10000;
      background: #dc3545; color: white; padding: 15px 20px;
      border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      max-width: 300px;
    `;
    notification.innerHTML = `
      <div style="display: flex; align-items: center; gap: 10px;">
        <i class="fas fa-exclamation-circle" style="font-size: 18px;"></i>
        <div>
          <strong>Feed Consumption Failed</strong><br>
          <small>${feed.name}</small>
        </div>
      </div>
    `;

    document.body.appendChild(notification);
    setTimeout(() => {
      notification.remove();
    }, 7000);
  };

  // Request notification permission on component mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const getStatusIcon = (status) => {
    const icons = {
      active: 'fas fa-check-circle',
      pending: 'fas fa-clock',
      error: 'fas fa-exclamation-circle',
      disabled: 'fas fa-pause-circle'
    };
    return icons[status] || 'fas fa-question-circle';
  };

  const getStatusColor = (status) => {
    const colors = {
      active: '#28a745',
      pending: '#ffc107',
      error: '#dc3545',
      disabled: '#6c757d'
    };
    return colors[status] || '#6c757d';
  };

  const getTrustLevelColor = (level) => {
    const colors = {
      high: '#28a745',
      medium: '#ffc107',
      low: '#fd7e14'
    };
    return colors[level] || '#6c757d';
  };

  const toggleSubscription = (feedId) => {
    setFeeds(prev => prev.map(f =>
      f.id === feedId ? { ...f, subscribed: !f.subscribed } : f
    ));
  };

  const handleConsumeFeed = async (feedId) => {
    try {
      setConsumingFeeds(prev => new Set(prev).add(feedId));
      console.log(`🔄 Starting consumption for feed ${feedId}`);

      const result = await consumeThreatFeed(feedId, {
        limit: 10,
        batch_size: 100
      });

      console.log('Feed consumption result:', result);

      // Trigger refresh for related components
      refreshManager.triggerRelated('threat-feeds', 'feed_consumption_completed');

      // Also immediately refresh this component
      setTimeout(() => {
        fetchFeeds();
      }, 1000);

    } catch (error) {
      console.error('Feed consumption error:', error);
      setError(`Failed to consume feed: ${error.message}`);
    } finally {
      setConsumingFeeds(prev => {
        const newSet = new Set(prev);
        newSet.delete(feedId);
        return newSet;
      });
    }
  };

  if (loading) {
    return (
      <div className="threat-feeds">
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading threat feeds...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="threat-feeds">
        <div className="error-state">
          <i className="fas fa-exclamation-triangle"></i>
          <p>Error loading threat feeds: {error}</p>
          <button onClick={fetchFeeds} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="threat-feeds">
      <div className="header">
        <h2>Threat Intelligence Feeds</h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowSubscribeModal(true)}
        >
          <i className="fas fa-plus"></i>
          Subscribe to Feed
        </button>
      </div>

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-rss"></i>
          </div>
          <div className="stat-content">
            <h3>{feeds.filter(f => f.subscribed).length}</h3>
            <p>Subscribed Feeds</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-shield-alt"></i>
          </div>
          <div className="stat-content">
            <h3>{feeds.reduce((sum, f) => sum + f.indicators_count, 0).toLocaleString()}</h3>
            <p>Total Indicators</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-check-circle" style={{color: '#28a745'}}></i>
          </div>
          <div className="stat-content">
            <h3>{feeds.filter(f => f.status === 'active').length}</h3>
            <p>Active Feeds</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-clock" style={{color: '#ffc107'}}></i>
          </div>
          <div className="stat-content">
            <h3>{feeds.filter(f => f.status === 'pending').length}</h3>
            <p>Pending Setup</p>
          </div>
        </div>
      </div>

      <div className="filters">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All Feeds
        </button>
        <button
          className={`filter-btn ${filter === 'subscribed' ? 'active' : ''}`}
          onClick={() => setFilter('subscribed')}
        >
          Subscribed
        </button>
        <button
          className={`filter-btn ${filter === 'available' ? 'active' : ''}`}
          onClick={() => setFilter('available')}
        >
          Available
        </button>
        <button
          className={`filter-btn ${filter === 'STIX/TAXII' ? 'active' : ''}`}
          onClick={() => setFilter('STIX/TAXII')}
        >
          STIX/TAXII
        </button>
        <button
          className={`filter-btn ${filter === 'MISP' ? 'active' : ''}`}
          onClick={() => setFilter('MISP')}
        >
          MISP
        </button>
      </div>

      <div className="feeds-list">
        {feeds.length === 0 ? (
          <div className="empty-state">
            <i className="fas fa-rss"></i>
            <h3>No threat feeds found</h3>
            <p>Subscribe to threat intelligence feeds to start receiving indicators.</p>
            <button 
              className="btn btn-primary"
              onClick={() => setShowSubscribeModal(true)}
            >
              <i className="fas fa-plus"></i>
              Subscribe to Feed
            </button>
          </div>
        ) : (
          feeds.map(feed => (
            <div key={feed.id} className="feed-card">
              <div className="feed-header">
                <div className="feed-info">
                  <div className="feed-title">
                    <h3>{feed.name}</h3>
                    <div className="feed-badges">
                      <span className="type-badge">{feed.is_external ? 'External' : 'Internal'}</span>
                      <span
                        className="trust-badge"
                        style={{ backgroundColor: getTrustLevelColor('medium') }}
                      >
                        {feed.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                  <p className="feed-description">{feed.description || 'No description available'}</p>
                  <div className="feed-details">
                    <span className="detail-item">
                      <i className="fas fa-building"></i>
                      {feed.owner?.name || 'Unknown'}
                    </span>
                    {feed.taxii_server_url && (
                      <span className="detail-item">
                        <i className="fas fa-link"></i>
                        {feed.taxii_server_url}
                      </span>
                    )}
                    {feed.last_sync && (
                      <span className="detail-item">
                        <i className="fas fa-calendar"></i>
                        Last synced: {new Date(feed.last_sync).toLocaleString()}
                      </span>
                    )}
                    {feed.last_consumed && (
                      <span className="detail-item">
                        <i className="fas fa-check-circle"></i>
                        Last consumed: {new Date(feed.last_consumed).toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
                <div className="feed-status">
                  <span
                    className="status-indicator"
                    style={{ color: getStatusColor(feed.consumption_status || 'idle') }}
                  >
                    <i className={getStatusIcon(feed.consumption_status || 'idle')}></i>
                    {(feed.consumption_status || 'idle').charAt(0).toUpperCase() + (feed.consumption_status || 'idle').slice(1)}
                  </span>
                </div>
              </div>

              <div className="feed-stats">
                <div className="stat">
                  <i className="fas fa-shield-alt"></i>
                  <span className="stat-number">{(feed.indicators_count || 0).toLocaleString()}</span>
                  <span className="stat-label">Indicators</span>
                </div>
                <div className="stat">
                  <i className="fas fa-clock"></i>
                  <span className="stat-number">{feed.sync_count || 0}</span>
                  <span className="stat-label">Sync Count</span>
                </div>
              </div>

              {feed.taxii_collection_id && (
                <div className="feed-collections">
                  <h4>Collection:</h4>
                  <div className="collections-list">
                    <span className="collection-tag">
                      {feed.taxii_collection_id}
                    </span>
                  </div>
                </div>
              )}

              <div className="feed-actions">
                {feed.is_external && feed.taxii_server_url && (
                  <button
                    className={`btn btn-sm ${consumingFeeds.has(feed.id) ? 'btn-secondary' : 'btn-primary'}`}
                    onClick={() => handleConsumeFeed(feed.id)}
                    disabled={consumingFeeds.has(feed.id) || feed.consumption_status === 'running'}
                  >
                    <i className={`fas ${consumingFeeds.has(feed.id) || feed.consumption_status === 'running' ? 'fa-spinner fa-spin' : 'fa-download'}`}></i>
                    {consumingFeeds.has(feed.id) || feed.consumption_status === 'running' ? 'Consuming...' : 'Consume'}
                  </button>
                )}
                <button className="btn btn-sm btn-outline">
                  <i className="fas fa-eye"></i>
                  View Details
                </button>
                <button className="btn btn-sm btn-outline">
                  <i className="fas fa-cog"></i>
                  Configure
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <style jsx>{`
        .threat-feeds {
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

        .feeds-list {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .feed-card {
          background: white;
          border-radius: 12px;
          padding: 24px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          transition: box-shadow 0.2s;
          border-left: 4px solid #0056b3;
        }

        .feed-card:hover {
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .feed-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 20px;
        }

        .feed-info {
          flex: 1;
        }

        .feed-title {
          display: flex;
          align-items: center;
          gap: 15px;
          margin-bottom: 8px;
        }

        .feed-title h3 {
          margin: 0;
          color: #333;
          font-size: 20px;
        }

        .feed-badges {
          display: flex;
          gap: 8px;
        }

        .type-badge, .trust-badge {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
          text-transform: uppercase;
        }

        .type-badge {
          background: #e3f2fd;
          color: #0056b3;
        }

        .trust-badge {
          color: white;
        }

        .feed-description {
          margin: 0 0 15px 0;
          color: #6c757d;
          line-height: 1.5;
        }

        .feed-details {
          display: flex;
          flex-wrap: wrap;
          gap: 20px;
        }

        .detail-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;
          color: #6c757d;
        }

        .detail-item i {
          width: 16px;
          text-align: center;
        }

        .feed-status {
          flex-shrink: 0;
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          font-weight: 500;
          padding: 8px 12px;
          border-radius: 20px;
          background: rgba(255,255,255,0.8);
          border: 1px solid currentColor;
        }

        .feed-stats {
          display: flex;
          gap: 30px;
          margin-bottom: 20px;
          padding: 15px 0;
          border-top: 1px solid #f8f9fa;
          border-bottom: 1px solid #f8f9fa;
        }

        .stat {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
        }

        .stat i {
          font-size: 18px;
          color: #0056b3;
        }

        .stat-number {
          font-size: 18px;
          font-weight: 600;
          color: #333;
        }

        .stat-label {
          font-size: 12px;
          color: #6c757d;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .feed-collections {
          margin-bottom: 20px;
        }

        .feed-collections h4 {
          margin: 0 0 10px 0;
          color: #495057;
          font-size: 14px;
          font-weight: 600;
        }

        .collections-list {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .collection-tag {
          background: #f8f9fa;
          color: #495057;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          border: 1px solid #dee2e6;
        }

        .feed-actions {
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

        .btn-success {
          background: #28a745;
          color: white;
        }

        .btn-success:hover {
          background: #218838;
        }

        .btn-danger {
          background: #dc3545;
          color: white;
        }

        .btn-danger:hover {
          background: #c82333;
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

export default ThreatFeedList;
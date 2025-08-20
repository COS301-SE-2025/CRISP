import React, { useState, useEffect } from 'react';

const ThreatFeedList = () => {
  const [feeds, setFeeds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [showSubscribeModal, setShowSubscribeModal] = useState(false);

  useEffect(() => {
    fetchFeeds();
  }, [filter]);

  const fetchFeeds = async () => {
    try {
      setLoading(true);
      // Mock threat feed data - replace with actual API call
      const mockFeeds = [
        {
          id: '1',
          name: 'AlienVault OTX',
          type: 'STIX/TAXII',
          status: 'active',
          description: 'Open Threat Exchange community threat intelligence feed',
          url: 'https://otx.alienvault.com/taxii/discovery',
          indicators_count: 15432,
          last_updated: '2025-01-15T14:30:00Z',
          update_frequency: '1 hour',
          subscribed: true,
          trust_level: 'high',
          organization: 'AlienVault',
          collections: ['indicators', 'malware', 'campaigns']
        },
        {
          id: '2',
          name: 'MISP Feed',
          type: 'MISP',
          status: 'active',
          description: 'Malware Information Sharing Platform community feed',
          url: 'https://misppriv.circl.lu',
          indicators_count: 8921,
          last_updated: '2025-01-15T12:15:00Z',
          update_frequency: '30 minutes',
          subscribed: true,
          trust_level: 'medium',
          organization: 'CIRCL',
          collections: ['events', 'attributes', 'objects']
        },
        {
          id: '3',
          name: 'Emerging Threats',
          type: 'STIX/TAXII',
          status: 'pending',
          description: 'Proofpoint Emerging Threats intelligence feed',
          url: 'https://rules.emergingthreats.net/taxii',
          indicators_count: 0,
          last_updated: null,
          update_frequency: '6 hours',
          subscribed: false,
          trust_level: 'high',
          organization: 'Proofpoint',
          collections: ['signatures', 'indicators', 'rules']
        },
        {
          id: '4',
          name: 'Internal Threat Feed',
          type: 'Custom',
          status: 'active',
          description: 'Organization-specific threat intelligence collected internally',
          url: 'internal://threat-feed',
          indicators_count: 2145,
          last_updated: '2025-01-15T16:00:00Z',
          update_frequency: 'Real-time',
          subscribed: true,
          trust_level: 'high',
          organization: 'Internal',
          collections: ['incidents', 'indicators', 'artifacts']
        }
      ];

      let filteredFeeds = mockFeeds;
      if (filter !== 'all') {
        filteredFeeds = mockFeeds.filter(f => {
          if (filter === 'subscribed') return f.subscribed;
          if (filter === 'available') return !f.subscribed;
          return f.status === filter || f.type === filter;
        });
      }

      setFeeds(filteredFeeds);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

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
                      <span className="type-badge">{feed.type}</span>
                      <span 
                        className="trust-badge"
                        style={{ backgroundColor: getTrustLevelColor(feed.trust_level) }}
                      >
                        {feed.trust_level} trust
                      </span>
                    </div>
                  </div>
                  <p className="feed-description">{feed.description}</p>
                  <div className="feed-details">
                    <span className="detail-item">
                      <i className="fas fa-building"></i>
                      {feed.organization}
                    </span>
                    <span className="detail-item">
                      <i className="fas fa-link"></i>
                      {feed.url}
                    </span>
                    <span className="detail-item">
                      <i className="fas fa-sync-alt"></i>
                      Updates every {feed.update_frequency}
                    </span>
                    {feed.last_updated && (
                      <span className="detail-item">
                        <i className="fas fa-calendar"></i>
                        Last updated: {new Date(feed.last_updated).toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
                <div className="feed-status">
                  <span 
                    className="status-indicator"
                    style={{ color: getStatusColor(feed.status) }}
                  >
                    <i className={getStatusIcon(feed.status)}></i>
                    {feed.status.charAt(0).toUpperCase() + feed.status.slice(1)}
                  </span>
                </div>
              </div>

              <div className="feed-stats">
                <div className="stat">
                  <i className="fas fa-shield-alt"></i>
                  <span className="stat-number">{feed.indicators_count.toLocaleString()}</span>
                  <span className="stat-label">Indicators</span>
                </div>
                <div className="stat">
                  <i className="fas fa-layer-group"></i>
                  <span className="stat-number">{feed.collections.length}</span>
                  <span className="stat-label">Collections</span>
                </div>
              </div>

              <div className="feed-collections">
                <h4>Collections:</h4>
                <div className="collections-list">
                  {feed.collections.map(collection => (
                    <span key={collection} className="collection-tag">
                      {collection}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="feed-actions">
                <button 
                  className={`btn btn-sm ${feed.subscribed ? 'btn-danger' : 'btn-success'}`}
                  onClick={() => toggleSubscription(feed.id)}
                >
                  <i className={`fas ${feed.subscribed ? 'fa-unlink' : 'fa-link'}`}></i>
                  {feed.subscribed ? 'Unsubscribe' : 'Subscribe'}
                </button>
                <button className="btn btn-sm btn-outline">
                  <i className="fas fa-eye"></i>
                  View Details
                </button>
                <button className="btn btn-sm btn-outline">
                  <i className="fas fa-cog"></i>
                  Configure
                </button>
                <button className="btn btn-sm btn-outline">
                  <i className="fas fa-download"></i>
                  Export
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
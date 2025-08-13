import React, { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner.jsx';

const ThreatFeedList = ({ active = true, userRole = 'admin' }) => {
  const [threatFeeds, setThreatFeeds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (active) {
      loadThreatFeeds();
    }
  }, [active]);

  const loadThreatFeeds = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('crisp_auth_token');
      console.log('Fetching threat feeds from API...');
      
      const response = await fetch('http://localhost:8000/api/threat-feeds/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch threat feeds`);
      }

      const data = await response.json();
      console.log('Threat feeds loaded from API:', data);
      
      const feeds = Array.isArray(data) ? data : (data.data || data.results || []);
      setThreatFeeds(feeds);
    } catch (err) {
      console.error('Error loading threat feeds:', err);
      setError(err.message || 'Failed to load threat feeds');
    } finally {
      setLoading(false);
    }
  };

  const handleConsumeFeed = async (feedId) => {
    try {
      const token = localStorage.getItem('crisp_auth_token');
      console.log('Starting feed consumption for feed:', feedId);
      
      const response = await fetch(`http://localhost:8000/api/threat-feeds/${feedId}/consume/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Feed consumption result:', result);
        alert(`Feed consumption started successfully! Check the backend logs for progress.`);
      } else {
        throw new Error(`HTTP ${response.status}: Failed to consume feed`);
      }
    } catch (err) {
      console.error('Error consuming feed:', err);
      alert(`Error consuming feed: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="card-content">
          <LoadingSpinner />
          <p>Loading real threat feeds from AlienVault OTX...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="card-content">
          <div className="error-message">
            <i className="fas fa-exclamation-triangle"></i>
            <p>Error: {error}</p>
            <button className="btn btn-primary" onClick={loadThreatFeeds}>
              <i className="fas fa-sync-alt"></i> Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="threat-feeds-container">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <i className="fas fa-rss card-icon"></i> 
            Real Threat Feeds ({threatFeeds.length})
          </h2>
          <div className="card-actions">
            <button className="btn btn-outline btn-sm" onClick={loadThreatFeeds}>
              <i className="fas fa-sync-alt"></i> Refresh
            </button>
          </div>
        </div>
        <div className="card-content">
          {threatFeeds.length === 0 ? (
            <div className="empty-state">
              <i className="fas fa-rss"></i>
              <p>No threat feeds configured</p>
              <p>Add a threat feed to start collecting threat intelligence</p>
            </div>
          ) : (
            <ul className="feed-items">
              {threatFeeds.map((feed) => (
                <li key={feed.id} className="feed-item">
                  <div className="feed-icon">
                    <i className="fas fa-globe"></i>
                  </div>
                  <div className="feed-details">
                    <div className="feed-name">{feed.name}</div>
                    <div className="feed-description">{feed.description || 'No description available'}</div>
                    <div className="feed-meta">
                      <div className="feed-stats">
                        <div className="stat-item">
                          <i className="fas fa-server"></i> {feed.taxii_server_url || 'No URL'}
                        </div>
                        <div className="stat-item">
                          <i className="fas fa-database"></i> {feed.taxii_collection_id || 'No collection'}
                        </div>
                        {feed.last_sync && (
                          <div className="stat-item">
                            <i className="fas fa-sync-alt"></i> Last sync: {new Date(feed.last_sync).toLocaleString()}
                          </div>
                        )}
                      </div>
                      <div className="feed-badges">
                        <span className={`badge ${feed.is_active ? 'badge-active' : 'badge-inactive'}`}>
                          {feed.is_active ? 'Active' : 'Inactive'}
                        </span>
                        {feed.is_external && (
                          <span className="badge badge-connected">External</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="feed-actions">
                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={() => handleConsumeFeed(feed.id)}
                      disabled={!feed.is_active}
                      title="Consume threat data from this feed"
                    >
                      <i className="fas fa-download"></i> Consume
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default ThreatFeedList;
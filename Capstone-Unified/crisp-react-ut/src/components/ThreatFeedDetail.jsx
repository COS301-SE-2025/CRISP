import React, { useState, useEffect, useMemo } from 'react';
import LoadingSpinner from './LoadingSpinner.jsx';
import ConfirmationModal from './ConfirmationModal.jsx';
import IndicatorTable from './IndicatorTable.jsx';

const ThreatFeedDetail = ({ active = true, feedId, onNavigate, userRole }) => {
  console.log('ThreatFeedDetail rendered with props:', { active, feedId });
  
  // States following existing patterns
  const [feedDetails, setFeedDetails] = useState(null);
  const [feedStatus, setFeedStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [operationLoading, setOperationLoading] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationData, setConfirmationData] = useState(null);
  const [syncHistory, setSyncHistory] = useState([]);
  const [isSubscribed, setIsSubscribed] = useState(false);

  // Permission checks following existing patterns
  const isAdmin = userRole === 'admin' || userRole === 'BlueVisionAdmin';
  const isPublisher = userRole === 'publisher' || isAdmin;
  const isViewer = userRole === 'viewer';

  useEffect(() => {
    if (active && feedId) {
      loadFeedDetails();
      loadFeedStatus();
      loadSyncHistory();
    }
  }, [active, feedId]);

  const loadFeedDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch(`http://localhost:8000/api/v1/threat-feeds/${feedId}/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch feed details`);
      }

      const data = await response.json();
      console.log('Feed details loaded:', data);
      setFeedDetails(data);
      setIsSubscribed(data.is_subscribed || false);
    } catch (err) {
      console.error('Error loading feed details:', err);
      setError(err.message || 'Failed to load feed details');
    } finally {
      setLoading(false);
    }
  };

  const loadFeedStatus = async () => {
    try {
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch(`http://localhost:8000/api/v1/threat-feeds/${feedId}/status/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const status = await response.json();
        console.log('Feed status loaded:', status);
        setFeedStatus(status);
      }
    } catch (err) {
      console.error('Error loading feed status:', err);
      // Status is optional, don't set error state
    }
  };

  const loadSyncHistory = async () => {
    try {
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch(`http://localhost:8000/api/v1/threat-feeds/${feedId}/sync-history/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const history = await response.json();
        setSyncHistory(Array.isArray(history) ? history : []);
      }
    } catch (err) {
      console.error('Error loading sync history:', err);
      // History is optional, don't set error state
    }
  };

  const handleConsumeFeed = async () => {
    setOperationLoading(true);
    try {
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch(`http://localhost:8000/api/v1/threat-feeds/${feedId}/consume/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Feed consumed successfully! ${result.indicators || 0} indicators processed.`);
        // Refresh feed status
        await loadFeedStatus();
        await loadSyncHistory();
      } else {
        throw new Error('Failed to consume feed');
      }
    } catch (err) {
      console.error('Error consuming feed:', err);
      alert(err.message || 'Failed to consume feed');
    } finally {
      setOperationLoading(false);
    }
  };

  const handleTestConnection = async () => {
    setOperationLoading(true);
    try {
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch(`http://localhost:8000/api/v1/threat-feeds/${feedId}/test/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Connection test successful! Found ${result.collections_found || 0} collections.`);
      } else {
        const error = await response.json();
        alert(`Connection test failed: ${error.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error testing connection:', err);
      alert(err.message || 'Failed to test connection');
    } finally {
      setOperationLoading(false);
    }
  };

  const handleSubscribe = async () => {
    setOperationLoading(true);
    try {
      const token = localStorage.getItem('crisp_auth_token');
      const method = isSubscribed ? 'DELETE' : 'POST';
      const response = await fetch(`http://localhost:8000/api/v1/threat-feeds/${feedId}/subscribe/`, {
        method: method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setIsSubscribed(!isSubscribed);
        alert(isSubscribed ? 'Unsubscribed from feed' : 'Subscribed to feed');
      } else {
        throw new Error('Failed to update subscription');
      }
    } catch (err) {
      console.error('Error updating subscription:', err);
      alert(err.message || 'Failed to update subscription');
    } finally {
      setOperationLoading(false);
    }
  };

  const handleDeleteFeed = async () => {
    setOperationLoading(true);
    try {
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch(`http://localhost:8000/api/v1/threat-feeds/${feedId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        alert('Threat feed deleted successfully');
        // Navigate back to feeds list
        onNavigate && onNavigate('threat-feeds');
      } else {
        throw new Error('Failed to delete threat feed');
      }
    } catch (err) {
      console.error('Error deleting feed:', err);
      alert(err.message || 'Failed to delete threat feed');
    } finally {
      setOperationLoading(false);
    }
  };

  // Don't render if not active
  if (!active) return null;

  if (loading) {
    return <LoadingSpinner message="Loading feed details..." />;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <h3>Error Loading Feed Details</h3>
          <p>{error}</p>
          <div className="error-actions">
            <button className="btn btn-primary" onClick={loadFeedDetails}>
              <i className="fas fa-redo"></i> Retry
            </button>
            <button 
              className="btn btn-outline" 
              onClick={() => onNavigate && onNavigate('threat-feeds')}
            >
              <i className="fas fa-arrow-left"></i> Back to Feeds
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!feedDetails) {
    return (
      <div className="error-container">
        <div className="error-message">
          <i className="fas fa-search"></i>
          <h3>Feed Not Found</h3>
          <p>The requested threat feed could not be found.</p>
          <button 
            className="btn btn-outline" 
            onClick={() => onNavigate && onNavigate('threat-feeds')}
          >
            <i className="fas fa-arrow-left"></i> Back to Feeds
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="feed-detail-container">
      {/* Header */}
      <div className="page-header">
        <div className="page-title-section">
          <button 
            className="btn btn-icon back-button"
            onClick={() => onNavigate && onNavigate('threat-feeds')}
            title="Back to Threat Feeds"
          >
            <i className="fas fa-arrow-left"></i>
          </button>
          <div className="title-content">
            <h1 className="page-title">
              <i className="fas fa-rss"></i>
              {feedDetails.name}
            </h1>
            <p className="page-subtitle">
              {feedDetails.description || 'Threat intelligence feed details and indicators'}
            </p>
          </div>
        </div>
        
        {/* Feed Actions */}
        <div className="page-actions">
          {isViewer && (
            <button 
              className={`btn ${isSubscribed ? 'btn-outline' : 'btn-primary'}`}
              onClick={handleSubscribe}
              disabled={operationLoading}
            >
              <i className={`fas ${isSubscribed ? 'fa-bell-slash' : 'fa-bell'}`}></i>
              {isSubscribed ? 'Unsubscribe' : 'Subscribe'}
            </button>
          )}
          
          {isPublisher && (
            <>
              <button 
                className="btn btn-outline"
                onClick={handleTestConnection}
                disabled={operationLoading}
              >
                <i className="fas fa-link"></i>
                Test Connection
              </button>
              <button 
                className="btn btn-primary"
                onClick={handleConsumeFeed}
                disabled={operationLoading}
              >
                <i className="fas fa-download"></i>
                Consume Feed
              </button>
            </>
          )}
        </div>
      </div>

      {/* Feed Status Cards */}
      <div className="status-cards">
        <div className="status-card">
          <div className="status-icon">
            <i className={`fas ${feedDetails.is_active ? 'fa-check-circle' : 'fa-pause-circle'}`}></i>
          </div>
          <div className="status-content">
            <h3>Status</h3>
            <p className={feedDetails.is_active ? 'status-active' : 'status-inactive'}>
              {feedDetails.is_active ? 'Active' : 'Inactive'}
            </p>
          </div>
        </div>
        
        <div className="status-card">
          <div className="status-icon">
            <i className="fas fa-globe"></i>
          </div>
          <div className="status-content">
            <h3>Type</h3>
            <p>{feedDetails.is_external ? 'External' : 'Internal'}</p>
          </div>
        </div>
        
        <div className="status-card">
          <div className="status-icon">
            <i className="fas fa-search"></i>
          </div>
          <div className="status-content">
            <h3>Indicators</h3>
            <p>{feedStatus?.indicator_count || 0}</p>
          </div>
        </div>
        
        <div className="status-card">
          <div className="status-icon">
            <i className="fas fa-clock"></i>
          </div>
          <div className="status-content">
            <h3>Last Sync</h3>
            <p>{feedDetails.last_sync ? 
              new Date(feedDetails.last_sync).toLocaleDateString() : 
              'Never'
            }</p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <i className="fas fa-chart-line"></i>
          Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'indicators' ? 'active' : ''}`}
          onClick={() => setActiveTab('indicators')}
        >
          <i className="fas fa-search"></i>
          Indicators
        </button>
        <button 
          className={`tab-button ${activeTab === 'configuration' ? 'active' : ''}`}
          onClick={() => setActiveTab('configuration')}
        >
          <i className="fas fa-cog"></i>
          Configuration
        </button>
        {isPublisher && (
          <button 
            className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <i className="fas fa-history"></i>
            Sync History
          </button>
        )}
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="overview-content">
            <div className="overview-grid">
              <div className="overview-section">
                <h3>Feed Information</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <label>Name:</label>
                    <span>{feedDetails.name}</span>
                  </div>
                  {feedDetails.description && (
                    <div className="info-item">
                      <label>Description:</label>
                      <span>{feedDetails.description}</span>
                    </div>
                  )}
                  <div className="info-item">
                    <label>Type:</label>
                    <span>{feedDetails.is_external ? 'External Feed' : 'Internal Feed'}</span>
                  </div>
                  <div className="info-item">
                    <label>Status:</label>
                    <span className={feedDetails.is_active ? 'status-active' : 'status-inactive'}>
                      {feedDetails.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div className="info-item">
                    <label>Created:</label>
                    <span>{feedDetails.created_at ? 
                      new Date(feedDetails.created_at).toLocaleDateString() : 
                      'Unknown'
                    }</span>
                  </div>
                </div>
              </div>
              
              {feedStatus && (
                <div className="overview-section">
                  <h3>Statistics</h3>
                  <div className="stats-grid">
                    <div className="stat-item">
                      <div className="stat-icon">
                        <i className="fas fa-search"></i>
                      </div>
                      <div className="stat-content">
                        <span className="stat-number">{feedStatus.indicator_count || 0}</span>
                        <span className="stat-label">Indicators</span>
                      </div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-icon">
                        <i className="fas fa-sitemap"></i>
                      </div>
                      <div className="stat-content">
                        <span className="stat-number">{feedStatus.ttp_count || 0}</span>
                        <span className="stat-label">TTPs</span>
                      </div>
                    </div>
                    {feedStatus.latest_indicator_date && (
                      <div className="stat-item full-width">
                        <div className="stat-icon">
                          <i className="fas fa-calendar"></i>
                        </div>
                        <div className="stat-content">
                          <span className="stat-date">
                            {new Date(feedStatus.latest_indicator_date).toLocaleDateString()}
                          </span>
                          <span className="stat-label">Latest Indicator</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Indicators Tab */}
        {activeTab === 'indicators' && (
          <IndicatorTable 
            active={true}
            feedId={feedId}
            userRole={userRole}
          />
        )}

        {/* Configuration Tab */}
        {activeTab === 'configuration' && (
          <div className="configuration-content">
            <div className="config-section">
              <h3>Feed Configuration</h3>
              {feedDetails.is_external ? (
                <div className="config-grid">
                  {feedDetails.taxii_server_url && (
                    <div className="config-item">
                      <label>TAXII Server:</label>
                      <span>{feedDetails.taxii_server_url}</span>
                    </div>
                  )}
                  {feedDetails.taxii_api_root && (
                    <div className="config-item">
                      <label>API Root:</label>
                      <span>{feedDetails.taxii_api_root}</span>
                    </div>
                  )}
                  {feedDetails.taxii_collection_id && (
                    <div className="config-item">
                      <label>Collection ID:</label>
                      <span>{feedDetails.taxii_collection_id}</span>
                    </div>
                  )}
                  <div className="config-item">
                    <label>Sync Interval:</label>
                    <span>{feedDetails.sync_interval_hours || 24} hours</span>
                  </div>
                </div>
              ) : (
                <div className="config-info">
                  <i className="fas fa-info-circle"></i>
                  <p>This is an internal feed. Configuration is managed automatically.</p>
                </div>
              )}
            </div>

            {isAdmin && (
              <div className="config-actions">
                <button 
                  className="btn btn-outline"
                  onClick={() => onNavigate && onNavigate('edit-threat-feed', { feedId })}
                >
                  <i className="fas fa-edit"></i>
                  Edit Configuration
                </button>
                <button 
                  className="btn btn-danger"
                  onClick={() => {
                    setConfirmationData({
                      title: 'Delete Threat Feed',
                      message: `Are you sure you want to delete "${feedDetails.name}"? This action cannot be undone.`,
                      confirmText: 'Delete',
                      onConfirm: () => handleDeleteFeed()
                    });
                    setShowConfirmation(true);
                  }}
                >
                  <i className="fas fa-trash"></i>
                  Delete Feed
                </button>
              </div>
            )}
          </div>
        )}

        {/* Sync History Tab */}
        {activeTab === 'history' && isPublisher && (
          <div className="history-content">
            <h3>Synchronization History</h3>
            {syncHistory.length > 0 ? (
              <div className="history-list">
                {syncHistory.map((sync, index) => (
                  <div key={index} className="history-item">
                    <div className="history-icon">
                      <i className={`fas ${sync.success ? 'fa-check-circle' : 'fa-times-circle'}`}></i>
                    </div>
                    <div className="history-content">
                      <div className="history-header">
                        <span className="history-date">
                          {new Date(sync.timestamp).toLocaleString()}
                        </span>
                        <span className={`history-status ${sync.success ? 'success' : 'error'}`}>
                          {sync.success ? 'Success' : 'Failed'}
                        </span>
                      </div>
                      <div className="history-details">
                        {sync.success ? (
                          <span>
                            Processed {sync.indicators_count || 0} indicators, 
                            {sync.ttps_count || 0} TTPs
                          </span>
                        ) : (
                          <span>{sync.error_message || 'Unknown error'}</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-history">
                <i className="fas fa-history"></i>
                <p>No synchronization history available</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Confirmation Modal */}
      {showConfirmation && confirmationData && (
        <ConfirmationModal
          isOpen={showConfirmation}
          title={confirmationData.title}
          message={confirmationData.message}
          confirmText={confirmationData.confirmText}
          onConfirm={() => {
            confirmationData.onConfirm();
            setShowConfirmation(false);
          }}
          onCancel={() => setShowConfirmation(false)}
        />
      )}
    </div>
  );
};

export default ThreatFeedDetail;
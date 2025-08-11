import React, { useState, useEffect, useMemo } from 'react';
import LoadingSpinner from './LoadingSpinner.jsx';
import ConfirmationModal from './ConfirmationModal.jsx';
import Pagination from './Pagination.jsx';

const ThreatFeedList = ({ active = true, initialSection = null, onNavigate, userRole }) => {
  console.log('ThreatFeedList rendered with props:', { active, initialSection });
  
  // States following existing patterns
  const [threatFeeds, setThreatFeeds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedFeed, setSelectedFeed] = useState(null);
  const [showActionsPopup, setShowActionsPopup] = useState(false);
  const [selectedFeedForActions, setSelectedFeedForActions] = useState(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationData, setConfirmationData] = useState(null);
  const [operationLoading, setOperationLoading] = useState(false);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [allFeeds, setAllFeeds] = useState([]);

  // Permission checks following existing patterns
  const isAdmin = userRole === 'admin' || userRole === 'BlueVisionAdmin';
  const isPublisher = userRole === 'publisher' || isAdmin;
  const isViewer = userRole === 'viewer';

  useEffect(() => {
    if (active) {
      loadThreatFeeds();
    }
  }, [active]);

  const loadThreatFeeds = async () => {
    setLoading(true);
    setError(null);
    try {
      // API call following existing patterns
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch('http://localhost:8000/api/v1/threat-feeds/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch threat feeds`);
      }

      const data = await response.json();
      console.log('Threat feeds loaded:', data);
      
      // Handle both direct array and wrapped response formats
      const feeds = Array.isArray(data) ? data : (data.data || data.results || []);
      setAllFeeds(feeds);
      setThreatFeeds(feeds);
    } catch (err) {
      console.error('Error loading threat feeds:', err);
      setError(err.message || 'Failed to load threat feeds');
    } finally {
      setLoading(false);
    }
  };

  // Search and filter functionality following existing patterns
  const filteredFeeds = useMemo(() => {
    let filtered = allFeeds;

    if (searchTerm) {
      filtered = filtered.filter(feed =>
        feed.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        feed.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (statusFilter) {
      filtered = filtered.filter(feed => {
        if (statusFilter === 'active') return feed.is_active;
        if (statusFilter === 'inactive') return !feed.is_active;
        if (statusFilter === 'external') return feed.is_external;
        if (statusFilter === 'internal') return !feed.is_external;
        return true;
      });
    }

    return filtered;
  }, [allFeeds, searchTerm, statusFilter]);

  // Pagination logic following existing patterns
  const totalItems = filteredFeeds.length;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedFeeds = filteredFeeds.slice(startIndex, startIndex + itemsPerPage);

  const handleFeedClick = (feed) => {
    console.log('Feed clicked:', feed);
    if (onNavigate) {
      onNavigate('threat-feed-detail', { feedId: feed.id, feed: feed });
    }
  };

  const handleSubscribeToFeed = async (feedId) => {
    setOperationLoading(true);
    try {
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch(`http://localhost:8000/api/v1/threat-feeds/${feedId}/subscribe/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        await loadThreatFeeds(); // Refresh the list
        alert('Successfully subscribed to threat feed');
      } else {
        throw new Error('Failed to subscribe to threat feed');
      }
    } catch (err) {
      console.error('Error subscribing to feed:', err);
      alert(err.message || 'Failed to subscribe to threat feed');
    } finally {
      setOperationLoading(false);
      setShowActionsPopup(false);
    }
  };

  const handleDeleteFeed = async (feedId) => {
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
        loadThreatFeeds(); // Refresh the list
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

  const handleActionsClick = (e, feed) => {
    e.preventDefault();
    e.stopPropagation();
    setSelectedFeedForActions(feed);
    setShowActionsPopup(true);
  };

  // Don't render if not active
  if (!active) return null;

  if (loading) {
    return <LoadingSpinner message="Loading threat feeds..." />;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <h3>Error Loading Threat Feeds</h3>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={loadThreatFeeds}>
            <i className="fas fa-redo"></i> Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="threat-feeds-container">
      {/* Header following existing patterns */}
      <div className="page-header">
        <div className="page-title-section">
          <h1 className="page-title">
            <i className="fas fa-rss"></i>
            Threat Feeds
          </h1>
          <p className="page-subtitle">
            Monitor and manage threat intelligence feeds for your organization
          </p>
        </div>
        
        {/* Action buttons for publishers/admins */}
        {isPublisher && (
          <div className="page-actions">
            <button 
              className="btn btn-primary"
              onClick={() => onNavigate && onNavigate('add-threat-feed')}
            >
              <i className="fas fa-plus"></i>
              Add Feed
            </button>
            <button 
              className="btn btn-outline"
              onClick={() => onNavigate && onNavigate('feed-subscriptions')}
            >
              <i className="fas fa-cog"></i>
              Manage Subscriptions
            </button>
          </div>
        )}
      </div>

      {/* Search and Filter Section */}
      <div className="filters-section">
        <div className="search-box">
          <i className="fas fa-search"></i>
          <input
            type="text"
            placeholder="Search threat feeds..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="filter-controls">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Feeds</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="external">External</option>
            <option value="internal">Internal</option>
          </select>
        </div>
      </div>

      {/* Feeds Table */}
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Type</th>
              <th>Status</th>
              <th>Last Sync</th>
              <th>Indicators</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {paginatedFeeds.length > 0 ? (
              paginatedFeeds.map((feed) => (
                <tr 
                  key={feed.id} 
                  onClick={() => handleFeedClick(feed)}
                  className="clickable-row"
                >
                  <td>
                    <div className="feed-name">
                      <i className="fas fa-rss feed-icon"></i>
                      <span className="feed-title">{feed.name || 'Unnamed Feed'}</span>
                    </div>
                  </td>
                  <td>
                    <span className="feed-description">
                      {feed.description ? 
                        (feed.description.length > 80 ? 
                          feed.description.substring(0, 80) + '...' : 
                          feed.description
                        ) : 
                        'No description available'
                      }
                    </span>
                  </td>
                  <td>
                    <span className={`feed-type-badge ${feed.is_external ? 'external' : 'internal'}`}>
                      {feed.is_external ? 'External' : 'Internal'}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${feed.is_active ? 'active' : 'inactive'}`}>
                      {feed.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    {feed.last_sync ? 
                      new Date(feed.last_sync).toLocaleDateString() : 
                      'Never'
                    }
                  </td>
                  <td>
                    <span className="indicator-count">
                      {feed.indicator_count || 0} indicators
                    </span>
                  </td>
                  <td>
                    <button 
                      className="btn btn-icon"
                      onClick={(e) => handleActionsClick(e, feed)}
                      title="Actions"
                    >
                      <i className="fas fa-ellipsis-v"></i>
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="no-data">
                  {searchTerm || statusFilter ? 
                    'No threat feeds match your search criteria' : 
                    'No threat feeds available'
                  }
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalItems > itemsPerPage && (
        <Pagination
          currentPage={currentPage}
          totalItems={totalItems}
          itemsPerPage={itemsPerPage}
          onPageChange={setCurrentPage}
          onItemsPerPageChange={setItemsPerPage}
        />
      )}

      {/* Actions Popup */}
      {showActionsPopup && selectedFeedForActions && (
        <div className="popup-overlay" onClick={() => setShowActionsPopup(false)}>
          <div className="actions-popup" onClick={(e) => e.stopPropagation()}>
            <h3>Feed Actions</h3>
            <div className="popup-actions">
              <button 
                className="popup-action"
                onClick={() => {
                  setShowActionsPopup(false);
                  handleFeedClick(selectedFeedForActions);
                }}
              >
                <i className="fas fa-eye"></i>
                View Details
              </button>
              
              {isPublisher && (
                <>
                  <button 
                    className="popup-action"
                    onClick={() => handleSubscribeToFeed(selectedFeedForActions.id)}
                    disabled={operationLoading}
                  >
                    <i className="fas fa-bell"></i>
                    Subscribe
                  </button>
                  
                  <button 
                    className="popup-action"
                    onClick={() => {
                      setShowActionsPopup(false);
                      if (onNavigate) onNavigate('edit-threat-feed', { feedId: selectedFeedForActions.id });
                    }}
                  >
                    <i className="fas fa-edit"></i>
                    Edit Feed
                  </button>
                </>
              )}
              
              {isAdmin && (
                <button 
                  className="popup-action danger"
                  onClick={() => {
                    setShowActionsPopup(false);
                    setConfirmationData({
                      title: 'Delete Threat Feed',
                      message: `Are you sure you want to delete "${selectedFeedForActions.name}"? This action cannot be undone.`,
                      confirmText: 'Delete',
                      onConfirm: () => handleDeleteFeed(selectedFeedForActions.id)
                    });
                    setShowConfirmation(true);
                  }}
                >
                  <i className="fas fa-trash"></i>
                  Delete Feed
                </button>
              )}
            </div>
            <button 
              className="btn btn-outline btn-small"
              onClick={() => setShowActionsPopup(false)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

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

export default ThreatFeedList;
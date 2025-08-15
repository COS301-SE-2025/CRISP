import React, { useState, useEffect, useMemo } from 'react';
import LoadingSpinner from './LoadingSpinner.jsx';
import ConfirmationModal from './ConfirmationModal.jsx';
import Pagination from './Pagination.jsx';

const IndicatorTable = ({ active = true, feedId = null, searchQuery = '', userRole }) => {
  console.log('IndicatorTable rendered with props:', { active, feedId, searchQuery });
  
  // States following existing patterns
  const [indicators, setIndicators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState(searchQuery || '');
  const [typeFilter, setTypeFilter] = useState('');
  const [confidenceFilter, setConfenceFilter] = useState('');
  const [selectedIndicator, setSelectedIndicator] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showActionsPopup, setShowActionsPopup] = useState(false);
  const [selectedIndicatorForActions, setSelectedIndicatorForActions] = useState(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationData, setConfirmationData] = useState(null);
  const [operationLoading, setOperationLoading] = useState(false);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(20);
  const [allIndicators, setAllIndicators] = useState([]);

  // Permission checks following existing patterns
  const isAdmin = userRole === 'admin' || userRole === 'BlueVisionAdmin';
  const isPublisher = userRole === 'publisher' || isAdmin;
  const isViewer = userRole === 'viewer';

  // Common indicator types for filtering
  const indicatorTypes = [
    'domain-name',
    'ipv4-addr',
    'ipv6-addr',
    'url',
    'file',
    'email-addr',
    'malware',
    'registry-key',
    'process',
    'network-traffic'
  ];

  useEffect(() => {
    if (active) {
      loadIndicators();
    }
  }, [active, feedId]);

  // Update search term when prop changes
  useEffect(() => {
    setSearchTerm(searchQuery || '');
  }, [searchQuery]);

  const loadIndicators = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('crisp_auth_token');
      
      // Construct API URL - get real indicators from our new API
      let apiUrl = 'http://localhost:8000/api/indicators/';
      if (feedId) {
        // For specific feed indicators, we'll add a filter parameter
        apiUrl = `http://localhost:8000/api/indicators/?feed=${feedId}`;
      }

      const response = await fetch(apiUrl, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch indicators`);
      }

      const data = await response.json();
      console.log('Indicators loaded:', data);
      
      // Handle both direct array and wrapped response formats
      const indicators = Array.isArray(data) ? data : (data.data || data.results || []);
      setAllIndicators(indicators);
      setIndicators(indicators);
    } catch (err) {
      console.error('Error loading indicators:', err);
      setError(err.message || 'Failed to load indicators');
    } finally {
      setLoading(false);
    }
  };

  // Search and filter functionality following existing patterns
  const filteredIndicators = useMemo(() => {
    let filtered = allIndicators;

    if (searchTerm) {
      filtered = filtered.filter(indicator =>
        indicator.pattern?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        indicator.indicator_type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        indicator.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        indicator.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (typeFilter) {
      filtered = filtered.filter(indicator => indicator.indicator_type === typeFilter);
    }

    if (confidenceFilter) {
      filtered = filtered.filter(indicator => {
        if (confidenceFilter === 'high') return indicator.confidence >= 75;
        if (confidenceFilter === 'medium') return indicator.confidence >= 50 && indicator.confidence < 75;
        if (confidenceFilter === 'low') return indicator.confidence < 50;
        return true;
      });
    }

    return filtered;
  }, [allIndicators, searchTerm, typeFilter, confidenceFilter]);

  // Pagination logic following existing patterns
  const totalItems = filteredIndicators.length;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedIndicators = filteredIndicators.slice(startIndex, startIndex + itemsPerPage);

  const handleIndicatorClick = (indicator) => {
    console.log('Indicator clicked:', indicator);
    setSelectedIndicator(indicator);
    setShowDetailsModal(true);
  };

  const handleActionsClick = (e, indicator) => {
    e.preventDefault();
    e.stopPropagation();
    setSelectedIndicatorForActions(indicator);
    setShowActionsPopup(true);
  };

  const handleRemoveIndicator = async (indicatorId) => {
    setOperationLoading(true);
    try {
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch(`http://localhost:8000/api/v1/indicators/${indicatorId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        alert('Indicator removed successfully');
        loadIndicators(); // Refresh the list
      } else {
        throw new Error('Failed to remove indicator');
      }
    } catch (err) {
      console.error('Error removing indicator:', err);
      alert(err.message || 'Failed to remove indicator');
    } finally {
      setOperationLoading(false);
    }
  };

  const handleAddToWatchlist = async (indicatorId) => {
    setOperationLoading(true);
    try {
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch(`http://localhost:8000/api/v1/indicators/${indicatorId}/watchlist/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        alert('Indicator added to watchlist');
      } else {
        throw new Error('Failed to add to watchlist');
      }
    } catch (err) {
      console.error('Error adding to watchlist:', err);
      alert(err.message || 'Failed to add to watchlist');
    } finally {
      setOperationLoading(false);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 75) return 'high';
    if (confidence >= 50) return 'medium';
    return 'low';
  };

  const formatPattern = (pattern) => {
    if (!pattern) return 'N/A';
    return pattern.length > 50 ? pattern.substring(0, 50) + '...' : pattern;
  };

  const formatIndicatorType = (type) => {
    if (!type) return 'Unknown';
    return type.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // Don't render if not active
  if (!active) return null;

  if (loading) {
    return <LoadingSpinner message="Loading threat indicators..." />;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <h3>Error Loading Indicators</h3>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={loadIndicators}>
            <i className="fas fa-redo"></i> Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="indicators-container">
      {/* Header */}
      <div className="page-header">
        <div className="page-title-section">
          <h1 className="page-title">
            <i className="fas fa-search"></i>
            {feedId ? 'Feed Indicators' : 'Threat Indicators'}
          </h1>
          <p className="page-subtitle">
            {feedId ? 
              'View indicators from this threat feed' : 
              'Browse and analyze threat indicators from all feeds'
            }
          </p>
        </div>
        
        <div className="page-stats">
          <div className="stat-item">
            <span className="stat-number">{totalItems}</span>
            <span className="stat-label">Total Indicators</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{filteredIndicators.filter(i => i.confidence >= 75).length}</span>
            <span className="stat-label">High Confidence</span>
          </div>
        </div>
      </div>

      {/* Search and Filter Section */}
      <div className="filters-section">
        <div className="search-box">
          <i className="fas fa-search"></i>
          <input
            type="text"
            placeholder="Search indicators by pattern, type, or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="filter-controls">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Types</option>
            {indicatorTypes.map(type => (
              <option key={type} value={type}>
                {formatIndicatorType(type)}
              </option>
            ))}
          </select>
          
          <select
            value={confidenceFilter}
            onChange={(e) => setConfenceFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Confidence Levels</option>
            <option value="high">High (75+)</option>
            <option value="medium">Medium (50-74)</option>
            <option value="low">Low (&lt;50)</option>
          </select>
        </div>
      </div>

      {/* Indicators Table */}
      <div className="table-container">
        <table className="data-table indicators-table">
          <thead>
            <tr>
              <th>Pattern</th>
              <th>Type</th>
              <th>Confidence</th>
              <th>Labels</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {paginatedIndicators.length > 0 ? (
              paginatedIndicators.map((indicator) => (
                <tr 
                  key={indicator.id} 
                  onClick={() => handleIndicatorClick(indicator)}
                  className="clickable-row"
                >
                  <td>
                    <div className="indicator-pattern">
                      <span className="pattern-text" title={indicator.pattern}>
                        {formatPattern(indicator.pattern)}
                      </span>
                      {indicator.is_malicious && (
                        <span className="malicious-badge" title="Malicious">
                          <i className="fas fa-exclamation-triangle"></i>
                        </span>
                      )}
                    </div>
                  </td>
                  <td>
                    <span className="indicator-type">
                      {formatIndicatorType(indicator.indicator_type)}
                    </span>
                  </td>
                  <td>
                    <span className={`confidence-badge ${getConfidenceColor(indicator.confidence)}`}>
                      {indicator.confidence || 0}%
                    </span>
                  </td>
                  <td>
                    <div className="labels-container">
                      {indicator.labels && indicator.labels.length > 0 ? (
                        indicator.labels.slice(0, 2).map((label, index) => (
                          <span key={index} className="label-tag">
                            {label}
                          </span>
                        ))
                      ) : (
                        <span className="no-labels">No labels</span>
                      )}
                      {indicator.labels && indicator.labels.length > 2 && (
                        <span className="more-labels">+{indicator.labels.length - 2}</span>
                      )}
                    </div>
                  </td>
                  <td>
                    {indicator.created ? 
                      new Date(indicator.created).toLocaleDateString() : 
                      'Unknown'
                    }
                  </td>
                  <td>
                    <button 
                      className="btn btn-icon"
                      onClick={(e) => handleActionsClick(e, indicator)}
                      title="Actions"
                    >
                      <i className="fas fa-ellipsis-v"></i>
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="no-data">
                  {searchTerm || typeFilter || confidenceFilter ? 
                    'No indicators match your search criteria' : 
                    'No indicators available'
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

      {/* Indicator Details Modal */}
      {showDetailsModal && selectedIndicator && (
        <div className="modal-overlay" onClick={() => setShowDetailsModal(false)}>
          <div className="modal-content large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Indicator Details</h2>
              <button 
                className="modal-close"
                onClick={() => setShowDetailsModal(false)}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <div className="modal-body">
              <div className="indicator-details">
                <div className="detail-row">
                  <label>Pattern:</label>
                  <span className="pattern-full">{selectedIndicator.pattern}</span>
                </div>
                
                <div className="detail-row">
                  <label>Type:</label>
                  <span>{formatIndicatorType(selectedIndicator.indicator_type)}</span>
                </div>
                
                <div className="detail-row">
                  <label>Confidence:</label>
                  <span className={`confidence-badge ${getConfidenceColor(selectedIndicator.confidence)}`}>
                    {selectedIndicator.confidence || 0}%
                  </span>
                </div>
                
                {selectedIndicator.name && (
                  <div className="detail-row">
                    <label>Name:</label>
                    <span>{selectedIndicator.name}</span>
                  </div>
                )}
                
                {selectedIndicator.description && (
                  <div className="detail-row">
                    <label>Description:</label>
                    <span>{selectedIndicator.description}</span>
                  </div>
                )}
                
                {selectedIndicator.labels && selectedIndicator.labels.length > 0 && (
                  <div className="detail-row">
                    <label>Labels:</label>
                    <div className="labels-list">
                      {selectedIndicator.labels.map((label, index) => (
                        <span key={index} className="label-tag">
                          {label}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="detail-row">
                  <label>Created:</label>
                  <span>
                    {selectedIndicator.created ? 
                      new Date(selectedIndicator.created).toLocaleString() : 
                      'Unknown'
                    }
                  </span>
                </div>
                
                <div className="detail-row">
                  <label>Modified:</label>
                  <span>
                    {selectedIndicator.modified ? 
                      new Date(selectedIndicator.modified).toLocaleString() : 
                      'Unknown'
                    }
                  </span>
                </div>
              </div>
            </div>
            
            <div className="modal-footer">
              <button 
                className="btn btn-outline"
                onClick={() => setShowDetailsModal(false)}
              >
                Close
              </button>
              {isPublisher && (
                <button 
                  className="btn btn-primary"
                  onClick={() => {
                    handleAddToWatchlist(selectedIndicator.id);
                    setShowDetailsModal(false);
                  }}
                  disabled={operationLoading}
                >
                  <i className="fas fa-plus"></i>
                  Add to Watchlist
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Actions Popup */}
      {showActionsPopup && selectedIndicatorForActions && (
        <div className="popup-overlay" onClick={() => setShowActionsPopup(false)}>
          <div className="actions-popup" onClick={(e) => e.stopPropagation()}>
            <h3>Indicator Actions</h3>
            <div className="popup-actions">
              <button 
                className="popup-action"
                onClick={() => {
                  setShowActionsPopup(false);
                  handleIndicatorClick(selectedIndicatorForActions);
                }}
              >
                <i className="fas fa-eye"></i>
                View Details
              </button>
              
              <button 
                className="popup-action"
                onClick={() => {
                  navigator.clipboard.writeText(selectedIndicatorForActions.pattern);
                  alert('Pattern copied to clipboard');
                  setShowActionsPopup(false);
                }}
              >
                <i className="fas fa-copy"></i>
                Copy Pattern
              </button>
              
              {isPublisher && (
                <button 
                  className="popup-action"
                  onClick={() => {
                    setShowActionsPopup(false);
                    handleAddToWatchlist(selectedIndicatorForActions.id);
                  }}
                >
                  <i className="fas fa-bookmark"></i>
                  Add to Watchlist
                </button>
              )}
              
              {isAdmin && (
                <button 
                  className="popup-action danger"
                  onClick={() => {
                    setShowActionsPopup(false);
                    setConfirmationData({
                      title: 'Remove Indicator',
                      message: `Are you sure you want to remove this indicator? This action cannot be undone.`,
                      confirmText: 'Remove',
                      onConfirm: () => handleRemoveIndicator(selectedIndicatorForActions.id)
                    });
                    setShowConfirmation(true);
                  }}
                >
                  <i className="fas fa-trash"></i>
                  Remove Indicator
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

export default IndicatorTable;
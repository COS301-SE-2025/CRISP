import React, { useState, useEffect } from 'react';
import { useNotifications } from '../enhanced/NotificationManager.jsx';
import { getIndicators, checkUpdates, markUpdateSeen } from '../../api.js';

const IndicatorTable = () => {
  const { showError } = useNotifications();
  const [indicators, setIndicators] = useState([]);
  const [sharedIndicators, setSharedIndicators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });
  const [currentPage, setCurrentPage] = useState(1);
  const [autoRefresh, setAutoRefresh] = useState(true); // Enable auto-refresh by default
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [selectedIndicators, setSelectedIndicators] = useState(new Set());
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [lastSyncCheck, setLastSyncCheck] = useState(null);
  const itemsPerPage = 20;

  useEffect(() => {
    fetchIndicators();
    // Clear selections when filter or search changes
    setSelectedIndicators(new Set());
    // Reset to first page when filter changes
    setCurrentPage(1);
  }, [filter, searchTerm]);

  // Check for updates every 5 seconds when enabled (smart syncing)
  useEffect(() => {
    let interval;
    if (autoRefresh) {
      interval = setInterval(async () => {
        try {
          const updateData = await checkUpdates();

          if (updateData.success && updateData.updates.indicators_updated) {
            const lastUpdate = updateData.updates.indicators_updated;
            const lastUpdateDate = new Date(lastUpdate);
            const lastCheckDate = lastSyncCheck ? new Date(lastSyncCheck) : null;

            // console.log('🔍 Sync check:', {
              lastUpdate: lastUpdate,
              lastSyncCheck: lastSyncCheck,
              shouldRefresh: !lastCheckDate || lastUpdateDate > lastCheckDate
            });

            // Only refresh if there's a new update since our last check
            if (!lastCheckDate || lastUpdateDate > lastCheckDate) {
              console.log('🔄 New indicators detected, refreshing table...');
              setRefreshing(true);
              await fetchIndicators(false); // Silent refresh
              setLastRefresh(new Date());
              setLastSyncCheck(lastUpdate);
              setRefreshing(false);

              // Mark this update as seen
              await markUpdateSeen('indicators_updated', lastUpdate);
            } else {
              // console.log('📊 No new indicators since last check');
            }
          } else {
            console.log('⏸️ No indicators_updated in response:', updateData);
          }
        } catch (error) {
          // Fallback to regular interval refresh if sync API fails
          console.warn('⚠️ Sync check failed, falling back to regular refresh:', error);
          setRefreshing(true);
          await fetchIndicators(false);
          setLastRefresh(new Date());
          setRefreshing(false);
        }
      }, 600000); // 10 minutes to dramatically prevent performance issues
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, filter, searchTerm, lastSyncCheck]);

  // Clear selections when page changes
  useEffect(() => {
    setSelectedIndicators(new Set());
  }, [currentPage]);

  // Listen for feed consumption completion events and asset monitoring updates
  useEffect(() => {
    const handleFeedUpdate = (event) => {
      // Refresh indicators when feed consumption completes or asset monitoring runs
      fetchIndicators(false); // Silent refresh
      setLastRefresh(new Date());
    };

    // Listen for custom events from other components
    window.addEventListener('feedConsumptionComplete', handleFeedUpdate);
    window.addEventListener('indicatorsUpdated', handleFeedUpdate);
    window.addEventListener('assetMonitoringComplete', handleFeedUpdate);
    window.addEventListener('newIndicatorDetected', handleFeedUpdate);

    return () => {
      window.removeEventListener('feedConsumptionComplete', handleFeedUpdate);
      window.removeEventListener('indicatorsUpdated', handleFeedUpdate);
      window.removeEventListener('assetMonitoringComplete', handleFeedUpdate);
      window.removeEventListener('newIndicatorDetected', handleFeedUpdate);
    };
  }, []);

  const fetchIndicators = async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }

      // Build query parameters for filtering
      const queryParams = {
        limit: 500, // Get more indicators for better filtering
        ordering: '-created_at', // Newest first
      };

      // Add specific filters
      if (filter === 'critical') {
        queryParams.severity = 'critical';
      } else if (filter === 'IP Address') {
        queryParams.type = 'ip';
      } else if (filter === 'Domain') {
        queryParams.type = 'domain';
      } else if (filter === 'File Hash') {
        queryParams.type = 'file_hash';
      }

      // Add search term
      if (searchTerm) {
        queryParams.search = searchTerm;
      }

      // console.log('🔍 Fetching indicators with params:', queryParams);

      // Use the proper API function
      const indicatorsData = await getIndicators(queryParams);

      // console.log('📡 Indicators API response:', indicatorsData);

      // Handle different response formats for indicators
      let indicatorsList = Array.isArray(indicatorsData) ? indicatorsData :
                          indicatorsData.results || indicatorsData.indicators || indicatorsData.data || [];

      // Debug: Log the first indicator to see its structure
      if (indicatorsList.length > 0) {
        // console.log('🔍 First indicator structure:', indicatorsList[0]);
      }

      // Transform indicators to consistent format
      const allIndicators = indicatorsList.map(indicator => ({
        id: indicator.id || indicator.uuid,
        type: indicator.type || indicator.indicator_type || 'Unknown',
        value: indicator.value || indicator.indicator_value || '',
        threat_type: indicator.threat_type || 'Unknown',
        confidence: indicator.confidence || 'medium',
        severity: indicator.severity || 'medium',
        source: indicator.source || indicator.threat_feed?.name || indicator.feed_name || 'Unknown',
        sharing: indicator.sharing || { is_shared: false },
        created_at: indicator.created_at || indicator.timestamp || new Date().toISOString(),
        first_seen: indicator.first_seen || indicator.created_at || new Date().toISOString(),
        last_seen: indicator.last_seen || indicator.created_at || new Date().toISOString(),
        tags: indicator.tags || [],
        description: indicator.description || indicator.name || '',
        ttps: indicator.ttps || [],
        false_positive_score: indicator.false_positive_score || 0,
        is_shared: indicator.sharing?.is_shared || false,
        sharing_info: indicator.sharing || null
      }));

      // Count shared indicators for stats
      const sharedIndicators = allIndicators.filter(i => i.is_shared);
      setSharedIndicators(sharedIndicators);

      let filteredIndicators = [...allIndicators];

      // Apply client-side type filter if not already applied in API
      if (filter === 'shared') {
        filteredIndicators = filteredIndicators.filter(i => i.is_shared);
      } else if (filter === 'own') {
        filteredIndicators = filteredIndicators.filter(i => !i.is_shared);
      }

      // Apply client-side search filter if not already applied in API
      if (searchTerm && !queryParams.search) {
        filteredIndicators = filteredIndicators.filter(i =>
          i.value.toLowerCase().includes(searchTerm.toLowerCase()) ||
          i.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          i.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())) ||
          (i.sharing_info && i.sharing_info.sharing_organization && i.sharing_info.sharing_organization.toLowerCase().includes(searchTerm.toLowerCase()))
        );
      }

      // console.log(`📊 Setting ${filteredIndicators.length} indicators (${sharedIndicators.length} shared)`);
      setIndicators(filteredIndicators);

      // Clear error if fetch was successful
      if (error) {
        setError(null);
      }

    } catch (err) {
      console.error('❌ Error fetching indicators:', err);
      if (showLoading) {
        setError(err.message);
      }
      // Don't show error for silent refreshes to avoid UI disruption
    } finally {
      if (showLoading) {
        setLoading(false);
      } else {
        setRefreshing(false);
      }
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

  // Selection logic
  const handleSelectAll = () => {
    if (selectedIndicators.size === currentItems.length) {
      // If all current items are selected, deselect all
      setSelectedIndicators(new Set());
    } else {
      // Select all current items
      setSelectedIndicators(new Set(currentItems.map(indicator => indicator.id)));
    }
  };

  const handleSelectIndicator = (indicatorId) => {
    const newSelected = new Set(selectedIndicators);
    if (newSelected.has(indicatorId)) {
      newSelected.delete(indicatorId);
    } else {
      newSelected.add(indicatorId);
    }
    setSelectedIndicators(newSelected);
  };

  const isAllSelected = currentItems.length > 0 && selectedIndicators.size === currentItems.length;
  const isIndeterminate = selectedIndicators.size > 0 && selectedIndicators.size < currentItems.length;

  const handleBulkDelete = () => {
    if (selectedIndicators.size === 0) return;
    setShowDeleteConfirm(true);
  };

  const handleDelete = (clickedIndicatorId) => {
    // If multiple indicators are selected and the clicked indicator is one of them,
    // delete all selected indicators. Otherwise, delete just the clicked one.
    if (selectedIndicators.size > 1 && selectedIndicators.has(clickedIndicatorId)) {
      // Bulk delete scenario
      setShowDeleteConfirm(true);
    } else if (selectedIndicators.size > 0) {
      // If some indicators are selected but clicked one is not among them,
      // select just the clicked one and delete it
      setSelectedIndicators(new Set([clickedIndicatorId]));
      setShowDeleteConfirm(true);
    } else {
      // Single delete scenario
      setSelectedIndicators(new Set([clickedIndicatorId]));
      setShowDeleteConfirm(true);
    }
  };

  const confirmBulkDelete = async () => {
    setDeleting(true);
    try {
      const selectedIds = Array.from(selectedIndicators);
      
      // Make DELETE requests for each selected indicator
      const deletePromises = selectedIds.map(async (id) => {
        const response = await fetch(`/api/indicators/${id}/`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            ...(localStorage.getItem('token') && {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            })
          }
        });
        
        if (!response.ok) {
          throw new Error(`Failed to delete indicator ${id}: ${response.status}`);
        }
        
        return id;
      });

      await Promise.all(deletePromises);
      
      console.log(`Successfully deleted ${selectedIds.length} indicators`);
      
      // Clear selections and refresh data
      setSelectedIndicators(new Set());
      setShowDeleteConfirm(false);
      fetchIndicators();
      
    } catch (error) {
      console.error('Error during bulk delete:', error);
      showError('Delete Error', `Error deleting indicators: ${error.message}`);
    } finally {
      setDeleting(false);
    }
  };

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
          <div className="refresh-controls">
            <button
              className={`btn btn-outline ${autoRefresh ? 'active' : ''}`}
              onClick={() => setAutoRefresh(!autoRefresh)}
              title={autoRefresh ? 'Auto-refresh enabled (every 5s) - Click to disable' : 'Auto-refresh disabled - Click to enable'}
            >
              <i className={`fas fa-sync-alt ${autoRefresh ? 'fa-spin' : ''}`}></i>
              {autoRefresh ? 'Auto ON' : 'Auto OFF'}
            </button>
            <button
              className="btn btn-outline"
              onClick={() => {
                fetchIndicators(true);
                setLastRefresh(new Date());
              }}
              title="Manual refresh now"
            >
              <i className="fas fa-refresh"></i>
              Refresh
            </button>
            <span className="last-refresh">
              Last: {lastRefresh.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
              {autoRefresh && <small style={{display: 'block', color: '#28a745'}}>Auto: 5s</small>}
              {refreshing && <small style={{display: 'block', color: '#ffc107'}}>Syncing...</small>}
            </span>
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
            <i className="fas fa-share-alt" style={{color: '#17a2b8'}}></i>
          </div>
          <div className="stat-content">
            <h3>{sharedIndicators.length.toLocaleString()}</h3>
            <p>Shared with Us</p>
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
          All Indicators
        </button>
        <button
          className={`filter-btn ${filter === 'own' ? 'active' : ''}`}
          onClick={() => setFilter('own')}
        >
          <i className="fas fa-home"></i> Own Indicators
        </button>
        <button
          className={`filter-btn ${filter === 'shared' ? 'active' : ''}`}
          onClick={() => setFilter('shared')}
        >
          <i className="fas fa-share-alt"></i> Shared with Us
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
      </div>

      {selectedIndicators.size > 0 && (
        <div className="selection-info">
          <i className="fas fa-check-circle"></i>
          {selectedIndicators.size} indicator{selectedIndicators.size !== 1 ? 's' : ''} selected
          <div className="selection-actions">
            <button 
              className="btn btn-sm btn-danger"
              onClick={handleBulkDelete}
              title="Delete selected indicators"
            >
              <i className="fas fa-trash"></i>
              Delete Selected
            </button>
            <button 
              className="btn btn-sm btn-outline"
              onClick={() => setSelectedIndicators(new Set())}
              title="Clear selection"
            >
              <i className="fas fa-times"></i>
              Clear
            </button>
          </div>
        </div>
      )}

      <div className="table-container">
        <table className="indicators-table">
          <thead>
            <tr>
              <th className="select-column">
                <input
                  type="checkbox"
                  checked={isAllSelected}
                  ref={(input) => {
                    if (input) input.indeterminate = isIndeterminate;
                  }}
                  onChange={handleSelectAll}
                  title={selectedIndicators.size > 0 ? `${selectedIndicators.size} selected` : 'Select all'}
                />
              </th>
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
              <tr key={indicator.id} className={indicator.is_shared ? 'shared-indicator' : ''}>
                <td className="select-column">
                  <input
                    type="checkbox"
                    checked={selectedIndicators.has(indicator.id)}
                    onChange={() => handleSelectIndicator(indicator.id)}
                  />
                </td>
                <td>
                  <div className="type-cell">
                    <i className={getTypeIcon(indicator.type)}></i>
                    {indicator.type}
                    {indicator.is_shared && (
                      <span className="shared-badge" title={`Shared by ${indicator.sharing_info?.sharing_organization}`}>
                        <i className="fas fa-share-alt"></i>
                      </span>
                    )}
                  </div>
                </td>
                <td>
                  <div className="value-cell">
                    <span className="value">{indicator.value}</span>
                    <div className="tags">
                      {indicator.is_shared && (
                        <span className="tag shared-tag">
                          <i className="fas fa-share-alt"></i> Shared
                        </span>
                      )}
                      {indicator.tags.slice(0, indicator.is_shared ? 1 : 2).map(tag => (
                        <span key={tag} className="tag">{tag}</span>
                      ))}
                      {indicator.tags.length > (indicator.is_shared ? 1 : 2) && (
                        <span className="tag">+{indicator.tags.length - (indicator.is_shared ? 1 : 2)}</span>
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
                  <div className="source-cell">
                    <span className="source">{indicator.source}</span>
                    {indicator.sharing && indicator.sharing.is_shared && (
                      <div className="sharing-details">
                        <small className="shared-badge">
                          <i className="fas fa-share"></i>
                          Shared from {indicator.sharing_info?.sharing_organization || indicator.sharing.shared_from}
                        </small>
                        <small className="share-date">
                          {new Date(indicator.sharing.shared_at).toLocaleDateString()}
                        </small>
                        {indicator.sharing.anonymization_level && indicator.sharing.anonymization_level !== 'none' && (
                          <small className="anonymization-badge">
                            <i className="fas fa-user-secret"></i>
                            {indicator.sharing.anonymization_level}
                          </small>
                        )}
                      </div>
                    )}
                  </div>
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
                    {!indicator.is_shared && (
                      <>
                        <button className="btn-icon" title="Share Indicator">
                          <i className="fas fa-share"></i>
                        </button>
                        <button className="btn-icon" title="Block">
                          <i className="fas fa-ban"></i>
                        </button>
                      </>
                    )}
                    <button className="btn-icon" title="Export">
                      <i className="fas fa-download"></i>
                    </button>
                    <button 
                      className="btn-icon delete-btn" 
                      onClick={() => handleDelete(indicator.id)}
                      title={selectedIndicators.size > 1 ? `Delete ${selectedIndicators.size} selected indicators` : "Delete indicator"}
                    >
                      <i className="fas fa-trash"></i>
                      {selectedIndicators.size > 1 && selectedIndicators.has(indicator.id) && (
                        <span className="bulk-indicator">{selectedIndicators.size}</span>
                      )}
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

      {/* Bulk Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Confirm Bulk Delete</h3>
              <i className="fas fa-exclamation-triangle" style={{color: '#dc3545', marginLeft: '10px'}}></i>
            </div>
            <div className="modal-body">
              {deleting ? (
                <div style={{textAlign: 'center', padding: '20px'}}>
                  <i className="fas fa-spinner fa-spin" style={{fontSize: '32px', color: '#007bff', marginBottom: '15px'}}></i>
                  <p style={{fontSize: '16px', margin: '10px 0'}}>Deleting {selectedIndicators.size} indicator{selectedIndicators.size !== 1 ? 's' : ''}...</p>
                  <p style={{color: '#6c757d', fontSize: '14px'}}>Please wait, this may take a moment.</p>
                </div>
              ) : (
                <>
                  <p>Are you sure you want to delete <strong>{selectedIndicators.size}</strong> selected indicator{selectedIndicators.size !== 1 ? 's' : ''}?</p>
                  <p style={{color: '#dc3545', fontSize: '14px', marginTop: '10px'}}>
                    <i className="fas fa-warning"></i> This action cannot be undone.
                  </p>
                </>
              )}
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-outline"
                onClick={() => setShowDeleteConfirm(false)}
                disabled={deleting}
              >
                Cancel
              </button>
              <button 
                className="btn btn-danger"
                onClick={confirmBulkDelete}
                disabled={deleting}
              >
                {deleting ? (
                  <>
                    <i className="fas fa-spinner fa-spin"></i>
                    Deleting...
                  </>
                ) : (
                  <>
                    <i className="fas fa-trash"></i>
                    Delete {selectedIndicators.size} Indicator{selectedIndicators.size !== 1 ? 's' : ''}
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
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

        .refresh-controls {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .refresh-controls .btn {
          padding: 6px 12px;
          font-size: 12px;
        }

        .refresh-controls .btn.active {
          background: #0056b3;
          color: white;
          border-color: #0056b3;
        }

        .last-refresh {
          font-size: 11px;
          color: #6c757d;
          white-space: nowrap;
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

        .delete-btn {
          position: relative;
        }

        .delete-btn:hover {
          background: #fee;
          color: #dc3545;
        }

        .bulk-indicator {
          position: absolute;
          top: -6px;
          right: -6px;
          background: #dc3545;
          color: white;
          border-radius: 50%;
          width: 18px;
          height: 18px;
          font-size: 10px;
          font-weight: bold;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 2px solid white;
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

        /* Shared indicator styles */
        .shared-indicator {
          background: #f8fdff;
          border-left: 3px solid #17a2b8;
        }

        .shared-badge {
          margin-left: 8px;
          padding: 2px 6px;
          background: #17a2b8;
          color: white;
          border-radius: 10px;
          font-size: 10px;
        }

        .shared-tag {
          background: #17a2b8 !important;
          color: white !important;
        }

        .sharing-details {
          margin-top: 2px;
        }

        .sharing-details small {
          color: #17a2b8;
          font-size: 10px;
          font-style: italic;
        }

        .source-cell {
          display: flex;
          flex-direction: column;
        }

        .filter-btn i {
          margin-right: 5px;
        }

        .sharing-details .shared-badge {
          background: #17a2b8;
          color: white;
          padding: 2px 6px;
          border-radius: 8px;
          font-size: 10px;
          margin-right: 4px;
          display: inline-flex;
          align-items: center;
          gap: 3px;
        }

        .sharing-details .share-date {
          color: #6c757d;
          font-size: 10px;
          display: block;
          margin-top: 2px;
        }

        .sharing-details .anonymization-badge {
          background: #ffc107;
          color: #212529;
          padding: 2px 6px;
          border-radius: 8px;
          font-size: 10px;
          margin-top: 2px;
          display: inline-flex;
          align-items: center;
          gap: 3px;
        }

        .select-column {
          width: 40px;
          text-align: center;
          padding: 8px !important;
        }

        .select-column input[type="checkbox"] {
          cursor: pointer;
          transform: scale(1.1);
        }

        .select-column input[type="checkbox"]:indeterminate {
          background-color: #0056b3;
        }

        .selection-info {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 12px 16px;
          background: #e3f2fd;
          border: 1px solid #bbdefb;
          border-radius: 8px;
          margin-bottom: 16px;
          color: #0056b3;
          font-weight: 500;
        }

        .selection-info i {
          color: #0056b3;
        }

        .selection-info .btn {
          margin-left: auto;
        }

        .selection-actions {
          display: flex;
          gap: 8px;
          margin-left: auto;
        }

        .btn-danger {
          background: #dc3545;
          color: white;
          border: 1px solid #dc3545;
        }

        .btn-danger:hover {
          background: #c82333;
          border-color: #bd2130;
        }

        /* Modal Styles */
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal-content {
          background: white;
          border-radius: 8px;
          padding: 0;
          max-width: 500px;
          width: 90%;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }

        .modal-header {
          padding: 20px;
          border-bottom: 1px solid #dee2e6;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .modal-header h3 {
          margin: 0;
          color: #333;
          font-size: 18px;
        }

        .modal-body {
          padding: 20px;
          color: #495057;
          line-height: 1.5;
        }

        .modal-body p {
          margin: 0 0 10px 0;
        }

        .modal-actions {
          padding: 20px;
          border-top: 1px solid #dee2e6;
          display: flex;
          gap: 10px;
          justify-content: flex-end;
        }
      `}</style>
    </div>
  );
};

export default IndicatorTable;
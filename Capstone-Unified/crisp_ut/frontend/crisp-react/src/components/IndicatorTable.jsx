import React, { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner.jsx';
import Pagination from './Pagination.jsx';
import './modal-styles.css';

const IndicatorTable = ({ active = true, userRole = 'admin' }) => {
  const [indicators, setIndicators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({});
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(20);
  const [editingIndicator, setEditingIndicator] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  useEffect(() => {
    if (active) {
      loadIndicators();
      loadIndicatorStats();
    }
  }, [active]);

  const loadIndicators = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('crisp_auth_token');
      console.log('Fetching indicators from API...');
      
      const response = await fetch('http://localhost:8000/api/indicators/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch indicators`);
      }

      const data = await response.json();
      console.log('Indicators loaded from API:', data);
      
      const indicators = Array.isArray(data) ? data : (data.data || data.results || []);
      setIndicators(indicators);
    } catch (err) {
      console.error('Error loading indicators:', err);
      setError(err.message || 'Failed to load indicators');
    } finally {
      setLoading(false);
    }
  };

  const loadIndicatorStats = async () => {
    try {
      const token = localStorage.getItem('crisp_auth_token');
      
      const response = await fetch('http://localhost:8000/api/indicators/stats/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const statsData = await response.json();
        console.log('Indicator stats loaded:', statsData);
        setStats(statsData);
      }
    } catch (err) {
      console.error('Error loading indicator stats:', err);
    }
  };

  const formatValue = (value, type) => {
    if (value.length > 50) {
      return value.substring(0, 50) + '...';
    }
    return value;
  };

  const getTypeIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'domain':
        return 'fas fa-globe';
      case 'url':
        return 'fas fa-link';
      case 'file_hash':
        return 'fas fa-fingerprint';
      case 'ip':
      case 'ipv4-addr':
      case 'ipv6-addr':
        return 'fas fa-network-wired';
      case 'email':
        return 'fas fa-envelope';
      default:
        return 'fas fa-search';
    }
  };

  const getConfidenceBadge = (confidence) => {
    if (confidence >= 80) return 'badge-high';
    if (confidence >= 60) return 'badge-medium';
    return 'badge-low';
  };

  const handleEdit = (indicator) => {
    setEditingIndicator({...indicator});
    setShowEditModal(true);
  };

  const handleSaveEdit = async () => {
    if (!editingIndicator) return;

    try {
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch(`http://localhost:8000/api/indicators/${editingIndicator.id}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          type: editingIndicator.type,
          value: editingIndicator.value,
          description: editingIndicator.description,
          confidence: editingIndicator.confidence,
          is_anonymized: editingIndicator.is_anonymized,
          hash_type: editingIndicator.hash_type
        })
      });

      if (response.ok) {
        setShowEditModal(false);
        setEditingIndicator(null);
        loadIndicators(); // Reload the list
        alert('Indicator updated successfully');
      } else {
        throw new Error(`HTTP ${response.status}: Failed to update indicator`);
      }
    } catch (err) {
      console.error('Error updating indicator:', err);
      alert(`Error updating indicator: ${err.message}`);
    }
  };

  const handleDelete = (indicator) => {
    setDeleteConfirm(indicator);
  };

  const confirmDelete = async () => {
    if (!deleteConfirm) return;

    try {
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch(`http://localhost:8000/api/indicators/${deleteConfirm.id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setDeleteConfirm(null);
        loadIndicators(); // Reload the list
        alert('Indicator deleted successfully');
      } else {
        throw new Error(`HTTP ${response.status}: Failed to delete indicator`);
      }
    } catch (err) {
      console.error('Error deleting indicator:', err);
      alert(`Error deleting indicator: ${err.message}`);
    }
  };

  // Pagination
  const totalItems = indicators.length;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedIndicators = indicators.slice(startIndex, startIndex + itemsPerPage);

  if (loading) {
    return (
      <div className="card">
        <div className="card-content">
          <LoadingSpinner />
          <p>Loading real threat indicators from AlienVault OTX...</p>
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
            <button className="btn btn-primary" onClick={loadIndicators}>
              <i className="fas fa-sync-alt"></i> Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="ioc-management-container">
      {/* Statistics Cards */}
      {Object.keys(stats).length > 0 && (
        <div className="stats-grid mb-4">
          <div className="stat-card">
            <div className="stat-title">
              <div className="stat-icon"><i className="fas fa-search"></i></div>
              <span>Total Indicators</span>
            </div>
            <div className="stat-value">{stats.total || 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-title">
              <div className="stat-icon"><i className="fas fa-clock"></i></div>
              <span>Recent (24h)</span>
            </div>
            <div className="stat-value">{stats.recent_24h || 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-title">
              <div className="stat-icon"><i className="fas fa-shield-alt"></i></div>
              <span>High Confidence</span>
            </div>
            <div className="stat-value">{stats.high_confidence || 0}</div>
          </div>
        </div>
      )}

      {/* Main Indicators Table */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <i className="fas fa-search card-icon"></i> 
            Real Threat Indicators ({totalItems})
          </h2>
          <div className="card-actions">
            <button className="btn btn-outline btn-sm" onClick={loadIndicators}>
              <i className="fas fa-sync-alt"></i> Refresh
            </button>
          </div>
        </div>
        <div className="card-content">
          {indicators.length === 0 ? (
            <div className="empty-state">
              <i className="fas fa-search"></i>
              <p>No indicators found</p>
              <p>Import threat data or add indicators manually</p>
            </div>
          ) : (
            <>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Value</th>
                    <th>Confidence</th>
                    <th>First Seen</th>
                    <th>Last Seen</th>
                    <th>Source</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedIndicators.map((indicator) => (
                    <tr key={indicator.id}>
                      <td>
                        <div className="indicator-type">
                          <i className={getTypeIcon(indicator.type)}></i>
                          <span>{indicator.type}</span>
                        </div>
                      </td>
                      <td>
                        <span className="indicator-value" title={indicator.value}>
                          {formatValue(indicator.value, indicator.type)}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${getConfidenceBadge(indicator.confidence)}`}>
                          {indicator.confidence}%
                        </span>
                      </td>
                      <td>
                        {indicator.first_seen ? 
                          new Date(indicator.first_seen).toLocaleDateString() : 'Unknown'}
                      </td>
                      <td>
                        {indicator.last_seen ? 
                          new Date(indicator.last_seen).toLocaleDateString() : 'Unknown'}
                      </td>
                      <td>
                        <span className="badge badge-connected">
                          AlienVault OTX
                        </span>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button 
                            className="btn btn-outline btn-sm" 
                            onClick={() => handleEdit(indicator)}
                            title="Edit Indicator"
                          >
                            <i className="fas fa-edit"></i>
                          </button>
                          <button 
                            className="btn btn-danger btn-sm ml-1" 
                            onClick={() => handleDelete(indicator)}
                            title="Delete Indicator"
                          >
                            <i className="fas fa-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Pagination */}
              {totalItems > itemsPerPage && (
                <Pagination
                  currentPage={currentPage}
                  totalItems={totalItems}
                  itemsPerPage={itemsPerPage}
                  onPageChange={setCurrentPage}
                />
              )}
            </>
          )}
        </div>
      </div>

      {/* Edit Modal */}
      {showEditModal && editingIndicator && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Edit Indicator</h3>
              <button className="modal-close" onClick={() => setShowEditModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Type</label>
                <select 
                  value={editingIndicator.type} 
                  onChange={e => setEditingIndicator({...editingIndicator, type: e.target.value})}
                >
                  <option value="domain">Domain</option>
                  <option value="url">URL</option>
                  <option value="file_hash">File Hash</option>
                  <option value="ipv4-addr">IPv4 Address</option>
                  <option value="ipv6-addr">IPv6 Address</option>
                  <option value="email">Email</option>
                </select>
              </div>
              <div className="form-group">
                <label>Value</label>
                <input 
                  type="text" 
                  value={editingIndicator.value} 
                  onChange={e => setEditingIndicator({...editingIndicator, value: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea 
                  value={editingIndicator.description || ''} 
                  onChange={e => setEditingIndicator({...editingIndicator, description: e.target.value})}
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>Confidence (%)</label>
                <input 
                  type="number" 
                  min="0" 
                  max="100" 
                  value={editingIndicator.confidence || 50} 
                  onChange={e => setEditingIndicator({...editingIndicator, confidence: parseInt(e.target.value)})}
                />
              </div>
              {editingIndicator.type === 'file_hash' && (
                <div className="form-group">
                  <label>Hash Type</label>
                  <select 
                    value={editingIndicator.hash_type || ''} 
                    onChange={e => setEditingIndicator({...editingIndicator, hash_type: e.target.value})}
                  >
                    <option value="">Select Hash Type</option>
                    <option value="MD5">MD5</option>
                    <option value="SHA1">SHA1</option>
                    <option value="SHA256">SHA256</option>
                    <option value="SHA512">SHA512</option>
                  </select>
                </div>
              )}
              <div className="form-group">
                <label>
                  <input 
                    type="checkbox" 
                    checked={editingIndicator.is_anonymized || false} 
                    onChange={e => setEditingIndicator({...editingIndicator, is_anonymized: e.target.checked})}
                  />
                  Anonymized
                </label>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setShowEditModal(false)}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleSaveEdit}>
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="modal-overlay" onClick={() => setDeleteConfirm(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Confirm Delete</h3>
              <button className="modal-close" onClick={() => setDeleteConfirm(null)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <p>Are you sure you want to delete this indicator?</p>
              <div className="indicator-preview">
                <strong>Type:</strong> {deleteConfirm.type}<br/>
                <strong>Value:</strong> {deleteConfirm.value}<br/>
                <strong>Confidence:</strong> {deleteConfirm.confidence}%
              </div>
              <p className="warning-text">
                <i className="fas fa-exclamation-triangle"></i>
                This action cannot be undone.
              </p>
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setDeleteConfirm(null)}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={confirmDelete}>
                Delete Indicator
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IndicatorTable;
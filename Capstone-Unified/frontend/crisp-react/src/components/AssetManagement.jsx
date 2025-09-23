/**
 * Asset Management Component for CRISP WOW Factor #1
 * Provides UI for managing asset inventories and viewing custom alerts
 */

import React, { useState, useEffect } from 'react';
import './AssetManagement.css';

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('crisp_auth_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

const AssetManagement = ({ active }) => {
  const [activeTab, setActiveTab] = useState('inventory');
  const [assets, setAssets] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showAddAsset, setShowAddAsset] = useState(false);
  const [showBulkUpload, setShowBulkUpload] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [filters, setFilters] = useState({
    assetType: '',
    criticality: '',
    alertStatus: '',
    severity: ''
  });

  // Load data on component mount and tab changes
  useEffect(() => {
    if (active) {
      if (activeTab === 'inventory') {
        loadAssets();
      } else if (activeTab === 'alerts') {
        loadAlerts();
      } else if (activeTab === 'statistics') {
        loadStatistics();
      }
    }
  }, [active, activeTab, filters]);

  const loadAssets = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.assetType) params.append('asset_type', filters.assetType);
      if (filters.criticality) params.append('criticality', filters.criticality);

      const response = await fetch(`/api/assets/inventory/?${params}`, {
        headers: getAuthHeaders()
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Asset data received:', data);
        const assetsArray = data.results?.data || data.data || data.results || [];
        console.log('Parsed assets array:', assetsArray);
        setAssets(assetsArray);
      } else {
        console.error('Failed to load assets');
      }
    } catch (error) {
      console.error('Error loading assets:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.alertStatus) params.append('status', filters.alertStatus);
      if (filters.severity) params.append('severity', filters.severity);

      const response = await fetch(`/api/assets/alerts/?${params}`, {
        headers: getAuthHeaders()
      });

      if (response.ok) {
        const data = await response.json();
        setAlerts(data.results?.data || data.data || data.results || []);
      } else {
        console.error('Failed to load alerts');
      }
    } catch (error) {
      console.error('Error loading alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/assets/statistics/', {
        headers: getAuthHeaders()
      });

      if (response.ok) {
        const data = await response.json();
        setStatistics(data.results?.data || data.data || data.results || {});
      } else {
        console.error('Failed to load statistics');
      }
    } catch (error) {
      console.error('Error loading statistics:', error);
    } finally {
      setLoading(false);
    }
  };

  const triggerCorrelation = async () => {
    try {
      const response = await fetch('/api/assets/correlation/trigger/', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ days: 1 })
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Correlation triggered successfully! Generated ${data.data.alerts_generated} alerts.`);
        if (activeTab === 'alerts') {
          loadAlerts();
        }
      } else {
        alert('Failed to trigger correlation');
      }
    } catch (error) {
      console.error('Error triggering correlation:', error);
      alert('Error triggering correlation');
    }
  };

  const handleAlertAction = async (alertId, action) => {
    try {
      const response = await fetch(`/api/assets/alerts/${alertId}/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ action })
      });

      if (response.ok) {
        alert(`Alert ${action} successfully`);
        loadAlerts();
        setSelectedAlert(null);
      } else {
        alert(`Failed to ${action} alert`);
      }
    } catch (error) {
      console.error(`Error ${action} alert:`, error);
    }
  };

  const getSeverityIcon = (severity) => {
    const icons = {
      critical: '🔴',
      high: '🟠',
      medium: '🟡',
      low: '🟢',
      info: '🔵'
    };
    return icons[severity] || '⚪';
  };

  const getCriticalityIcon = (criticality) => {
    const icons = {
      critical: '🔴',
      high: '🟠',
      medium: '🟡',
      low: '🟢'
    };
    return icons[criticality] || '⚪';
  };

  const renderInventoryTab = () => (
    <div className="inventory-tab">
      <div style={{background: 'red', color: 'white', padding: '20px', fontSize: '20px', border: '5px solid yellow'}}>
        🚨 DEBUG: INVENTORY TAB RENDERING - Active: {active ? 'YES' : 'NO'}, Loading: {loading ? 'YES' : 'NO'}, Assets: {assets.length}
      </div>
      <div className="tab-header">
        <h3>Asset Inventory</h3>
        <div className="tab-actions">
          <button onClick={() => setShowAddAsset(true)} className="btn btn-primary">
            Add Asset
          </button>
          <button onClick={() => setShowBulkUpload(true)} className="btn btn-secondary">
            Bulk Upload
          </button>
          <button onClick={triggerCorrelation} className="btn btn-warning">
            Trigger Correlation
          </button>
        </div>
      </div>

      <div className="filters">
        <select
          value={filters.assetType}
          onChange={(e) => setFilters({...filters, assetType: e.target.value})}
        >
          <option value="">All Asset Types</option>
          <option value="ip_range">IP Range</option>
          <option value="domain">Domain</option>
          <option value="software">Software</option>
          <option value="hardware">Hardware</option>
          <option value="service">Service</option>
        </select>

        <select
          value={filters.criticality}
          onChange={(e) => setFilters({...filters, criticality: e.target.value})}
        >
          <option value="">All Criticality Levels</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      <div style={{background: 'red', padding: '10px', margin: '10px'}}>
        DEBUG: Component Active: {active ? 'YES' : 'NO'}, Loading: {loading ? 'YES' : 'NO'}, Assets: {assets.length}
      </div>

      {loading ? (
        <div className="loading">Loading assets...</div>
      ) : (
        <div className="assets-table">
          <div style={{background: 'yellow', padding: '5px', margin: '5px'}}>
            DEBUG: Table container - Assets length: {assets.length}
          </div>
          <table style={{border: '2px solid blue', width: '100%'}}>
            <thead style={{background: 'lightgreen'}}>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Value</th>
                <th>Criticality</th>
                <th>Environment</th>
                <th>Alerts</th>
                <th>Alert Enabled</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody style={{background: 'lightblue'}}>
              <tr style={{background: 'orange', border: '2px solid red'}}>
                <td>HARDCODED TEST ROW</td>
                <td>Should Always Show</td>
                <td>No Conditions</td>
                <td>Test</td>
                <td>Test</td>
                <td>Test</td>
                <td>Test</td>
                <td>Test</td>
              </tr>
              {assets.map((asset, index) => (
                <tr key={asset.id} style={{background: 'pink', border: '1px solid green'}}>
                  <td>REAL ROW {index + 1}: {asset.name}</td>
                  <td>{asset.asset_type_display}</td>
                  <td className="asset-value">{asset.asset_value}</td>
                  <td>
                    {getCriticalityIcon(asset.criticality)} {asset.criticality_display}
                  </td>
                  <td>{asset.environment}</td>
                  <td>{asset.alert_count}</td>
                  <td>
                    <span className={`status ${asset.alert_enabled ? 'enabled' : 'disabled'}`}>
                      {asset.alert_enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </td>
                  <td className="actions">
                    <button
                      onClick={() => setSelectedAsset(asset)}
                      className="btn btn-sm btn-outline"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  const renderAlertsTab = () => (
    <div className="alerts-tab">
      <div className="tab-header">
        <h3>Custom Alerts</h3>
        <div className="tab-actions">
          <button onClick={triggerCorrelation} className="btn btn-warning">
            Trigger Correlation
          </button>
        </div>
      </div>

      <div className="filters">
        <select
          value={filters.alertStatus}
          onChange={(e) => setFilters({...filters, alertStatus: e.target.value})}
        >
          <option value="">All Statuses</option>
          <option value="new">New</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="investigating">Investigating</option>
          <option value="resolved">Resolved</option>
          <option value="false_positive">False Positive</option>
        </select>

        <select
          value={filters.severity}
          onChange={(e) => setFilters({...filters, severity: e.target.value})}
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
          <option value="info">Info</option>
        </select>
      </div>

      {loading ? (
        <div className="loading">Loading alerts...</div>
      ) : (
        <div className="alerts-table">
          <table>
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Title</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Assets</th>
                <th>Confidence</th>
                <th>Detected</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map(alert => (
                <tr key={alert.id} className={`alert-row ${alert.severity}`}>
                  <td>{alert.alert_id}</td>
                  <td className="alert-title">{alert.title}</td>
                  <td>
                    {getSeverityIcon(alert.severity)} {alert.severity_display}
                  </td>
                  <td>
                    <span className={`status ${alert.status}`}>
                      {alert.status_display}
                    </span>
                  </td>
                  <td>{alert.matched_assets_count}</td>
                  <td>{Math.round(alert.confidence_score * 100)}%</td>
                  <td>{new Date(alert.detected_at).toLocaleDateString()}</td>
                  <td className="actions">
                    <button
                      onClick={() => setSelectedAlert(alert)}
                      className="btn btn-sm btn-outline"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  const renderStatisticsTab = () => (
    <div className="statistics-tab">
      <h3>Asset & Alert Statistics</h3>

      {loading ? (
        <div className="loading">Loading statistics...</div>
      ) : statistics ? (
        <div className="stats-grid">
          <div className="stat-card">
            <h4>Asset Overview</h4>
            <div className="stat-item">
              <span>Total Assets:</span>
              <span>{statistics.asset_statistics.total_assets}</span>
            </div>
            <div className="stat-item">
              <span>Alert Enabled:</span>
              <span>{statistics.asset_statistics.alert_enabled_assets}</span>
            </div>
            <div className="stat-item">
              <span>Coverage:</span>
              <span>{statistics.asset_statistics.alert_coverage_percentage}%</span>
            </div>
          </div>

          <div className="stat-card">
            <h4>Alert Statistics</h4>
            <div className="stat-item">
              <span>Total Alerts:</span>
              <span>{statistics.alert_statistics.total_alerts}</span>
            </div>
            <div className="stat-item">
              <span>Recent (30d):</span>
              <span>{statistics.alert_statistics.recent_alerts}</span>
            </div>
            <div className="stat-item">
              <span>Avg Confidence:</span>
              <span>{Math.round(statistics.alert_statistics.avg_confidence * 100)}%</span>
            </div>
          </div>

          <div className="stat-card">
            <h4>Assets by Type</h4>
            {Object.entries(statistics.asset_statistics.by_type).map(([type, count]) => (
              <div key={type} className="stat-item">
                <span>{type}:</span>
                <span>{count}</span>
              </div>
            ))}
          </div>

          <div className="stat-card">
            <h4>Alerts by Severity</h4>
            {Object.entries(statistics.alert_statistics.by_severity).map(([severity, count]) => (
              <div key={severity} className="stat-item">
                <span>{getSeverityIcon(severity)} {severity}:</span>
                <span>{count}</span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div>No statistics available</div>
      )}
    </div>
  );

  const renderAssetModal = () => {
    if (!selectedAsset) return null;

    return (
      <div className="modal-overlay" onClick={() => setSelectedAsset(null)}>
        <div className="modal" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h3>Asset Details</h3>
            <button onClick={() => setSelectedAsset(null)}>✕</button>
          </div>
          <div className="modal-body">
            <div className="asset-details">
              <div className="detail-row">
                <strong>Name:</strong> {selectedAsset.name}
              </div>
              <div className="detail-row">
                <strong>Type:</strong> {selectedAsset.asset_type_display}
              </div>
              <div className="detail-row">
                <strong>Value:</strong> {selectedAsset.asset_value}
              </div>
              <div className="detail-row">
                <strong>Criticality:</strong> {getCriticalityIcon(selectedAsset.criticality)} {selectedAsset.criticality_display}
              </div>
              <div className="detail-row">
                <strong>Environment:</strong> {selectedAsset.environment}
              </div>
              <div className="detail-row">
                <strong>Alert Enabled:</strong> {selectedAsset.alert_enabled ? 'Yes' : 'No'}
              </div>
              <div className="detail-row">
                <strong>Created:</strong> {new Date(selectedAsset.created_at).toLocaleString()}
              </div>

              {selectedAsset.recent_alerts && selectedAsset.recent_alerts.length > 0 && (
                <div className="recent-alerts">
                  <h4>Recent Alerts</h4>
                  {selectedAsset.recent_alerts.map(alert => (
                    <div key={alert.id} className="alert-item">
                      <span>{getSeverityIcon(alert.severity)} {alert.title}</span>
                      <span>{new Date(alert.detected_at).toLocaleDateString()}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderAlertModal = () => {
    if (!selectedAlert) return null;

    return (
      <div className="modal-overlay" onClick={() => setSelectedAlert(null)}>
        <div className="modal large" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h3>Alert Details - {selectedAlert.alert_id}</h3>
            <button onClick={() => setSelectedAlert(null)}>✕</button>
          </div>
          <div className="modal-body">
            <div className="alert-details">
              <div className="alert-meta">
                <span className={`severity-badge ${selectedAlert.severity}`}>
                  {getSeverityIcon(selectedAlert.severity)} {selectedAlert.severity_display}
                </span>
                <span className={`status-badge ${selectedAlert.status}`}>
                  {selectedAlert.status_display}
                </span>
                <span className="confidence">
                  Confidence: {Math.round(selectedAlert.confidence_score * 100)}%
                </span>
              </div>

              <div className="alert-title">
                <h4>{selectedAlert.title}</h4>
              </div>

              <div className="alert-description">
                <p>{selectedAlert.description}</p>
              </div>

              <div className="alert-assets">
                <h5>Affected Assets ({selectedAlert.matched_assets_count})</h5>
                <div className="asset-summary">
                  {selectedAlert.asset_summary && Object.entries(selectedAlert.asset_summary.by_criticality).map(([criticality, count]) => (
                    <span key={criticality} className="asset-count">
                      {getCriticalityIcon(criticality)} {criticality}: {count}
                    </span>
                  ))}
                </div>
              </div>

              {selectedAlert.response_actions && selectedAlert.response_actions.length > 0 && (
                <div className="response-actions">
                  <h5>Recommended Actions</h5>
                  {selectedAlert.response_actions.map((action, index) => (
                    <div key={index} className={`action-item ${action.priority}`}>
                      <strong>{action.title}</strong>
                      <p>{action.description}</p>
                    </div>
                  ))}
                </div>
              )}

              <div className="alert-actions">
                {selectedAlert.status === 'new' && (
                  <button
                    onClick={() => handleAlertAction(selectedAlert.id, 'acknowledge')}
                    className="btn btn-primary"
                  >
                    Acknowledge
                  </button>
                )}
                {selectedAlert.is_active && (
                  <>
                    <button
                      onClick={() => handleAlertAction(selectedAlert.id, 'resolve')}
                      className="btn btn-success"
                    >
                      Resolve
                    </button>
                    <button
                      onClick={() => handleAlertAction(selectedAlert.id, 'false_positive')}
                      className="btn btn-warning"
                    >
                      False Positive
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // FORCE RENDER FOR DEBUGGING - REMOVE LATER
  // if (!active) return null;

  return (
    <div className="asset-management">
      <div style={{background: 'purple', color: 'yellow', padding: '15px', fontSize: '18px', border: '3px solid orange'}}>
        🔥 MAIN COMPONENT DEBUG: ActiveTab = "{activeTab}", Active = {active ? 'YES' : 'NO'}
      </div>
      <div className="asset-header">
        <h2>🎯 Asset-Based Alert System</h2>
        <p>Custom threat intelligence based on your infrastructure</p>
      </div>

      <div className="tab-navigation">
        <button
          className={`tab-btn ${activeTab === 'inventory' ? 'active' : ''}`}
          onClick={() => setActiveTab('inventory')}
        >
          Asset Inventory
        </button>
        <button
          className={`tab-btn ${activeTab === 'alerts' ? 'active' : ''}`}
          onClick={() => setActiveTab('alerts')}
        >
          Custom Alerts
        </button>
        <button
          className={`tab-btn ${activeTab === 'statistics' ? 'active' : ''}`}
          onClick={() => setActiveTab('statistics')}
        >
          Statistics
        </button>
      </div>

      <div className="tab-content">
        <div style={{background: 'cyan', color: 'black', padding: '20px', fontSize: '24px', border: '5px solid red'}}>
          🚨 ALWAYS VISIBLE DEBUG - activeTab: {activeTab}
        </div>
        {activeTab === 'inventory' && (
          <div>
            <div style={{background: 'lime', padding: '10px'}}>🟢 TRYING TO RENDER INVENTORY TAB</div>
            {(() => {
              try {
                return renderInventoryTab();
              } catch (error) {
                return <div style={{background: 'red', color: 'white', padding: '20px'}}>❌ ERROR IN INVENTORY TAB: {error.toString()}</div>;
              }
            })()}
          </div>
        )}
        {activeTab === 'alerts' && renderAlertsTab()}
        {activeTab === 'statistics' && renderStatisticsTab()}
      </div>

      {renderAssetModal()}
      {renderAlertModal()}
    </div>
  );
};

export default AssetManagement;
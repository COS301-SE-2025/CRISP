import React, { useState, useEffect, Fragment } from 'react';
import { get } from '../../api';
import { getAssetInventory, createAsset, updateAsset, deleteAsset, bulkUploadAssets, getCustomAlerts, getAssetAlertStatistics, triggerAssetCorrelation, getCustomAlertDetails, updateAlertStatus, deleteAlert, clearDemoData } from '../../api/assets';
import LoadingSpinner from '../enhanced/LoadingSpinner';
import NotificationToast from '../enhanced/NotificationToast';
import ConfirmationModal from '../enhanced/ConfirmationModal';
import { useNotifications } from '../enhanced/NotificationManager.jsx';
import refreshManager from '../../utils/RefreshManager.js';
import './AssetManagement.css';

// Helper functions for standardized criticality colors - Blue/White theme
const getCriticalityColor = (criticality) => {
  switch (criticality?.toLowerCase()) {
    case 'critical': return 'var(--danger)'; // Only critical uses red
    case 'high': return 'var(--secondary-blue)';
    case 'medium': return 'var(--info)';
    case 'low': return 'var(--light-blue)';
    default: return 'var(--medium-gray)';
  }
};

const getCriticalityBgColor = (criticality) => {
  switch (criticality?.toLowerCase()) {
    case 'critical': return '#fef2f2';
    case 'high': return '#dbeafe';
    case 'medium': return '#e0f2fe';
    case 'low': return 'var(--light-blue)';
    default: return 'var(--light-gray)';
  }
};

const getCriticalityTextColor = (criticality) => {
  switch (criticality?.toLowerCase()) {
    case 'critical': return 'var(--danger)';
    case 'high': return 'var(--secondary-blue)';
    case 'medium': return 'var(--info)';
    case 'low': return 'var(--primary-blue)';
    default: return 'var(--text-muted)';
  }
};

const AssetInventoryTab = ({ assets, onAdd, onEdit, onDelete, onBulkUpload, loading }) => {
  return (
    <div style={{ padding: '1rem 0' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '2rem'
      }}>
        <div>
          <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-dark)', fontSize: '1.125rem', fontWeight: '600' }}>Asset Inventory</h3>
          <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.875rem' }}>Manage and monitor your organization's digital assets</p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={onAdd}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--success)',
              color: 'var(--white)',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500'
            }}
          >
            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Add Asset
          </button>
          <button
            onClick={onBulkUpload}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--secondary-blue)',
              color: 'var(--white)',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500'
            }}
          >
            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            Bulk Upload
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
          <LoadingSpinner />
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
          gap: '1rem',
          minHeight: '400px'
        }}>
          {assets && assets.length > 0 ? assets.map((asset, index) => (
            <div key={asset.id || index} style={{
              backgroundColor: 'white',
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
              padding: '1.5rem',
              transition: 'box-shadow 0.2s'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: getCriticalityColor(asset.criticality)
                      }}></div>
                      <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: '600', color: 'var(--text-dark)' }}>
                        {asset.name || 'Unnamed Asset'}
                      </h4>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
                      <span style={{
                        display: 'inline-block',
                        padding: '0.25rem 0.5rem',
                        fontSize: '0.75rem',
                        fontWeight: '500',
                        borderRadius: '4px',
                        backgroundColor: 'var(--light-blue)',
                        color: 'var(--info)'
                      }}>
                        {asset.asset_type_display || asset.asset_type}
                      </span>
                      <span style={{
                        display: 'inline-block',
                        padding: '0.25rem 0.5rem',
                        fontSize: '0.75rem',
                        fontWeight: '500',
                        borderRadius: '4px',
                        backgroundColor: getCriticalityBgColor(asset.criticality),
                        color: getCriticalityTextColor(asset.criticality)
                      }}>
                        {asset.criticality === 'critical' && '🔴'}
                        {asset.criticality === 'high' && '🟠'}
                        {asset.criticality === 'medium' && '🟡'}
                        {asset.criticality === 'low' && '🟢'}
                        {' ' + (asset.criticality?.charAt(0).toUpperCase() + asset.criticality?.slice(1))}
                      </span>
                    </div>
                    <div style={{ marginBottom: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        {asset.asset_value}
                      </div>
                      {asset.alert_enabled && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--success)', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                          <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                          Alerts Enabled
                        </div>
                      )}
                    </div>
                    {asset.description && (
                      <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text-muted)' }}>{asset.description}</p>
                    )}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', marginLeft: '1rem' }}>
                  <button
                    onClick={() => onEdit(asset)}
                    title="Edit asset"
                    style={{
                      padding: '0.5rem',
                      backgroundColor: 'var(--secondary-blue)',
                      color: 'var(--white)',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      console.log('Asset delete button clicked for asset:', asset);
                      onDelete(asset);
                    }}
                    title="Delete asset"
                    style={{
                      padding: '0.5rem',
                      backgroundColor: 'var(--danger)',
                      color: 'var(--white)',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      pointerEvents: 'auto',
                      position: 'relative',
                      zIndex: 20
                    }}
                  >
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          )) : (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '3rem',
              textAlign: 'center',
              gridColumn: '1 / -1'
            }}>
              <svg width="48" height="48" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
              <h3 style={{ color: 'var(--text-dark)', marginBottom: '0.5rem' }}>No assets found</h3>
              <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Get started by adding your first asset to monitor</p>
              <button
                onClick={onAdd}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.75rem 1.5rem',
                  backgroundColor: 'var(--success)',
                  color: 'var(--white)',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}
              >
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Add Asset
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const CustomAlertsTab = ({ alerts, onView, onDelete, loading, refreshInterval }) => {
  return (
    <div style={{ padding: '1rem 0' }}>
      <div style={{ marginBottom: '2rem' }}>
        <div>
          <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-dark)', fontSize: '1.125rem', fontWeight: '600' }}>Custom Asset Alerts</h3>
          <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Smart alerts generated from IoC correlation with your assets
            {refreshInterval && (
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem', marginLeft: '0.5rem', color: 'var(--success)' }}>
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Auto-refreshing
              </span>
            )}
          </p>
        </div>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
          <LoadingSpinner />
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))',
          gap: '1rem',
          minHeight: '400px'
        }}>
          {alerts && alerts.length > 0 ? alerts.map((alert, index) => (
            <div
              key={alert.id || index}
              style={{
                backgroundColor: 'white',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                padding: '1.5rem',
                transition: 'box-shadow 0.2s'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', width: '100%', position: 'relative' }}>
                <div style={{ flex: 1, minWidth: 0, marginRight: '1rem', overflow: 'hidden' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: getCriticalityColor(alert.severity)
                      }}></div>
                      <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: '600', color: 'var(--text-dark)' }}>
                        {alert.title || 'Unnamed Alert'}
                      </h4>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
                      <span style={{
                        display: 'inline-block',
                        padding: '0.25rem 0.5rem',
                        fontSize: '0.75rem',
                        fontWeight: '500',
                        borderRadius: '4px',
                        backgroundColor: getCriticalityBgColor(alert.severity),
                        color: getCriticalityTextColor(alert.severity)
                      }}>
                        {alert.severity === 'critical' && '🔴'}
                        {alert.severity === 'high' && '🟠'}
                        {alert.severity === 'medium' && '🟡'}
                        {alert.severity === 'low' && '🟢'}
                        {' ' + (alert.severity_display || alert.severity)}
                      </span>
                      <span style={{
                        display: 'inline-block',
                        padding: '0.25rem 0.5rem',
                        fontSize: '0.75rem',
                        fontWeight: '500',
                        borderRadius: '4px',
                        backgroundColor: 'var(--light-gray)',
                        color: 'var(--text-muted)'
                      }}>
                        {alert.status_display || alert.status}
                      </span>
                      {alert.confidence_score && (
                        <span style={{
                          display: 'inline-block',
                          padding: '0.25rem 0.5rem',
                          fontSize: '0.75rem',
                          fontWeight: '500',
                          borderRadius: '4px',
                          backgroundColor: 'var(--light-blue)',
                          color: 'var(--info)'
                        }}>
                          🎯 {Math.round(alert.confidence_score * 100)}% confidence
                        </span>
                      )}
                    </div>
                    <div style={{ marginBottom: '0.75rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {new Date(alert.detected_at).toLocaleString()}
                      </div>
                      {alert.matched_assets && alert.matched_assets.length > 0 && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                          <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                          </svg>
                          {alert.matched_assets.length} affected asset{alert.matched_assets.length !== 1 ? 's' : ''}
                        </div>
                      )}
                    </div>
                    {alert.description && (
                      <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                        {alert.description}
                      </p>
                    )}
                  </div>
                </div>
                <div style={{
                  display: 'flex',
                  gap: '0.5rem',
                  flexShrink: 0,
                  position: 'relative',
                  zIndex: 20,
                  alignItems: 'flex-start'
                }}>
                  <button
                    onClick={() => onView(alert)}
                    title="View alert details"
                    style={{
                      padding: '0.5rem',
                      backgroundColor: 'var(--secondary-blue)',
                      color: 'var(--white)',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      pointerEvents: 'auto',
                      position: 'relative',
                      zIndex: 30
                    }}
                  >
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      console.log('Alert delete button clicked for alert:', alert);
                      onDelete(alert);
                    }}
                    title="Delete alert"
                    style={{
                      padding: '0.5rem',
                      backgroundColor: 'var(--danger)',
                      color: 'var(--white)',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      pointerEvents: 'auto',
                      position: 'relative',
                      zIndex: 30
                    }}
                  >
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          )) : (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '3rem',
              textAlign: 'center',
              gridColumn: '1 / -1'
            }}>
              <svg width="48" height="48" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5-5-5h5v-5a7.5 7.5 0 00-15 0v5h5l-5 5-5-5h5V7.5a7.5 7.5 0 0115 0V17z" />
              </svg>
              <h3 style={{ color: 'var(--text-dark)', marginBottom: '0.5rem' }}>No alerts detected</h3>
              <p style={{ color: 'var(--text-muted)', margin: 0 }}>Your assets are currently secure. New alerts will appear here when threats are detected.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const AssetManagement = ({ active }) => {
  const { showError, showWarning } = useNotifications();

  if (!active) {
    return null;
  }

  const [activeTab, setActiveTab] = useState('inventory');
  const [assets, setAssets] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAssetModal, setShowAssetModal] = useState(false);
  const [editingAsset, setEditingAsset] = useState(null);
  const [showAlertModal, setShowAlertModal] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [showBulkUploadModal, setShowBulkUploadModal] = useState(false);
  const [notification, setNotification] = useState(null);
  const [confirmModal, setConfirmModal] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [refreshInterval, setRefreshInterval] = useState(null);
  const [assetModalError, setAssetModalError] = useState(null);

  useEffect(() => {
    if (active) {
      fetchData();

      // Subscribe to RefreshManager for cross-component updates
      refreshManager.subscribe('assets', () => {
        console.log('🔄 RefreshManager: Refreshing asset data');
        fetchData();
      }, {
        backgroundRefresh: true,
        isVisible: () => active
      });

      return () => {
        refreshManager.unsubscribe('assets');
      };
    }
  }, [active]);

  const fetchAllAssets = async () => {
    let assets = [];
    let nextPage = '/api/assets/inventory/';
    while (nextPage) {
      const res = await get(nextPage);
      if (res?.results?.data) {
        assets = assets.concat(res.results.data);
      }
      nextPage = res.next ? new URL(res.next).pathname + new URL(res.next).search : null;
    }
    return assets;
  };

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [assetsData, alertsRes, statsRes] = await Promise.all([
        fetchAllAssets(),
        getCustomAlerts(),
        getAssetAlertStatistics()
      ]);

      const alertsData = alertsRes?.results?.data || [];

      // Force state updates with new arrays to ensure re-render
      setAssets([...assetsData]);
      setAlerts([...alertsData]);
      setStats({...(statsRes?.data || statsRes || {})});
    } catch (err) {
      setError(`Failed to load asset data: ${err.message}`);
      setAssets([]);
      setAlerts([]);
      setStats({});
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  const handleTriggerCorrelation = async () => {
    setLoading(true);
    try {
      await triggerAssetCorrelation();
      showNotification('Asset correlation triggered successfully! New alerts will be generated based on your asset inventory.', 'success');

      // Trigger refresh of related components after correlation
      refreshManager.triggerRelated('assets', 'asset_correlation_triggered');

      setTimeout(() => {
        fetchData();
      }, 2000); // 2 second delay
    } catch (err) {
      console.error('Correlation error:', err);
      showNotification('Failed to trigger asset correlation. Please try again.', 'error');
      setLoading(false);
    }
  };

  const handleClearDemoData = async () => {
    if (!window.confirm('Are you sure you want to clear all demo data? This will remove demo alerts and assets and cannot be undone.')) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await clearDemoData();
      showNotification(`Demo data cleared successfully! ${response.data.deleted_alerts} alerts and ${response.data.deleted_assets} assets removed.`, 'success');
      fetchData();
    } catch (err) {
      console.error('Clear demo data error:', err);
      showNotification('Failed to clear demo data. Please try again.', 'error');
      setLoading(false);
    }
  };

  const handleOpenAssetModal = (asset = null) => {
    setEditingAsset(asset);
    setShowAssetModal(true);
    setAssetModalError(null);
  };

  const handleCloseAssetModal = () => {
    setEditingAsset(null);
    setShowAssetModal(false);
    setAssetModalError(null);
  };

  const handleSaveAsset = async (assetData) => {
    try {
      let result;
      if (editingAsset) {
        result = await updateAsset(editingAsset.id, assetData);
        if (result && result.success !== false) {
          showNotification(`Asset "${assetData.name}" updated successfully.`, 'success');

          // Trigger refresh of related components after asset update
          refreshManager.triggerRelated('assets', 'asset_updated');

          fetchData();
          handleCloseAssetModal();
        } else {
          throw new Error(result?.message || 'Failed to update asset');
        }
      } else {
        result = await createAsset(assetData);
        if (result && result.data) {
          showNotification(`Asset "${assetData.name}" created successfully.`, 'success');

          // Trigger refresh of related components after asset creation
          refreshManager.triggerRelated('assets', 'asset_created');

          setAssets(prevAssets => [result.data, ...prevAssets]);
          handleCloseAssetModal();
        } else {
          throw new Error(result?.message || 'Failed to create asset');
        }
      }
    } catch (err) {
      console.error('Asset save error:', err);
      const errorMessage = err.message || `Failed to ${editingAsset ? 'update' : 'create'} asset`;
      setAssetModalError(errorMessage);
      // showNotification(errorMessage, 'error');
      // Don't close the modal on error so user can fix issues
    }
  };

  const handleDeleteAsset = (asset) => {
    console.log('handleDeleteAsset called with asset:', asset);
    const modalConfig = {
      title: 'Delete Asset',
      message: `Are you sure you want to delete "${asset.name}"? This action cannot be undone.`,
      confirmText: 'Delete',
      cancelText: 'Cancel',
      isDestructive: true,
      actionType: 'delete',
      onClose: () => setConfirmModal(null),
      onConfirm: async () => {
        try {
          setLoading(true);
          const result = await deleteAsset(asset.id);
          console.log('Asset delete result:', result);

          if (result && result.success !== false) {
            showNotification(`Asset "${asset.name}" deleted successfully.`, 'success');

            // Trigger refresh of related components after asset deletion
            refreshManager.triggerRelated('assets', 'asset_deleted');

            // Remove the asset from state immediately for better UX
            setAssets(prevAssets => prevAssets.filter(a => a.id !== asset.id));
            // Refresh data to ensure consistency
            await fetchData();
          } else {
            throw new Error(result?.message || 'Failed to delete asset');
          }
        } catch (err) {
          console.error('Asset deletion error:', err);
          showNotification(`Failed to delete asset: ${err.message}`, 'error');
        } finally {
          setLoading(false);
          setConfirmModal(null);
        }
      },
      onCancel: () => setConfirmModal(null)
    };
    console.log('Setting confirmModal with config:', modalConfig);
    setConfirmModal(modalConfig);
  };

  const handleDeleteAlert = (alert) => {
    console.log('handleDeleteAlert called with alert:', alert);
    const modalConfig = {
      title: 'Delete Alert',
      message: `Are you sure you want to delete this alert "${alert.title}"? This action cannot be undone.`,
      confirmText: 'Delete',
      cancelText: 'Cancel',
      isDestructive: true,
      actionType: 'delete',
      onClose: () => setConfirmModal(null),
      onConfirm: async () => {
        try {
          setLoading(true);
          const result = await deleteAlert(alert.id);
          console.log('Alert delete result:', result);

          if (result && result.success !== false) {
            showNotification(`Alert "${alert.title}" deleted successfully.`, 'success');
            // Remove the alert from state immediately for better UX
            setAlerts(prevAlerts => prevAlerts.filter(a => a.id !== alert.id));
            // Refresh data to ensure consistency
            await fetchData();
          } else {
            throw new Error(result?.message || 'Failed to delete alert');
          }
        } catch (err) {
          console.error('Alert deletion error:', err);
          showNotification(`Failed to delete alert: ${err.message}`, 'error');
        } finally {
          setLoading(false);
          setConfirmModal(null);
        }
      },
      onCancel: () => setConfirmModal(null)
    };
    console.log('Setting alert confirmModal with config:', modalConfig);
    setConfirmModal(modalConfig);
  };

  const handleOpenAlertModal = (alert) => {
    setSelectedAlert(alert);
    setShowAlertModal(true);
  };

  const handleCloseAlertModal = () => {
    setSelectedAlert(null);
    setShowAlertModal(false);
  };

  const handleOpenBulkUploadModal = () => {
    setShowBulkUploadModal(true);
  };

  const handleCloseBulkUploadModal = () => {
    setShowBulkUploadModal(false);
  };

  const handleBulkUpload = async (file) => {
    try {
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const content = e.target.result;
          const assets = JSON.parse(content);
          
          if (!Array.isArray(assets) || assets.length === 0) {
            showNotification('Invalid file format. Expected an array of assets.', 'error');
            return;
          }
          
          setLoading(true);
          const result = await bulkUploadAssets(assets);
          
          if (result && result.success !== false) {
            fetchData();
            handleCloseBulkUploadModal();
            showNotification(`Successfully uploaded ${assets.length} assets!`, 'success');
          } else {
            throw new Error(result?.message || 'Bulk upload failed');
          }
        } catch (parseErr) {
          setLoading(false);
          if (parseErr.message && parseErr.message.includes('JSON')) {
            showNotification('Invalid JSON file. Please check the file format.', 'error');
          } else {
            console.error('Upload error:', parseErr);
            showNotification(`Upload failed: ${parseErr.message}`, 'error');
            handleCloseBulkUploadModal();
          }
        } finally {
          setLoading(false);
        }
      };
      reader.readAsText(file);
    } catch (err) {
      showNotification('Failed to read file. Please try again.', 'error');
      console.error(err);
    }
  };

  // Auto-refresh for alerts
  useEffect(() => {
    if (active && activeTab === 'alerts') {
      const interval = setInterval(() => {
        fetchData();
      }, 300000); // Refresh every 5 minutes instead of 30 seconds
      setRefreshInterval(interval);
      return () => clearInterval(interval);
    } else if (refreshInterval) {
      clearInterval(refreshInterval);
      setRefreshInterval(null);
    }
  }, [active, activeTab]);

  if (!active) {
    return null;
  }

  // Filter functions
  const filteredAssets = assets.filter(asset => {
    const matchesSearch = asset.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         asset.asset_value?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || asset.asset_type === filterType;
    return matchesSearch && matchesType;
  });

  const filteredAlerts = alerts.filter(alert => {
    const matchesSearch = alert.title?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = filterSeverity === 'all' || alert.severity === filterSeverity;
    return matchesSearch && matchesSeverity;
  });


  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <div style={{ color: 'var(--danger)', padding: '1rem' }}>{error}</div>;
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif', position: 'relative' }}>
      {loading && <LoadingSpinner fullscreen={true} />}

      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ marginBottom: '0.5rem', color: 'var(--text-dark)' }}>Asset Management</h1>
        <p style={{ color: 'var(--text-muted)', margin: 0 }}>Manage and monitor your organization's digital assets and security alerts</p>
      </div>

      {/* Statistics Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        <div style={{
          backgroundColor: 'var(--white)',
          padding: '1.5rem',
          borderRadius: '8px',
          border: '1px solid var(--medium-gray)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary-blue)' }}>
            {stats?.asset_statistics?.total_assets || assets.length}
          </div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Total Assets</div>
        </div>

        <div style={{
          backgroundColor: 'var(--white)',
          padding: '1.5rem',
          borderRadius: '8px',
          border: '1px solid var(--medium-gray)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--secondary-blue)' }}>
            {stats?.alert_statistics?.recent_alerts || alerts.length}
          </div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Active Alerts</div>
        </div>

        <div style={{
          backgroundColor: 'var(--white)',
          padding: '1.5rem',
          borderRadius: '8px',
          border: '1px solid var(--medium-gray)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--info)' }}>
            {stats?.asset_statistics?.alert_coverage_percentage || 100}%
          </div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Coverage</div>
        </div>

        <div style={{
          backgroundColor: 'var(--white)',
          padding: '1.5rem',
          borderRadius: '8px',
          border: '1px solid var(--medium-gray)',
          textAlign: 'center'
        }}>
          <button
            onClick={handleTriggerCorrelation}
            disabled={loading}
            style={{
              backgroundColor: 'var(--accent-blue)',
              color: 'var(--white)',
              border: 'none',
              borderRadius: '4px',
              padding: '0.5rem 1rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1
            }}
          >
            {loading ? 'Processing...' : 'Trigger Correlation'}
          </button>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.5rem' }}>Smart Analysis</div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{
        borderBottom: '2px solid #e0e0e0',
        marginBottom: '1rem'
      }}>
        <button
          onClick={() => setActiveTab('inventory')}
          style={{
            padding: '0.75rem 1.5rem',
            marginRight: '0.5rem',
            backgroundColor: activeTab === 'inventory' ? '#2196F3' : 'transparent',
            color: activeTab === 'inventory' ? 'white' : '#666',
            border: 'none',
            borderRadius: '4px 4px 0 0',
            cursor: 'pointer',
            fontWeight: '500'
          }}
        >
          Asset Inventory ({filteredAssets.length})
        </button>
        <button
          onClick={() => setActiveTab('alerts')}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: activeTab === 'alerts' ? '#FF5722' : 'transparent',
            color: activeTab === 'alerts' ? 'white' : '#666',
            border: 'none',
            borderRadius: '4px 4px 0 0',
            cursor: 'pointer',
            fontWeight: '500'
          }}
        >
          Custom Alerts ({filteredAlerts.length})
        </button>
      </div>

      {/* Controls */}
      <div style={{
        display: 'flex',
        gap: '1rem',
        marginBottom: '2rem',
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <input
          type="text"
          placeholder={`Search ${activeTab === 'inventory' ? 'assets' : 'alerts'}...`}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            padding: '0.5rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            minWidth: '200px',
            backgroundColor: 'var(--white)',
            color: 'var(--text-dark)'
          }}
        />

        {activeTab === 'inventory' ? (
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            style={{
              padding: '0.5rem',
              border: '1px solid var(--medium-gray)',
              borderRadius: '4px',
              backgroundColor: 'var(--white)',
              color: 'var(--text-dark)'
            }}
          >
            <option value="all">All Types</option>
            <option value="domain">Domains</option>
            <option value="ip_range">IP Ranges</option>
            <option value="software">Software</option>
            <option value="service">Services</option>
          </select>
        ) : (
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            style={{
              padding: '0.5rem',
              border: '1px solid var(--medium-gray)',
              borderRadius: '4px',
              backgroundColor: 'var(--white)',
              color: 'var(--text-dark)'
            }}
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        )}

        {activeTab === 'inventory' && (
          <>
            <button
              onClick={() => handleOpenAssetModal()}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: 'var(--success)',
                color: 'var(--white)',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Add Asset
            </button>
            <button
              onClick={handleOpenBulkUploadModal}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: 'var(--secondary-blue)',
                color: 'var(--white)',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Bulk Upload
            </button>
          </>
        )}

        {activeTab === 'alerts' && (
          <>
            <button
              onClick={handleTriggerCorrelation}
              disabled={loading}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: loading ? '#ccc' : '#FF9800',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? 'Processing...' : 'Trigger New Correlation'}
            </button>
            <button
              onClick={handleClearDemoData}
              disabled={loading}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: loading ? '#ccc' : '#f44336',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              Clear Demo Data
            </button>
          </>
        )}
      </div>

      {/* Content */}
      <div>
        {activeTab === 'inventory' && (
          <AssetInventoryTab
            assets={filteredAssets.length > 0 ? filteredAssets : assets}
            onAdd={() => handleOpenAssetModal()}
            onEdit={handleOpenAssetModal}
            onDelete={handleDeleteAsset}
            onBulkUpload={handleOpenBulkUploadModal}
            loading={loading}
          />
        )}
        {activeTab === 'alerts' && (
          <CustomAlertsTab
            alerts={searchTerm || filterSeverity !== 'all' ? filteredAlerts : alerts}
            onView={handleOpenAlertModal}
            onDelete={handleDeleteAlert}
            loading={loading}
            refreshInterval={refreshInterval !== null}
          />
        )}
      </div>

      {/* Modals and Notifications */}
      {showAssetModal && <AssetModal asset={editingAsset} onSave={handleSaveAsset} onClose={handleCloseAssetModal} errorMessage={assetModalError} />}
      {showAlertModal && <AlertModal alert={selectedAlert} onClose={handleCloseAlertModal} />}
      {showBulkUploadModal && <BulkUploadModal onUpload={handleBulkUpload} onClose={handleCloseBulkUploadModal} />}
      {notification && <NotificationToast message={notification.message} type={notification.type} onClose={() => setNotification(null)} />}
      {confirmModal && <ConfirmationModal isOpen={true} {...confirmModal} />}
    </div>
  );
};

const AssetModal = ({ asset, onSave, onClose, errorMessage }) => {
  const { showWarning } = useNotifications();
  const [formData, setFormData] = useState({
    name: '',
    asset_type: 'domain',
    asset_value: '',
    description: '',
    criticality: 'medium',
    alert_enabled: true,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Initialize form data with asset data if provided
  useEffect(() => {
    if (asset) {
      setFormData(prev => ({
        ...prev,
        ...asset
      }));
    } else {
      // Reset to defaults when no asset is provided
      setFormData({
        name: '',
        asset_type: 'domain',
        asset_value: '',
        description: '',
        criticality: 'medium',
        alert_enabled: true,
      });
    }
  }, [asset]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Basic validation
    if (!formData.name?.trim()) {
      showWarning('Validation Error', 'Please enter an asset name');
      return;
    }
    if (!formData.asset_value?.trim()) {
      showWarning('Validation Error', 'Please enter an asset value');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSave(formData);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0, 0, 0, 0.6)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1rem'
    }}>
      <div style={{
        background: 'rgba(255, 255, 255, 0.98)',
        backdropFilter: 'blur(20px)',
        borderRadius: '24px',
        boxShadow: '0 16px 64px rgba(0, 0, 0, 0.15)',
        border: '1px solid rgba(255, 255, 255, 0.3)',
        maxWidth: '600px',
        width: '100%',
        maxHeight: '90vh',
        overflow: 'hidden',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
        position: 'relative'
      }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          padding: '2rem 2rem 1.5rem',
          color: 'white',
          position: 'relative'
        }}>
          <button
            onClick={onClose}
            style={{
              position: 'absolute',
              top: '1rem',
              right: '1rem',
              background: 'rgba(255, 255, 255, 0.2)',
              border: 'none',
              borderRadius: '50%',
              width: '40px',
              height: '40px',
              cursor: 'pointer',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.3)';
              e.target.style.transform = 'rotate(90deg)';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.2)';
              e.target.style.transform = 'rotate(0deg)';
            }}
          >
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              background: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '16px',
              padding: '1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h2 style={{
                fontSize: '2rem',
                fontWeight: '800',
                margin: '0 0 0.5rem 0',
                textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
              }}>
                {asset ? 'Edit Asset' : 'Add New Asset'}
              </h2>
              <p style={{
                fontSize: '1rem',
                margin: 0,
                opacity: 0.9,
                fontWeight: '500'
              }}>
                {asset ? 'Update asset information and settings' : 'Create a new digital asset for monitoring'}
              </p>
            </div>
          </div>
        </div>

        {/* Form Content */}
        <form onSubmit={handleSubmit} style={{ height: 'calc(100% - 140px)', display: 'flex', flexDirection: 'column' }}>
          <div style={{
            padding: '2rem',
            flex: 1,
            overflowY: 'auto',
            background: 'linear-gradient(to bottom, rgba(255, 255, 255, 0.95), rgba(248, 250, 252, 0.95))'
          }}>
            {/* Error Message */}
            {errorMessage && (
              <div style={{
                background: 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)',
                border: '1px solid #f87171',
                borderRadius: '12px',
                padding: '1rem 1.5rem',
                marginBottom: '2rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem'
              }}>
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20" style={{ color: 'var(--danger)', flexShrink: 0 }}>
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span style={{ color: 'var(--danger)', fontWeight: '600', fontSize: '0.875rem' }}>{errorMessage}</span>
              </div>
            )}

            {/* Form Fields Grid */}
            <div style={{ display: 'grid', gap: '1.5rem' }}>
              {/* Asset Name */}
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '0.875rem',
                  fontWeight: '700',
                  color: '#374151',
                  marginBottom: '0.5rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Asset Name
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Enter a descriptive name for this asset..."
                  required
                  style={{
                    width: '100%',
                    padding: '1rem 1.25rem',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '1rem',
                    fontWeight: '500',
                    color: '#111827',
                    background: 'white',
                    transition: 'all 0.3s ease',
                    outline: 'none'
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#667eea';
                    e.target.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
                    e.target.style.transform = 'translateY(-1px)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#e5e7eb';
                    e.target.style.boxShadow = 'none';
                    e.target.style.transform = 'translateY(0)';
                  }}
                />
              </div>

              {/* Asset Type and Value Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '0.875rem',
                    fontWeight: '700',
                    color: '#374151',
                    marginBottom: '0.5rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px'
                  }}>
                    Asset Type
                  </label>
                  <select
                    name="asset_type"
                    value={formData.asset_type}
                    onChange={handleChange}
                    style={{
                      width: '100%',
                      padding: '1rem 1.25rem',
                      border: '2px solid #e5e7eb',
                      borderRadius: '12px',
                      fontSize: '1rem',
                      fontWeight: '500',
                      color: '#111827',
                      background: 'white',
                      transition: 'all 0.3s ease',
                      outline: 'none',
                      cursor: 'pointer'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#667eea';
                      e.target.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#e5e7eb';
                      e.target.style.boxShadow = 'none';
                    }}
                  >
                    <option value="domain">🌐 Domain</option>
                    <option value="ip_range">📡 IP Range</option>
                    <option value="software">💻 Software</option>
                    <option value="service">⚙️ Service</option>
                  </select>
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '0.875rem',
                    fontWeight: '700',
                    color: '#374151',
                    marginBottom: '0.5rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px'
                  }}>
                    Criticality Level
                  </label>
                  <select
                    name="criticality"
                    value={formData.criticality}
                    onChange={handleChange}
                    style={{
                      width: '100%',
                      padding: '1rem 1.25rem',
                      border: '2px solid #e5e7eb',
                      borderRadius: '12px',
                      fontSize: '1rem',
                      fontWeight: '500',
                      color: '#111827',
                      background: 'white',
                      transition: 'all 0.3s ease',
                      outline: 'none',
                      cursor: 'pointer'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#667eea';
                      e.target.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#e5e7eb';
                      e.target.style.boxShadow = 'none';
                    }}
                  >
                    <option value="low">🟢 Low</option>
                    <option value="medium">🟡 Medium</option>
                    <option value="high">🟠 High</option>
                    <option value="critical">🔴 Critical</option>
                  </select>
                </div>
              </div>

              {/* Asset Value */}
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '0.875rem',
                  fontWeight: '700',
                  color: '#374151',
                  marginBottom: '0.5rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Asset Value
                </label>
                <input
                  type="text"
                  name="asset_value"
                  value={formData.asset_value}
                  onChange={handleChange}
                  placeholder="e.g., example.com, 192.168.1.0/24, Apache v2.4.41"
                  required
                  style={{
                    width: '100%',
                    padding: '1rem 1.25rem',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '1rem',
                    fontWeight: '500',
                    color: '#111827',
                    background: 'white',
                    transition: 'all 0.3s ease',
                    outline: 'none',
                    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Monaco, Consolas, monospace'
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#667eea';
                    e.target.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
                    e.target.style.transform = 'translateY(-1px)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#e5e7eb';
                    e.target.style.boxShadow = 'none';
                    e.target.style.transform = 'translateY(0)';
                  }}
                />
              </div>

              {/* Description */}
              <div>
                <label style={{
                  display: 'block',
                  fontSize: '0.875rem',
                  fontWeight: '700',
                  color: '#374151',
                  marginBottom: '0.5rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Description (Optional)
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="Provide additional context or notes about this asset..."
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '1rem 1.25rem',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '1rem',
                    fontWeight: '500',
                    color: '#111827',
                    background: 'white',
                    transition: 'all 0.3s ease',
                    outline: 'none',
                    resize: 'vertical',
                    minHeight: '80px'
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#667eea';
                    e.target.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#e5e7eb';
                    e.target.style.boxShadow = 'none';
                  }}
                />
              </div>

              {/* Alert Enabled Toggle */}
              <div style={{
                background: 'rgba(255, 255, 255, 0.8)',
                border: '2px solid #e5e7eb',
                borderRadius: '12px',
                padding: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <div style={{
                    fontSize: '0.875rem',
                    fontWeight: '700',
                    color: '#374151',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    marginBottom: '0.25rem'
                  }}>
                    Smart Monitoring
                  </div>
                  <div style={{
                    fontSize: '0.875rem',
                    color: '#6b7280',
                    fontWeight: '500'
                  }}>
                    Enable intelligent threat detection for this asset
                  </div>
                </div>
                <label style={{
                  display: 'flex',
                  alignItems: 'center',
                  cursor: 'pointer',
                  position: 'relative'
                }}>
                  <input
                    type="checkbox"
                    name="alert_enabled"
                    checked={formData.alert_enabled}
                    onChange={handleChange}
                    style={{ display: 'none' }}
                  />
                  <div style={{
                    width: '60px',
                    height: '32px',
                    borderRadius: '16px',
                    background: formData.alert_enabled
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                      : '#d1d5db',
                    transition: 'all 0.3s ease',
                    position: 'relative',
                    boxShadow: formData.alert_enabled
                      ? '0 4px 12px rgba(102, 126, 234, 0.4)'
                      : '0 2px 4px rgba(0, 0, 0, 0.1)'
                  }}>
                    <div style={{
                      width: '28px',
                      height: '28px',
                      borderRadius: '50%',
                      background: 'white',
                      position: 'absolute',
                      top: '2px',
                      left: formData.alert_enabled ? '30px' : '2px',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      {formData.alert_enabled && (
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20" style={{ color: '#667eea' }}>
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                  </div>
                </label>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div style={{
            background: 'rgba(248, 250, 252, 0.95)',
            backdropFilter: 'blur(10px)',
            borderTop: '1px solid rgba(226, 232, 240, 0.8)',
            padding: '1.5rem 2rem',
            display: 'flex',
            justifyContent: 'flex-end',
            gap: '1rem'
          }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                background: 'white',
                border: '2px solid #e5e7eb',
                borderRadius: '12px',
                padding: '0.75rem 1.5rem',
                fontSize: '1rem',
                fontWeight: '600',
                color: '#6b7280',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
              onMouseEnter={(e) => {
                e.target.style.borderColor = '#d1d5db';
                e.target.style.color = '#374151';
                e.target.style.transform = 'translateY(-1px)';
              }}
              onMouseLeave={(e) => {
                e.target.style.borderColor = '#e5e7eb';
                e.target.style.color = '#6b7280';
                e.target.style.transform = 'translateY(0)';
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              style={{
                background: isSubmitting
                  ? 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)'
                  : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                borderRadius: '12px',
                padding: '0.75rem 2rem',
                fontSize: '1rem',
                fontWeight: '700',
                color: 'white',
                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                transition: 'all 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                boxShadow: isSubmitting
                  ? 'none'
                  : '0 4px 16px rgba(102, 126, 234, 0.4)'
              }}
              onMouseEnter={(e) => {
                if (!isSubmitting) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 8px 24px rgba(102, 126, 234, 0.5)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isSubmitting) {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 4px 16px rgba(102, 126, 234, 0.4)';
                }
              }}
            >
              {isSubmitting ? (
                <>
                  <svg style={{ animation: 'spin 1s linear infinite' }} width="20" height="20" fill="none" viewBox="0 0 24 24">
                    <circle style={{ opacity: 0.25 }} cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path style={{ opacity: 0.75 }} fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Saving Asset...
                </>
              ) : (
                <>
                  <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {asset ? 'Update Asset' : 'Create Asset'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const AlertModal = ({ alert, onClose }) => {
  if (!alert) return null;

  const severityConfig = {
    critical: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-800', icon: '🔴' },
    high: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-800', icon: '🟠' },
    medium: { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-800', icon: '🟡' },
    low: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-800', icon: '🟢' }
  };

  const config = severityConfig[alert.severity] || severityConfig.medium;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        maxWidth: '800px',
        width: '90%',
        maxHeight: '80vh',
        overflow: 'auto',
        fontFamily: 'Arial, sans-serif'
      }}>
        <div style={{ padding: '1.5rem' }}>
          {/* Header */}
          <div style={{
            padding: '1rem 0 1rem 0',
            borderBottom: '1px solid #e0e0e0',
            marginBottom: '1rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span style={{ fontSize: '1.125rem' }}>{config.icon}</span>
                <div>
                  <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.125rem', fontWeight: '600', color: '#333' }}>{alert.title}</h3>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '1rem',
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      backgroundColor: alert.severity === 'critical' ? '#ffebee' :
                                      alert.severity === 'high' ? '#fff3e0' :
                                      alert.severity === 'medium' ? '#fffde7' : '#e8f5e8',
                      color: alert.severity === 'critical' ? '#c62828' :
                             alert.severity === 'high' ? '#ef6c00' :
                             alert.severity === 'medium' ? '#f57f17' : '#2e7d32'
                    }}>
                      {alert.severity_display || alert.severity}
                    </span>
                    <span style={{ fontSize: '0.875rem', color: '#666' }}>
                      Alert ID: {alert.alert_id || alert.id}
                    </span>
                  </div>
                </div>
              </div>
              <button
                onClick={onClose}
                style={{
                  padding: '0.5rem',
                  backgroundColor: 'transparent',
                  border: 'none',
                  color: '#999',
                  cursor: 'pointer'
                }}
              >
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
          </div>

          {/* Content */}
          <div style={{ maxHeight: '400px', overflowY: 'auto', padding: '0 0 1rem 0' }}>
              {/* Alert Description */}
              <div style={{ marginBottom: '1.5rem' }}>
                <h4 style={{ fontSize: '0.875rem', fontWeight: '500', color: '#111827', marginBottom: '0.5rem' }}>Description</h4>
                <div style={{ backgroundColor: '#f9fafb', borderRadius: '0.5rem', padding: '1rem' }}>
                  <p style={{ fontSize: '0.875rem', color: '#374151', whiteSpace: 'pre-wrap' }}>{alert.description}</p>
                </div>
              </div>

              {/* Alert Metrics */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                <div style={{ backgroundColor: '#eff6ff', borderRadius: '0.5rem', padding: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <svg width="20" height="20" style={{ color: '#2563eb', marginRight: '0.5rem' }} fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <div>
                      <p style={{ fontSize: '0.875rem', fontWeight: '500', color: '#1e3a8a' }}>Confidence</p>
                      <p style={{ fontSize: '1.125rem', fontWeight: 'bold', color: '#2563eb' }}>{Math.round((alert.confidence_score || 0) * 100)}%</p>
                    </div>
                  </div>
                </div>
                <div style={{ backgroundColor: '#faf5ff', borderRadius: '0.5rem', padding: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <svg width="20" height="20" style={{ color: '#7c3aed', marginRight: '0.5rem' }} fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <div>
                      <p style={{ fontSize: '0.875rem', fontWeight: '500', color: '#581c87' }}>Relevance</p>
                      <p style={{ fontSize: '1.125rem', fontWeight: 'bold', color: '#7c3aed' }}>{Math.round((alert.relevance_score || 0) * 100)}%</p>
                    </div>
                  </div>
                </div>
                <div style={{ backgroundColor: '#f0fdf4', borderRadius: '0.5rem', padding: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <svg width="20" height="20" style={{ color: '#059669', marginRight: '0.5rem' }} fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.414-1.415L11 9.586V6z" clipRule="evenodd" />
                    </svg>
                    <div>
                      <p style={{ fontSize: '0.875rem', fontWeight: '500', color: '#14532d' }}>Detected</p>
                      <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#059669' }}>{new Date(alert.detected_at).toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Matched Assets */}
              {alert.matched_assets && alert.matched_assets.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                    <svg width="20" height="20" style={{ marginRight: '0.5rem' }} fill="currentColor" viewBox="0 0 20 20">
                      <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
                    </svg>
                    Affected Assets ({alert.matched_assets.length})
                  </h4>
                  <div className="space-y-2">
                    {alert.matched_assets.map((asset, index) => (
                      <div key={asset.id || index} className="bg-red-50 border border-red-200 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className={`w-2 h-2 rounded-full ${
                              asset.criticality === 'critical' ? 'bg-red-500' :
                              asset.criticality === 'high' ? 'bg-orange-500' :
                              asset.criticality === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                            }`}></div>
                            <div>
                              <p className="font-medium text-gray-900">{asset.name}</p>
                              <p className="text-sm text-gray-600">{asset.asset_type} • {asset.asset_value}</p>
                            </div>
                          </div>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            asset.criticality === 'critical' ? 'bg-red-100 text-red-800' :
                            asset.criticality === 'high' ? 'bg-orange-100 text-orange-800' :
                            asset.criticality === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {asset.criticality}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Source Indicators */}
              {alert.source_indicators && alert.source_indicators.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                    <svg width="20" height="20" style={{ marginRight: '0.5rem' }} fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"/>
                    </svg>
                    Threat Indicators ({alert.source_indicators.length})
                  </h4>
                  <div className="space-y-2">
                    {alert.source_indicators.map((indicator, index) => (
                      <div key={indicator.id || index} className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-mono text-sm font-medium text-gray-900">{indicator.value}</p>
                            <p className="text-xs text-gray-600 mt-1">{indicator.type}</p>
                          </div>
                          <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                            {indicator.type}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Response Actions */}
              {alert.response_actions && alert.response_actions.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                    <svg width="20" height="20" style={{ marginRight: '0.5rem' }} fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 2a4 4 0 00-4 4v1H5a1 1 0 00-.994.89l-1 9A1 1 0 004 18h12a1 1 0 00.994-1.11l-1-9A1 1 0 0015 7h-1V6a4 4 0 00-4-4zm2 5V6a2 2 0 10-4 0v1h4zm-6 3a1 1 0 112 0 1 1 0 01-2 0zm7-1a1 1 0 100 2 1 1 0 000-2z" clipRule="evenodd" />
                    </svg>
                    Recommended Actions
                  </h4>
                  <div className="space-y-3">
                    {alert.response_actions.map((action, index) => (
                      <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                        <div className="flex items-start space-x-3">
                          <div className={`w-2 h-2 rounded-full mt-2 ${
                            action.priority === 'high' ? 'bg-red-500' :
                            action.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                          }`}></div>
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{action.title}</p>
                            <p className="text-sm text-gray-600 mt-1">{action.description}</p>
                            <span className={`inline-block mt-2 px-2 py-1 text-xs font-medium rounded-full ${
                              action.priority === 'high' ? 'bg-red-100 text-red-800' :
                              action.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {action.priority} priority
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="bg-gray-50 px-6 py-4 flex justify-between items-center border-t">
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span>Status: {alert.status_display || alert.status}</span>
                <span>•</span>
                <span>Created: {new Date(alert.created_at || alert.detected_at).toLocaleString()}</span>
              </div>
              <button
                onClick={onClose}
                className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const BulkUploadModal = ({ onUpload, onClose }) => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (file) {
      setIsUploading(true);
      try {
        await onUpload(file);
      } finally {
        setIsUploading(false);
      }
    }
  };

  const sampleData = [
    {
      "name": "Corporate Web Server",
      "asset_type": "domain",
      "asset_value": "company.example.com",
      "description": "Main corporate website",
      "criticality": "high",
      "alert_enabled": true
    },
    {
      "name": "Internal Network Range",
      "asset_type": "ip_range",
      "asset_value": "192.168.1.0/24",
      "description": "Internal office network",
      "criticality": "medium",
      "alert_enabled": true
    }
  ];

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '2rem',
        maxWidth: '600px',
        width: '90%',
        maxHeight: '80vh',
        overflow: 'auto',
        fontFamily: 'Arial, sans-serif'
      }}>
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600', color: '#333' }}>
              Bulk Upload Assets
            </h3>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '0.5rem',
                backgroundColor: 'transparent',
                border: 'none',
                color: '#999',
                cursor: 'pointer'
              }}
            >
              <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <p style={{ margin: '0 0 1rem 0', fontSize: '0.875rem', color: '#666' }}>
              Upload a JSON file containing an array of asset objects. Each asset should include name, asset_type, asset_value, and other properties.
            </p>

            {/* File Upload Area */}
            <div
              style={{
                position: 'relative',
                border: '2px dashed',
                borderColor: dragActive ? '#3f51b5' :
                            file ? '#4caf50' : '#ddd',
                backgroundColor: dragActive ? '#f3f4f6' :
                                file ? '#f1f8e9' : 'transparent',
                borderRadius: '8px',
                padding: '2rem',
                textAlign: 'center',
                marginBottom: '1rem'
              }}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                onChange={handleFileChange}
                accept=".json"
                style={{
                  position: 'absolute',
                  inset: 0,
                  width: '100%',
                  height: '100%',
                  opacity: 0,
                  cursor: 'pointer'
                }}
                disabled={isUploading}
              />
              <div>
                {file ? (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <svg width="32" height="32" fill="currentColor" viewBox="0 0 20 20" style={{ color: '#4caf50', marginRight: '0.5rem' }}>
                      <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                    <div>
                      <p style={{ fontSize: '0.875rem', fontWeight: '500', color: '#2e7d32', margin: 0 }}>{file.name}</p>
                      <p style={{ fontSize: '0.75rem', color: '#4caf50', margin: 0 }}>{(file.size / 1024).toFixed(1)} KB</p>
                    </div>
                  </div>
                ) : (
                  <div>
                    <svg width="48" height="48" stroke="currentColor" fill="none" viewBox="0 0 48 48" style={{ color: '#999', margin: '0 auto 1rem' }}>
                      <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <div>
                      <p style={{ fontSize: '0.875rem', color: '#333', margin: 0 }}>Drop your JSON file here, or <span style={{ color: '#2196F3', fontWeight: '500' }}>click to browse</span></p>
                      <p style={{ fontSize: '0.75rem', color: '#999', margin: '0.25rem 0 0 0' }}>JSON files only</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Sample Data */}
            <div style={{ backgroundColor: '#f5f5f5', borderRadius: '8px', padding: '1rem', marginBottom: '1rem' }}>
              <h4 style={{ fontSize: '0.875rem', fontWeight: '500', color: '#333', margin: '0 0 0.5rem 0' }}>Sample JSON Format:</h4>
              <pre style={{ fontSize: '0.75rem', color: '#666', overflowX: 'auto', margin: 0, whiteSpace: 'pre' }}>
                {JSON.stringify(sampleData, null, 2)}
              </pre>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '1.5rem' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '0.5rem 1rem',
                border: '1px solid #ddd',
                backgroundColor: 'white',
                color: '#666',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!file || isUploading}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: (!file || isUploading) ? '#999' : '#2196F3',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: (!file || isUploading) ? 'not-allowed' : 'pointer',
                fontSize: '0.875rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              {isUploading ? (
                <>
                  <svg style={{ animation: 'spin 1s linear infinite' }} width="16" height="16" fill="none" viewBox="0 0 24 24">
                    <circle style={{ opacity: 0.25 }} cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path style={{ opacity: 0.75 }} fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Uploading...
                </>
              ) : (
                'Upload Assets'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AssetManagement;

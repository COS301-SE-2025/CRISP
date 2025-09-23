import React, { useState, useEffect, Fragment } from 'react';
import { getAssetInventory, createAsset, updateAsset, deleteAsset, bulkUploadAssets, getCustomAlerts, getAssetAlertStatistics, triggerAssetCorrelation, getCustomAlertDetails, updateAlertStatus } from '../../api/assets';
import LoadingSpinner from '../enhanced/LoadingSpinner';
import NotificationToast from '../enhanced/NotificationToast';
import ConfirmationModal from '../enhanced/ConfirmationModal';

const AssetInventoryTab = ({ assets, onAdd, onEdit, onDelete, onBulkUpload, loading }) => {
    return (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Asset Inventory</h3>
              <p className="text-sm text-gray-600 mt-1">Manage and monitor your organization's digital assets</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={onAdd}
                className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
              >
                <svg className="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Add Asset
              </button>
              <button
                onClick={onBulkUpload}
                className="inline-flex items-center px-4 py-2 border border-gray-300 bg-white hover:bg-gray-50 text-gray-700 text-sm font-medium rounded-lg transition-colors shadow-sm"
              >
                <svg className="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                Bulk Upload
              </button>
            </div>
          </div>

          {loading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner />
            </div>
          ) : (
            <div className="grid gap-4">
              {assets.map((asset) => (
                <div key={asset.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`w-3 h-3 rounded-full flex-shrink-0 ${
                        asset.criticality === 'critical' ? 'bg-red-500 animate-pulse' :
                        asset.criticality === 'high' ? 'bg-orange-500' :
                        asset.criticality === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                      }`}></div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-3">
                          <h4 className="text-lg font-semibold text-gray-900 truncate">{asset.name}</h4>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            asset.asset_type === 'domain' ? 'bg-blue-100 text-blue-800' :
                            asset.asset_type === 'ip_range' ? 'bg-purple-100 text-purple-800' :
                            asset.asset_type === 'software' ? 'bg-green-100 text-green-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {asset.asset_type_display || asset.asset_type}
                          </span>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            asset.criticality === 'critical' ? 'bg-red-100 text-red-800' :
                            asset.criticality === 'high' ? 'bg-orange-100 text-orange-800' :
                            asset.criticality === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {asset.criticality === 'critical' ? '🔴' : asset.criticality === 'high' ? '🟠' : asset.criticality === 'medium' ? '🟡' : '🟢'} {asset.criticality?.charAt(0).toUpperCase() + asset.criticality?.slice(1)}
                          </span>
                        </div>
                        <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
                          <span className="flex items-center">
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            {asset.asset_value}
                          </span>
                          {asset.alert_enabled && (
                            <span className="flex items-center text-green-600">
                              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                              </svg>
                              Alerts Enabled
                            </span>
                          )}
                        </div>
                        {asset.description && (
                          <p className="mt-2 text-sm text-gray-600 line-clamp-2">{asset.description}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => onEdit(asset)}
                        className="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                        title="Edit asset"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => onDelete(asset)}
                        className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Delete asset"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
              {assets.length === 0 && (
                <div className="text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No assets found</h3>
                  <p className="mt-1 text-sm text-gray-500">Get started by adding your first asset to monitor</p>
                  <div className="mt-6">
                    <button
                      onClick={onAdd}
                      className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                    >
                      <svg className="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                      Add Asset
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
    );
};

const CustomAlertsTab = ({ alerts, onView, loading, refreshInterval }) => {
    return (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Custom Asset Alerts</h3>
              <p className="text-sm text-gray-600 mt-1">
                Smart alerts generated from IoC correlation with your assets
                {refreshInterval && (
                  <span className="ml-2 inline-flex items-center text-green-600">
                    <svg className="w-4 h-4 mr-1 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Auto-refreshing
                  </span>
                )}
              </p>
            </div>
          </div>

          {loading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner />
            </div>
          ) : (
            <div className="space-y-4">
              {alerts.map((alert) =>
                <div
                  key={alert.id}
                  onClick={() => onView(alert.id)}
                  className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-all cursor-pointer group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start space-x-3">
                        <div className={`w-3 h-3 rounded-full mt-1 flex-shrink-0 ${
                          alert.severity === 'critical' ? 'bg-red-500 animate-pulse' :
                          alert.severity === 'high' ? 'bg-orange-500' :
                          alert.severity === 'medium' ? 'bg-yellow-500' :
                          'bg-green-500'
                        }`}></div>
                        <div className="flex-1">
                          <h4 className="text-lg font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                            {alert.title}
                          </h4>
                          <div className="mt-2 flex flex-wrap items-center gap-3">
                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                              alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                              alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                              alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {alert.severity === 'critical' ? '🔴' : alert.severity === 'high' ? '🟠' : alert.severity === 'medium' ? '🟡' : '🟢'}
                              {alert.severity_display || alert.severity}
                            </span>
                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                              alert.status === 'new' ? 'bg-blue-100 text-blue-800' :
                              alert.status === 'investigating' ? 'bg-yellow-100 text-yellow-800' :
                              alert.status === 'resolved' ? 'bg-green-100 text-green-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {alert.status_display || alert.status}
                            </span>
                            {alert.confidence_score && (
                              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                                🎯 {Math.round(alert.confidence_score * 100)}% confidence
                              </span>
                            )}
                          </div>
                          <div className="mt-3 flex items-center space-x-6 text-sm text-gray-600">
                            <span className="flex items-center">
                              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              {new Date(alert.detected_at).toLocaleString()}
                            </span>
                            {alert.matched_assets && alert.matched_assets.length > 0 && (
                              <span className="flex items-center">
                                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                                </svg>
                                {alert.matched_assets.length} affected asset{alert.matched_assets.length !== 1 ? 's' : ''}
                              </span>
                            )}
                          </div>
                          {alert.description && (
                            <p className="mt-3 text-sm text-gray-600 line-clamp-3">{alert.description}</p>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="ml-4 flex-shrink-0">
                      <svg className="w-5 h-5 text-gray-400 group-hover:text-indigo-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              )}
              {alerts.length === 0 && (
                <div className="text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5-5-5h5v-5a7.5 7.5 0 00-15 0v5h5l-5 5-5-5h5V7.5a7.5 7.5 0 0115 0V17z" />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No alerts detected</h3>
                  <p className="mt-1 text-sm text-gray-500">Your assets are currently secure. New alerts will appear here when threats are detected.</p>
                </div>
              )}
            </div>
          )}
        </div>
    );
};

const AssetManagement = ({ active }) => {
  const [activeTab, setActiveTab] = useState('inventory');
  const [assets, setAssets] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
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

  useEffect(() => {
    if (active) {
      fetchData();
    }
  }, [active]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [assetsRes, alertsRes, statsRes] = await Promise.all([
        getAssetInventory(),
        getCustomAlerts(),
        getAssetAlertStatistics()
      ]);
      if (assetsRes && assetsRes.data) {
        setAssets(assetsRes.data.results);
      }
      if (alertsRes && alertsRes.data) {
        setAlerts(alertsRes.data.results);
      }
      if (statsRes && statsRes.data) {
        setStats(statsRes.data);
      }
    } catch (err) {
      setError('Failed to fetch data. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  const handleTriggerCorrelation = async () => {
    try {
      setLoading(true);
      await triggerAssetCorrelation();
      showNotification('Asset correlation triggered successfully! New alerts will be generated based on your asset inventory.', 'success');
      fetchData();
    } catch (err) {
      showNotification('Failed to trigger asset correlation. Please try again.', 'error');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAssetModal = (asset = null) => {
    setEditingAsset(asset);
    setShowAssetModal(true);
  };

  const handleCloseAssetModal = () => {
    setEditingAsset(null);
    setShowAssetModal(false);
  };

  const handleSaveAsset = async (assetData) => {
    try {
      if (editingAsset) {
        await updateAsset(editingAsset.id, assetData);
        showNotification(`Asset "${assetData.name}" updated successfully.`, 'success');
      } else {
        await createAsset(assetData);
        showNotification(`Asset "${assetData.name}" created successfully.`, 'success');
      }
      fetchData();
      handleCloseAssetModal();
    } catch (err) {
      showNotification('Failed to save asset. Please check your input and try again.', 'error');
      console.error(err);
    }
  };

  const handleDeleteAsset = (asset) => {
    setConfirmModal({
      title: 'Delete Asset',
      message: `Are you sure you want to delete "${asset.name}"? This action cannot be undone.`,
      confirmText: 'Delete',
      cancelText: 'Cancel',
      onConfirm: async () => {
        try {
          await deleteAsset(asset.id);
          showNotification(`Asset "${asset.name}" deleted successfully.`, 'success');
          fetchData();
        } catch (err) {
          showNotification('Failed to delete asset. Please try again.', 'error');
          console.error(err);
        }
        setConfirmModal(null);
      },
      onCancel: () => setConfirmModal(null)
    });
  };

  const handleOpenAlertModal = async (alertId) => {
    try {
        const res = await getCustomAlertDetails(alertId);
        setSelectedAlert(res.data);
        setShowAlertModal(true);
    } catch (err) {
        console.error('Failed to fetch alert details', err);
        alert('Failed to fetch alert details.');
    }
  }

  const handleCloseAlertModal = () => {
    setSelectedAlert(null);
    setShowAlertModal(false);
  }

  const handleOpenBulkUploadModal = () => {
    setShowBulkUploadModal(true);
  }

  const handleCloseBulkUploadModal = () => {
    setShowBulkUploadModal(false);
  }

  const handleBulkUpload = async (file) => {
    try {
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const content = e.target.result;
          const assets = JSON.parse(content);
          setLoading(true);
          await bulkUploadAssets(assets);
          fetchData();
          handleCloseBulkUploadModal();
          showNotification(`Successfully uploaded ${assets.length} assets!`, 'success');
        } catch (parseErr) {
          showNotification('Invalid JSON file. Please check the file format.', 'error');
          console.error(parseErr);
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

  if (!active) {
    return null;
  }

  // Auto-refresh for alerts
  useEffect(() => {
    if (active && activeTab === 'alerts') {
      const interval = setInterval(() => {
        fetchData();
      }, 30000); // Refresh every 30 seconds
      setRefreshInterval(interval);
      return () => clearInterval(interval);
    } else if (refreshInterval) {
      clearInterval(refreshInterval);
      setRefreshInterval(null);
    }
  }, [active, activeTab]);

  // Filter functions
  const filteredAssets = assets.filter(asset => {
    const matchesSearch = asset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         asset.asset_value.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || asset.asset_type === filterType;
    return matchesSearch && matchesType;
  });

  const filteredAlerts = alerts.filter(alert => {
    const matchesSearch = alert.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = filterSeverity === 'all' || alert.severity === filterSeverity;
    return matchesSearch && matchesSeverity;
  });

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <div className="space-y-6">
      {/* Enhanced Stats Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl border border-blue-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-600 mb-1">Total Assets</p>
              <p className="text-3xl font-bold text-blue-900">{stats?.asset_statistics?.total_assets || 0}</p>
              <p className="text-xs text-blue-600 mt-1">Managed assets</p>
            </div>
            <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-50 to-orange-100 p-6 rounded-xl border border-yellow-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-orange-600 mb-1">Active Alerts</p>
              <p className="text-3xl font-bold text-orange-900">{stats?.alert_statistics?.recent_alerts || 0}</p>
              <p className="text-xs text-orange-600 mt-1">Last 30 days</p>
            </div>
            <div className="w-12 h-12 bg-orange-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"/>
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-emerald-100 p-6 rounded-xl border border-green-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-600 mb-1">Coverage</p>
              <p className="text-3xl font-bold text-green-900">{stats?.asset_statistics?.alert_coverage_percentage || 0}%</p>
              <p className="text-xs text-green-600 mt-1">Asset monitoring</p>
            </div>
            <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-indigo-100 p-6 rounded-xl border border-purple-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-600 mb-1">Smart Correlation</p>
              <button
                onClick={handleTriggerCorrelation}
                disabled={loading}
                className="mt-2 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
              >
                {loading ? 'Processing...' : 'Trigger Now'}
              </button>
            </div>
            <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Tabs with Search and Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between p-6">
            <nav className="flex space-x-8 mb-4 lg:mb-0">
              <button
                onClick={() => setActiveTab('inventory')}
                className={`relative py-2 px-1 font-medium text-sm transition-colors ${
                  activeTab === 'inventory'
                    ? 'text-indigo-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
                  </svg>
                  <span>Asset Inventory</span>
                  <span className="ml-2 bg-gray-100 text-gray-600 text-xs font-medium px-2 py-1 rounded-full">
                    {filteredAssets.length}
                  </span>
                </div>
                {activeTab === 'inventory' && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 rounded-full"></div>
                )}
              </button>
              <button
                onClick={() => setActiveTab('alerts')}
                className={`relative py-2 px-1 font-medium text-sm transition-colors ${
                  activeTab === 'alerts'
                    ? 'text-indigo-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"/>
                  </svg>
                  <span>Custom Alerts</span>
                  <span className="ml-2 bg-orange-100 text-orange-600 text-xs font-medium px-2 py-1 rounded-full">
                    {filteredAlerts.length}
                  </span>
                </div>
                {activeTab === 'alerts' && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 rounded-full"></div>
                )}
              </button>
            </nav>

            {/* Search and Filter Controls */}
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative">
                <input
                  type="text"
                  placeholder={`Search ${activeTab === 'inventory' ? 'assets' : 'alerts'}...`}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent w-full sm:w-64"
                />
                <svg className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>

              {activeTab === 'inventory' ? (
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
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
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="all">All Severities</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              )}
            </div>
          </div>
        </div>

        {/* Enhanced Content */}
        <div className="p-6">
          {activeTab === 'inventory' && (
            <AssetInventoryTab
              assets={filteredAssets}
              onAdd={() => handleOpenAssetModal()}
              onEdit={handleOpenAssetModal}
              onDelete={handleDeleteAsset}
              onBulkUpload={handleOpenBulkUploadModal}
              loading={loading}
            />
          )}
          {activeTab === 'alerts' && (
            <CustomAlertsTab
              alerts={filteredAlerts}
              onView={handleOpenAlertModal}
              loading={loading}
              refreshInterval={refreshInterval !== null}
            />
          )}
        </div>
      </div>

      {/* Modals and Notifications */}
      {showAssetModal && <AssetModal asset={editingAsset} onSave={handleSaveAsset} onClose={handleCloseAssetModal} />}
      {showAlertModal && <AlertModal alert={selectedAlert} onClose={handleCloseAlertModal} />}
      {showBulkUploadModal && <BulkUploadModal onUpload={handleBulkUpload} onClose={handleCloseBulkUploadModal} />}
      {notification && <NotificationToast message={notification.message} type={notification.type} onClose={() => setNotification(null)} />}
      {confirmModal && <ConfirmationModal {...confirmModal} />}
    </div>
  );
};

const AssetModal = ({ asset, onSave, onClose }) => {
    const [formData, setFormData] = useState({
        name: '',
        asset_type: 'domain',
        asset_value: '',
        description: '',
        criticality: 'medium',
        alert_enabled: true,
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        if (asset) {
            setFormData(asset);
        }
    }, [asset]);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        try {
            await onSave(formData);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed z-10 inset-0 overflow-y-auto">
            <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                <div className="fixed inset-0 transition-opacity" aria-hidden="true">
                    <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
                </div>
                <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                    <form onSubmit={handleSubmit}>
                        <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                            <h3 className="text-lg leading-6 font-medium text-gray-900">{asset ? 'Edit' : 'Add'} Asset</h3>
                            <div className="mt-2">
                                <div className="mb-4">
                                    <label className="block text-gray-700 text-sm font-bold mb-2">Name</label>
                                    <input type="text" name="name" value={formData.name} onChange={handleChange} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required />
                                </div>
                                <div className="mb-4">
                                    <label className="block text-gray-700 text-sm font-bold mb-2">Asset Type</label>
                                    <select name="asset_type" value={formData.asset_type} onChange={handleChange} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                                        <option value="domain">Domain</option>
                                        <option value="ip_range">IP Range</option>
                                        <option value="software">Software</option>
                                    </select>
                                </div>
                                <div className="mb-4">
                                    <label className="block text-gray-700 text-sm font-bold mb-2">Asset Value</label>
                                    <input type="text" name="asset_value" value={formData.asset_value} onChange={handleChange} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required />
                                </div>
                                <div className="mb-4">
                                    <label className="block text-gray-700 text-sm font-bold mb-2">Description</label>
                                    <textarea name="description" value={formData.description} onChange={handleChange} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"></textarea>
                                </div>
                                <div className="mb-4">
                                    <label className="block text-gray-700 text-sm font-bold mb-2">Criticality</label>
                                    <select name="criticality" value={formData.criticality} onChange={handleChange} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                                        <option value="low">Low</option>
                                        <option value="medium">Medium</option>
                                        <option value="high">High</option>
                                        <option value="critical">Critical</option>
                                    </select>
                                </div>
                                <div className="mb-4">
                                    <label className="flex items-center">
                                        <input type="checkbox" name="alert_enabled" checked={formData.alert_enabled} onChange={handleChange} className="mr-2" />
                                        <span>Enable Alerts</span>
                                    </label>
                                </div>
                            </div>
                        </div>
                        <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                            <button
                                type="submit"
                                disabled={isSubmitting}
                                className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isSubmitting ? (
                                    <div className="flex items-center">
                                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Saving...
                                    </div>
                                ) : (
                                    'Save Asset'
                                )}
                            </button>
                            <button type="button" onClick={onClose} className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">Cancel</button>
                        </div>
                    </form>
                </div>
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
        <div className="fixed z-50 inset-0 overflow-y-auto">
            <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                <div className="fixed inset-0 transition-opacity" aria-hidden="true">
                    <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
                </div>
                <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                <div className="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
                    <div className="bg-white">
                        {/* Header */}
                        <div className={`${config.bg} ${config.border} border-b px-6 py-4`}>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    <span className="text-2xl">{config.icon}</span>
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-900">{alert.title}</h3>
                                        <div className="flex items-center space-x-3 mt-1">
                                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.text}`}>
                                                {alert.severity_display || alert.severity}
                                            </span>
                                            <span className="text-sm text-gray-600">
                                                Alert ID: {alert.alert_id || alert.id}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <button
                                    onClick={onClose}
                                    className="text-gray-400 hover:text-gray-600 transition-colors"
                                >
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        </div>

                        {/* Content */}
                        <div className="px-6 py-6 max-h-96 overflow-y-auto">
                            {/* Alert Description */}
                            <div className="mb-6">
                                <h4 className="text-sm font-medium text-gray-900 mb-2">Description</h4>
                                <div className="bg-gray-50 rounded-lg p-4">
                                    <p className="text-sm text-gray-700 whitespace-pre-wrap">{alert.description}</p>
                                </div>
                            </div>

                            {/* Alert Metrics */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                                <div className="bg-blue-50 rounded-lg p-4">
                                    <div className="flex items-center">
                                        <svg className="w-5 h-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                        </svg>
                                        <div>
                                            <p className="text-sm font-medium text-blue-900">Confidence</p>
                                            <p className="text-lg font-bold text-blue-600">{Math.round((alert.confidence_score || 0) * 100)}%</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="bg-purple-50 rounded-lg p-4">
                                    <div className="flex items-center">
                                        <svg className="w-5 h-5 text-purple-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                        </svg>
                                        <div>
                                            <p className="text-sm font-medium text-purple-900">Relevance</p>
                                            <p className="text-lg font-bold text-purple-600">{Math.round((alert.relevance_score || 0) * 100)}%</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="bg-green-50 rounded-lg p-4">
                                    <div className="flex items-center">
                                        <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.414-1.415L11 9.586V6z" clipRule="evenodd" />
                                        </svg>
                                        <div>
                                            <p className="text-sm font-medium text-green-900">Detected</p>
                                            <p className="text-sm font-semibold text-green-600">{new Date(alert.detected_at).toLocaleString()}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Matched Assets */}
                            {alert.matched_assets && alert.matched_assets.length > 0 && (
                                <div className="mb-6">
                                    <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                                        <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
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
                                        <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
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
                                        <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
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
}

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
        <div className="fixed z-50 inset-0 overflow-y-auto">
            <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                <div className="fixed inset-0 transition-opacity" aria-hidden="true">
                    <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
                </div>
                <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                <div className="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
                    <form onSubmit={handleSubmit}>
                        <div className="bg-white px-6 pt-6 pb-4">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">Bulk Upload Assets</h3>
                                <button
                                    type="button"
                                    onClick={onClose}
                                    className="text-gray-400 hover:text-gray-600 transition-colors"
                                >
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>

                            <div className="space-y-4">
                                <p className="text-sm text-gray-600">
                                    Upload a JSON file containing an array of asset objects. Each asset should include name, asset_type, asset_value, and other properties.
                                </p>

                                {/* File Upload Area */}
                                <div
                                    className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                                        dragActive ? 'border-indigo-400 bg-indigo-50' :
                                        file ? 'border-green-400 bg-green-50' : 'border-gray-300 hover:border-gray-400'
                                    }`}
                                    onDragEnter={handleDrag}
                                    onDragLeave={handleDrag}
                                    onDragOver={handleDrag}
                                    onDrop={handleDrop}
                                >
                                    <input
                                        type="file"
                                        onChange={handleFileChange}
                                        accept=".json"
                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                        disabled={isUploading}
                                    />
                                    <div>
                                        {file ? (
                                            <div className="flex items-center justify-center">
                                                <svg className="w-8 h-8 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                                                </svg>
                                                <div>
                                                    <p className="text-sm font-medium text-green-900">{file.name}</p>
                                                    <p className="text-xs text-green-600">{(file.size / 1024).toFixed(1)} KB</p>
                                                </div>
                                            </div>
                                        ) : (
                                            <div>
                                                <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                                                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                                                </svg>
                                                <div className="mt-2">
                                                    <p className="text-sm text-gray-900">Drop your JSON file here, or <span className="text-indigo-600 font-medium">click to browse</span></p>
                                                    <p className="text-xs text-gray-500 mt-1">JSON files only</p>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Sample Data */}
                                <div className="bg-gray-50 rounded-lg p-4">
                                    <h4 className="text-sm font-medium text-gray-900 mb-2">Sample JSON Format:</h4>
                                    <pre className="text-xs text-gray-600 overflow-x-auto">
                                        {JSON.stringify(sampleData, null, 2)}
                                    </pre>
                                </div>
                            </div>
                        </div>

                        <div className="bg-gray-50 px-6 py-4 flex justify-end space-x-3 border-t">
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={!file || isUploading}
                                className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                            >
                                {isUploading ? (
                                    <div className="flex items-center">
                                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Uploading...
                                    </div>
                                ) : (
                                    'Upload Assets'
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default AssetManagement;
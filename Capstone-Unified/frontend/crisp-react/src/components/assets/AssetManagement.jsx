import React, { useState, useEffect } from 'react';
import { getAssetInventory, createAsset, updateAsset, deleteAsset, bulkUploadAssets, getCustomAlerts, getAssetAlertStatistics, triggerAssetCorrelation, getCustomAlertDetails, updateAlertStatus } from '../../api/assets';
import LoadingSpinner from '../LoadingSpinner';

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

  const handleTriggerCorrelation = async () => {
    try {
      await triggerAssetCorrelation();
      alert('Asset correlation triggered successfully!');
      fetchData(); // Refresh data
    } catch (err) {
      alert('Failed to trigger asset correlation.');
      console.error(err);
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
      } else {
        await createAsset(assetData);
      }
      fetchData();
      handleCloseAssetModal();
    } catch (err) {
      console.error('Failed to save asset', err);
      alert('Failed to save asset. Please check the console for details.');
    }
  };

  const handleDeleteAsset = async (assetId) => {
    if (window.confirm('Are you sure you want to delete this asset?')) {
        try {
            await deleteAsset(assetId);
            fetchData();
        } catch (err) {
            console.error('Failed to delete asset', err);
            alert('Failed to delete asset.');
        }
    }
  }

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
            const content = e.target.result;
            const assets = JSON.parse(content);
            await bulkUploadAssets(assets);
            fetchData();
            handleCloseBulkUploadModal();
            alert('Bulk upload successful!');
        };
        reader.readAsText(file);
    } catch (err) {
        console.error('Bulk upload failed', err);
        alert('Bulk upload failed. Please check the file format and content.');
    }
  }

  if (!active) return null;

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Subtle Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Asset-Based Alert System</h1>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Compact Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-6 h-6 bg-blue-100 rounded flex items-center justify-center">
                  <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
                  </svg>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Assets</p>
                <p className="text-lg font-semibold text-gray-900">{stats?.asset_statistics?.total_assets || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-6 h-6 bg-yellow-100 rounded flex items-center justify-center">
                  <svg className="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"/>
                  </svg>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Alerts (Last 30d)</p>
                <p className="text-lg font-semibold text-gray-900">{stats?.alert_statistics?.recent_alerts || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-6 h-6 bg-green-100 rounded flex items-center justify-center">
                  <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                  </svg>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Alert Coverage</p>
                <p className="text-lg font-semibold text-gray-900">{stats?.asset_statistics?.alert_coverage_percentage || 0}%</p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end mb-4">
          <button
            onClick={handleTriggerCorrelation}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <svg className="-ml-0.5 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Trigger Correlation
          </button>
        </div>

        {/* Tabs */}
        <div className="mb-4">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-4" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('inventory')}
                className={`${
                  activeTab === 'inventory'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
              >
                Asset Inventory
              </button>
              <button
                onClick={() => setActiveTab('alerts')}
                className={`${
                  activeTab === 'alerts'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
              >
                Custom Alerts
              </button>
            </nav>
          </div>
        </div>

        {/* Content */}
        <div>
          {activeTab === 'inventory' && (
            <AssetInventoryTab assets={assets} onAdd={() => handleOpenAssetModal()} onEdit={handleOpenAssetModal} onDelete={handleDeleteAsset} onBulkUpload={handleOpenBulkUploadModal} />
          )}
          {activeTab === 'alerts' && <CustomAlertsTab alerts={alerts} onView={handleOpenAlertModal} />}
        </div>

        {showAssetModal && <AssetModal asset={editingAsset} onSave={handleSaveAsset} onClose={handleCloseAssetModal} />}
        {showAlertModal && <AlertModal alert={selectedAlert} onClose={handleCloseAlertModal} />}
        {showBulkUploadModal && <BulkUploadModal onUpload={handleBulkUpload} onClose={handleCloseBulkUploadModal} />}
      </div>
    </div>
  );
};


const AssetInventoryTab = ({ assets, onAdd, onEdit, onDelete, onBulkUpload }) => {
    return (
        <div className="bg-white shadow-sm rounded-lg border border-gray-200">
          <div className="px-4 py-3 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h3 className="text-base font-medium text-gray-900">Your Organization's Assets</h3>
              <div className="flex space-x-2">
                <button 
                  onClick={onAdd} 
                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  <svg className="-ml-0.5 mr-1.5 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Add Asset
                </button>
                <button 
                  onClick={onBulkUpload} 
                  className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <svg className="-ml-0.5 mr-1.5 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  Bulk Upload
                </button>
              </div>
            </div>
          </div>
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      <ul className="divide-y divide-gray-200">
        {assets.map((asset) => (
          <li key={asset.id}>
            <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-indigo-600 truncate">{asset.name}</p>
                  <div className="ml-2 flex-shrink-0 flex">
                    <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        asset.criticality === 'critical' ? 'bg-red-100 text-red-800' :
                        asset.criticality === 'high' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                    }`}>
                      {asset.criticality_display}
                    </p>
                  </div>
                </div>
                <div className="mt-2 sm:flex sm:justify-between">
                  <div className="sm:flex">
                    <p className="flex items-center text-sm text-gray-500">
                      {asset.asset_type_display}
                    </p>
                    <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6">
                      {asset.asset_value}
                    </p>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                    <p>{asset.alert_enabled ? 'Alerts Enabled' : 'Alerts Disabled'}</p>
                  </div>
                </div>
                <div className="mt-4 flex justify-end">
                    <button onClick={() => onEdit(asset)} className="text-sm font-medium text-indigo-600 hover:text-indigo-900">Edit</button>
                    <button onClick={() => onDelete(asset.id)} className="ml-4 text-sm font-medium text-red-600 hover:text-red-900">Delete</button>
                </div>
              </div>
          </li>
        ))}
      </ul>
    </div>
    </div>
    )
};

const CustomAlertsTab = ({ alerts, onView }) => {
    return (
        <div>
        <h2 className="text-xl font-semibold mb-2">Recent Custom Alerts</h2>
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      <ul className="divide-y divide-gray-200">
        {alerts.map((alert) => (
          <li key={alert.id} onClick={() => onView(alert.id)} className="cursor-pointer hover:bg-gray-50">
            <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-indigo-600 truncate">{alert.title}</p>
                  <div className="ml-2 flex-shrink-0 flex">
                  <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                        alert.severity === 'high' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                    }`}>
                      {alert.severity_display}
                    </p>
                  </div>
                </div>
                <div className="mt-2 sm:flex sm:justify-between">
                  <div className="sm:flex">
                    <p className="flex items-center text-sm text-gray-500">
                      {alert.status_display}
                    </p>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                    <p>Detected: {new Date(alert.detected_at).toLocaleString()}</p>
                  </div>
                </div>
              </div>
          </li>
        ))}
      </ul>
    </div>
    </div>
    )
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

    useEffect(() => {
        if (asset) {
            setFormData(asset);
        }
    }, [asset]);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSave(formData);
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
                            <button type="submit" className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm">Save</button>
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

    return (
        <div className="fixed z-10 inset-0 overflow-y-auto">
            <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                <div className="fixed inset-0 transition-opacity" aria-hidden="true">
                    <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
                </div>
                <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                    <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                        <h3 className="text-lg leading-6 font-medium text-gray-900">{alert.title}</h3>
                        <div className="mt-2">
                            <p className="text-sm text-gray-500">{alert.description}</p>
                            <div className="mt-4">
                                <p><strong>Severity:</strong> {alert.severity_display}</p>
                                <p><strong>Status:</strong> {alert.status_display}</p>
                                <p><strong>Detected:</strong> {new Date(alert.detected_at).toLocaleString()}</p>
                                <p><strong>Confidence:</strong> {alert.confidence_score}</p>
                                <p><strong>Relevance:</strong> {alert.relevance_score}</p>
                            </div>
                            <div className="mt-4">
                                <h4 className="text-md font-medium text-gray-800">Matched Assets</h4>
                                <ul>
                                    {alert.matched_assets.map(asset => (
                                        <li key={asset.id}>{asset.name} ({asset.asset_type}) - {asset.asset_value}</li>
                                    ))}
                                </ul>
                            </div>
                            <div className="mt-4">
                                <h4 className="text-md font-medium text-gray-800">Source Indicators</h4>
                                <ul>
                                    {alert.source_indicators.map(indicator => (
                                        <li key={indicator.id}>{indicator.value} ({indicator.type})</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                        <button type="button" onClick={onClose} className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">Close</button>
                    </div>
                </div>
            </div>
        </div>
    );
}

const BulkUploadModal = ({ onUpload, onClose }) => {
    const [file, setFile] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (file) {
            onUpload(file);
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
                            <h3 className="text-lg leading-6 font-medium text-gray-900">Bulk Upload Assets</h3>
                            <div className="mt-2">
                                <p className="text-sm text-gray-500">Upload a JSON file with an array of asset objects.</p>
                                <div className="mt-4">
                                    <input type="file" onChange={handleFileChange} accept=".json" className="w-full" />
                                </div>
                            </div>
                        </div>
                        <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                            <button type="submit" className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm" disabled={!file}>Upload</button>
                            <button type="button" onClick={onClose} className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default AssetManagement;
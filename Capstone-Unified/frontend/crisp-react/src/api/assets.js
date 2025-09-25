
import { get, post, put, deleteRequest } from '../api.js';

const BASE_URL = '/api';

// Asset Inventory API

export const getAssetInventory = (params) => {
  return get(`${BASE_URL}/assets/inventory/`, params);
};

export const getAssetDetails = (assetId) => {
  return get(`${BASE_URL}/assets/inventory/${assetId}/`);
};

export const createAsset = (assetData) => {
  return post(`${BASE_URL}/assets/inventory/`, assetData);
};

export const updateAsset = (assetId, assetData) => {
  return put(`${BASE_URL}/assets/inventory/${assetId}/`, assetData);
};

export const deleteAsset = (assetId) => {
  return deleteRequest(`${BASE_URL}/assets/inventory/${assetId}/`);
};

export const bulkUploadAssets = (assets) => {
  return post(`${BASE_URL}/assets/bulk-upload/`, { assets });
};

// Custom Alerts API

export const getCustomAlerts = (params) => {
  return get(`${BASE_URL}/assets/alerts/`, params);
};

export const getCustomAlertDetails = (alertId) => {
  return get(`${BASE_URL}/assets/alerts/${alertId}/`);
};

export const updateAlertStatus = (alertId, action) => {
  return post(`${BASE_URL}/assets/alerts/${alertId}/action/`, { action });
};

export const deleteAlert = (alertId) => {
  return deleteRequest(`${BASE_URL}/assets/alerts/${alertId}/`);
};

// Statistics and Correlation API

export const getAssetAlertStatistics = () => {
  return get(`${BASE_URL}/assets/statistics/`);
};

export const triggerAssetCorrelation = (days = 1) => {
  return post(`${BASE_URL}/assets/correlation/trigger/`, { days });
};

// Real-time alert feed
export const getAssetAlertFeed = (params) => {
  return get(`${BASE_URL}/assets/alerts/feed/`, params);
};

// Alert actions
export const acknowledgeAlert = (alertId) => {
  return updateAlertStatus(alertId, 'acknowledge');
};

export const resolveAlert = (alertId) => {
  return updateAlertStatus(alertId, 'resolve');
};

export const dismissAlert = (alertId) => {
  return updateAlertStatus(alertId, 'dismiss');
};

export const escalateAlert = (alertId) => {
  return updateAlertStatus(alertId, 'escalate');
};

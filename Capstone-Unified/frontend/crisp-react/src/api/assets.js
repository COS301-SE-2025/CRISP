
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
  return post(`${BASE_URL}/assets/alerts/${alertId}/`, { action });
};

// Statistics and Correlation API

export const getAssetAlertStatistics = () => {
  return get(`${BASE_URL}/assets/statistics/`);
};

export const triggerAssetCorrelation = (days = 1) => {
  return post(`${BASE_URL}/assets/correlation/trigger/`, { days });
};

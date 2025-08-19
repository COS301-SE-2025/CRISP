// API functions for CRISP application

const API_BASE_URL = 'http://localhost:8000';

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('crisp_auth_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

// Helper function to get current user from localStorage
export const getCurrentUser = () => {
  try {
    const userString = localStorage.getItem('crisp_user');
    return userString ? JSON.parse(userString) : null;
  } catch (error) {
    console.error('Error parsing current user from localStorage:', error);
    return null;
  }
};

// Login function
export const loginUser = async (username, password) => {
  const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: username,
      password: password,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Login failed');
  }

  const data = await response.json();
  
  // Transform the response to match expected format
  // Capstone-Unified API returns: { access, refresh, user }
  // Frontend expects: { tokens: { access }, user }
  return {
    tokens: {
      access: data.access,
      refresh: data.refresh
    },
    user: data.user
  };
};

// User Management Functions
export const getUsersList = async (queryParams = {}) => {
  const params = new URLSearchParams(queryParams).toString();
  const url = `${API_BASE_URL}/api/users/${params ? `?${params}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch users');
  }

  return await response.json();
};

export const getUserDetails = async (userId) => {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch user');
  }

  return await response.json();
};

export const createUser = async (userData) => {
  const response = await fetch(`${API_BASE_URL}/api/users/create/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to create user');
  }

  return await response.json();
};

export const updateUser = async (userId, userData) => {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/update/`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to update user');
  }

  return await response.json();
};

export const deactivateUser = async (userId, reason = '') => {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/deactivate/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ reason }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to deactivate user');
  }

  return await response.json();
};

export const reactivateUser = async (userId, reason = '') => {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/reactivate/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ reason }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to reactivate user');
  }

  return await response.json();
};

export const deleteUserPermanently = async (userId, reason = '') => {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/delete-permanently/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
    body: JSON.stringify({ 
      confirm: true,
      reason 
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to permanently delete user');
  }

  // For DELETE requests, we might get 204 No Content with no response body
  if (response.status === 204) {
    return { success: true };
  }
  
  // Try to parse JSON, but handle empty responses
  const text = await response.text();
  return text ? JSON.parse(text) : { success: true };
};


// Organization Management Functions
export const getOrganizations = async (queryParams = {}) => {
  const params = new URLSearchParams(queryParams).toString();
  const url = `${API_BASE_URL}/api/organizations/${params ? `?${params}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch organizations');
  }

  return await response.json();
};

export const createOrganization = async (orgData) => {
  const response = await fetch(`${API_BASE_URL}/api/organizations/create/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(orgData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to create organization');
  }

  return await response.json();
};

export const updateOrganization = async (orgId, orgData) => {
  const response = await fetch(`${API_BASE_URL}/api/organizations/${orgId}/update/`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(orgData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to update organization');
  }

  return await response.json();
};

export const deactivateOrganization = async (orgId, reason = '') => {
  const response = await fetch(`${API_BASE_URL}/api/organizations/${orgId}/deactivate/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ reason }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to deactivate organization');
  }

  return await response.json();
};

export const reactivateOrganization = async (orgId, reason = '') => {
  const response = await fetch(`${API_BASE_URL}/api/organizations/${orgId}/reactivate/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ reason }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to reactivate organization');
  }

  return await response.json();
};

export const deleteOrganizationPermanently = async (orgId, reason = '') => {
  const response = await fetch(`${API_BASE_URL}/api/organizations/${orgId}/delete-permanently/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
    body: JSON.stringify({ 
      confirm: true,
      reason 
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to permanently delete organization');
  }

  // For DELETE requests, we might get 204 No Content with no response body
  if (response.status === 204) {
    return { success: true };
  }
  
  // Try to parse JSON, but handle empty responses
  const text = await response.text();
  return text ? JSON.parse(text) : { success: true };
};

export const getOrganizationDetails = async (orgId) => {
  const response = await fetch(`${API_BASE_URL}/api/organizations/${orgId}/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch organization details');
  }

  return await response.json();
};

export const getOrganizationTypes = async () => {
  const response = await fetch(`${API_BASE_URL}/api/organizations/types/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch organization types');
  }

  return await response.json();
};

export const getOrganizationTrustRelationships = async (orgId) => {
  const response = await fetch(`${API_BASE_URL}/api/organizations/${orgId}/trust-relationships/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch organization trust relationships');
  }

  return await response.json();
};

export const getOrganizationTrustGroups = async (orgId) => {
  // Trust groups are retrieved from the community endpoint with organization filtering
  const response = await fetch(`${API_BASE_URL}/api/trust/community/?organization=${orgId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch organization trust groups');
  }

  return await response.json();
};

// Trust Management Functions
export const getTrustRelationships = async (queryParams = {}) => {
  // By default, exclude revoked relationships unless specifically requested
  const defaultParams = {
    // Only include active, pending, and suspended relationships by default
    // Exclude 'revoked' and 'expired' unless explicitly overridden
    ...queryParams
  };
  
  // If no status filter is provided, exclude revoked relationships
  if (!defaultParams.status) {
    // We'll filter out revoked relationships in the response instead
    // This way users can still see them if they specifically request 'revoked' status
  }
  
  // Cache-busting temporarily disabled to avoid CORS issues
  // defaultParams._t = Date.now();
  
  const params = new URLSearchParams(defaultParams).toString();
  const url = `${API_BASE_URL}/api/trust/bilateral/${params ? `?${params}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch trust relationships');
  }

  const data = await response.json();
  
  // Filter out revoked and expired relationships unless specifically requested
  if (!queryParams.status || !['revoked', 'expired'].includes(queryParams.status)) {
    // Filter data.trusts if it exists (direct array)
    if (data.trusts && Array.isArray(data.trusts)) {
      const originalCount = data.trusts.length;
      data.trusts = data.trusts.filter(trust => 
        trust.status && 
        !['revoked', 'expired'].includes(trust.status.toLowerCase())
      );
      console.log(`🔍 Filtered trust relationships: ${originalCount} -> ${data.trusts.length} (excluded revoked/expired)`);
    }
    
    // Filter data.results.trusts if it exists (paginated response)
    if (data.results && data.results.trusts && Array.isArray(data.results.trusts)) {
      const originalCount = data.results.trusts.length;
      data.results.trusts = data.results.trusts.filter(trust => 
        trust.status && 
        !['revoked', 'expired'].includes(trust.status.toLowerCase())
      );
      console.log(`🔍 Filtered paginated trust relationships: ${originalCount} -> ${data.results.trusts.length} (excluded revoked/expired)`);
    }
  } else {
    console.log(`🔍 Showing ALL '${queryParams.status}' relationships (no filtering)`);
  }
  
  return data;
};

export const createTrustRelationship = async (relationshipData) => {
  // Map frontend field names to backend expectations
  const mappedData = {
    responding_organization_id: relationshipData.target_organization,
    trust_level: relationshipData.trust_level,
    message: relationshipData.notes || ''
  };
  
  const response = await fetch(`${API_BASE_URL}/api/trust/bilateral/request/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(mappedData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to create trust relationship');
  }

  return await response.json();
};

export const updateTrustRelationship = async (relationshipId, relationshipData) => {
  const response = await fetch(`${API_BASE_URL}/api/trust/bilateral/${relationshipId}/update/`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(relationshipData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to update trust relationship');
  }

  return await response.json();
};

export const respondToTrustRelationship = async (relationshipId, action, trustLevel = null, message = '') => {
  const response = await fetch(`${API_BASE_URL}/api/trust/bilateral/${relationshipId}/respond/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      action: action, // 'accept' or 'reject'
      trust_level: trustLevel,
      message: message
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to respond to trust relationship');
  }

  return await response.json();
};

export const deleteTrustRelationship = async (relationshipId, reason = '') => {
  const response = await fetch(`${API_BASE_URL}/api/trust/bilateral/${relationshipId}/revoke/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
    body: JSON.stringify({ message: reason }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to delete trust relationship');
  }

  // For DELETE requests, we might get 204 No Content with no response body
  if (response.status === 204) {
    return { success: true };
  }
  
  // Try to parse JSON, but handle empty responses
  const text = await response.text();
  return text ? JSON.parse(text) : { success: true };
};

export const getTrustGroups = async (queryParams = {}) => {
  // Cache-busting temporarily disabled to avoid CORS issues  
  const params = new URLSearchParams(queryParams).toString();
  const url = `${API_BASE_URL}/api/trust/community/${params ? `?${params}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch trust groups');
  }

  return await response.json();
};

export const createTrustGroup = async (groupData) => {
  const response = await fetch(`${API_BASE_URL}/api/trust/community/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(groupData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to create trust group');
  }

  return await response.json();
};

export const updateTrustGroup = async (groupId, groupData) => {
  const response = await fetch(`${API_BASE_URL}/api/trust-management/groups/${groupId}/`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(groupData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to update trust group');
  }

  return await response.json();
};

export const deleteTrustGroup = async (groupId) => {
  const response = await fetch(`${API_BASE_URL}/api/trust-management/groups/${groupId}/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to delete trust group');
  }

  // For DELETE requests, we might get 204 No Content with no response body
  if (response.status === 204) {
    return { success: true };
  }
  
  // Try to parse JSON, but handle empty responses
  const text = await response.text();
  return text ? JSON.parse(text) : { success: true };
};

export const joinTrustGroup = async (groupId) => {
  const response = await fetch(`${API_BASE_URL}/api/trust-management/groups/${groupId}/join/`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to join trust group');
  }

  return await response.json();
};

export const getTrustMetrics = async () => {
  const response = await fetch(`${API_BASE_URL}/api/trust-management/metrics/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch trust metrics');
  }

  return await response.json();
};

export const getTrustLevels = async () => {
  const response = await fetch(`${API_BASE_URL}/api/trust/levels/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch trust levels');
  }

  return await response.json();
};

// Notification Management Functions
export const getAlerts = async (queryParams = {}) => {
  const params = new URLSearchParams(queryParams).toString();
  const url = `${API_BASE_URL}/api/alerts/list/${params ? `?${params}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch alerts');
  }

  return await response.json();
};

export const createNotification = async (notificationData) => {
  const response = await fetch(`${API_BASE_URL}/api/alerts/create/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(notificationData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || errorData.message || 'Failed to create notification');
  }

  return await response.json();
};

export const markNotificationRead = async (notificationId) => {
  const response = await fetch(`${API_BASE_URL}/api/alerts/${notificationId}/mark-read/`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || errorData.message || 'Failed to mark notification as read');
  }

  return await response.json();
};

export const markAllNotificationsRead = async () => {
  const response = await fetch(`${API_BASE_URL}/api/alerts/mark-all-read/`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || errorData.message || 'Failed to mark all notifications as read');
  }

  return await response.json();
};

// TTP Analysis Functions
export const getThreatFeedTtps = async (feedId, queryParams = {}) => {
  const params = new URLSearchParams(queryParams).toString();
  const url = `${API_BASE_URL}/api/threat-feeds/${feedId}/ttps/${params ? `?${params}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch threat feed TTPs');
  }

  return await response.json();
};

export const getMitreMatrix = async () => {
  const response = await fetch(`${API_BASE_URL}/api/ttps/mitre-matrix/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch MITRE matrix');
  }

  return await response.json();
};

export const getTtpFeedComparison = async (days = 30) => {
  const response = await fetch(`${API_BASE_URL}/api/ttps/feed-comparison/?days=${days}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch TTP feed comparison');
  }

  return await response.json();
};

export const getTtpSeasonalPatterns = async (days = 180) => {
  const response = await fetch(`${API_BASE_URL}/api/ttps/seasonal-patterns/?days=${days}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch TTP seasonal patterns');
  }

  return await response.json();
};

export const getTtpTechniqueFrequencies = async (days = 30) => {
  const response = await fetch(`${API_BASE_URL}/api/ttps/technique-frequencies/?days=${days}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch TTP technique frequencies');
  }

  return await response.json();
};

export const getTtps = async (queryParams = {}) => {
  const params = new URLSearchParams(queryParams).toString();
  const url = `${API_BASE_URL}/api/ttps/${params ? `?${params}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch TTPs');
  }

  return await response.json();
};

export const getTtpFilterOptions = async () => {
  const response = await fetch(`${API_BASE_URL}/api/ttps/filter-options/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch TTP filter options');
  }

  return await response.json();
};

export const getTtpTrends = async (days = 120, granularity = 'month', groupBy = 'tactic') => {
  const params = new URLSearchParams({ days, granularity, group_by: groupBy });
  const response = await fetch(`${API_BASE_URL}/api/ttps/trends/?${params.toString()}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch TTP trends');
  }

  return await response.json();
};

export const getTtpDetails = async (ttpId) => {
  const response = await fetch(`${API_BASE_URL}/api/ttps/${ttpId}/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch TTP details');
  }

  return await response.json();
};

export const updateTtp = async (ttpId, ttpData) => {
  const response = await fetch(`${API_BASE_URL}/api/ttps/${ttpId}/`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(ttpData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to update TTP');
  }

  return await response.json();
};

export const getMatrixCellDetails = async (tactic, techniqueId = null, includeRelated = true, pageSize = 50) => {
  const params = new URLSearchParams({ tactic });
  if (techniqueId) params.append('technique_id', techniqueId);
  if (includeRelated) params.append('include_related', 'true');
  params.append('page_size', pageSize.toString());
  
  const response = await fetch(`${API_BASE_URL}/api/ttps/matrix-cell-details/?${params.toString()}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch matrix cell details');
  }

  return await response.json();
};

export const getTechniqueDetails = async (techniqueId) => {
  const response = await fetch(`${API_BASE_URL}/api/ttps/technique-details/${techniqueId}/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch technique details');
  }

  return await response.json();
};

// Generic API helper functions for backward compatibility
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes cache duration
const apiCache = new Map();

// Function to clear API cache
export const clearApiCache = () => {
  console.log('🧹 Clearing API cache...', `${apiCache.size} items removed`);
  apiCache.clear();
};

// Function to clear specific cache entries
export const clearCacheForEndpoint = (endpoint) => {
  const keysToRemove = [];
  for (const key of apiCache.keys()) {
    if (key.includes(endpoint)) {
      keysToRemove.push(key);
    }
  }
  keysToRemove.forEach(key => apiCache.delete(key));
  console.log(`🧹 Cleared ${keysToRemove.length} cache entries for ${endpoint}`);
};

export const get = async (endpoint) => {
  try {
    // Check cache first
    const cacheKey = endpoint;
    const cached = apiCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      return cached.data;
    }

    const token = localStorage.getItem('crisp_auth_token');
    
    // Don't make API calls if we don't have a token (except for auth endpoints)
    if (!token && !endpoint.includes('/auth/')) {
      return null;
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        // Token expired or invalid - redirect to login with proper base path
        localStorage.removeItem('crisp_auth_token');
        localStorage.removeItem('crisp_user');
        window.location.href = '/static/react/login';
      }
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    
    // Cache the response for dashboard endpoints only
    if (endpoint.includes('/api/threat-feeds/') || 
        endpoint.includes('/api/system-health/') ||
        endpoint.includes('/api/organizations/')) {
      apiCache.set(cacheKey, {
        data: data,
        timestamp: Date.now()
      });
    }
    
    return data;
  } catch (error) {
    // Only log non-auth errors to reduce console spam
    if (!error.message.includes('401')) {
      console.error(`API Error: ${endpoint}`, error);
    }
    return null;
  }
};

export const post = async (endpoint, data) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`API Error: ${endpoint}`, error);
    return null;
  }
};

export const put = async (endpoint, data) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`API Error: ${endpoint}`, error);
    return null;
  }
};

export const deleteRequest = async (endpoint) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    // For DELETE requests, we might get 204 No Content with no response body
    if (response.status === 204) {
      return { success: true };
    }
    
    // Try to parse JSON, but handle empty responses
    const text = await response.text();
    return text ? JSON.parse(text) : { success: true };
  } catch (error) {
    console.error(`API Error: ${endpoint}`, error);
    return null;
  }
};

// Export delete function with alias for compatibility
export { deleteRequest as delete };

export const exportTtps = async (format, filters = {}) => {
  const params = new URLSearchParams();
  params.append('format', format);
  
  // Add filters if specified
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      params.append(key, value.toString());
    }
  });
  
  const headers = {
    ...getAuthHeaders(),
    'Accept': format === 'csv' ? 'text/csv' : 
             format === 'stix' ? 'application/stix+json' : 
             'application/json'
  };
  
  const response = await fetch(`${API_BASE_URL}/api/ttps/export/?${params.toString()}`, {
    method: 'GET',
    headers: headers
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `Export failed: ${response.status} ${response.statusText}`);
  }
  
  return response; // Return the response object so caller can handle blob/filename
};
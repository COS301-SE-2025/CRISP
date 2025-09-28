// API functions for CRISP application

const API_BASE_URL = 'http://localhost:8000';

// Helper function to get auth headers
const getAuthHeaders = () => {
  // Try both token keys for compatibility
  const token = localStorage.getItem('access_token') || localStorage.getItem('crisp_auth_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

// Helper function to create user-friendly error messages
const createUserFriendlyError = (response, defaultMessage, context = '') => {
  const status = response.status;
  const contextPrefix = context ? `${context}: ` : '';

  switch (status) {
    case 403:
      return `${contextPrefix}Access denied. You don't have permission to view this content. Please check with your administrator if you need access.`;
    case 401:
      return `${contextPrefix}Authentication required. Please log in again.`;
    case 404:
      return `${contextPrefix}The requested resource was not found.`;
    case 500:
      return `${contextPrefix}Server error. Please try again later or contact support.`;
    case 429:
      return `${contextPrefix}Too many requests. Please wait a moment before trying again.`;
    case 0:
    case 'Failed to fetch':
      return `${contextPrefix}Network error. Please check your internet connection and try again.`;
    default:
      return `${contextPrefix}${defaultMessage}`;
  }
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
    const friendlyMessage = createUserFriendlyError(response, 'Failed to fetch organizations', 'Organizations');
    throw new Error(friendlyMessage);
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

export const getConnectedOrganizations = async () => {
  const response = await fetch(`${API_BASE_URL}/api/organizations/connected/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const friendlyMessage = createUserFriendlyError(response, 'Failed to fetch connected organizations', 'Connected Organizations');
    throw new Error(friendlyMessage);
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
// PERFORMANCE FIX: console.log(`🔍 Filtered trust relationships: ${originalCount} -> ${data.trusts.length} (excluded revoked/expired)`);
    }
    
    // Filter data.results.trusts if it exists (paginated response)
    if (data.results && data.results.trusts && Array.isArray(data.results.trusts)) {
      const originalCount = data.results.trusts.length;
      data.results.trusts = data.results.trusts.filter(trust => 
        trust.status && 
        !['revoked', 'expired'].includes(trust.status.toLowerCase())
      );
// PERFORMANCE FIX: console.log(`🔍 Filtered paginated trust relationships: ${originalCount} -> ${data.results.trusts.length} (excluded revoked/expired)`);
    }
  } else {
// PERFORMANCE FIX: console.log(`🔍 Showing ALL '${queryParams.status}' relationships (no filtering)`);
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
  
// PERFORMANCE FIX: console.log('🚀 Creating trust relationship:', {
  //   original: relationshipData,
  //   mapped: mappedData
  // });
  
  const response = await fetch(`${API_BASE_URL}/api/trust/bilateral/request/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(mappedData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    console.error('❌ Trust relationship creation failed:', {
      status: response.status,
      statusText: response.statusText,
      errorData
    });
    
    // Handle specific error messages
    if (response.status === 400 && errorData.message) {
      if (errorData.message.includes('already exists')) {
        throw new Error('A trust relationship already exists between these organizations. Please edit the existing relationship instead.');
      }
      if (errorData.message.includes('not found')) {
        throw new Error('One of the selected organizations was not found. Please refresh the page and try again.');
      }
    }
    
    throw new Error(errorData.message || `Failed to create trust relationship (${response.status})`);
  }

  const result = await response.json();
// PERFORMANCE FIX: console.log('✅ Trust relationship created successfully:', result);
  return result;
};

export const updateTrustRelationship = async (relationshipId, relationshipData) => {
// PERFORMANCE FIX: console.log('🔄 API: Updating trust relationship:', {
  //   id: relationshipId,
  //   data: relationshipData,
  //   url: `${API_BASE_URL}/api/trust/bilateral/${relationshipId}/update/`
  // });
  
  const response = await fetch(`${API_BASE_URL}/api/trust/bilateral/${relationshipId}/update/`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(relationshipData),
  });

// PERFORMANCE FIX: console.log('📡 API Response:', {
  //   status: response.status,
  //   statusText: response.statusText,
  //   ok: response.ok
  // });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    console.error('❌ Update failed:', errorData);
    throw new Error(errorData.message || 'Failed to update trust relationship');
  }

  const result = await response.json();
// PERFORMANCE FIX: console.log('✅ Update successful:', result);
  return result;
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
  const url = `${API_BASE_URL}/api/trust-management/groups/${params ? `?${params}` : ''}`;
  
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
  const response = await fetch(`${API_BASE_URL}/api/trust-management/groups/`, {
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
// PERFORMANCE FIX: console.log('🔄 API: Updating trust group:', {
  //   id: groupId,
  //   data: groupData,
  //   url: `${API_BASE_URL}/api/trust-management/groups/${groupId}/`
  // });
  
  const response = await fetch(`${API_BASE_URL}/api/trust-management/groups/${groupId}/`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(groupData),
  });

// PERFORMANCE FIX: console.log('📡 API Response:', {
  //   status: response.status,
  //   statusText: response.statusText,
  //   ok: response.ok
  // });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    console.error('❌ Group update failed:', errorData);
    throw new Error(errorData.message || 'Failed to update trust group');
  }

  const result = await response.json();
// PERFORMANCE FIX: console.log('✅ Group update successful:', result);
  return result;
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

export const addOrganizationToTrustGroup = async (groupId, organizationId) => {
  const response = await fetch(`${API_BASE_URL}/api/trust-management/groups/${groupId}/add_organization/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      organization_id: organizationId
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to add organization to trust group');
  }

  return await response.json();
};

export const getTrustGroupMembers = async (groupId) => {
  const response = await fetch(`${API_BASE_URL}/api/trust-management/groups/${groupId}/members/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch trust group members');
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

export const deleteNotification = async (notificationId) => {
  const response = await fetch(`${API_BASE_URL}/api/alerts/${notificationId}/delete/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || errorData.message || 'Failed to delete notification');
  }

  return await response.json();
};

export const deleteAllNotifications = async () => {
  const response = await fetch(`${API_BASE_URL}/api/alerts/delete-all/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || errorData.message || 'Failed to delete all notifications');
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
  console.log('updateTtp called with:', { ttpId, ttpData });
  
  const response = await fetch(`${API_BASE_URL}/api/ttps/${ttpId}/`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(ttpData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    console.error('TTP Update Error Response:', {
      status: response.status,
      statusText: response.statusText,
      errorData
    });
    
    // Provide more detailed error message
    if (errorData.error && errorData.details) {
      throw new Error(`${errorData.error}: ${errorData.details.join(', ')}`);
    } else if (errorData.message) {
      throw new Error(errorData.message);
    } else if (response.status === 403) {
      throw new Error('Access denied. You need publisher or admin permissions to edit TTPs.');
    } else if (response.status === 400) {
      throw new Error('Invalid data provided. Please check all required fields are filled correctly.');
    } else {
      throw new Error(`Failed to update TTP (HTTP ${response.status})`);
    }
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
// PERFORMANCE FIX: console.log('🧹 Clearing API cache...', `${apiCache.size} items removed`);
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
// PERFORMANCE FIX: console.log(`🧹 Cleared ${keysToRemove.length} cache entries for ${endpoint}`);
};

export const get = async (endpoint) => {
  try {
    // Check cache first
    const cacheKey = endpoint;
    const cached = apiCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      return cached.data;
    }

    const token = localStorage.getItem('access_token') || localStorage.getItem('crisp_auth_token');

    // Don't make API calls if we don't have a token (except for auth endpoints)
    if (!token && !endpoint.includes('/auth/')) {
      console.error(`No auth token found for endpoint: ${endpoint}`);
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

      // Try to get detailed error message
      let errorMessage = '';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || 'Request failed';
      } catch (parseError) {
        errorMessage = 'Request failed';
      }

      // Create user-friendly error message
      const friendlyMessage = createUserFriendlyError(response, errorMessage);
      throw new Error(friendlyMessage);
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
    throw error;
  }
};

export const post = async (endpoint, data) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      // Try to get detailed error message
      let errorMessage = '';
      try {
        const errorData = await response.json();
        console.error(`API Error Details for ${endpoint}:`, errorData);
        errorMessage = errorData.detail || errorData.message || 'Request failed';
      } catch (parseError) {
        console.error(`Could not parse error response for ${endpoint}`);
        errorMessage = 'Request failed';
      }

      // Create user-friendly error message
      const friendlyMessage = createUserFriendlyError(response, errorMessage);
      throw new Error(friendlyMessage);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API Error: ${endpoint}`, error);
    throw error;
  }
};

export const put = async (endpoint, data) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      // Try to get detailed error message
      let errorMessage = '';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || 'Request failed';
      } catch (parseError) {
        errorMessage = 'Request failed';
      }

      // Create user-friendly error message
      const friendlyMessage = createUserFriendlyError(response, errorMessage);
      throw new Error(friendlyMessage);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error: ${endpoint}`, error);
    throw error;
  }
};

export const deleteRequest = async (endpoint) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });

    // Handle different response scenarios
    if (!response.ok) {
      // Try to get detailed error message from response
      let errorMessage = '';
      try {
        const errorData = await response.json();
        console.error(`DELETE API Error Details for ${endpoint}:`, errorData);
        errorMessage = errorData.message || errorData.detail || 'Request failed';
      } catch (parseError) {
        console.error(`Could not parse error response for DELETE ${endpoint}`);
        errorMessage = 'Request failed';
      }

      // Create user-friendly error message
      const friendlyMessage = createUserFriendlyError(response, errorMessage);
      throw new Error(friendlyMessage);
    }

    // For DELETE requests, we might get 204 No Content with no response body
    if (response.status === 204) {
// PERFORMANCE FIX: console.log(`DELETE ${endpoint} returned 204 No Content`);
      return { success: true };
    }

    // Try to parse JSON, but handle empty responses
    const text = await response.text();
    const result = text ? JSON.parse(text) : { success: true };
// PERFORMANCE FIX: console.log(`DELETE ${endpoint} result:`, result);
    return result;
  } catch (error) {
    console.error(`DELETE API Error: ${endpoint}`, error);
    throw error;
  }
};

// Export delete function with alias for compatibility
export { deleteRequest as delete };

export const exportTtps = async (format, filters = {}) => {
  const params = new URLSearchParams();

  // Add filters if specified (don't add format as it's in the endpoint)
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

  // Use dedicated endpoints instead of format parameter
  const endpoint = format === 'csv' ? 'export-csv' :
                   format === 'stix' ? 'export-stix' :
                   'export';

  const url = params.toString() ?
    `${API_BASE_URL}/api/ttps/${endpoint}/?${params.toString()}` :
    `${API_BASE_URL}/api/ttps/${endpoint}/`;

  const response = await fetch(url, {
    method: 'GET',
    headers: headers
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `Export failed: ${response.status} ${response.statusText}`);
  }

  return response; // Return the response object so caller can handle blob/filename
};

// Indicators API functions
export const getIndicators = async (queryParams = {}) => {
  const params = new URLSearchParams();
  
  // Add pagination and filtering parameters
  Object.entries(queryParams).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      params.append(key, value.toString());
    }
  });

  const url = `${API_BASE_URL}/api/indicators/${params.toString() ? `?${params.toString()}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch indicators');
  }

  return await response.json();
};


// Threat Feed Pause/Resume API Functions
export const pauseFeedConsumption = async (feedId) => {
  const response = await fetch(`${API_BASE_URL}/api/threat-feeds/${feedId}/pause_consumption/`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || 'Failed to pause feed consumption');
  }

  return await response.json();
};

export const resumeFeedConsumption = async (feedId) => {
  const response = await fetch(`${API_BASE_URL}/api/threat-feeds/${feedId}/resume_consumption/`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || 'Failed to resume feed consumption');
  }

  return await response.json();
};

export const resetFeedStatus = async (feedId) => {
  const response = await fetch(`${API_BASE_URL}/api/threat-feeds/${feedId}/reset_feed_status/`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || 'Failed to reset feed status');
  }

  return await response.json();
};

export const getFeedConsumptionStatus = async (feedId) => {
  const response = await fetch(`${API_BASE_URL}/api/threat-feeds/${feedId}/consumption_status/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || 'Failed to get feed consumption status');
  }

  return await response.json();
};

export const consumeThreatFeed = async (feedId, options = {}) => {
  const params = new URLSearchParams();

  // Add optional parameters
  if (options.limit) params.append('limit', options.limit);
  if (options.force_days) params.append('force_days', options.force_days);
  if (options.batch_size) params.append('batch_size', options.batch_size);

  const url = `${API_BASE_URL}/api/threat-feeds/${feedId}/consume/${params.toString() ? `?${params.toString()}` : ''}`;

  const response = await fetch(url, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || errorData.message || 'Failed to consume threat feed');
  }

  return await response.json();
};

export const getThreatFeeds = async (queryParams = {}) => {
  const params = new URLSearchParams(queryParams).toString();
  const url = `${API_BASE_URL}/api/threat-feeds/${params ? `?${params}` : ''}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch threat feeds');
  }

  return await response.json();
};

// Enhanced SOC API Functions

export const getSOCDashboard = async () => {
  const response = await fetch(`${API_BASE_URL}/api/soc/dashboard/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch SOC dashboard data');
  }

  return await response.json();
};

export const getSOCThreatMap = async () => {
  const response = await fetch(`${API_BASE_URL}/api/soc/threat-map/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch threat map data');
  }

  return await response.json();
};

export const getSOCSystemHealth = async () => {
  const response = await fetch(`${API_BASE_URL}/api/soc/system-health/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch system health data');
  }

  return await response.json();
};


export const getSOCTopThreats = async () => {
  const response = await fetch(`${API_BASE_URL}/api/soc/top-threats/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch top threats data');
  }

  return await response.json();
};

export const getSOCMitreTactics = async () => {
  const response = await fetch(`${API_BASE_URL}/api/soc/mitre-tactics/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch MITRE tactics data');
  }

  return await response.json();
};

export const getSOCThreatIntelligence = async () => {
  const response = await fetch(`${API_BASE_URL}/api/soc/threat-intelligence/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch threat intelligence data');
  }

  return await response.json();
};

export const exportSOCIncidents = async (format = 'csv', options = {}) => {
  const params = new URLSearchParams({
    format,
    ...options
  });

  const response = await fetch(`${API_BASE_URL}/api/soc/incidents/export/?${params.toString()}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to export SOC incidents');
  }

  return response; // Return the response object for blob handling
};

export const getSOCIncidents = async (queryParams = {}) => {
  const params = new URLSearchParams(queryParams).toString();
  const url = `${API_BASE_URL}/api/soc/incidents/${params ? `?${params}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch SOC incidents');
  }

  return await response.json();
};

export const createSOCIncident = async (incidentData) => {
  const response = await fetch(`${API_BASE_URL}/api/soc/incidents/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(incidentData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to create SOC incident');
  }

  return await response.json();
};

export const updateSOCIncident = async (incidentId, incidentData) => {
  const response = await fetch(`${API_BASE_URL}/api/soc/incidents/${incidentId}/`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(incidentData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to update SOC incident');
  }

  return await response.json();
};

export const getSOCIncidentDetail = async (incidentId) => {
  const response = await fetch(`${API_BASE_URL}/api/soc/incidents/${incidentId}/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch SOC incident details');
  }

  return await response.json();
};

// SOC IOC Integration APIs
export const getLiveIOCAlerts = async () => {
  const response = await fetch(`${API_BASE_URL}/api/soc/live-ioc-alerts/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch live IOC alerts');
  }

  return await response.json();
};

export const getIOCIncidentCorrelation = async () => {
  const response = await fetch(`${API_BASE_URL}/api/soc/ioc-incident-correlation/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch IOC-incident correlation data');
  }

  return await response.json();
};

export const assignSOCIncident = async (incidentId, username) => {
  const response = await fetch(`${API_BASE_URL}/api/soc/incidents/${incidentId}/assign/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ username }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to assign SOC incident');
  }

  return await response.json();
};

export const addSOCIncidentComment = async (incidentId, comment) => {
  const response = await fetch(`${API_BASE_URL}/api/soc/incidents/${incidentId}/comment/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ comment }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to add comment to SOC incident');
  }

  return await response.json();
};

export const deleteSOCIncident = async (incidentId) => {
  const response = await fetch(`${API_BASE_URL}/api/soc/incidents/${incidentId}/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to delete SOC incident');
  }

  return await response.json();
};

export const createSOCIncidentWithIOCs = async (incidentData, selectedIOCs = []) => {
  const response = await fetch(`${API_BASE_URL}/api/soc/incidents/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      ...incidentData,
      related_indicators: selectedIOCs.map(ioc => ioc.id)
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to create SOC incident with IOCs');
  }

  return await response.json();
};

// Sync API Functions for real-time updates
export const checkUpdates = async () => {
  const response = await fetch(`${API_BASE_URL}/api/sync/check-updates/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to check updates');
  }

  return await response.json();
};

export const markUpdateSeen = async (updateType, timestamp) => {
  const response = await fetch(`${API_BASE_URL}/api/sync/mark-seen/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      update_type: updateType,
      timestamp: timestamp
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to mark update as seen');
  }

  return await response.json();
};

export const getLastSeen = async () => {
  const response = await fetch(`${API_BASE_URL}/api/sync/last-seen/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to get last seen timestamps');
  }

  return await response.json();
};

// Check for cache-based refresh triggers from backend
export const checkRefreshTriggers = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/sync/check-refresh-triggers/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      return { triggers: [] }; // Return empty triggers on error
    }

    return await response.json();
  } catch (error) {
    console.error('Error checking refresh triggers:', error);
    return { triggers: [] };
  }
};

// Behavior Analytics API Functions
export const getBehaviorAnalyticsDashboard = async (days = 7) => {
  const response = await fetch(`${API_BASE_URL}/api/behavior-analytics/dashboard/?days=${days}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch behavior analytics dashboard');
  }

  return await response.json();
};

export const getBehaviorAnomalies = async (queryParams = {}) => {
  const params = new URLSearchParams(queryParams).toString();
  const url = `${API_BASE_URL}/api/behavior-analytics/anomalies/${params ? `?${params}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch behavior anomalies');
  }

  return await response.json();
};

export const investigateAnomaly = async (anomalyId, investigationData) => {
  const response = await fetch(`${API_BASE_URL}/api/behavior-analytics/anomalies/${anomalyId}/investigate/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(investigationData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to investigate anomaly');
  }

  return await response.json();
};

export const getUserBehaviorProfile = async (userId, days = 30) => {
  const response = await fetch(`${API_BASE_URL}/api/behavior-analytics/users/${userId}/profile/?days=${days}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch user behavior profile');
  }

  return await response.json();
};

export const generateUserBaseline = async (userId) => {
  const response = await fetch(`${API_BASE_URL}/api/behavior-analytics/users/${userId}/generate-baseline/`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to generate user baseline');
  }

  return await response.json();
};

export const getBehaviorAlerts = async (queryParams = {}) => {
  const params = new URLSearchParams(queryParams).toString();
  const url = `${API_BASE_URL}/api/behavior-analytics/alerts/${params ? `?${params}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch behavior alerts');
  }

  return await response.json();
};

export const acknowledgeBehaviorAlert = async (alertId) => {
  const response = await fetch(`${API_BASE_URL}/api/behavior-analytics/alerts/${alertId}/acknowledge/`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to acknowledge behavior alert');
  }

  return await response.json();
};

// System Logs API Functions
export const getSystemActivityLogs = async (queryParams = {}) => {
  const params = new URLSearchParams(queryParams).toString();
  const url = `${API_BASE_URL}/api/behavior-analytics/logs/${params ? `?${params}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch system activity logs');
  }

  return await response.json();
};

export const downloadSystemLogs = async (queryParams = {}) => {
  const params = new URLSearchParams(queryParams).toString();
  const url = `${API_BASE_URL}/api/behavior-analytics/logs/download/${params ? `?${params}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to download system logs');
  }

  return response; // Return the response object for blob handling
};


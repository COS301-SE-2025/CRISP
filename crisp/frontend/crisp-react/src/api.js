// api.js - API Service for CRISP

// Base API URL - UserTrust Django backend
const API_URL = 'http://localhost:8000/api/v1/';

// Helper function to handle API responses
const handleResponse = async (response) => {
  const data = await response.json();
  
  console.log('API Response Status:', response.status);
  console.log('API Response Data:', data);
  
  if (!response.ok) {
    // Handle different error response formats
    let error;
    
    if (data && data.detail) {
      error = data.detail;
    } else if (data && data.message) {
      error = data.message;
    } else if (data && data.non_field_errors) {
      error = Array.isArray(data.non_field_errors) ? data.non_field_errors.join(', ') : data.non_field_errors;
    } else if (data && Array.isArray(data)) {
      error = data.join(', ');
    } else if (data && typeof data === 'object') {
      // Handle field-specific errors
      const fieldErrors = [];
      for (const [field, messages] of Object.entries(data)) {
        if (Array.isArray(messages)) {
          fieldErrors.push(...messages);
        } else if (typeof messages === 'string') {
          fieldErrors.push(messages);
        }
      }
      error = fieldErrors.length > 0 ? fieldErrors.join(', ') : response.statusText || 'Something went wrong';
    } else {
      error = response.statusText || 'Something went wrong';
    }
    
    console.error('API Error:', error);
    return Promise.reject(error);
  }
  
  // Check for UserTrust success field
  if (data.success === false) {
    const error = data.message || 'Authentication failed';
    console.error('API Success=false Error:', error);
    return Promise.reject(error);
  }
  
  return data;
};

// Login API function
export const loginUser = async (username, password) => {
  const response = await fetch(`${API_URL}auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  const data = await handleResponse(response);
  
  // Save auth data to localStorage - match main.jsx format
  if (data.success && data.tokens) {
    localStorage.setItem('crisp_auth_token', data.tokens.access);
    localStorage.setItem('crisp_user', JSON.stringify(data.user));
    // Also store refresh token for later use
    localStorage.setItem('crisp_refresh_token', data.tokens.refresh);
  }
  
  return data;
};

// Register user API function
export const registerUser = async (username, password, fullName, organization, role) => {
  const [firstName, lastName] = fullName.split(' ', 2);
  
  const response = await fetch(`${API_URL}auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username,
      password,
      password_confirm: password,
      email: username.includes('@') ? username : `${username}@crisp.local`,
      first_name: firstName || '',
      last_name: lastName || '',
      organization: organization || 'Default Organization',
      role: role || 'viewer'
    })
  });
  
  const data = await handleResponse(response);
  
  // Save auth data to localStorage if tokens are returned - match main.jsx format
  if (data.success && data.tokens) {
    localStorage.setItem('crisp_auth_token', data.tokens.access);
    localStorage.setItem('crisp_user', JSON.stringify(data.user));
    // Also store refresh token for later use
    localStorage.setItem('crisp_refresh_token', data.tokens.refresh);
  }
  
  return data;
};

// Get current user function - useful for checking auth status
export const getCurrentUser = () => {
  // Use the correct localStorage key structure from main.jsx
  const userStr = localStorage.getItem('crisp_user');
  return userStr ? JSON.parse(userStr) : null;
};

// Logout function
export const logoutUser = () => {
  // Clear all authentication-related localStorage keys
  localStorage.removeItem('crisp_auth_token');
  localStorage.removeItem('crisp_user');
  localStorage.removeItem('crisp_refresh_token');
};

// Add authentication header to requests
export const authHeader = () => {
  // Use the correct localStorage key structure from main.jsx
  const token = localStorage.getItem('crisp_auth_token');
  
  // Debug logging
  console.log('Token from localStorage:', token ? token.substring(0, 50) + '...' : 'No token');
  
  if (token) {
    return { 'Authorization': `Bearer ${token}` };
  } else {
    return {};
  }
};

// Function to refresh the token
export const refreshToken = async () => {
  const refreshToken = localStorage.getItem('crisp_refresh_token');
  
  if (!refreshToken) {
    return Promise.reject('No refresh token available');
  }
  
  const response = await fetch(`${API_URL}auth/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refreshToken })
  });
  
  const data = await handleResponse(response);
  
  // Update tokens with new access token
  if (data.success && data.data && data.data.tokens) {
    localStorage.setItem('crisp_auth_token', data.data.tokens.access);
    if (data.data.tokens.refresh) {
      localStorage.setItem('crisp_refresh_token', data.data.tokens.refresh);
    }
  }
  
  return data;
};

// Dashboard API functions
export const getDashboard = async () => {
  const response = await fetch(`${API_URL}auth/dashboard/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

export const getAdminDashboard = async () => {
  const response = await fetch(`${API_URL}admin/dashboard/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

// User Management API functions
export const getUsers = async (organizationId = null, filters = {}) => {
  let url = `${API_URL}users/list/`;
  const params = new URLSearchParams();
  
  if (organizationId) {
    params.append('organization_id', organizationId);
  }
  
  // Add additional filters
  Object.keys(filters).forEach(key => {
    if (filters[key] !== null && filters[key] !== undefined) {
      params.append(key, filters[key]);
    }
  });
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

export const createUser = async (userData) => {
  const response = await fetch(`${API_URL}users/create_user/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(userData)
  });
  
  return await handleResponse(response);
};

export const getUserProfile = async () => {
  const response = await fetch(`${API_URL}users/profile/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

export const updateUserProfile = async (profileData) => {
  const response = await fetch(`${API_URL}users/profile/`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(profileData)
  });
  
  return await handleResponse(response);
};

export const getUserStatistics = async () => {
  const response = await fetch(`${API_URL}users/statistics/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

// Organization Management API functions
export const getOrganizations = async () => {
  const response = await fetch(`${API_URL}organizations/list/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

export const createOrganization = async (orgData) => {
  const response = await fetch(`${API_URL}organizations/create_organization/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(orgData)
  });
  
  return await handleResponse(response);
};

export const getOrganizationDetails = async (organizationId) => {
  const response = await fetch(`${API_URL}organizations/${organizationId}/get_organization/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

export const updateOrganization = async (organizationId, updateData) => {
  const response = await fetch(`${API_URL}organizations/${organizationId}/update_organization/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(updateData)
  });
  
  return await handleResponse(response);
};

export const deactivateOrganization = async (organizationId, reason = '') => {
  const response = await fetch(`${API_URL}organizations/${organizationId}/deactivate_organization/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify({ reason })
  });
  
  return await handleResponse(response);
};

export const reactivateOrganization = async (organizationId, reason = '') => {
  const response = await fetch(`${API_URL}organizations/${organizationId}/reactivate_organization/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify({ reason })
  });
  
  return await handleResponse(response);
};

export const getOrganizationStatistics = async () => {
  const response = await fetch(`${API_URL}organizations/statistics/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

// Admin API functions
export const getSystemHealth = async () => {
  const response = await fetch(`${API_URL}admin/system-health/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

export const getAuditLogs = async () => {
  const response = await fetch(`${API_URL}admin/audit-logs/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

export const getTrustOverview = async () => {
  const response = await fetch(`${API_URL}admin/trust-overview/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

export const getSecurityEvents = async () => {
  const response = await fetch(`${API_URL}admin/security-events/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

// Change Password API function
export const changePassword = async (currentPassword, newPassword, confirmPassword) => {
  const response = await fetch(`${API_URL}auth/change-password/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
      new_password_confirm: confirmPassword
    })
  });
  
  return await handleResponse(response);
};

// Email Statistics API function
export const getEmailStatistics = async () => {
  const response = await fetch(`${API_URL}alerts/statistics/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

// Test Gmail Connection API function
export const testGmailConnection = async () => {
  const response = await fetch(`${API_URL}alerts/test-connection/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

// Send Test Email API function
export const sendTestEmail = async (email) => {
  const response = await fetch(`${API_URL}alerts/test-email/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify({ recipient_email: email })
  });
  
  return await handleResponse(response);
};

// Alert System API functions
export const sendThreatAlert = async (alertData) => {
  const response = await fetch(`${API_URL}alerts/threat/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(alertData)
  });
  
  return await handleResponse(response);
};

export const sendFeedNotification = async (notificationData) => {
  const response = await fetch(`${API_URL}alerts/feed/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(notificationData)
  });
  
  return await handleResponse(response);
};

export const getAlerts = async () => {
  const response = await fetch(`${API_URL}alerts/list/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

export const markAlertAsRead = async (alertId) => {
  const response = await fetch(`${API_URL}alerts/${alertId}/mark-read/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() }
  });
  
  return await handleResponse(response);
};

export const getAlertSubscriptions = async () => {
  const response = await fetch(`${API_URL}alerts/subscriptions/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

export const updateAlertSubscriptions = async (subscriptionData) => {
  const response = await fetch(`${API_URL}alerts/subscriptions/`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(subscriptionData)
  });
  
  return await handleResponse(response);
};

// Trust Management API functions
export const getTrustRelationships = async () => {
  try {
    // Use the correct organization endpoint for trust relationships
    const response = await fetch(`${API_URL}organizations/trust-relationships/`, {
      method: 'GET',
      headers: { ...authHeader() }
    });
    
    const result = await handleResponse(response);
    return result.data || [];
  } catch (error) {
    console.error('Failed to fetch trust relationships:', error);
    // Try admin endpoint as fallback for admin users
    try {
      const adminResponse = await fetch(`${API_URL}admin/trust-overview/`, {
        method: 'GET',
        headers: { ...authHeader() }
      });
      
      const adminResult = await handleResponse(adminResponse);
      return adminResult.data && adminResult.data.relationships ? adminResult.data.relationships : [];
    } catch (adminError) {
      console.error('Failed to fetch admin trust overview:', adminError);
      return [];
    }
  }
};

export const createTrustRelationship = async (trustData) => {
  const response = await fetch(`${API_URL}organizations/${trustData.target_organization}/trust-relationship/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(trustData)
  });
  
  return await handleResponse(response);
};

export const getTrustMetrics = async () => {
  try {
    const response = await fetch(`${API_URL}organizations/trust-metrics/`, {
      method: 'GET',
      headers: { ...authHeader() }
    });
    
    const result = await handleResponse(response);
    return result.data || {};
  } catch (error) {
    console.error('Failed to fetch trust metrics:', error);
    // Try to get from admin trust overview as fallback
    try {
      const adminResponse = await fetch(`${API_URL}admin/trust-overview/`, {
        method: 'GET',
        headers: { ...authHeader() }
      });
      
      const adminResult = await handleResponse(adminResponse);
      return adminResult.data || {};
    } catch (adminError) {
      console.error('Failed to fetch admin trust overview:', adminError);
      return {};
    }
  }
};

export const updateTrustRelationship = async (relationshipId, updateData) => {
  const response = await fetch(`${API_URL}organizations/trust-relationships/${relationshipId}/`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(updateData)
  });
  
  return await handleResponse(response);
};

export const deleteTrustRelationship = async (relationshipId) => {
  const response = await fetch(`${API_URL}organizations/trust-relationships/${relationshipId}/`, {
    method: 'DELETE',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

// Organization scope enforcement functions
export const getCurrentUserOrganization = () => {
  const auth = JSON.parse(localStorage.getItem('auth'));
  return auth?.user?.organization || null;
};

export const getUserAccessibleOrganizations = async () => {
  const response = await fetch(`${API_URL}users/accessible-organizations/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

export const getOrganizationData = async (organizationId, dataType) => {
  const response = await fetch(`${API_URL}organizations/${organizationId}/data/${dataType}/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

// Threat Intelligence with organization scoping
export const getThreatIntelligence = async (organizationId = null, filters = {}) => {
  let url = `${API_URL}threat-intelligence/`;
  const params = new URLSearchParams();
  
  if (organizationId) {
    params.append('organization_id', organizationId);
  }
  
  Object.keys(filters).forEach(key => {
    if (filters[key] !== null && filters[key] !== undefined) {
      params.append(key, filters[key]);
    }
  });
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

export const createThreatIntelligence = async (threatData) => {
  const response = await fetch(`${API_URL}threat-intelligence/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(threatData)
  });
  
  return await handleResponse(response);
};

// User Session Management API functions
export const getUserSessions = async () => {
  const response = await fetch(`${API_URL}users/sessions/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

export const revokeSession = async (sessionId) => {
  const response = await fetch(`${API_URL}users/sessions/${sessionId}/revoke/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() }
  });
  
  return await handleResponse(response);
};

// Trust Groups API functions
export const getTrustGroups = async () => {
  try {
    const response = await fetch(`${API_URL}organizations/trust-groups/`, {
      method: 'GET',
      headers: { ...authHeader() }
    });
    
    const result = await handleResponse(response);
    return result.data || [];
  } catch (error) {
    console.error('Failed to fetch trust groups:', error);
    // Return empty array if user doesn't have organization or other error
    return [];
  }
};

export const createTrustGroup = async (groupData) => {
  const response = await fetch(`${API_URL}organizations/trust-groups/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(groupData)
  });
  
  return await handleResponse(response);
};

// User List API function
export const getUsersList = async () => {
  const response = await fetch(`${API_URL}users/list/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

// Get specific user details
export const getUserDetails = async (userId) => {
  const response = await fetch(`${API_URL}users/${userId}/`, {
    method: 'GET',
    headers: { ...authHeader() }
  });
  
  return await handleResponse(response);
};

// Update specific user
export const updateUser = async (userId, userData) => {
  const response = await fetch(`${API_URL}users/${userId}/`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(userData)
  });
  
  return await handleResponse(response);
};

// Deactivate user (soft delete)
export const deactivateUser = async (userId, reason = '') => {
  const response = await fetch(`${API_URL}users/${userId}/deactivate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify({ reason })
  });
  
  return await handleResponse(response);
};

// Reactivate user
export const reactivateUser = async (userId, reason = '') => {
  const response = await fetch(`${API_URL}users/${userId}/reactivate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify({ reason })
  });
  
  return await handleResponse(response);
};

// Permanently delete user
export const deleteUser = async (userId, reason = '') => {
  const response = await fetch(`${API_URL}users/${userId}/delete_user/`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify({ reason, confirm: true })
  });
  
  return await handleResponse(response);
};

// Change username
export const changeUsername = async (userId, newUsername) => {
  const response = await fetch(`${API_URL}users/${userId}/change_username/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify({ new_username: newUsername })
  });
  
  return await handleResponse(response);
};
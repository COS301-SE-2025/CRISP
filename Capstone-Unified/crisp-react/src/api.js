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
  const response = await fetch(`${API_BASE_URL}/api/users/`, {
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
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/`, {
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

export const deleteUser = async (userId, reason = '') => {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
    body: JSON.stringify({ reason }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to delete user');
  }

  return await response.json();
};

export const changeUsername = async (userId, newUsername) => {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/change_username/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ username: newUsername }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to change username');
  }

  return await response.json();
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

export const deleteOrganization = async (orgId, reason = '') => {
  const response = await fetch(`${API_BASE_URL}/api/organizations/${orgId}/delete/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
    body: JSON.stringify({ reason }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to delete organization');
  }

  return await response.json();
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

// Trust Management Functions
export const getTrustRelationships = async (queryParams = {}) => {
  const params = new URLSearchParams(queryParams).toString();
  const url = `${API_BASE_URL}/api/trust-management/relationships/${params ? `?${params}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch trust relationships');
  }

  return await response.json();
};

export const createTrustRelationship = async (relationshipData) => {
  const response = await fetch(`${API_BASE_URL}/api/trust-management/relationships/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(relationshipData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to create trust relationship');
  }

  return await response.json();
};

export const updateTrustRelationship = async (relationshipId, relationshipData) => {
  const response = await fetch(`${API_BASE_URL}/api/trust-management/relationships/${relationshipId}/`, {
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

export const deleteTrustRelationship = async (relationshipId) => {
  const response = await fetch(`${API_BASE_URL}/api/trust-management/relationships/${relationshipId}/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to delete trust relationship');
  }

  return await response.json();
};

export const getTrustGroups = async (queryParams = {}) => {
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

  return await response.json();
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
  const response = await fetch(`${API_BASE_URL}/api/trust-management/levels/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch trust levels');
  }

  return await response.json();
};
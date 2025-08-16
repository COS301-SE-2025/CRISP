// API functions for CRISP application

const API_BASE_URL = 'http://localhost:8000';

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('token');
  console.log('Getting auth headers - token found:', token ? 'Yes' : 'No');
  console.log('Available localStorage keys:', Object.keys(localStorage));
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

// Helper function to get current user from localStorage
export const getCurrentUser = () => {
  try {
    const userString = localStorage.getItem('current_user');
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

export const deactivateUser = async (userId) => {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/deactivate/`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to deactivate user');
  }

  return await response.json();
};

export const reactivateUser = async (userId) => {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/reactivate/`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to reactivate user');
  }

  return await response.json();
};

export const deleteUser = async (userId) => {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
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
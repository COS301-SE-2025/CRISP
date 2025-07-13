// api.js - API Service for CRISP

// Base API URL - updated to match UserTrust Django backend URL
const API_URL = 'http://localhost:8000/api/v1/';

// Helper function to handle API responses
const handleResponse = async (response) => {
  const data = await response.json();
  
  if (!response.ok) {
    // If response has a detail message, use it, otherwise use a generic error
    const error = (data && data.detail) || 
                  (data && data.message) ||
                  (data && data.non_field_errors && data.non_field_errors[0]) || 
                  response.statusText || 
                  'Something went wrong';
    return Promise.reject(error);
  }
  
  // Check for UserTrust success field
  if (data.success === false) {
    const error = data.message || 'Authentication failed';
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
  
  // Save auth data to localStorage - UserTrust format
  if (data.success && data.tokens) {
    localStorage.setItem('auth', JSON.stringify({
      token: data.tokens.access,
      refresh: data.tokens.refresh,
      user: data.user
    }));
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
      email: `${username}@crisp.local`,
      first_name: firstName || '',
      last_name: lastName || '',
      role: role || 'viewer'
    })
  });
  
  const data = await handleResponse(response);
  
  // Save auth data to localStorage if tokens are returned
  if (data.success && data.tokens) {
    localStorage.setItem('auth', JSON.stringify({
      token: data.tokens.access,
      refresh: data.tokens.refresh,
      user: data.user
    }));
  }
  
  return data;
};

// Get current user function - useful for checking auth status
export const getCurrentUser = () => {
  const auth = JSON.parse(localStorage.getItem('auth'));
  return auth?.user || null;
};

// Logout function
export const logoutUser = () => {
  localStorage.removeItem('auth');
};

// Add authentication header to requests
export const authHeader = () => {
  const auth = JSON.parse(localStorage.getItem('auth'));
  
  if (auth && auth.token) {
    return { 'Authorization': `Bearer ${auth.token}` };
  } else {
    return {};
  }
};

// Function to refresh the token
export const refreshToken = async () => {
  const auth = JSON.parse(localStorage.getItem('auth'));
  
  if (!auth || !auth.refresh) {
    return Promise.reject('No refresh token available');
  }
  
  const response = await fetch(`${API_URL}auth/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: auth.refresh })
  });
  
  const data = await handleResponse(response);
  
  if (data.success && data.tokens && data.tokens.access) {
    // Update stored token
    auth.token = data.tokens.access;
    localStorage.setItem('auth', JSON.stringify(auth));
  }
  
  return data;
};
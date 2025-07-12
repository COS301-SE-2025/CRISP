// api.js - API Service for CRISP

// Base API URL - updated to match TrustManagement Django backend URL  
const API_URL = 'http://127.0.0.1:8000/api/v1/';

// Helper function to handle API responses
const handleResponse = async (response) => {
  const data = await response.json();
  
  if (!response.ok) {
    // If response has a detail message, use it, otherwise use a generic error
    const error = (data && data.detail) || 
                  (data && data.non_field_errors && data.non_field_errors[0]) || 
                  response.statusText || 
                  'Something went wrong';
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
  
  // Handle the backend response format
  if (data.access) {
    const authData = {
      token: data.access,
      refresh: data.refresh,
      user: data.user
    };
    
    localStorage.setItem('auth', JSON.stringify(authData));
    return authData;
  }
  
  return data;
};

// Register user API function
export const registerUser = async (username, password, fullName, organization, role) => {
  const response = await fetch(`${API_URL}users/create/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username,
      password,
      confirm_password: password,
      full_name: fullName,
      organization,
      role
    })
  });
  
  const data = await handleResponse(response);
  
  // Save auth data to localStorage if token is returned
  if (data.token) {
    localStorage.setItem('auth', JSON.stringify({
      token: data.token,
      refresh: data.refresh,
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
    body: JSON.stringify({ refresh: auth.refresh })
  });
  
  const data = await handleResponse(response);
  
  if (data.access) {
    // Update stored token
    auth.token = data.access;
    localStorage.setItem('auth', JSON.stringify(auth));
  }
  
  return data;
};

// ===========================
// USER MANAGEMENT FUNCTIONS
// ===========================

// Get user profile
export const getUserProfile = async () => {
  const response = await fetch(`${API_URL}users/profile/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// Update user profile
export const updateUserProfile = async (profileData) => {
  const response = await fetch(`${API_URL}users/profile/`, {
    method: 'PUT',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    },
    body: JSON.stringify(profileData)
  });
  
  return await handleResponse(response);
};

// Get users list (admin only)
export const getUsersList = async () => {
  const response = await fetch(`${API_URL}users/list/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// Get user statistics
export const getUserStatistics = async () => {
  const response = await fetch(`${API_URL}users/statistics/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// ===========================
// TRUST MANAGEMENT FUNCTIONS
// ===========================

// Get trust relationships
export const getTrustRelationships = async () => {
  const response = await fetch(`${API_URL}trust/relationships/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// Create trust relationship
export const createTrustRelationship = async (trustData) => {
  const response = await fetch(`${API_URL}trust/relationships/`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    },
    body: JSON.stringify(trustData)
  });
  
  return await handleResponse(response);
};

// Get trust groups
export const getTrustGroups = async () => {
  const response = await fetch(`${API_URL}trust/groups/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// Create trust group
export const createTrustGroup = async (groupData) => {
  const response = await fetch(`${API_URL}trust/groups/`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    },
    body: JSON.stringify(groupData)
  });
  
  return await handleResponse(response);
};

// ===========================
// ORGANIZATION FUNCTIONS
// ===========================

// Get organizations list
export const getOrganizations = async () => {
  const response = await fetch(`${API_URL}organizations/list/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// Create organization
export const createOrganization = async (orgData) => {
  const response = await fetch(`${API_URL}organizations/create/`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    },
    body: JSON.stringify(orgData)
  });
  
  return await handleResponse(response);
};

// Get organization trust metrics
export const getOrganizationTrustMetrics = async () => {
  const response = await fetch(`${API_URL}organizations/trust-metrics/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// ===========================
// ADMIN FUNCTIONS
// ===========================

// Get admin dashboard data
export const getAdminDashboard = async () => {
  const response = await fetch(`${API_URL}admin/dashboard/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// Get system health
export const getSystemHealth = async () => {
  const response = await fetch(`${API_URL}admin/system-health/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// Get audit logs
export const getAuditLogs = async () => {
  const response = await fetch(`${API_URL}admin/audit-logs/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// Get trust overview
export const getTrustOverview = async () => {
  const response = await fetch(`${API_URL}admin/trust-overview/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// ===========================
// ALERTS FUNCTIONS
// ===========================

// Send threat alert email
export const sendThreatAlert = async (alertData) => {
  const response = await fetch(`http://127.0.0.1:8000/api/alerts/threat/`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    },
    body: JSON.stringify(alertData)
  });
  
  return await handleResponse(response);
};

// Send feed notification email
export const sendFeedNotification = async (notificationData) => {
  const response = await fetch(`http://127.0.0.1:8000/api/alerts/feed/`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    },
    body: JSON.stringify(notificationData)
  });
  
  return await handleResponse(response);
};

// Test Gmail connection
export const testGmailConnection = async () => {
  const response = await fetch(`http://127.0.0.1:8000/api/alerts/test-connection/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// Get email statistics
export const getEmailStatistics = async () => {
  const response = await fetch(`http://127.0.0.1:8000/api/alerts/statistics/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// Send test email
export const sendTestEmail = async (recipientEmail) => {
  const response = await fetch(`http://127.0.0.1:8000/api/alerts/test-email/`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    },
    body: JSON.stringify({ recipient_email: recipientEmail })
  });
  
  return await handleResponse(response);
};

// ===========================
// DASHBOARD FUNCTIONS
// ===========================

// Get user dashboard data
export const getUserDashboard = async () => {
  const response = await fetch(`${API_URL}auth/dashboard/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// Change password
export const changePassword = async (currentPassword, newPassword) => {
  const response = await fetch(`${API_URL}auth/change-password/`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: newPassword
    })
  });
  
  return await handleResponse(response);
};

// Get user sessions
export const getUserSessions = async () => {
  const response = await fetch(`${API_URL}auth/sessions/`, {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    }
  });
  
  return await handleResponse(response);
};

// Revoke session
export const revokeSession = async (sessionId) => {
  const response = await fetch(`${API_URL}auth/revoke-session/`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...authHeader()
    },
    body: JSON.stringify({ session_id: sessionId })
  });
  
  return await handleResponse(response);
};
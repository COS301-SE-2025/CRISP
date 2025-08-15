// API functions for CRISP application

const API_BASE_URL = 'http://localhost:8000';

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
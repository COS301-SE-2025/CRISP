// API utility functions for CRISP application

// Update the port to match your Django backend
const API_BASE_URL = 'http://127.0.0.1:8001/api';

// Authentication functions
export async function loginUser(username, password) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
      credentials: 'include', // Include cookies if your API uses session auth
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Authentication failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

// More API functions as needed...
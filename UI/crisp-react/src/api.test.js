// api.test.js - Unit tests for API Service

import {
  loginUser,
  registerUser,
  getCurrentUser,
  logoutUser,
  authHeader,
  refreshToken
} from './api.js';

// Mock fetch globally
global.fetch = jest.fn();

// Create a proper localStorage mock
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: jest.fn((key) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
    get length() {
      return Object.keys(store).length;
    },
    key: jest.fn((index) => {
      const keys = Object.keys(store);
      return keys[index] || null;
    })
  };
})();

// Replace the global localStorage with our mock
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('API Service Tests', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    fetch.mockClear();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
    localStorageMock.clear.mockClear();
    
    // Clear localStorage data
    localStorageMock.clear();
  });

  describe('loginUser', () => {
    it('should login successfully and store auth data', async () => {
      const mockResponse = {
        token: 'mock-access-token',
        refresh: 'mock-refresh-token',
        user: { id: 1, username: 'testuser', full_name: 'Test User' }
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await loginUser('testuser', 'password123');

      expect(fetch).toHaveBeenCalledWith('http://localhost:8001/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'testuser', password: 'password123' })
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'auth',
        JSON.stringify(mockResponse)
      );

      expect(result).toEqual(mockResponse);
    });

    it('should handle login failure with detail message', async () => {
      const errorResponse = { detail: 'Invalid credentials' };

      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => errorResponse,
        statusText: 'Unauthorized'
      });

      await expect(loginUser('testuser', 'wrongpassword'))
        .rejects.toBe('Invalid credentials');

      expect(localStorageMock.setItem).not.toHaveBeenCalled();
    });

    it('should handle login failure with non_field_errors', async () => {
      const errorResponse = { non_field_errors: ['Account disabled'] };

      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => errorResponse,
        statusText: 'Bad Request'
      });

      await expect(loginUser('testuser', 'password123'))
        .rejects.toBe('Account disabled');
    });

    it('should handle login failure with generic error', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({}),
        statusText: 'Internal Server Error'
      });

      await expect(loginUser('testuser', 'password123'))
        .rejects.toBe('Internal Server Error');
    });

    it('should not store auth data if no token returned', async () => {
      const mockResponse = { message: 'Login successful but no token' };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await loginUser('testuser', 'password123');

      expect(localStorageMock.setItem).not.toHaveBeenCalled();
      expect(result).toEqual(mockResponse);
    });
  });

  describe('registerUser', () => {
    it('should register successfully and store auth data', async () => {
      const mockResponse = {
        token: 'mock-access-token',
        refresh: 'mock-refresh-token',
        user: { id: 1, username: 'newuser', full_name: 'New User' }
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await registerUser(
        'newuser',
        'password123',
        'New User',
        'Test Org',
        'researcher'
      );

      expect(fetch).toHaveBeenCalledWith('http://localhost:8001/api/auth/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'newuser',
          password: 'password123',
          confirm_password: 'password123',
          full_name: 'New User',
          organization: 'Test Org',
          role: 'researcher'
        })
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'auth',
        JSON.stringify(mockResponse)
      );

      expect(result).toEqual(mockResponse);
    });

    it('should handle registration failure', async () => {
      const errorResponse = { username: ['Username already exists'] };

      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => errorResponse,
        statusText: 'Bad Request'
      });

      await expect(registerUser('existinguser', 'password123', 'User', 'Org', 'role'))
        .rejects.toBe('Bad Request');
    });

    it('should not store auth data if no token returned', async () => {
      const mockResponse = { message: 'Registration successful, please verify email' };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await registerUser('newuser', 'password123', 'User', 'Org', 'role');

      expect(localStorageMock.setItem).not.toHaveBeenCalled();
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getCurrentUser', () => {
    it('should return current user when auth data exists', () => {
      const mockAuth = {
        token: 'mock-token',
        refresh: 'mock-refresh',
        user: { id: 1, username: 'testuser' }
      };

      // Manually set the data in our mock store
      localStorageMock.setItem('auth', JSON.stringify(mockAuth));

      const result = getCurrentUser();

      expect(result).toEqual(mockAuth.user);
    });

    it('should return null when no auth data exists', () => {
      // Ensure localStorage is empty
      localStorageMock.clear();

      const result = getCurrentUser();

      expect(result).toBeNull();
    });

    it('should return null when auth data exists but no user', () => {
      const mockAuth = {
        token: 'mock-token',
        refresh: 'mock-refresh'
      };

      localStorageMock.setItem('auth', JSON.stringify(mockAuth));

      const result = getCurrentUser();

      expect(result).toBeNull();
    });

    it('should handle invalid JSON in localStorage', () => {
      // Mock getItem to return invalid JSON
      localStorageMock.getItem.mockReturnValueOnce('invalid-json');

      expect(() => getCurrentUser()).toThrow();
    });
  });

  describe('logoutUser', () => {
    it('should remove auth data from localStorage', () => {
      // Pre-populate localStorage
      localStorageMock.setItem('auth', JSON.stringify({ token: 'test' }));

      logoutUser();

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth');
    });
  });

  describe('authHeader', () => {
    it('should return authorization header when token exists', () => {
      const mockAuth = {
        token: 'mock-access-token',
        refresh: 'mock-refresh-token'
      };

      localStorageMock.setItem('auth', JSON.stringify(mockAuth));

      const result = authHeader();

      expect(result).toEqual({ 'Authorization': 'Bearer mock-access-token' });
    });

    it('should return empty object when no auth data exists', () => {
      localStorageMock.clear();

      const result = authHeader();

      expect(result).toEqual({});
    });

    it('should return empty object when auth data exists but no token', () => {
      const mockAuth = { refresh: 'mock-refresh-token' };

      localStorageMock.setItem('auth', JSON.stringify(mockAuth));

      const result = authHeader();

      expect(result).toEqual({});
    });

    it('should handle invalid JSON in localStorage', () => {
      localStorageMock.getItem.mockReturnValueOnce('invalid-json');

      expect(() => authHeader()).toThrow();
    });
  });

  describe('refreshToken', () => {
    it('should refresh token successfully and update localStorage', async () => {
      const mockAuth = {
        token: 'old-token',
        refresh: 'mock-refresh-token',
        user: { id: 1, username: 'testuser' }
      };

      const mockResponse = { access: 'new-access-token' };

      localStorageMock.setItem('auth', JSON.stringify(mockAuth));

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await refreshToken();

      expect(fetch).toHaveBeenCalledWith('http://localhost:8001/api/auth/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: 'mock-refresh-token' })
      });

      const expectedUpdatedAuth = {
        ...mockAuth,
        token: 'new-access-token'
      };

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'auth',
        JSON.stringify(expectedUpdatedAuth)
      );

      expect(result).toEqual(mockResponse);
    });

    it('should reject when no auth data exists', async () => {
      localStorageMock.clear();

      await expect(refreshToken()).rejects.toBe('No refresh token available');

      expect(fetch).not.toHaveBeenCalled();
    });

    it('should reject when no refresh token exists', async () => {
      const mockAuth = { token: 'mock-token' };

      localStorageMock.setItem('auth', JSON.stringify(mockAuth));

      await expect(refreshToken()).rejects.toBe('No refresh token available');

      expect(fetch).not.toHaveBeenCalled();
    });

    it('should handle refresh token failure', async () => {
      const mockAuth = {
        token: 'old-token',
        refresh: 'invalid-refresh-token'
      };

      localStorageMock.setItem('auth', JSON.stringify(mockAuth));

      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Token is invalid or expired' }),
        statusText: 'Unauthorized'
      });

      await expect(refreshToken()).rejects.toBe('Token is invalid or expired');

      expect(localStorageMock.setItem).toHaveBeenCalledTimes(1); // Only the initial setup call
    });

    it('should not update localStorage if no access token returned', async () => {
      const mockAuth = {
        token: 'old-token',
        refresh: 'mock-refresh-token'
      };

      const mockResponse = { message: 'Refreshed but no token' };

      localStorageMock.setItem('auth', JSON.stringify(mockAuth));

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await refreshToken();

      // Should only have been called once during setup, not again during the function
      expect(localStorageMock.setItem).toHaveBeenCalledTimes(1);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Error Handling Edge Cases', () => {
    beforeEach(() => {
      // Clear any existing mocks for these specific tests
      fetch.mockClear();
    });

    it('should handle network errors', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(loginUser('testuser', 'password123')).rejects.toThrow('Network error');
    });

    it('should handle JSON parsing errors in API responses', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => { throw new Error('Invalid JSON'); }
      });

      await expect(loginUser('testuser', 'password123')).rejects.toThrow('Invalid JSON');
    });
  });
});
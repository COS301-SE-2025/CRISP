import { loginUser, getCurrentUser } from './api'

describe('API Module', () => {
  beforeEach(() => {
    localStorage.clear()
    global.fetch = vi.fn()
  })

  describe('getCurrentUser', () => {
    test('returns null when no user in localStorage', () => {
      const user = getCurrentUser()
      expect(user).toBeNull()
    })

    test('returns parsed user when valid user data in localStorage', () => {
      const userData = { username: 'testuser', role: 'admin' }
      localStorage.setItem('crisp_user', JSON.stringify(userData))

      const user = getCurrentUser()
      expect(user).toEqual(userData)
    })

    test('returns null when invalid JSON in localStorage', () => {
      localStorage.setItem('crisp_user', 'invalid-json')

      const user = getCurrentUser()
      expect(user).toBeNull()
    })

    test('handles localStorage errors gracefully', () => {
      // Mock localStorage to throw an error
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn().mockImplementation(() => {
        throw new Error('LocalStorage error')
      })

      const user = getCurrentUser()
      expect(user).toBeNull()

      // Restore original
      localStorage.getItem = originalGetItem
    })
  })

  describe('loginUser', () => {
    test('successfully logs in user with valid credentials', async () => {
      const mockResponse = {
        success: true,
        data: {
          user: {
            username: 'testuser',
            role: 'admin',
            email: 'test@example.com'
          },
          token: 'mock-jwt-token'
        }
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await loginUser('testuser', 'password123')

      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: 'testuser',
          password: 'password123'
        })
      })

      expect(result).toEqual(mockResponse)
      expect(localStorage.getItem('crisp_auth_token')).toBe('mock-jwt-token')
      expect(localStorage.getItem('crisp_user')).toBe(JSON.stringify(mockResponse.data.user))
    })

    test('handles login failure with invalid credentials', async () => {
      const mockErrorResponse = {
        success: false,
        error: 'Invalid credentials'
      }

      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => mockErrorResponse
      })

      const result = await loginUser('testuser', 'wrongpassword')

      expect(result).toEqual(mockErrorResponse)
      expect(localStorage.getItem('crisp_auth_token')).toBeNull()
      expect(localStorage.getItem('crisp_user')).toBeNull()
    })

    test('handles network errors', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(loginUser('testuser', 'password123')).rejects.toThrow('Network error')
      expect(localStorage.getItem('crisp_auth_token')).toBeNull()
      expect(localStorage.getItem('crisp_user')).toBeNull()
    })

    test('handles empty credentials', async () => {
      const mockErrorResponse = {
        success: false,
        error: 'Username and password are required'
      }

      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => mockErrorResponse
      })

      const result = await loginUser('', '')
      expect(result).toEqual(mockErrorResponse)
    })

    test('handles server errors (500)', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({
          success: false,
          error: 'Internal server error'
        })
      })

      const result = await loginUser('testuser', 'password123')
      expect(result.success).toBe(false)
      expect(result.error).toBe('Internal server error')
    })

    test('handles malformed response JSON', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON')
        }
      })

      await expect(loginUser('testuser', 'password123')).rejects.toThrow('Invalid JSON')
    })

    test('stores different user roles correctly', async () => {
      const roles = ['admin', 'viewer', 'publisher', 'BlueVisionAdmin']
      
      for (const role of roles) {
        localStorage.clear()
        
        const mockResponse = {
          success: true,
          data: {
            user: {
              username: 'testuser',
              role: role,
              email: 'test@example.com'
            },
            token: 'mock-jwt-token'
          }
        }

        global.fetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse
        })

        await loginUser('testuser', 'password123')

        const storedUser = JSON.parse(localStorage.getItem('crisp_user'))
        expect(storedUser.role).toBe(role)
      }
    })

    test('handles login with special characters in password', async () => {
      const mockResponse = {
        success: true,
        data: {
          user: {
            username: 'testuser',
            role: 'admin',
            email: 'test@example.com'
          },
          token: 'mock-jwt-token'
        }
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const specialPassword = 'p@$$w0rd!@#$%^&*()_+'
      await loginUser('testuser', specialPassword)

      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: 'testuser',
          password: specialPassword
        })
      })
    })
  })
})
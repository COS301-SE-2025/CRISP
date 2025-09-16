import '@testing-library/jest-dom'

// Test environment configuration
global.process.env = {
  ...global.process.env,
  NODE_ENV: 'test',
  VITE_API_BASE_URL: 'http://localhost:8000'
}

// Real browser APIs - no mocking
// Tests will use actual localStorage, sessionStorage, and fetch

// Test helper utilities
global.testUtils = {
  // Helper to create test user credentials
  getTestUser: () => ({
    username: 'testuser',
    password: 'testpass123',
    email: 'test@example.com'
  }),
  
  // Helper to clean up test data
  cleanupTestData: async () => {
    localStorage.clear()
    sessionStorage.clear()
  },
  
  // Helper to wait for API calls
  waitForApiCall: (timeout = 5000) => {
    return new Promise((resolve) => {
      setTimeout(resolve, timeout)
    })
  }
}

// Global test cleanup
afterEach(async () => {
  // Clean up any test data after each test
  await global.testUtils.cleanupTestData()
})
/**
 * Integration Test Script for CRISP UI-Backend Integration
 * This script tests all the major flows for different user roles
 */

import * as api from './api.js';

class IntegrationTester {
  constructor() {
    this.testResults = [];
    this.currentUser = null;
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const result = { timestamp, message, type };
    this.testResults.push(result);
    console.log(`[${timestamp}] ${type.toUpperCase()}: ${message}`);
  }

  async runTest(testName, testFunction) {
    try {
      this.log(`Starting test: ${testName}`, 'test');
      await testFunction();
      this.log(`✅ Test passed: ${testName}`, 'success');
    } catch (error) {
      this.log(`❌ Test failed: ${testName} - ${error.message}`, 'error');
    }
  }

  async testLogin(username, password) {
    const result = await api.loginUser(username, password);
    this.currentUser = result.user;
    return result;
  }

  async testProfileUpdate() {
    const profileData = {
      first_name: 'Test',
      last_name: 'User',
      department: 'IT Security',
      phone_number: '+27123456789'
    };
    
    return await api.updateUserProfile(profileData);
  }

  async testUserManagement() {
    // Test getting users list
    const users = await api.getUsers();
    
    // Test user statistics
    const stats = await api.getUserStatistics();
    
    return { users, stats };
  }

  async testTrustManagement() {
    // Test getting trust metrics
    const metrics = await api.getTrustMetrics();
    
    // Test getting trust relationships
    const relationships = await api.getTrustRelationships();
    
    return { metrics, relationships };
  }

  async testAlertSystem() {
    // Test getting alert subscriptions
    const subscriptions = await api.getAlertSubscriptions();
    
    // Test email statistics
    const emailStats = await api.getEmailStatistics();
    
    return { subscriptions, emailStats };
  }

  async testOrganizationScoping() {
    // Test getting current user organization
    const userOrg = api.getCurrentUserOrganization();
    
    // Test getting accessible organizations
    const accessibleOrgs = await api.getUserAccessibleOrganizations();
    
    // Test organization-scoped data access
    const orgStats = await api.getOrganizationStatistics();
    
    return { userOrg, accessibleOrgs, orgStats };
  }

  async testRoleBasedAccess(userRole) {
    const tests = [];
    
    // All users should be able to access profile
    tests.push(this.runTest('Profile Access', () => this.testProfileUpdate()));
    
    // All users should see dashboard
    tests.push(this.runTest('Dashboard Access', () => api.getDashboard()));
    
    if (userRole === 'publisher' || userRole === 'BlueVisionAdmin') {
      // Publishers and admins can access user management
      tests.push(this.runTest('User Management Access', () => this.testUserManagement()));
      
      // Publishers and admins can access trust management
      tests.push(this.runTest('Trust Management Access', () => this.testTrustManagement()));
    }
    
    if (userRole === 'BlueVisionAdmin') {
      // Only BlueVision admins can access admin settings
      tests.push(this.runTest('Admin Dashboard Access', () => api.getAdminDashboard()));
      tests.push(this.runTest('System Health Access', () => api.getSystemHealth()));
    }
    
    // All users can access alerts
    tests.push(this.runTest('Alert System Access', () => this.testAlertSystem()));
    
    // Test organization scoping
    tests.push(this.runTest('Organization Scoping', () => this.testOrganizationScoping()));
    
    await Promise.all(tests);
  }

  async runAllTests() {
    this.log('Starting CRISP Integration Tests', 'info');
    
    // Test different user roles
    const testUsers = [
      { username: 'viewer@test.edu', password: 'testpass123', role: 'viewer' },
      { username: 'publisher@test.edu', password: 'testpass123', role: 'publisher' },
      { username: 'admin@bluevision.com', password: 'testpass123', role: 'BlueVisionAdmin' }
    ];
    
    for (const testUser of testUsers) {
      try {
        this.log(`Testing user role: ${testUser.role}`, 'info');
        
        // Login as user
        await this.runTest('Login', () => this.testLogin(testUser.username, testUser.password));
        
        // Test role-based access
        await this.testRoleBasedAccess(testUser.role);
        
        // Logout
        await this.runTest('Logout', () => api.logoutUser());
        
      } catch (error) {
        this.log(`Failed to test user ${testUser.username}: ${error.message}`, 'error');
      }
    }
    
    this.generateReport();
  }

  generateReport() {
    const totalTests = this.testResults.filter(r => r.type === 'test').length;
    const passedTests = this.testResults.filter(r => r.type === 'success').length;
    const failedTests = this.testResults.filter(r => r.type === 'error').length;
    
    this.log('='.repeat(50), 'info');
    this.log('INTEGRATION TEST REPORT', 'info');
    this.log('='.repeat(50), 'info');
    this.log(`Total Tests: ${totalTests}`, 'info');
    this.log(`Passed: ${passedTests}`, 'success');
    this.log(`Failed: ${failedTests}`, 'error');
    this.log(`Success Rate: ${((passedTests / totalTests) * 100).toFixed(2)}%`, 'info');
    
    if (failedTests > 0) {
      this.log('\nFailed Tests:', 'error');
      this.testResults
        .filter(r => r.type === 'error')
        .forEach(r => this.log(`- ${r.message}`, 'error'));
    }
  }
}

// Export for use in testing
export default IntegrationTester;

// Auto-run tests if this script is executed directly
if (typeof window !== 'undefined' && window.location.pathname.includes('test')) {
  const tester = new IntegrationTester();
  tester.runAllTests();
}
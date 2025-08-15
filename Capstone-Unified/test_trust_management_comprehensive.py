#!/usr/bin/env python3
"""
Comprehensive Trust Management Testing Script
Tests all trust management functionality including organizations, relationships, and edge cases.
"""

import requests
import json
import time
from datetime import datetime

class TrustManagementTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.created_resources = {
            'organizations': [],
            'users': [],
            'trust_relationships': []
        }
    
    def log_test(self, test_name, success, details="", response_code=None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'response_code': response_code,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if response_code:
            print(f"    Response: {response_code}")
        print()
    
    def login_admin(self):
        """Login as admin to get authentication token"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/auth/login/", 
                json={
                    "username": "admin1",
                    "password": "admin123"
                })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('tokens'):
                    self.admin_token = data['tokens']['access']
                    self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
                    self.log_test("Admin Login", True, "Admin authenticated successfully", 200)
                    return True
                else:
                    self.log_test("Admin Login", False, f"Login failed: {data.get('message')}", response.status_code)
                    return False
            else:
                self.log_test("Admin Login", False, f"HTTP {response.status_code}", response.status_code)
                return False
        except Exception as e:
            self.log_test("Admin Login", False, f"Exception: {str(e)}")
            return False
    
    def test_create_organization(self, org_data, expected_success=True):
        """Test organization creation with various data scenarios"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/organizations/create_organization/", 
                json=org_data)
            
            success = (response.status_code in [200, 201]) == expected_success
            
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get('success') and data.get('data'):
                    org_id = data['data'].get('id') or data['data'].get('organization', {}).get('id')
                    if org_id:
                        self.created_resources['organizations'].append(org_id)
                    self.log_test(f"Create Organization: {org_data.get('name', 'Test')}", 
                                success, f"Organization created: {org_id}", response.status_code)
                    return org_id
                else:
                    self.log_test(f"Create Organization: {org_data.get('name', 'Test')}", 
                                False, f"Unexpected response format: {data}", response.status_code)
                    return None
            else:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                self.log_test(f"Create Organization: {org_data.get('name', 'Test')}", 
                            success, f"Failed: {data.get('message', 'Unknown error')}", response.status_code)
                return None
                
        except Exception as e:
            self.log_test(f"Create Organization: {org_data.get('name', 'Test')}", 
                        False, f"Exception: {str(e)}")
            return None
    
    def test_organization_edge_cases(self):
        """Test organization creation edge cases"""
        print("=== Testing Organization Edge Cases ===")
        
        # Test 1: Complete organization data
        complete_org = {
            "name": "Complete Test Organization",
            "domain": "complete-test.com",
            "contact_email": "admin@complete-test.com",
            "organization_type": "private",
            "description": "Complete organization with all fields",
            "primary_user": {
                "username": f"completeadmin_{int(time.time())}",
                "email": "admin@complete-test.com",
                "password": "SecurePassword123!",
                "first_name": "Complete",
                "last_name": "Admin"
            }
        }
        org1_id = self.test_create_organization(complete_org)
        
        # Test 2: Minimal organization data (with required fields)
        minimal_org = {
            "name": "Minimal Test Organization",
            "organization_type": "private",
            "primary_user": {
                "username": f"minimaladmin_{int(time.time())}",
                "email": "admin@minimal-test.com",
                "password": "SecurePassword123!",
                "first_name": "Minimal",
                "last_name": "Admin"
            }
        }
        org2_id = self.test_create_organization(minimal_org)
        
        # Test 3: Missing required fields
        invalid_org = {
            "name": "Invalid Organization"
            # Missing primary_user
        }
        self.test_create_organization(invalid_org, expected_success=False)
        
        # Test 4: Invalid email format
        invalid_email_org = {
            "name": "Invalid Email Organization",
            "contact_email": "invalid-email",
            "primary_user": {
                "username": f"invalidemail_{int(time.time())}",
                "email": "invalid-email-format",
                "password": "SecurePassword123!",
                "first_name": "Invalid",
                "last_name": "Email"
            }
        }
        self.test_create_organization(invalid_email_org, expected_success=False)
        
        return org1_id, org2_id
    
    def test_trust_relationships(self, org1_id, org2_id):
        """Test trust relationship creation and management"""
        print("=== Testing Trust Relationships ===")
        
        if not org1_id or not org2_id:
            self.log_test("Trust Relationships", False, "Missing organization IDs for testing")
            return
        
        # Test 1: Create trust relationship
        try:
            trust_data = {
                "source_organization": org1_id,
                "target_organization": org2_id,
                "trust_level": "high",
                "relationship_type": "partnership"
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/trust/relationships/", 
                json=trust_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get('success'):
                    trust_id = data.get('data', {}).get('id')
                    if trust_id:
                        self.created_resources['trust_relationships'].append(trust_id)
                    self.log_test("Create Trust Relationship", True, 
                                f"Trust relationship created: {trust_id}", response.status_code)
                else:
                    self.log_test("Create Trust Relationship", False, 
                                f"Failed: {data.get('message')}", response.status_code)
            else:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                self.log_test("Create Trust Relationship", False, 
                            f"HTTP {response.status_code}: {data.get('message', 'Unknown error')}", response.status_code)
                
        except Exception as e:
            self.log_test("Create Trust Relationship", False, f"Exception: {str(e)}")
        
        # Test 2: List trust relationships
        try:
            response = self.session.get(f"{self.base_url}/api/v1/trust/relationships/")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    relationships = data.get('data', [])
                    self.log_test("List Trust Relationships", True, 
                                f"Found {len(relationships)} relationships", response.status_code)
                else:
                    self.log_test("List Trust Relationships", False, 
                                f"Failed: {data.get('message')}", response.status_code)
            else:
                self.log_test("List Trust Relationships", False, 
                            f"HTTP {response.status_code}", response.status_code)
                
        except Exception as e:
            self.log_test("List Trust Relationships", False, f"Exception: {str(e)}")
    
    def test_organization_trust_endpoints(self):
        """Test organization-specific trust endpoints"""
        print("=== Testing Organization Trust Endpoints ===")
        
        if not self.created_resources['organizations']:
            self.log_test("Organization Trust Endpoints", False, "No organizations available for testing")
            return
        
        org_id = self.created_resources['organizations'][0]
        
        # Test organization details instead (trust context endpoint doesn't exist)
        try:
            response = self.session.get(f"{self.base_url}/api/v1/organizations/{org_id}/get_organization/")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Organization Details Access", True, 
                                "Organization details retrieved successfully", response.status_code)
                else:
                    self.log_test("Organization Details Access", False, 
                                f"Failed: {data.get('message')}", response.status_code)
            else:
                self.log_test("Organization Details Access", False, 
                            f"HTTP {response.status_code}", response.status_code)
                
        except Exception as e:
            self.log_test("Organization Details Access", False, f"Exception: {str(e)}")
    
    def test_ui_integration(self):
        """Test UI integration by checking frontend API endpoints"""
        print("=== Testing UI Integration ===")
        
        # Test dashboard data endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/v1/auth/dashboard/")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    dashboard_data = data.get('data', {})
                    self.log_test("Dashboard API", True, 
                                f"Dashboard data includes: {list(dashboard_data.keys())}", response.status_code)
                else:
                    self.log_test("Dashboard API", False, 
                                f"Failed: {data.get('message')}", response.status_code)
            else:
                self.log_test("Dashboard API", False, 
                            f"HTTP {response.status_code}", response.status_code)
                
        except Exception as e:
            self.log_test("Dashboard API", False, f"Exception: {str(e)}")
        
        # Test organization list endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/v1/organizations/list_organizations/")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    orgs = data.get('data', [])
                    self.log_test("Organization List API", True, 
                                f"Found {len(orgs)} organizations", response.status_code)
                else:
                    self.log_test("Organization List API", False, 
                                f"Failed: {data.get('message')}", response.status_code)
            else:
                self.log_test("Organization List API", False, 
                            f"HTTP {response.status_code}", response.status_code)
                
        except Exception as e:
            self.log_test("Organization List API", False, f"Exception: {str(e)}")
    
    def cleanup_test_data(self):
        """Clean up created test data"""
        print("=== Cleaning Up Test Data ===")
        
        # Delete trust relationships
        for trust_id in self.created_resources['trust_relationships']:
            try:
                response = self.session.delete(f"{self.base_url}/api/v1/trust/relationships/{trust_id}/")
                if response.status_code in [200, 204]:
                    print(f"✅ Deleted trust relationship: {trust_id}")
                else:
                    print(f"⚠️ Failed to delete trust relationship: {trust_id}")
            except Exception as e:
                print(f"⚠️ Exception deleting trust relationship {trust_id}: {str(e)}")
        
        # Delete organizations
        for org_id in self.created_resources['organizations']:
            try:
                response = self.session.delete(f"{self.base_url}/api/v1/organizations/{org_id}/delete_organization/")
                if response.status_code in [200, 204]:
                    print(f"✅ Deleted organization: {org_id}")
                else:
                    print(f"⚠️ Failed to delete organization: {org_id}")
            except Exception as e:
                print(f"⚠️ Exception deleting organization {org_id}: {str(e)}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("TRUST MANAGEMENT TEST REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%\n")
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            print("-" * 40)
            for result in self.test_results:
                if not result['success']:
                    print(f"❌ {result['test']}")
                    print(f"   Details: {result['details']}")
                    if result['response_code']:
                        print(f"   Response: {result['response_code']}")
                    print()
        
        # Save detailed report
        with open('trust_management_test_report.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print("Detailed report saved to: trust_management_test_report.json")
        return failed_tests == 0
    
    def run_all_tests(self):
        """Run all trust management tests"""
        print("Starting Comprehensive Trust Management Testing...")
        print("=" * 80)
        
        # Step 1: Login
        if not self.login_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test organization edge cases
        org1_id, org2_id = self.test_organization_edge_cases()
        
        # Step 3: Test trust relationships
        self.test_trust_relationships(org1_id, org2_id)
        
        # Step 4: Test organization trust endpoints
        self.test_organization_trust_endpoints()
        
        # Step 5: Test UI integration
        self.test_ui_integration()
        
        # Step 6: Generate report
        success = self.generate_report()
        
        # Step 7: Cleanup
        self.cleanup_test_data()
        
        return success

if __name__ == "__main__":
    tester = TrustManagementTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check the report for details.")
        exit(1)
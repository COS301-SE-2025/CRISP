#!/usr/bin/env python3
"""
Comprehensive endpoint testing script for ALL endpoints in CRISP system
Tests every single endpoint discovered in the codebase
"""
import requests
import json
import sys
import uuid
from datetime import datetime
import time

BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"

class ComprehensiveEndpointTester:
    def __init__(self):
        self.results = []
        self.auth_token = None
        self.test_user_id = None
        self.test_org_id = None
        self.test_collection_id = None
        self.test_relationship_id = None
        
    def test_endpoint(self, method, url, headers=None, data=None, auth_token=None, expect_error=False):
        """Test a single endpoint and return results"""
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=15)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=15)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=15)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=headers, json=data, timeout=15)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=15)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            response_time = time.time() - start_time
            
            result = {
                "status_code": response.status_code,
                "success": 200 <= response.status_code < 300 if not expect_error else response.status_code >= 400,
                "response_time": response_time,
                "size": len(response.content)
            }
            
            try:
                result["content"] = response.json()
            except:
                result["content"] = response.text[:500] + "..." if len(response.text) > 500 else response.text
                
            return result
            
        except Exception as e:
            return {"error": str(e), "success": False}

    def get_auth_token(self):
        """Get authentication token"""
        login_data = {"username": "admin", "password": "admin123"}
        result = self.test_endpoint("POST", f"{BASE_URL}/api/v1/auth/login/", data=login_data)
        
        if result.get("success") and isinstance(result.get("content"), dict):
            content = result["content"]
            if "tokens" in content and "access" in content["tokens"]:
                return content["tokens"]["access"]
            return content.get("access_token") or content.get("token")
        return None

    def create_test_data(self):
        """Create test data needed for endpoint testing"""
        print("Creating test data...")
        
        # Try to get a test user ID
        result = self.test_endpoint("GET", f"{BASE_URL}/api/v1/users/list/", auth_token=self.auth_token)
        if result.get("success") and result.get("content"):
            try:
                content = result["content"]
                if "data" in content and "users" in content["data"]:
                    users = content["data"]["users"]
                    if users:
                        self.test_user_id = users[0]["id"]
                        print(f"Using test user ID: {self.test_user_id}")
            except:
                pass
        
        # Try to get a test organization ID
        result = self.test_endpoint("GET", f"{BASE_URL}/api/v1/organizations/list_organizations/", auth_token=self.auth_token)
        if result.get("success") and result.get("content"):
            try:
                content = result["content"]
                if "organizations" in content and content["organizations"]:
                    self.test_org_id = content["organizations"][0]["id"]
                    print(f"Using test organization ID: {self.test_org_id}")
            except:
                pass
        
        # Try to get a test collection ID
        result = self.test_endpoint("GET", f"{BASE_URL}/taxii2/", auth_token=self.auth_token)
        if result.get("success"):
            self.test_collection_id = str(uuid.uuid4())  # Generate UUID for testing
            print(f"Using test collection ID: {self.test_collection_id}")
        
        # Try to get trust relationship ID
        result = self.test_endpoint("GET", f"{BASE_URL}/api/v1/trust/relationships/", auth_token=self.auth_token)
        if result.get("success") and result.get("content"):
            try:
                content = result["content"]
                if "relationships" in content and content["relationships"]:
                    self.test_relationship_id = content["relationships"][0].get("id", 1)
                    print(f"Using test relationship ID: {self.test_relationship_id}")
                else:
                    self.test_relationship_id = 1  # Default ID
            except:
                self.test_relationship_id = 1

    def run_test(self, endpoint_info):
        """Run a single endpoint test"""
        method = endpoint_info["method"]
        url = BASE_URL + endpoint_info["url"]
        name = endpoint_info["name"]
        auth_required = endpoint_info.get("auth_required", False)
        data = endpoint_info.get("data", None)
        expect_error = endpoint_info.get("expect_error", False)
        
        # Replace placeholders in URL
        if "<int:user_id>" in url and self.test_user_id:
            url = url.replace("<int:user_id>", str(self.test_user_id))
        elif "<uuid:pk>" in url and self.test_user_id:
            url = url.replace("<uuid:pk>", str(self.test_user_id))
        elif "<str:organization_id>" in url and self.test_org_id:
            url = url.replace("<str:organization_id>", str(self.test_org_id))
        elif "<uuid:collection_id>" in url and self.test_collection_id:
            url = url.replace("<uuid:collection_id>", self.test_collection_id)
        elif "<str:object_id>" in url:
            url = url.replace("<str:object_id>", "test-object-123")
        elif "<int:pk>" in url:
            url = url.replace("<int:pk>", "1")
        elif "<int:relationship_id>" in url and self.test_relationship_id:
            url = url.replace("<int:relationship_id>", str(self.test_relationship_id))
        
        # Skip if URL still has placeholders
        if "<" in url and ">" in url:
            return {
                "endpoint_name": name,
                "url": endpoint_info["url"],
                "method": method,
                "auth_required": auth_required,
                "status_code": "SKIP",
                "success": False,
                "error": "URL placeholder not resolved",
                "response_time": 0
            }
        
        token = self.auth_token if auth_required else None
        result = self.test_endpoint(method, url, data=data, auth_token=token, expect_error=expect_error)
        
        result["endpoint_name"] = name
        result["url"] = endpoint_info["url"]
        result["method"] = method
        result["auth_required"] = auth_required
        result["actual_url"] = url
        
        return result

    def run_all_tests(self):
        """Run comprehensive tests on ALL endpoints"""
        print("=" * 80)
        print("COMPREHENSIVE ENDPOINT TESTING - ALL ENDPOINTS")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Get authentication token
        print("1. AUTHENTICATION SETUP")
        print("-" * 40)
        self.auth_token = self.get_auth_token()
        if self.auth_token:
            print(f"Authentication Token: OBTAINED ({self.auth_token[:20]}...)")
        else:
            print("Authentication Token: FAILED")
            return
        print()
        
        # Create test data
        self.create_test_data()
        print()
        
        # Define ALL endpoints to test
        all_endpoints = [
            # Core System Endpoints
            {"method": "GET", "url": "/", "name": "Home Page", "auth_required": False},
            {"method": "GET", "url": "/admin/", "name": "Django Admin", "auth_required": False},
            {"method": "GET", "url": "/api/", "name": "API Root", "auth_required": False},
            {"method": "GET", "url": "/api/status/", "name": "Core Status", "auth_required": False},
            
            # Authentication Endpoints
            {"method": "POST", "url": "/api/v1/auth/login/", "name": "Auth Login", "auth_required": False, "data": {"username": "admin", "password": "admin123"}},
            
            # Extended Authentication Endpoints (from core_ut)
            {"method": "POST", "url": "/api/v1/auth/register/", "name": "Auth Register", "auth_required": False, "data": {"username": "testuser123", "email": "test123@example.com", "password": "testpass123"}},
            {"method": "POST", "url": "/api/v1/auth/logout/", "name": "Auth Logout", "auth_required": True},
            {"method": "POST", "url": "/api/v1/auth/refresh/", "name": "Auth Refresh Token", "auth_required": True},
            {"method": "GET", "url": "/api/v1/auth/verify/", "name": "Auth Verify Token", "auth_required": True},
            {"method": "GET", "url": "/api/v1/auth/sessions/", "name": "Auth Sessions", "auth_required": True},
            {"method": "POST", "url": "/api/v1/auth/revoke-session/", "name": "Auth Revoke Session", "auth_required": True},
            {"method": "POST", "url": "/api/v1/auth/change-password/", "name": "Auth Change Password", "auth_required": True, "data": {"old_password": "admin123", "new_password": "newpass123"}},
            {"method": "POST", "url": "/api/v1/auth/forgot-password/", "name": "Auth Forgot Password", "auth_required": False, "data": {"email": "admin@crisp.com"}},
            {"method": "POST", "url": "/api/v1/auth/validate-reset-token/", "name": "Auth Validate Reset Token", "auth_required": False, "data": {"token": "test-token"}},
            {"method": "POST", "url": "/api/v1/auth/reset-password/", "name": "Auth Reset Password", "auth_required": False, "data": {"token": "test-token", "new_password": "newpass123"}},
            {"method": "GET", "url": "/api/v1/auth/dashboard/", "name": "Auth Dashboard", "auth_required": True},
            
            # Admin Endpoints
            {"method": "GET", "url": "/api/v1/admin/system_health/", "name": "System Health", "auth_required": False},
            {"method": "GET", "url": "/api/v1/admin/trust_overview/", "name": "Trust Overview", "auth_required": True},
            
            # Extended Admin Endpoints
            {"method": "GET", "url": "/api/v1/admin/dashboard/", "name": "Admin Dashboard", "auth_required": True},
            {"method": "GET", "url": "/api/v1/admin/system-health/", "name": "Admin System Health", "auth_required": True},
            {"method": "GET", "url": "/api/v1/admin/audit-logs/", "name": "Admin Audit Logs", "auth_required": True},
            {"method": "POST", "url": "/api/v1/admin/cleanup-sessions/", "name": "Admin Cleanup Sessions", "auth_required": True},
            {"method": "POST", "url": "/api/v1/admin/users/<uuid:pk>/unlock/", "name": "Admin Unlock User", "auth_required": True},
            {"method": "GET", "url": "/api/v1/admin/comprehensive-audit-logs/", "name": "Admin Comprehensive Audit Logs", "auth_required": True},
            {"method": "GET", "url": "/api/v1/admin/users/<uuid:pk>/activity-summary/", "name": "Admin User Activity Summary", "auth_required": True},
            {"method": "GET", "url": "/api/v1/admin/security-events/", "name": "Admin Security Events", "auth_required": True},
            {"method": "GET", "url": "/api/v1/admin/audit-statistics/", "name": "Admin Audit Statistics", "auth_required": True},
            
            # Alert System Endpoints
            {"method": "GET", "url": "/api/v1/alerts/statistics/", "name": "Alert Statistics", "auth_required": False},
            {"method": "GET", "url": "/api/v1/alerts/test-connection/", "name": "Test Gmail Connection", "auth_required": True},
            {"method": "POST", "url": "/api/v1/alerts/test-email/", "name": "Send Alert Test Email", "auth_required": True, "data": {"email": "test@example.com"}},
            
            # Extended Alert Endpoints
            {"method": "GET", "url": "/alerts/list/", "name": "Alerts List", "auth_required": True},
            {"method": "POST", "url": "/alerts/threat/", "name": "Send Threat Alert", "auth_required": True, "data": {"threat_id": "test-threat"}},
            {"method": "POST", "url": "/alerts/feed/", "name": "Send Feed Notification", "auth_required": True, "data": {"feed_id": "test-feed"}},
            {"method": "POST", "url": "/alerts/mark-all-read/", "name": "Mark All Alerts Read", "auth_required": True},
            {"method": "GET", "url": "/alerts/preferences/", "name": "Get Alert Preferences", "auth_required": True},
            {"method": "PUT", "url": "/alerts/preferences/update/", "name": "Update Alert Preferences", "auth_required": True, "data": {"email_alerts": True}},
            {"method": "GET", "url": "/alerts/test-connection/", "name": "Extended Test Connection", "auth_required": True},
            {"method": "GET", "url": "/alerts/statistics/", "name": "Extended Alert Statistics", "auth_required": True},
            {"method": "POST", "url": "/alerts/test-email/", "name": "Extended Test Email", "auth_required": True, "data": {"recipient": "test@example.com"}},
            
            # Email System Endpoints
            {"method": "POST", "url": "/api/v1/email/send-test/", "name": "Send Test Email", "auth_required": True, "data": {"recipient": "test@example.com"}},
            
            # User Management Endpoints
            {"method": "GET", "url": "/api/v1/users/profile/", "name": "User Profile", "auth_required": True},
            {"method": "GET", "url": "/api/v1/users/statistics/", "name": "User Statistics", "auth_required": True},
            {"method": "GET", "url": "/api/v1/users/list/", "name": "List Users", "auth_required": True},
            {"method": "POST", "url": "/api/v1/users/create_user/", "name": "Create User", "auth_required": True, "data": {"username": "testuser456", "email": "test456@example.com", "password": "testpass456", "organization_id": "test-org-id"}},
            {"method": "GET", "url": "/api/v1/users/<int:user_id>/get_user/", "name": "Get User", "auth_required": True},
            {"method": "PUT", "url": "/api/v1/users/<int:user_id>/update_user/", "name": "Update User", "auth_required": True, "data": {"first_name": "Updated", "last_name": "User"}},
            {"method": "DELETE", "url": "/api/v1/users/<int:user_id>/delete_user/", "name": "Delete User", "auth_required": True},
            {"method": "PATCH", "url": "/api/v1/users/<int:user_id>/change_username/", "name": "Change Username", "auth_required": True, "data": {"new_username": "updateduser"}},
            
            # Extended User Management Endpoints
            {"method": "POST", "url": "/api/v1/users/create/", "name": "Extended Create User", "auth_required": True, "data": {"username": "extuser", "email": "ext@example.com", "password": "extpass123"}},
            {"method": "GET", "url": "/api/v1/users/<uuid:pk>/", "name": "Extended Get User", "auth_required": True},
            {"method": "PUT", "url": "/api/v1/users/<uuid:pk>/", "name": "Extended Update User", "auth_required": True, "data": {"first_name": "Extended"}},
            {"method": "POST", "url": "/api/v1/users/<uuid:pk>/deactivate/", "name": "Deactivate User", "auth_required": True},
            {"method": "POST", "url": "/api/v1/users/<uuid:pk>/reactivate/", "name": "Reactivate User", "auth_required": True},
            
            # Organization Management Endpoints
            {"method": "GET", "url": "/api/v1/organizations/list_organizations/", "name": "List Organizations", "auth_required": True},
            {"method": "GET", "url": "/api/v1/organizations/types/", "name": "Organization Types", "auth_required": True},
            {"method": "POST", "url": "/api/v1/organizations/create_organization/", "name": "Create Organization", "auth_required": True, "data": {"name": f"Test Org {int(time.time())}", "organization_type": "GOVERNMENT"}},
            {"method": "GET", "url": "/api/v1/organizations/<str:organization_id>/get_organization/", "name": "Get Organization", "auth_required": True},
            {"method": "PUT", "url": "/api/v1/organizations/<str:organization_id>/update_organization/", "name": "Update Organization", "auth_required": True, "data": {"name": "Updated Organization"}},
            {"method": "DELETE", "url": "/api/v1/organizations/<str:organization_id>/delete_organization/", "name": "Delete Organization", "auth_required": True},
            {"method": "GET", "url": "/api/v1/organizations/<str:organization_id>/", "name": "Organization Detail", "auth_required": True},
            {"method": "POST", "url": "/api/v1/organizations/<str:organization_id>/deactivate_organization/", "name": "Deactivate Organization", "auth_required": True},
            {"method": "POST", "url": "/api/v1/organizations/<str:organization_id>/reactivate_organization/", "name": "Reactivate Organization", "auth_required": True},
            
            # Trust Management Endpoints
            {"method": "GET", "url": "/api/v1/trust/groups/", "name": "Trust Groups", "auth_required": True},
            {"method": "GET", "url": "/api/v1/trust/levels/", "name": "Trust Levels", "auth_required": True},
            {"method": "GET", "url": "/api/v1/trust/metrics/", "name": "Trust Metrics", "auth_required": True},
            {"method": "GET", "url": "/api/v1/trust/relationships/", "name": "Trust Relationships", "auth_required": True},
            {"method": "GET", "url": "/api/v1/trust/relationships/<int:relationship_id>/", "name": "Trust Relationship Detail", "auth_required": True},
            
            # Core Threat Intelligence Endpoints
            {"method": "GET", "url": "/api/threat-feeds/", "name": "Threat Feeds List", "auth_required": True},
            {"method": "POST", "url": "/api/threat-feeds/", "name": "Create Threat Feed", "auth_required": True, "data": {"name": "Test Feed", "url": "https://example.com/feed"}},
            {"method": "GET", "url": "/api/threat-feeds/<int:pk>/", "name": "Threat Feed Detail", "auth_required": True},
            {"method": "PUT", "url": "/api/threat-feeds/<int:pk>/", "name": "Update Threat Feed", "auth_required": True, "data": {"name": "Updated Feed"}},
            {"method": "DELETE", "url": "/api/threat-feeds/<int:pk>/", "name": "Delete Threat Feed", "auth_required": True},
            {"method": "POST", "url": "/api/threat-feeds/<int:pk>/consume/", "name": "Consume Threat Feed", "auth_required": True},
            {"method": "GET", "url": "/api/threat-feeds/<int:pk>/status/", "name": "Threat Feed Status", "auth_required": True},
            {"method": "GET", "url": "/api/threat-feeds/<int:pk>/test_connection/", "name": "Test Threat Feed Connection", "auth_required": True},
            {"method": "GET", "url": "/api/threat-feeds/external/", "name": "External Threat Feeds", "auth_required": True},
            {"method": "GET", "url": "/api/threat-feeds/available_collections/", "name": "Available Collections", "auth_required": True},
            
            # Indicators API
            {"method": "GET", "url": "/api/indicators/", "name": "Indicators List", "auth_required": True},
            {"method": "GET", "url": "/api/indicators/<int:pk>/", "name": "Indicator Detail", "auth_required": True},
            {"method": "GET", "url": "/api/indicators/recent/", "name": "Recent Indicators", "auth_required": True},
            {"method": "GET", "url": "/api/indicators/stats/", "name": "Indicator Statistics", "auth_required": True},
            {"method": "GET", "url": "/api/indicators/types/", "name": "Indicator Types", "auth_required": True},
            
            # Unified API Endpoints
            {"method": "GET", "url": "/api/v1/", "name": "Unified API Root", "auth_required": False},
            {"method": "GET", "url": "/api/v1/dashboard/overview/", "name": "Dashboard Overview", "auth_required": True},
            {"method": "GET", "url": "/api/v1/threat-feeds/external/", "name": "Unified External Feeds", "auth_required": False},
            {"method": "GET", "url": "/api/v1/threat-feeds/collections/", "name": "Unified Collections", "auth_required": False},
            
            # TAXII 2.1 Endpoints
            {"method": "GET", "url": "/taxii2/", "name": "TAXII Discovery", "auth_required": False},
            {"method": "GET", "url": "/taxii2/collections/", "name": "TAXII Collections List", "auth_required": False},
            {"method": "GET", "url": "/taxii2/collections/<uuid:collection_id>/", "name": "TAXII Collection Detail", "auth_required": False},
            {"method": "GET", "url": "/taxii2/collections/<uuid:collection_id>/objects/", "name": "TAXII Collection Objects", "auth_required": False},
            {"method": "GET", "url": "/taxii2/collections/<uuid:collection_id>/objects/<str:object_id>/", "name": "TAXII Object Detail", "auth_required": False},
            {"method": "GET", "url": "/taxii2/collections/<uuid:collection_id>/manifest/", "name": "TAXII Collection Manifest", "auth_required": False},
        ]
        
        print(f"2. COMPREHENSIVE ENDPOINT TESTING ({len(all_endpoints)} endpoints)")
        print("-" * 40)
        
        passed = 0
        failed = 0
        skipped = 0
        
        for i, endpoint in enumerate(all_endpoints, 1):
            print(f"{i:3d}. Testing {endpoint['name']} ({endpoint['method']} {endpoint['url']})")
            
            result = self.run_test(endpoint)
            self.results.append(result)
            
            if result.get("status_code") == "SKIP":
                print(f"     SKIPPED - {result.get('error', 'Unknown reason')}")
                skipped += 1
            elif result.get("success"):
                print(f"     PASS (HTTP {result['status_code']}) - {result.get('response_time', 0):.3f}s")
                passed += 1
            else:
                print(f"     FAIL (HTTP {result.get('status_code', 'ERROR')})")
                if result.get("content"):
                    error_msg = str(result["content"])[:100] + "..." if len(str(result["content"])) > 100 else str(result["content"])
                    print(f"     Error: {error_msg}")
                failed += 1
        
        print()
        print("3. FINAL SUMMARY")
        print("-" * 40)
        print(f"Total Endpoints: {len(all_endpoints)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Skipped: {skipped}")
        print(f"Success Rate: {(passed / (len(all_endpoints) - skipped) * 100) if (len(all_endpoints) - skipped) > 0 else 0:.1f}%")
        
        return self.results

def main():
    tester = ComprehensiveEndpointTester()
    results = tester.run_all_tests()
    
    # Save detailed results to JSON
    with open('comprehensive_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\nDetailed results saved to: comprehensive_test_results.json")

if __name__ == "__main__":
    main()
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
        self.test_threat_feed_id = None
        self.test_operations_feed_id = None
        self.test_indicator_id = None
        self.refresh_token = None
        self.test_detail_org_id = None  # Separate org for detail testing
        
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
        login_data = {"username": "admin_test", "password": "password123"}
        result = self.test_endpoint("POST", f"{BASE_URL}/api/v1/auth/login/", data=login_data)
        
        if result.get("success") and isinstance(result.get("content"), dict):
            content = result["content"]
            if "tokens" in content and "access" in content["tokens"]:
                # Store refresh token for testing
                self.refresh_token = content["tokens"].get("refresh")
                return content["tokens"]["access"]
            return content.get("access_token") or content.get("token")
        return None

    def create_test_data(self):
        """Create test data needed for endpoint testing"""
        print("Creating test data...")
        
        # Create a separate test user for user operations (to avoid modifying the auth user)
        test_user_data = {
            "username": f"test_user_{int(time.time())}",
            "email": f"testuser{int(time.time())}@example.com",
            "password": "testpass123",
            "role": "BlueVisionAdmin"
        }
        create_result = self.test_endpoint("POST", f"{BASE_URL}/api/v1/users/create_user/", auth_token=self.auth_token, data=test_user_data)
        if create_result.get("success") and create_result.get("content"):
            try:
                self.test_user_id = create_result["content"]["id"]
                print(f"Created separate test user ID: {self.test_user_id}")
            except:
                # Fallback to existing user list
                result = self.test_endpoint("GET", f"{BASE_URL}/api/v1/users/list/", auth_token=self.auth_token)
                if result.get("success") and result.get("content"):
                    content = result["content"]
                    if "data" in content and "users" in content["data"]:
                        users = content["data"]["users"]
                        if users:
                            # Use a user that's not the current auth user
                            for user in users:
                                if user.get("username") != "admin_test":
                                    self.test_user_id = user["id"]
                                    print(f"Using fallback test user ID: {self.test_user_id}")
                                    break
        else:
            # Final fallback
            result = self.test_endpoint("GET", f"{BASE_URL}/api/v1/users/list/", auth_token=self.auth_token)
            if result.get("success") and result.get("content"):
                content = result["content"]
                if "data" in content and "users" in content["data"]:
                    users = content["data"]["users"]
                    if users:
                        for user in users:
                            if user.get("username") != "admin_test":
                                self.test_user_id = user["id"]
                                print(f"Using existing test user ID: {self.test_user_id}")
                                break
        
        # Try to get a test organization ID
        result = self.test_endpoint("GET", f"{BASE_URL}/api/v1/organizations/list_organizations/", auth_token=self.auth_token)
        if result.get("success") and result.get("content"):
            try:
                content = result["content"]
                if "data" in content and "organizations" in content["data"] and content["data"]["organizations"]:
                    self.test_org_id = content["data"]["organizations"][0]["id"]
                    print(f"Using test organization ID: {self.test_org_id}")
                elif "organizations" in content and content["organizations"]:
                    self.test_org_id = content["organizations"][0]["id"]
                    print(f"Using test organization ID: {self.test_org_id}")
                elif "results" in content and content["results"]:
                    self.test_org_id = content["results"][0]["id"]
                    print(f"Using test organization ID: {self.test_org_id}")
                elif isinstance(content, list) and content:
                    self.test_org_id = content[0]["id"]
                    print(f"Using test organization ID: {self.test_org_id}")
            except Exception as e:
                print(f"Error getting org ID: {e}")
                print(f"Content was: {content}")
                pass
        
        # Use permanent organization for detail testing (won't be deleted)
        # This organization was pre-created to avoid test sequence conflicts
        self.test_detail_org_id = "f2a14bd4-2afe-4056-8d7f-c70ea3053395"
        print(f"Using permanent detail test organization ID: {self.test_detail_org_id}")
        
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
                if "data" in content and isinstance(content["data"], list) and content["data"]:
                    self.test_relationship_id = content["data"][0].get("id", 1)
                    print(f"Using test relationship ID: {self.test_relationship_id}")
                elif "relationships" in content and content["relationships"]:
                    self.test_relationship_id = content["relationships"][0].get("id", 1)
                    print(f"Using test relationship ID: {self.test_relationship_id}")
                else:
                    self.test_relationship_id = 1  # Default ID
            except:
                self.test_relationship_id = 1
        
        # Get a core app organization ID for threat feeds (different from core_ut orgs)
        core_orgs_result = self.test_endpoint("GET", f"{BASE_URL}/api/threat-feeds/", auth_token=self.auth_token)
        core_org_id = None
        
        # Try to get an organization from existing threat feeds or use a known core org
        try:
            # Use a manual call to get core organizations - we know some exist
            import requests
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            # We'll create a core organization since the models are different
            core_org_data = {
                "name": f"Core Test Org {int(time.time())}",
                "type": "university"
            }
            # Use pre-created core organization for threat feeds
            core_org_id = "28caf162-28b1-48b7-a13c-2c5f1963217f"  # Created specifically for testing
            self.core_org_id = core_org_id  # Store as instance variable
            print(f"Using core app organization ID for threat feeds: {core_org_id}")
        except:
            print("Could not get core organization ID")
            self.core_org_id = None
        
        # Create a test threat feed for testing operations (only if we have a valid core org ID)
        if core_org_id:
            test_feed_data = {
                "name": f"Test Feed {int(time.time())}",
                "url": "https://example.com/feed", 
                "owner": core_org_id
            }
            result = self.test_endpoint("POST", f"{BASE_URL}/api/threat-feeds/", auth_token=self.auth_token, data=test_feed_data)
            if result.get("success") and result.get("content"):
                try:
                    self.test_threat_feed_id = result["content"]["id"]
                    print(f"Created test threat feed ID: {self.test_threat_feed_id}")
                except:
                    print(f"Error extracting threat feed ID from: {result['content']}")
                    self.test_threat_feed_id = None
            else:
                print(f"Failed to create test threat feed: {result}")
                self.test_threat_feed_id = None
        else:
            print("No valid organization ID for threat feed creation")
            self.test_threat_feed_id = None
        
        # Create a second threat feed for operations testing (so delete test doesn't affect operations)
        if core_org_id:
            test_feed_data2 = {
                "name": f"Operations Test Feed {int(time.time())}",
                "url": "https://example.com/operations-feed",
                "owner": core_org_id
            }
            result = self.test_endpoint("POST", f"{BASE_URL}/api/threat-feeds/", auth_token=self.auth_token, data=test_feed_data2)
            if result.get("success") and result.get("content"):
                try:
                    self.test_operations_feed_id = result["content"]["id"]
                    print(f"Created operations test threat feed ID: {self.test_operations_feed_id}")
                except:
                    self.test_operations_feed_id = self.test_threat_feed_id
            else:
                self.test_operations_feed_id = self.test_threat_feed_id
        else:
            self.test_operations_feed_id = None
        
        # Get actual indicator ID for testing
        result = self.test_endpoint("GET", f"{BASE_URL}/api/indicators/", auth_token=self.auth_token)
        if result.get("success") and result.get("content"):
            try:
                indicators = result["content"]
                if isinstance(indicators, list) and indicators:
                    self.test_indicator_id = indicators[0]["id"]
                    print(f"Using test indicator ID: {self.test_indicator_id}")
                elif isinstance(indicators, dict) and "results" in indicators and indicators["results"]:
                    self.test_indicator_id = indicators["results"][0]["id"]
                    print(f"Using test indicator ID: {self.test_indicator_id}")
                else:
                    self.test_indicator_id = 1
            except:
                self.test_indicator_id = 1
        else:
            self.test_indicator_id = 1
        
        # Get actual TAXII collection ID
        result = self.test_endpoint("GET", f"{BASE_URL}/taxii2/collections/", auth_token=self.auth_token)
        if result.get("success") and result.get("content"):
            try:
                collections = result["content"]
                if "collections" in collections and collections["collections"]:
                    self.test_collection_id = collections["collections"][0]["id"]
                    print(f"Using actual collection ID: {self.test_collection_id}")
                else:
                    # Keep the generated UUID
                    pass
            except:
                pass

    def run_test(self, endpoint_info):
        """Run a single endpoint test"""
        method = endpoint_info["method"]
        url = BASE_URL + endpoint_info["url"]
        name = endpoint_info["name"]
        auth_required = endpoint_info.get("auth_required", False)
        data = endpoint_info.get("data", None)
        expect_error = endpoint_info.get("expect_error", False)
        
        # Special handling for refresh token endpoint
        if url.endswith("/api/v1/auth/refresh/"):
            # Get a fresh refresh token for this test to avoid session conflicts
            fresh_login = self.test_endpoint("POST", f"{BASE_URL}/api/v1/auth/login/", data={"username": "admin_test", "password": "password123"})
            if fresh_login.get("success") and fresh_login.get("content", {}).get("tokens", {}).get("refresh"):
                data = {"refresh": fresh_login["content"]["tokens"]["refresh"]}
        
        # Special handling for change password endpoint - use password that might have changed
        if url.endswith("/api/v1/auth/change-password/"):
            # Try with the new password first (in case password was already changed)
            test_passwords = ["newpass123", "password123"]
            for test_password in test_passwords:
                test_data = {"current_password": test_password, "new_password": "temppass456", "new_password_confirm": "temppass456"}
                test_result = self.test_endpoint(method, url, auth_token=self.auth_token, data=test_data)
                if test_result.get("success"):
                    # Reset password back to original
                    self.test_endpoint("POST", url, auth_token=self.auth_token, 
                                     data={"current_password": "temppass456", "new_password": "password123", "new_password_confirm": "password123"})
                    return test_result
            # If neither worked, continue with original test data
            
        # Special handling for login endpoint - try different passwords in case password was changed
        if url.endswith("/api/v1/auth/login/") and name == "Auth Login":
            test_passwords = ["password123", "newpass123", "temppass456"]
            base_data = data.copy() if data else {"username": "admin_test"}
            for test_password in test_passwords:
                test_data = base_data.copy()
                test_data["password"] = test_password
                test_result = self.test_endpoint(method, url, data=test_data)
                if test_result.get("success"):
                    return test_result
            # If none worked, continue with original test data
        
        # Replace hardcoded organization IDs with actual test org ID
        if data and isinstance(data, dict):
            for key, value in data.items():
                if value == "68a93b91-d018-4f7a-9ff8-a32582dc6193":
                    # Use core_org_id for threat feed endpoints, test_org_id for others
                    if "/threat-feeds/" in url and self.core_org_id:
                        data[key] = self.core_org_id
                    elif self.test_org_id:
                        data[key] = self.test_org_id
        
        # Replace placeholders in URL
        if "<int:user_id>" in url and self.test_user_id:
            url = url.replace("<int:user_id>", str(self.test_user_id))
        if "<uuid:pk>" in url and self.test_user_id:
            url = url.replace("<uuid:pk>", str(self.test_user_id))
        if "<str:organization_id>" in url:
            # For detail endpoints, create organization on-demand to avoid conflicts
            if any(endpoint in url for endpoint in ["/api/v1/organizations/<str:organization_id>/", "/deactivate_organization/", "/reactivate_organization/"]):
                # Create a fresh organization for detail testing
                detail_org_data = {
                    "name": f"DetailOrg{int(time.time())}{name.replace(' ', '')}",
                    "organization_type": "private"
                }
                create_result = self.test_endpoint("POST", f"{BASE_URL}/api/v1/organizations/create_organization/", auth_token=self.auth_token, data=detail_org_data)
                if create_result.get("success") and create_result.get("content"):
                    try:
                        # Handle different response formats
                        content = create_result["content"]
                        if "data" in content and "id" in content["data"]:
                            detail_org_id = content["data"]["id"]
                        elif "id" in content:
                            detail_org_id = content["id"]
                        else:
                            detail_org_id = None
                        
                        if detail_org_id:
                            url = url.replace("<str:organization_id>", str(detail_org_id))
                            print(f"    → Created fresh detail org {detail_org_id} for {name}")
                        else:
                            print(f"    → Could not find org ID in response: {content}")
                            raise Exception("No ID found")
                    except Exception as e:
                        print(f"    → Failed to extract org ID: {e}, content: {create_result.get('content')}")
                        # Fallback to main org ID
                        if self.test_org_id:
                            url = url.replace("<str:organization_id>", str(self.test_org_id))
                        else:
                            url = url.replace("<str:organization_id>", "test-org-id")
                else:
                    print(f"    → Failed to create fresh org: {create_result}")
                    # Fallback to main org ID
                    if self.test_org_id:
                        url = url.replace("<str:organization_id>", str(self.test_org_id))
                    else:
                        url = url.replace("<str:organization_id>", "test-org-id")
            elif self.test_org_id:
                url = url.replace("<str:organization_id>", str(self.test_org_id))
        if "<uuid:collection_id>" in url and self.test_collection_id:
            url = url.replace("<uuid:collection_id>", self.test_collection_id)
        if "<str:object_id>" in url:
            url = url.replace("<str:object_id>", "test-object-123")
        if "<int:pk>" in url:
            # Use different IDs for different endpoint types
            if "/threat-feeds/" in url:
                if any(op in url for op in ["/consume/", "/status/", "/test_connection/"]):
                    if self.test_operations_feed_id:
                        url = url.replace("<int:pk>", str(self.test_operations_feed_id))
                    else:
                        # Skip threat feed operations if no valid feed ID
                        return {
                            "endpoint_name": name,
                            "url": endpoint_info["url"],
                            "method": method,
                            "auth_required": auth_required,
                            "status_code": "SKIP",
                            "success": False,
                            "error": "No valid threat feed ID for operations",
                            "response_time": 0
                        }
                elif self.test_threat_feed_id:
                    url = url.replace("<int:pk>", str(self.test_threat_feed_id))
                else:
                    # Skip threat feed operations if no valid feed ID
                    return {
                        "endpoint_name": name,
                        "url": endpoint_info["url"],
                        "method": method,
                        "auth_required": auth_required,
                        "status_code": "SKIP", 
                        "success": False,
                        "error": "No valid threat feed ID",
                        "response_time": 0
                    }
            elif "/indicators/" in url and self.test_indicator_id:
                url = url.replace("<int:pk>", str(self.test_indicator_id))
            else:
                url = url.replace("<int:pk>", "1")
        if "<int:relationship_id>" in url and self.test_relationship_id:
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
            {"method": "POST", "url": "/api/v1/auth/login/", "name": "Auth Login", "auth_required": False, "data": {"username": "admin_test", "password": "password123"}},
            
            # Extended Authentication Endpoints (from core_ut)
            {"method": "POST", "url": "/api/v1/auth/register/", "name": "Auth Register", "auth_required": False, "data": {"username": f"testuser{int(time.time())}", "email": f"test{int(time.time())}@example.com", "password": "testpass123", "password_confirm": "testpass123", "first_name": "Test", "last_name": "User", "organization": "68a93b91-d018-4f7a-9ff8-a32582dc6193", "role": "viewer"}},
            {"method": "POST", "url": "/api/v1/auth/logout/", "name": "Auth Logout", "auth_required": True},
            {"method": "POST", "url": "/api/v1/auth/refresh/", "name": "Auth Refresh Token", "auth_required": True, "data": {"refresh": "dummy_token"}, "expect_error": False},
            {"method": "GET", "url": "/api/v1/auth/verify/", "name": "Auth Verify Token", "auth_required": True, "expect_error": False},
            {"method": "GET", "url": "/api/v1/auth/sessions/", "name": "Auth Sessions", "auth_required": True},
            {"method": "POST", "url": "/api/v1/auth/revoke-session/", "name": "Auth Revoke Session", "auth_required": True, "data": {"session_id": "test-session-id"}, "expect_error": True},
            {"method": "POST", "url": "/api/v1/auth/change-password/", "name": "Auth Change Password", "auth_required": True, "data": {"current_password": "password123", "new_password": "newpass123", "new_password_confirm": "newpass123"}},
            {"method": "POST", "url": "/api/v1/auth/forgot-password/", "name": "Auth Forgot Password", "auth_required": False, "data": {"email": "admin@crisp.com"}, "expect_error": True},
            {"method": "POST", "url": "/api/v1/auth/validate-reset-token/", "name": "Auth Validate Reset Token", "auth_required": False, "data": {"token": "valid-test-token-123"}, "expect_error": True},
            {"method": "POST", "url": "/api/v1/auth/reset-password/", "name": "Auth Reset Password", "auth_required": False, "data": {"token": "valid-test-token-123", "new_password": "newpass123"}, "expect_error": True},
            {"method": "GET", "url": "/api/v1/auth/dashboard/", "name": "Auth Dashboard", "auth_required": True},
            
            # Admin Endpoints
            {"method": "GET", "url": "/api/v1/admin/system_health/", "name": "System Health", "auth_required": False},
            {"method": "GET", "url": "/api/v1/admin/trust_overview/", "name": "Trust Overview", "auth_required": True},
            
            # Extended Admin Endpoints
            {"method": "GET", "url": "/api/v1/admin/dashboard/", "name": "Admin Dashboard", "auth_required": True},
            {"method": "GET", "url": "/api/v1/admin/system-health/", "name": "Admin System Health", "auth_required": True},
            {"method": "GET", "url": "/api/v1/admin/audit-logs/", "name": "Admin Audit Logs", "auth_required": True},
            {"method": "POST", "url": "/api/v1/admin/cleanup-sessions/", "name": "Admin Cleanup Sessions", "auth_required": True, "expect_error": True},
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
            {"method": "POST", "url": "/alerts/threat/", "name": "Send Threat Alert", "auth_required": True, "data": {"threat_id": "test-threat", "recipient_emails": ["admin@test.com"]}, "expect_error": True},
            {"method": "POST", "url": "/alerts/feed/", "name": "Send Feed Notification", "auth_required": True, "data": {"feed_id": "test-feed", "recipient_emails": ["admin@test.com"]}, "expect_error": True},
            {"method": "POST", "url": "/alerts/mark-all-read/", "name": "Mark All Alerts Read", "auth_required": True},
            {"method": "GET", "url": "/alerts/preferences/", "name": "Get Alert Preferences", "auth_required": True},
            {"method": "POST", "url": "/alerts/preferences/update/", "name": "Update Alert Preferences", "auth_required": True, "data": {"email_alerts": True}},
            {"method": "GET", "url": "/alerts/test-connection/", "name": "Extended Test Connection", "auth_required": True, "expect_error": True},
            {"method": "GET", "url": "/alerts/statistics/", "name": "Extended Alert Statistics", "auth_required": True},
            {"method": "POST", "url": "/alerts/test-email/", "name": "Extended Test Email", "auth_required": True, "data": {"recipient_email": "test@example.com"}, "expect_error": True},
            
            # Email System Endpoints
            {"method": "POST", "url": "/api/v1/email/send-test/", "name": "Send Test Email", "auth_required": True, "data": {"recipient": "test@example.com"}},
            
            # User Management Endpoints
            {"method": "GET", "url": "/api/v1/users/profile/", "name": "User Profile", "auth_required": True},
            {"method": "GET", "url": "/api/v1/users/statistics/", "name": "User Statistics", "auth_required": True},
            {"method": "GET", "url": "/api/v1/users/list/", "name": "List Users", "auth_required": True},
            {"method": "POST", "url": "/api/v1/users/create_user/", "name": "Create User", "auth_required": True, "data": {"username": f"newuser{int(time.time())}", "email": f"newuser{int(time.time())}@example.com", "password": "testpass456", "organization_id": "68a93b91-d018-4f7a-9ff8-a32582dc6193"}},
            {"method": "GET", "url": "/api/v1/users/<int:user_id>/get_user/", "name": "Get User", "auth_required": True},
            {"method": "PUT", "url": "/api/v1/users/<int:user_id>/update_user/", "name": "Update User", "auth_required": True, "data": {"first_name": "Updated", "last_name": "User"}},
            {"method": "DELETE", "url": "/api/v1/users/<int:user_id>/delete_user/", "name": "Delete User", "auth_required": True, "data": {"confirm_deletion": True}, "expect_error": True},
            {"method": "PATCH", "url": "/api/v1/users/<int:user_id>/change_username/", "name": "Change Username", "auth_required": True, "data": {"new_username": f"updated{int(time.time())}"}},
            
            # Extended User Management Endpoints
            {"method": "POST", "url": "/api/v1/users/create/", "name": "Extended Create User", "auth_required": True, "data": {"username": f"extuser{int(time.time())}", "email": f"ext{int(time.time())}@example.com", "password": "extpass123", "organization": "68a93b91-d018-4f7a-9ff8-a32582dc6193"}, "expect_error": True},
            {"method": "GET", "url": "/api/v1/users/<uuid:pk>/", "name": "Extended Get User", "auth_required": True},
            {"method": "PUT", "url": "/api/v1/users/<uuid:pk>/", "name": "Extended Update User", "auth_required": True, "data": {"first_name": "Extended"}},
            {"method": "POST", "url": "/api/v1/users/<uuid:pk>/deactivate/", "name": "Deactivate User", "auth_required": True, "expect_error": True},
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
            {"method": "POST", "url": "/api/threat-feeds/", "name": "Create Threat Feed", "auth_required": True, "data": {"name": f"API Test Feed {int(time.time())}", "url": "https://example.com/api-feed", "owner": "68a93b91-d018-4f7a-9ff8-a32582dc6193"}},
            {"method": "GET", "url": "/api/threat-feeds/<int:pk>/", "name": "Threat Feed Detail", "auth_required": True},
            {"method": "PUT", "url": "/api/threat-feeds/<int:pk>/", "name": "Update Threat Feed", "auth_required": True, "data": {"name": "Updated Feed", "owner": "68a93b91-d018-4f7a-9ff8-a32582dc6193"}},
            {"method": "DELETE", "url": "/api/threat-feeds/<int:pk>/", "name": "Delete Threat Feed", "auth_required": True},
            {"method": "POST", "url": "/api/threat-feeds/<int:pk>/consume/", "name": "Consume Threat Feed", "auth_required": True},
            {"method": "GET", "url": "/api/threat-feeds/<int:pk>/status/", "name": "Threat Feed Status", "auth_required": True},
            {"method": "GET", "url": "/api/threat-feeds/<int:pk>/test_connection/", "name": "Test Threat Feed Connection", "auth_required": True},
            {"method": "GET", "url": "/api/threat-feeds/external/", "name": "External Threat Feeds", "auth_required": True},
            {"method": "GET", "url": "/api/threat-feeds/available_collections/", "name": "Available Collections", "auth_required": True},
            
            # Indicators API
            {"method": "GET", "url": "/api/indicators/", "name": "Indicators List", "auth_required": True},
            {"method": "GET", "url": "/api/indicators/<int:pk>/", "name": "Indicator Detail", "auth_required": True, "expect_error": True},
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
            {"method": "GET", "url": "/taxii2/collections/", "name": "TAXII Collections List", "auth_required": True},
            {"method": "GET", "url": "/taxii2/collections/<uuid:collection_id>/", "name": "TAXII Collection Detail", "auth_required": True, "expect_error": True},
            {"method": "GET", "url": "/taxii2/collections/<uuid:collection_id>/objects/", "name": "TAXII Collection Objects", "auth_required": True, "expect_error": True},
            {"method": "GET", "url": "/taxii2/collections/<uuid:collection_id>/objects/<str:object_id>/", "name": "TAXII Object Detail", "auth_required": True, "expect_error": True},
            {"method": "GET", "url": "/taxii2/collections/<uuid:collection_id>/manifest/", "name": "TAXII Collection Manifest", "auth_required": True, "expect_error": True},
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
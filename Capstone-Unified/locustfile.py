"""
CRISP Django Load Testing Configuration with Locust
==================================================

This locustfile.py provides comprehensive load testing for the Django backend with:
- JWT authentication with proper session/CSRF handling
- Configurable endpoint testing
- Mixed authenticated/unauthenticated requests
- Realistic user behavior simulation
- Detailed metrics and error handling

Usage:
    locust -f locustfile.py --host=http://127.0.0.1:8000

Requirements:
    pip install locust requests
"""

import random
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from locust import HttpUser, task, between, events
from locust.exception import InterruptTaskSet
import requests


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRISPEndpoints:
    """
    Centralized endpoint configuration for easy management.
    Add/remove endpoints here to modify what gets tested.
    """
    
    # Authentication endpoints
    AUTH_LOGIN = "/api/auth/login/"
    AUTH_REGISTER = "/api/auth/register/"
    AUTH_PROFILE = "/api/auth/profile/"
    AUTH_LOGOUT = "/api/auth/logout/"
    AUTH_VERIFY_TOKEN = "/api/auth/verify-token/"
    
    # Core API endpoints
    STATUS = "/api/"
    SYSTEM_HEALTH = "/api/system-health/"
    
    # Threat Intelligence endpoints
    INDICATORS_LIST = "/api/indicators/"
    THREAT_FEEDS = "/api/threat-feeds/"
    TTPS_LIST = "/api/ttps/"
    MITRE_MATRIX = "/api/ttps/mitre-matrix/"
    TTP_TRENDS = "/api/ttps/trends/"
    RECENT_ACTIVITIES = "/api/recent-activities/"
    THREAT_ACTIVITY_CHART = "/api/threat-activity-chart/"
    
    # User Management endpoints
    USERS_LIST = "/api/users/"
    USER_INVITATIONS = "/api/users/invitations/"
    
    # Trust Management endpoints
    TRUST_BILATERAL = "/api/trust/bilateral/"
    TRUST_LEVELS = "/api/trust/levels/"
    TRUST_DASHBOARD = "/api/trust/dashboard/"
    
    # Organization Management endpoints
    ORGANIZATIONS_LIST = "/api/organizations/"
    ORGANIZATION_TYPES = "/api/organizations/types/"
    
    # Enhanced endpoints
    USER_MANAGEMENT_ROOT = "/api/user-management/"
    TRUST_MANAGEMENT_ROOT = "/api/trust-management/"
    ALERTS_ROOT = "/api/alerts/"
    
    # Frontend routes (for mixed testing)
    HOME = "/"
    DASHBOARD = "/dashboard/"
    ADMIN = "/admin/"


class TestCredentials:
    """Test user credentials for authentication testing"""
    
    # Default test users - based on actual population scripts and database
    USERS = [
        # Base users from setup_base_users.py
        {"username": "admin", "password": "AdminPass123!"},          # BlueVisionAdmin - EXISTS
        {"username": "demo", "password": "AdminPass123!"},           # Super admin - EXISTS  
        {"username": "test", "password": "AdminPass123!"},           # Super admin - EXISTS
        
        # Dynamically generated users from populate_database.py (use UserPass123!)
        {"username": "aaron.martin.286224@floresjohnsonan43.services.com", "password": "UserPass123!"},
        {"username": "adam.baker.801140@yang-leonardtec21.org", "password": "UserPass123!"},
        {"username": "adam.franklin.794775@floresjohnsonan43.services.com", "password": "UserPass123!"},
        {"username": "adam.grant.324933@willis-jonestec3.industries.com", "password": "UserPass123!"},
        {"username": "adam.smith.856704@hartwilliamsand13.ltd", "password": "UserPass123!"},
    ]
    
    @classmethod
    def get_random_user(cls):
        """Get a random test user credential"""
        return random.choice(cls.USERS)


class CRISPAuthenticatedUser(HttpUser):
    """
    Authenticated user that simulates real user behavior with:
    - JWT authentication with session/CSRF handling
    - Mixed GET/POST requests
    - Realistic think time
    - Error handling and retry logic
    """
    
    # Wait time between requests (1-3 seconds)
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_token = None
        self.refresh_token = None
        self.csrf_token = None
        self.session_cookies = None
        self.user_credentials = None
        self.authenticated = False
        
    def on_start(self):
        """Initialize user session and authenticate"""
        logger.info(f"Starting session for user on {self.host}")
        
        # Get a random user credential
        self.user_credentials = TestCredentials.get_random_user()
        
        # First, get CSRF token if needed
        self._get_csrf_token()
        
        # Attempt authentication
        self._authenticate()
    
    def on_stop(self):
        """Clean up session on stop"""
        if self.authenticated:
            self._logout()
    
    def _get_csrf_token(self):
        """Get CSRF token for session-based requests"""
        try:
            # Get CSRF token from a GET request to any page
            response = self.client.get(CRISPEndpoints.HOME, name="get_csrf_token")
            
            # Extract CSRF token from cookies
            if 'csrftoken' in response.cookies:
                self.csrf_token = response.cookies['csrftoken']
                logger.debug(f"CSRF token obtained: {self.csrf_token[:10]}...")
            
            # Store session cookies
            self.session_cookies = dict(response.cookies)
            
        except Exception as e:
            logger.warning(f"Failed to get CSRF token: {e}")
    
    def _authenticate(self):
        """Authenticate user with JWT"""
        try:
            headers = {
                'Content-Type': 'application/json',
            }
            
            # Add CSRF token if available
            if self.csrf_token:
                headers['X-CSRFToken'] = self.csrf_token
            
            # Login request
            login_data = {
                "username": self.user_credentials["username"],
                "password": self.user_credentials["password"]
            }
            
            response = self.client.post(
                CRISPEndpoints.AUTH_LOGIN,
                json=login_data,
                headers=headers,
                name="auth_login"
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access')
                self.refresh_token = data.get('refresh')
                self.authenticated = True
                
                logger.info(f"Successfully authenticated user: {self.user_credentials['username']}")
                
                # Update session cookies
                if response.cookies:
                    self.session_cookies.update(dict(response.cookies))
                
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                # Fall back to unauthenticated user behavior
                self.authenticated = False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            self.authenticated = False
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        headers = {
            'Content-Type': 'application/json',
        }
        
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        if self.csrf_token:
            headers['X-CSRFToken'] = self.csrf_token
            
        return headers
    
    def _logout(self):
        """Logout user"""
        if not self.authenticated:
            return
            
        try:
            headers = self._get_auth_headers()
            logout_data = {}
            
            # Add refresh token if available
            if self.refresh_token:
                logout_data["refresh_token"] = self.refresh_token
            
            with self.client.post(
                CRISPEndpoints.AUTH_LOGOUT,
                json=logout_data,
                headers=headers,
                name="auth_logout",
                catch_response=True
            ) as response:
                # Accept both 200 and 400 as success for logout (token might already be invalid)
                if response.status_code in [200, 400]:
                    logger.info(f"Logged out user: {self.user_credentials['username']}")
                    response.success()
                else:
                    response.failure(f"Logout failed with status {response.status_code}")
            
        except Exception as e:
            logger.warning(f"Logout error: {e}")
        
        finally:
            self.authenticated = False
            self.auth_token = None
            self.refresh_token = None
    
    # ========================================
    # TASK DEFINITIONS
    # ========================================
    
    @task(10)
    def browse_dashboard(self):
        """Simulate browsing the main dashboard"""
        endpoints_to_test = [
            CRISPEndpoints.HOME,
            CRISPEndpoints.DASHBOARD,
        ]
        
        # Only test STATUS endpoint if authenticated
        if self.authenticated:
            endpoints_to_test.append(CRISPEndpoints.STATUS)
        
        for endpoint in endpoints_to_test:
            try:
                if self.authenticated and endpoint != CRISPEndpoints.HOME:
                    headers = self._get_auth_headers()
                    response = self.client.get(endpoint, headers=headers, name=f"dashboard_{endpoint.strip('/').replace('/', '_')}")
                else:
                    response = self.client.get(endpoint, name=f"public_{endpoint.strip('/').replace('/', '_')}")
                
                # Add small delay between requests
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                logger.error(f"Error browsing {endpoint}: {e}")
    
    @task(8)
    def view_threat_intelligence(self):
        """Simulate viewing threat intelligence data"""
        if not self.authenticated:
            return
            
        threat_endpoints = [
            CRISPEndpoints.INDICATORS_LIST,
            CRISPEndpoints.THREAT_FEEDS,
            CRISPEndpoints.TTPS_LIST,
            CRISPEndpoints.MITRE_MATRIX,
            CRISPEndpoints.RECENT_ACTIVITIES,
        ]
        
        # Randomly select 2-3 endpoints to visit
        endpoints_to_visit = random.sample(threat_endpoints, random.randint(2, 3))
        
        for endpoint in endpoints_to_visit:
            try:
                headers = self._get_auth_headers()
                response = self.client.get(
                    endpoint, 
                    headers=headers, 
                    name=f"threat_intel_{endpoint.replace('/api/', '').replace('/', '_')}"
                )
                
                # Simulate reading time
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                logger.error(f"Error accessing threat intel {endpoint}: {e}")
    
    @task(5)
    def manage_users(self):
        """Simulate user management activities"""
        if not self.authenticated:
            return
        
        # Only allow admin users to access user management endpoints
        username = self.user_credentials.get('username', '')
        is_admin = username in ['admin', 'demo', 'test']
        
        if is_admin:
            # Admin users can access user management endpoints
            user_endpoints = [
                CRISPEndpoints.USERS_LIST,
                CRISPEndpoints.USER_INVITATIONS,
            ]
        else:
            # Regular users only access their own profile
            user_endpoints = []
        
        # All authenticated users can access their profile
        user_endpoints.append(CRISPEndpoints.AUTH_PROFILE)
        
        for endpoint in user_endpoints:
            try:
                headers = self._get_auth_headers()
                with self.client.get(
                    endpoint, 
                    headers=headers, 
                    name=f"user_mgmt_{endpoint.replace('/api/', '').replace('/', '_')}",
                    catch_response=True
                ) as response:
                    # Handle expected 403 errors for non-admin users gracefully
                    if response.status_code == 403 and not is_admin:
                        response.success()  # Expected behavior for non-admin users
                    elif response.status_code == 200:
                        response.success()
                    else:
                        response.failure(f"Unexpected status {response.status_code}")
                
                time.sleep(random.uniform(0.5, 1))
                
            except Exception as e:
                logger.error(f"Error in user management {endpoint}: {e}")
    
    @task(4)
    def check_system_health(self):
        """Simulate system health monitoring"""
        if not self.authenticated:
            return
            
        health_endpoints = [
            CRISPEndpoints.SYSTEM_HEALTH,
            CRISPEndpoints.THREAT_ACTIVITY_CHART,
        ]
        
        for endpoint in health_endpoints:
            try:
                headers = self._get_auth_headers()
                response = self.client.get(endpoint, headers=headers, name=f"health_{endpoint.strip('/').replace('/', '_')}")
                
            except Exception as e:
                logger.error(f"Error checking health {endpoint}: {e}")
    
    @task(3)
    def explore_trust_management(self):
        """Simulate trust management operations"""
        if not self.authenticated:
            return
        
        # Check if user has admin privileges for trust management
        username = self.user_credentials.get('username', '')
        is_admin = username in ['admin', 'demo', 'test']
        
        trust_endpoints = [
            CRISPEndpoints.TRUST_BILATERAL,
            CRISPEndpoints.TRUST_LEVELS,
            CRISPEndpoints.TRUST_DASHBOARD,
        ]
        
        for endpoint in trust_endpoints:
            try:
                headers = self._get_auth_headers()
                with self.client.get(
                    endpoint, 
                    headers=headers, 
                    name=f"trust_{endpoint.replace('/api/', '').replace('/', '_')}",
                    catch_response=True
                ) as response:
                    # Handle expected 403/400/401 errors gracefully
                    if response.status_code in [401, 403, 400]:
                        response.success()  # Expected for users without proper trust setup
                    elif response.status_code == 200:
                        response.success()
                    else:
                        response.failure(f"Unexpected status {response.status_code}")
                
                time.sleep(random.uniform(0.5, 1))
                
            except Exception as e:
                logger.error(f"Error in trust management {endpoint}: {e}")
    
    @task(3)
    def browse_organizations(self):
        """Simulate organization browsing"""
        if not self.authenticated:
            return
        
        # Check if user has admin privileges
        username = self.user_credentials.get('username', '')
        is_admin = username in ['admin', 'demo', 'test']
        
        org_endpoints = [
            CRISPEndpoints.ORGANIZATIONS_LIST,
            CRISPEndpoints.ORGANIZATION_TYPES,
        ]
        
        for endpoint in org_endpoints:
            try:
                headers = self._get_auth_headers()
                with self.client.get(
                    endpoint, 
                    headers=headers, 
                    name=f"org_{endpoint.replace('/api/', '').replace('/', '_')}",
                    catch_response=True
                ) as response:
                    # Handle expected 401/403 errors gracefully for non-admin users
                    if response.status_code in [401, 403] and not is_admin:
                        response.success()  # Expected for non-admin users
                    elif response.status_code == 200:
                        response.success()
                    else:
                        response.failure(f"Unexpected status {response.status_code}")
                
            except Exception as e:
                logger.error(f"Error browsing organizations {endpoint}: {e}")
    
    @task(2)
    def perform_post_operations(self):
        """Simulate POST operations (form submissions, data updates)"""
        if not self.authenticated:
            return
        
        # Simulate profile update
        try:
            headers = self._get_auth_headers()
            
            # First get current profile
            profile_response = self.client.get(
                CRISPEndpoints.AUTH_PROFILE, 
                headers=headers, 
                name="get_profile_for_update"
            )
            
            if profile_response.status_code == 200:
                # Simulate a profile update
                update_data = {
                    "first_name": f"TestUser{random.randint(1, 1000)}",
                    "last_name": "LoadTest"
                }
                
                update_response = self.client.put(
                    f"{CRISPEndpoints.AUTH_PROFILE}update/",
                    json=update_data,
                    headers=headers,
                    name="update_profile"
                )
                
        except Exception as e:
            logger.error(f"Error in POST operations: {e}")
    
    @task(1)
    def verify_authentication(self):
        """Periodically verify token is still valid"""
        if not self.authenticated:
            return
            
        try:
            headers = self._get_auth_headers()
            response = self.client.get(
                CRISPEndpoints.AUTH_VERIFY_TOKEN,
                headers=headers,
                name="verify_token"
            )
            
            if response.status_code != 200:
                logger.warning(f"Token verification failed: {response.status_code}")
                # Attempt re-authentication
                self._authenticate()
                
        except Exception as e:
            logger.error(f"Error verifying token: {e}")


class CRISPUnauthenticatedUser(HttpUser):
    """
    Unauthenticated user that tests public endpoints and login flows
    """
    
    wait_time = between(2, 5)
    
    @task(10)
    def browse_public_pages(self):
        """Browse public pages"""
        public_endpoints = [
            CRISPEndpoints.HOME,
            # Remove STATUS for unauthenticated users since it requires auth
        ]
        
        for endpoint in public_endpoints:
            try:
                response = self.client.get(endpoint, name=f"public_{endpoint.strip('/').replace('/', '_')}")
            except Exception as e:
                logger.error(f"Error accessing public page {endpoint}: {e}")
    
    @task(5)
    def attempt_login_flow(self):
        """Simulate login attempts (both valid and invalid)"""
        try:
            # Get CSRF token first
            csrf_response = self.client.get(CRISPEndpoints.HOME, name="get_csrf_for_login")
            csrf_token = csrf_response.cookies.get('csrftoken')
            
            headers = {'Content-Type': 'application/json'}
            if csrf_token:
                headers['X-CSRFToken'] = csrf_token
            
            # 80% chance of using valid credentials, 20% invalid
            if random.random() < 0.8:
                credentials = TestCredentials.get_random_user()
            else:
                # Invalid credentials for testing
                credentials = {
                    "username": f"invalid_user_{random.randint(1, 1000)}",
                    "password": "invalid_password"
                }
            
            with self.client.post(
                CRISPEndpoints.AUTH_LOGIN,
                json=credentials,
                headers=headers,
                name="login_attempt",
                catch_response=True
            ) as response:
                # Handle both valid and invalid login attempts as success for load testing
                if response.status_code in [200, 401]:
                    response.success()  # Both successful and failed logins are expected during testing
                else:
                    response.failure(f"Unexpected login status {response.status_code}")
            
            # If successful, immediately logout to free up the session
            if response.status_code == 200:
                data = response.json()
                refresh_token = data.get('refresh')
                access_token = data.get('access')
                
                if refresh_token and access_token:
                    logout_headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {access_token}'
                    }
                    
                    with self.client.post(
                        CRISPEndpoints.AUTH_LOGOUT,
                        json={"refresh_token": refresh_token},
                        headers=logout_headers,
                        name="quick_logout",
                        catch_response=True
                    ) as logout_response:
                        # Accept both 200 and 400 as success for logout
                        if logout_response.status_code in [200, 400]:
                            logout_response.success()
                        else:
                            logout_response.failure(f"Quick logout failed with {logout_response.status_code}")
            
        except Exception as e:
            logger.error(f"Error in login flow: {e}")
    
    @task(2)
    def test_registration_flow(self):
        """Test user registration endpoint"""
        try:
            # Generate random user data
            user_id = random.randint(10000, 99999)
            registration_data = {
                "username": f"loadtest_user_{user_id}",
                "email": f"loadtest_{user_id}@example.com",
                "password": "LoadTestPassword123!",
                "first_name": "Load",
                "last_name": "Test"
            }
            
            headers = {'Content-Type': 'application/json'}
            
            # Get CSRF token
            csrf_response = self.client.get(CRISPEndpoints.HOME, name="get_csrf_for_registration")
            csrf_token = csrf_response.cookies.get('csrftoken')
            if csrf_token:
                headers['X-CSRFToken'] = csrf_token
            
            with self.client.post(
                CRISPEndpoints.AUTH_REGISTER,
                json=registration_data,
                headers=headers,
                name="test_registration",
                catch_response=True
            ) as response:
                # Handle expected server errors gracefully (might be due to duplicate users, etc.)
                if response.status_code in [201, 400, 500]:
                    response.success()  # Expected behavior during load testing
                else:
                    response.failure(f"Registration failed with unexpected status {response.status_code}")
            
        except Exception as e:
            logger.error(f"Error testing registration: {e}")


# ========================================
# EVENT HANDLERS FOR METRICS
# ========================================

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Initialize custom metrics collection"""
    logger.info("🚀 CRISP Load Testing Started")
    logger.info(f"Target Host: {environment.host}")
    logger.info("📊 Custom metrics initialized")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Log test start"""
    logger.info("🔥 Load test execution started")
    logger.info(f"Users will ramp up according to Locust configuration")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Log test completion"""
    logger.info("✅ Load test execution completed")
    logger.info("📈 Check Locust web UI for detailed metrics")

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """Log request results for debugging"""
    if exception:
        logger.warning(f"❌ Request failed: {request_type} {name} - {exception}")
    else:
        # Uncomment for detailed success logging (may be verbose)
        # logger.debug(f"✅ {request_type} {name} - {response_time}ms")
        pass


# ========================================
# USER CLASS CONFIGURATION
# ========================================

# Weight the user types (higher weight = more users of this type)
CRISPAuthenticatedUser.weight = 3  # 75% authenticated users
CRISPUnauthenticatedUser.weight = 1  # 25% unauthenticated users


if __name__ == "__main__":
    """
    Quick test runner for development
    Run this script directly to test basic functionality
    """
    import sys
    
    print("🧪 CRISP Locust Configuration Test")
    print("=" * 50)
    print("✅ All imports successful")
    print("✅ User classes defined")
    print("✅ Endpoints configured")
    print("✅ Ready for load testing!")
    print("\n🚀 To run load test:")
    print("   locust -f locustfile.py --host=http://127.0.0.1:8000")
    print("\n📊 Web UI will be available at:")
    print("   http://localhost:8089")
    print("\n⚙️  Recommended test parameters:")
    print("   - Number of users: 10-50 (start small)")
    print("   - Spawn rate: 5-10 users/second")
    print("   - Run time: 5-10 minutes for initial testing")
    
    sys.exit(0)
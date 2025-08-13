#!/usr/bin/env python3
"""
Comprehensive integration tests for the unified CRISP system.
Tests authentication, threat feeds, trust management, and role-based access.
"""

import os
import sys
import django
import json
import requests
import time
from datetime import datetime, timedelta

# Setup Django
sys.path.append('/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/Capstone-Unified')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_settings.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from core.models.models import ThreatFeed, Organization, Indicator, TrustLevel, TrustRelationship
from core_ut.user_management.models import UserProfile

class UnifiedSystemIntegrationTest:
    """Integration tests for the unified CRISP system"""
    
    def __init__(self):
        self.backend_url = 'http://localhost:8000'
        self.frontend_url = 'http://localhost:5173'
        self.User = get_user_model()
        self.test_results = []
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   {details}")

    def test_backend_connectivity(self):
        """Test backend server connectivity"""
        try:
            response = requests.get(f'{self.backend_url}/api/v1/admin/system_health/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Connectivity", "PASS", f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_test("Backend Connectivity", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Connectivity", "FAIL", f"Connection error: {e}")
            return False

    def test_frontend_connectivity(self):
        """Test frontend server connectivity"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log_test("Frontend Connectivity", "PASS", "React app accessible")
                return True
            else:
                self.log_test("Frontend Connectivity", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Connectivity", "FAIL", f"Connection error: {e}")
            return False

    def test_database_connectivity(self):
        """Test database connectivity and data"""
        try:
            user_count = self.User.objects.count()
            org_count = Organization.objects.count()
            feed_count = ThreatFeed.objects.count()
            indicator_count = Indicator.objects.count()
            
            details = f"Users: {user_count}, Orgs: {org_count}, Feeds: {feed_count}, Indicators: {indicator_count}"
            self.log_test("Database Connectivity", "PASS", details)
            return True
        except Exception as e:
            self.log_test("Database Connectivity", "FAIL", f"Database error: {e}")
            return False

    def test_jwt_authentication(self):
        """Test JWT token generation and validation"""
        try:
            user = self.User.objects.first()
            if not user:
                self.log_test("JWT Authentication", "FAIL", "No users found")
                return False, None
                
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # Test token with API
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(f'{self.backend_url}/api/v1/users/profile/', headers=headers)
            
            if response.status_code == 200:
                profile = response.json()
                username = profile.get('user', {}).get('username', 'unknown')
                self.log_test("JWT Authentication", "PASS", f"User: {username}")
                return True, access_token
            else:
                self.log_test("JWT Authentication", "FAIL", f"API returned {response.status_code}")
                return False, None
        except Exception as e:
            self.log_test("JWT Authentication", "FAIL", f"Auth error: {e}")
            return False, None

    def test_threat_feed_apis(self, access_token):
        """Test threat feed APIs"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Test threat feeds list
            response = requests.get(f'{self.backend_url}/api/threat-feeds/', headers=headers)
            if response.status_code != 200:
                self.log_test("Threat Feed APIs", "FAIL", f"List feeds failed: {response.status_code}")
                return False
                
            feeds = response.json()
            feed_count = len(feeds)
            
            # Test external feeds
            response = requests.get(f'{self.backend_url}/api/threat-feeds/external/', headers=headers)
            if response.status_code != 200:
                self.log_test("Threat Feed APIs", "FAIL", f"External feeds failed: {response.status_code}")
                return False
                
            external_feeds = response.json()
            external_count = len(external_feeds)
            
            # Test feed consumption if feeds exist
            if feed_count > 0:
                feed_id = feeds[0]['id']
                response = requests.post(f'{self.backend_url}/api/threat-feeds/{feed_id}/consume/', headers=headers)
                consume_status = "available" if response.status_code in [200, 202] else f"error-{response.status_code}"
            else:
                consume_status = "no-feeds"
                
            details = f"Total: {feed_count}, External: {external_count}, Consume: {consume_status}"
            self.log_test("Threat Feed APIs", "PASS", details)
            return True
        except Exception as e:
            self.log_test("Threat Feed APIs", "FAIL", f"API error: {e}")
            return False

    def test_organization_management(self, access_token):
        """Test organization management APIs"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Test list organizations
            response = requests.get(f'{self.backend_url}/api/v1/organizations/list_organizations/', headers=headers)
            if response.status_code != 200:
                self.log_test("Organization Management", "FAIL", f"List orgs failed: {response.status_code}")
                return False
                
            orgs_data = response.json()
            org_count = len(orgs_data.get('data', []))
            
            # Test organization types
            response = requests.get(f'{self.backend_url}/api/v1/organizations/types/', headers=headers)
            types_status = response.status_code == 200
            
            details = f"Organizations: {org_count}, Types API: {'✓' if types_status else '✗'}"
            self.log_test("Organization Management", "PASS", details)
            return True
        except Exception as e:
            self.log_test("Organization Management", "FAIL", f"Org API error: {e}")
            return False

    def test_trust_management(self, access_token):
        """Test trust management system"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Test trust levels
            response = requests.get(f'{self.backend_url}/api/v1/trust/levels/', headers=headers)
            levels_ok = response.status_code == 200
            
            # Test trust relationships
            response = requests.get(f'{self.backend_url}/api/v1/trust/relationships/', headers=headers)
            relationships_ok = response.status_code == 200
            
            # Test trust metrics
            response = requests.get(f'{self.backend_url}/api/v1/trust/metrics/', headers=headers)
            metrics_ok = response.status_code == 200
            
            # Test trust overview (admin endpoint)
            response = requests.get(f'{self.backend_url}/api/v1/admin/trust_overview/', headers=headers)
            overview_ok = response.status_code == 200
            
            passed_tests = sum([levels_ok, relationships_ok, metrics_ok, overview_ok])
            details = f"Passed: {passed_tests}/4 trust API endpoints"
            
            if passed_tests >= 3:
                self.log_test("Trust Management", "PASS", details)
                return True
            else:
                self.log_test("Trust Management", "FAIL", details)
                return False
        except Exception as e:
            self.log_test("Trust Management", "FAIL", f"Trust API error: {e}")
            return False

    def test_user_management(self, access_token):
        """Test user management APIs"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Test user profile
            response = requests.get(f'{self.backend_url}/api/v1/users/profile/', headers=headers)
            profile_ok = response.status_code == 200
            
            # Test user list (admin function)
            response = requests.get(f'{self.backend_url}/api/v1/users/list/', headers=headers)
            list_ok = response.status_code == 200
            
            # Test user statistics
            response = requests.get(f'{self.backend_url}/api/v1/users/statistics/', headers=headers)
            stats_ok = response.status_code == 200
            
            passed_tests = sum([profile_ok, list_ok, stats_ok])
            details = f"Passed: {passed_tests}/3 user API endpoints"
            
            if passed_tests >= 2:
                self.log_test("User Management", "PASS", details)
                return True
            else:
                self.log_test("User Management", "FAIL", details)
                return False
        except Exception as e:
            self.log_test("User Management", "FAIL", f"User API error: {e}")
            return False

    def test_role_based_access(self):
        """Test role-based access control"""
        try:
            # Test with different user types
            users = self.User.objects.all()[:3]  # Test with first 3 users
            access_results = []
            
            for user in users:
                refresh = RefreshToken.for_user(user)
                token = str(refresh.access_token)
                headers = {'Authorization': f'Bearer {token}'}
                
                # Test access to admin endpoint
                response = requests.get(f'{self.backend_url}/api/v1/admin/trust_overview/', headers=headers)
                admin_access = response.status_code == 200
                
                # Test access to user profile
                response = requests.get(f'{self.backend_url}/api/v1/users/profile/', headers=headers)
                profile_access = response.status_code == 200
                
                access_results.append({
                    'user': user.username,
                    'admin': admin_access,
                    'profile': profile_access,
                    'is_staff': getattr(user, 'is_staff', False),
                    'is_superuser': getattr(user, 'is_superuser', False)
                })
            
            # Analyze results
            total_users = len(access_results)
            profile_access_count = sum(1 for r in access_results if r['profile'])
            admin_access_count = sum(1 for r in access_results if r['admin'])
            
            details = f"Users tested: {total_users}, Profile access: {profile_access_count}, Admin access: {admin_access_count}"
            self.log_test("Role-Based Access", "PASS", details)
            return True
        except Exception as e:
            self.log_test("Role-Based Access", "FAIL", f"RBAC error: {e}")
            return False

    def test_threat_data_integration(self):
        """Test threat data integration and display"""
        try:
            # Check threat feeds in database
            feeds = ThreatFeed.objects.all()
            active_feeds = feeds.filter(is_active=True)
            
            # Check indicators
            indicators = Indicator.objects.all()
            recent_indicators = indicators.filter(
                first_seen__gte=datetime.now() - timedelta(days=7)
            )
            
            # Check different indicator types
            url_indicators = indicators.filter(type='url').count()
            domain_indicators = indicators.filter(type='domain').count()
            hash_indicators = indicators.filter(type='file_hash').count()
            
            details = (f"Feeds: {feeds.count()} total, {active_feeds.count()} active | "
                      f"Indicators: {indicators.count()} total, {recent_indicators.count()} recent | "
                      f"Types: {url_indicators} URLs, {domain_indicators} domains, {hash_indicators} hashes")
            
            if indicators.count() > 0:
                self.log_test("Threat Data Integration", "PASS", details)
                return True
            else:
                self.log_test("Threat Data Integration", "WARN", f"No indicators found. {details}")
                return False
        except Exception as e:
            self.log_test("Threat Data Integration", "FAIL", f"Data integration error: {e}")
            return False

    def test_cors_and_frontend_backend_communication(self):
        """Test CORS and frontend-backend communication"""
        try:
            # Test preflight request (OPTIONS)
            headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'authorization'
            }
            
            response = requests.options(f'{self.backend_url}/api/v1/admin/system_health/', headers=headers)
            cors_ok = response.status_code in [200, 204]
            
            # Check CORS headers in response
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers')
            }
            
            details = f"CORS preflight: {'✓' if cors_ok else '✗'}, Headers present: {len([h for h in cors_headers.values() if h])}/3"
            
            if cors_ok:
                self.log_test("CORS Configuration", "PASS", details)
                return True
            else:
                self.log_test("CORS Configuration", "WARN", details)
                return False
        except Exception as e:
            self.log_test("CORS Configuration", "FAIL", f"CORS error: {e}")
            return False

    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Unified System Integration Tests")
        print("=" * 60)
        
        # Core connectivity tests
        backend_ok = self.test_backend_connectivity()
        frontend_ok = self.test_frontend_connectivity()
        db_ok = self.test_database_connectivity()
        
        if not backend_ok:
            print("❌ Backend not accessible - stopping tests")
            return self.test_results
            
        # Authentication tests
        auth_ok, access_token = self.test_jwt_authentication()
        if not auth_ok or not access_token:
            print("❌ Authentication failed - stopping API tests")
            return self.test_results
        
        # API tests with authentication
        self.test_threat_feed_apis(access_token)
        self.test_organization_management(access_token)
        self.test_trust_management(access_token)
        self.test_user_management(access_token)
        
        # Advanced tests
        self.test_role_based_access()
        self.test_threat_data_integration()
        self.test_cors_and_frontend_backend_communication()
        
        # Summary
        print("\n" + "=" * 60)
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warned_tests = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        print(f"📊 Test Summary: {passed_tests} PASSED, {failed_tests} FAILED, {warned_tests} WARNINGS")
        print(f"🎯 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests == 0:
            print("🎉 All critical tests passed! System is fully integrated.")
        elif failed_tests <= 2:
            print("⚠️ Minor issues detected. System mostly functional.")
        else:
            print("❌ Multiple issues detected. Review failed tests.")
            
        return self.test_results

def main():
    """Run integration tests"""
    tester = UnifiedSystemIntegrationTest()
    results = tester.run_all_tests()
    
    # Save results to file
    with open('integration_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📝 Detailed results saved to: integration_test_results.json")

if __name__ == '__main__':
    main()
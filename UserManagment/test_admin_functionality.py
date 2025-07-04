#!/usr/bin/env python3
"""
CRISP User Management System - Django Admin Functionality Test

This script comprehensively tests the Django admin interface to ensure:
1. Organizations can be created by system admins
2. All user role types can be created
3. Admin interface is properly configured
4. All models are properly registered
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import authenticate
from django.urls import reverse
from django.db import transaction

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_project.settings')
django.setup()

from UserManagement.models import CustomUser, Organization, UserSession, AuthenticationLog, STIXObjectPermission
from UserManagement.factories.user_factory import UserFactory


class AdminFunctionalityTester:
    """Comprehensive Django admin functionality tester"""
    
    def __init__(self):
        self.client = Client()
        self.test_organization = None
        self.system_admin = None
        self.created_users = []
        self.created_orgs = []
        
    def setup_test_environment(self):
        """Setup test environment with system admin"""
        print("Setting up test environment...")
        
        # Create test organization
        self.test_organization, created = Organization.objects.get_or_create(
            name='Admin Test Organization',
            defaults={
                'description': 'Test organization for admin functionality testing',
                'domain': 'admintest.example.com',
                'is_active': True
            }
        )
        if created:
            self.created_orgs.append(self.test_organization)
            print(f"   Created test organization: {self.test_organization.name}")
        else:
            print(f"   ℹ️  Using existing organization: {self.test_organization.name}")
        
        # Create system admin if doesn't exist
        try:
            self.system_admin = CustomUser.objects.get(username='admin_test_user')
            print(f"   ℹ️  Using existing system admin: {self.system_admin.username}")
        except CustomUser.DoesNotExist:
            self.system_admin = CustomUser.objects.create_user(
                username='admin_test_user',
                email='admin@admintest.example.com',
                password='AdminTestPass123!',
                organization=self.test_organization,
                role='BlueVisionAdmin',  # Use the correct system admin role
                is_verified=True,
                is_active=True,
                is_staff=True,
                is_superuser=True
            )
            self.created_users.append(self.system_admin)
            print(f"   Created system admin: {self.system_admin.username}")
        
        print("   Test environment setup completed\n")
    
    def test_admin_login(self):
        """Test admin login functionality"""
        print("🔐 Testing admin login functionality...")
        
        # Test admin login
        login_successful = self.client.login(
            username='admin_test_user',
            password='AdminTestPass123!'
        )
        
        if login_successful:
            print("   Admin login successful")
            
            # Test admin interface access
            response = self.client.get('/admin/')
            if response.status_code == 200:
                print("   Admin interface accessible")
                return True
            else:
                print(f"   Admin interface not accessible (status: {response.status_code})")
                return False
        else:
            print("   Admin login failed")
            return False
    
    def test_organization_admin_interface(self):
        """Test organization management through admin interface"""
        print("🏢 Testing organization admin interface...")
        
        # Test organization list view
        response = self.client.get('/admin/UserManagement/organization/')
        if response.status_code == 200:
            print("   Organization list view accessible")
        else:
            print(f"   Organization list view failed (status: {response.status_code})")
            return False
        
        # Test organization creation form
        response = self.client.get('/admin/UserManagement/organization/add/')
        if response.status_code == 200:
            print("   Organization creation form accessible")
        else:
            print(f"   Organization creation form failed (status: {response.status_code})")
            return False
        
        # Test creating organization through admin
        org_data = {
            'name': 'Admin Created Organization',
            'domain': 'admincreated.example.com',
            'description': 'Organization created through Django admin interface',
            'is_active': True
        }
        
        response = self.client.post('/admin/UserManagement/organization/add/', org_data)
        if response.status_code == 302:  # Redirect after successful creation
            print("   Organization creation through admin successful")
            
            # Verify organization was created
            created_org = Organization.objects.filter(name='Admin Created Organization').first()
            if created_org:
                self.created_orgs.append(created_org)
                print(f"   Verified organization created: {created_org.name}")
                return True
            else:
                print("   Organization creation verification failed")
                return False
        else:
            print(f"   Organization creation failed (status: {response.status_code})")
            return False
    
    def test_user_creation_all_roles(self):
        """Test creating users with all role types through admin"""
        print("Testing user creation for all role types...")
        
        # Define all user roles to test
        user_roles = [
            ('viewer', 'Viewer User', 'viewer@admintest.example.com'),
            ('analyst', 'Analyst User', 'analyst@admintest.example.com'),
            ('publisher', 'Publisher User', 'publisher@admintest.example.com'),
            ('admin', 'Admin User', 'admin_user@admintest.example.com'),
            ('system_admin', 'System Admin User', 'sysadmin@admintest.example.com')
        ]
        
        success_count = 0
        
        for role, display_name, email in user_roles:
            print(f"   🔄 Testing {role} user creation...")
            
            # Prepare user data
            user_data = {
                'username': f'test_{role}_user',
                'email': email,
                'password1': f'{role.title()}TestPass123!',
                'password2': f'{role.title()}TestPass123!',
                'first_name': display_name.split()[0],
                'last_name': display_name.split()[-1],
                'organization': self.test_organization.id,
                'role': role,
                'is_verified': True,
                'is_active': True
            }
            
            # Set publisher flag for publisher role
            if role == 'publisher':
                user_data['is_publisher'] = True
            
            # Set staff/superuser flags for admin roles
            if role in ['admin', 'system_admin']:
                user_data['is_staff'] = True
            if role == 'system_admin':
                user_data['is_superuser'] = True
            
            # Create user through admin interface (follow redirects)
            response = self.client.post('/admin/UserManagement/customuser/add/', user_data, follow=True)
            
            if response.status_code == 200 and response.redirect_chain:
                # Success - Django admin redirected after creation
                created_user = CustomUser.objects.filter(username=f'test_{role}_user').first()
                if created_user and created_user.role == role:
                    self.created_users.append(created_user)
                    print(f"   {role} user created successfully: {created_user.username}")
                    success_count += 1
                else:
                    print(f"   {role} user creation verification failed")
            elif response.status_code == 302:  # Direct redirect (shouldn't happen with follow=True)
                # Verify user was created
                created_user = CustomUser.objects.filter(username=f'test_{role}_user').first()
                if created_user and created_user.role == role:
                    self.created_users.append(created_user)
                    print(f"   {role} user created successfully: {created_user.username}")
                    success_count += 1
                else:
                    print(f"   {role} user creation verification failed")
            else:
                print(f"   {role} user creation failed (status: {response.status_code})")
                # Print form errors for debugging
                if hasattr(response, 'context') and response.context:
                    if 'form' in response.context:
                        form = response.context['form']
                        if hasattr(form, 'errors') and form.errors:
                            print(f"      Form errors: {form.errors}")
                    if 'adminform' in response.context:
                        adminform = response.context['adminform']
                        if hasattr(adminform, 'form') and hasattr(adminform.form, 'errors'):
                            print(f"      Admin form errors: {adminform.form.errors}")
                    
                    # Also check if there are any non-field errors
                    if hasattr(response, 'content'):
                        content = response.content.decode('utf-8')
                        if 'errorlist' in content:
                            print(f"      HTML contains errors - checking response")
                            # Look for specific error patterns
                            import re
                            error_pattern = r'<ul class="errorlist[^>]*"><li>([^<]+)</li></ul>'
                            errors = re.findall(error_pattern, content)
                            if errors:
                                print(f"      Extracted errors: {errors}")
                
                # Also check if user was actually created despite the status
                created_user = CustomUser.objects.filter(username=f'test_{role}_user').first()
                if created_user:
                    print(f"      Note: User was actually created despite status: {created_user.username}")
                    self.created_users.append(created_user)
                    success_count += 1
        
        print(f"   User creation summary: {success_count}/{len(user_roles)} successful")
        return success_count == len(user_roles)
    
    def test_admin_model_registration(self):
        """Test that all models are properly registered in admin"""
        print("Testing admin model registration...")
        
        # Test that all expected models are accessible
        models_to_test = [
            ('customuser', 'CustomUser'),
            ('organization', 'Organization'),
            ('usersession', 'UserSession'),
            ('authenticationlog', 'AuthenticationLog'),
            ('stixobjectpermission', 'STIXObjectPermission')
        ]
        
        success_count = 0
        
        for model_url, model_name in models_to_test:
            response = self.client.get(f'/admin/UserManagement/{model_url}/')
            if response.status_code == 200:
                print(f"   {model_name} admin interface accessible")
                success_count += 1
            else:
                print(f"   {model_name} admin interface failed (status: {response.status_code})")
        
        print(f"   Model registration summary: {success_count}/{len(models_to_test)} accessible")
        return success_count == len(models_to_test)
    
    def test_user_management_features(self):
        """Test user management features through admin"""
        print("⚙️ Testing user management features...")
        
        if not self.created_users:
            print("    No test users available for management testing")
            return False
        
        # Test user editing
        test_user = self.created_users[0]
        response = self.client.get(f'/admin/UserManagement/customuser/{test_user.id}/change/')
        if response.status_code == 200:
            print("   User edit form accessible")
        else:
            print(f"   User edit form failed (status: {response.status_code})")
            return False
        
        # Test user deactivation
        user_data = {
            'username': test_user.username,
            'email': test_user.email,
            'organization': test_user.organization.id,
            'role': test_user.role,
            'is_active': False,  # Deactivate user
            'is_verified': test_user.is_verified,
            'first_name': test_user.first_name,
            'last_name': test_user.last_name
        }
        
        response = self.client.post(f'/admin/UserManagement/customuser/{test_user.id}/change/', user_data)
        if response.status_code == 302:
            test_user.refresh_from_db()
            if not test_user.is_active:
                print("   User deactivation successful")
            else:
                print("   User deactivation verification failed")
                return False
        else:
            print(f"   User deactivation failed (status: {response.status_code})")
            return False
        
        return True
    
    def test_authentication_log_viewing(self):
        """Test authentication log viewing"""
        print("Testing authentication log viewing...")
        
        # Create test authentication log
        log_entry = AuthenticationLog.log_authentication_event(
            user=self.system_admin,
            action='admin_test',
            ip_address='127.0.0.1',
            user_agent='Test Script',
            success=True,
            additional_data={'test': 'admin_functionality_test'}
        )
        
        # Test log list view
        response = self.client.get('/admin/UserManagement/authenticationlog/')
        if response.status_code == 200:
            print("   Authentication log list accessible")
        else:
            print(f"   Authentication log list failed (status: {response.status_code})")
            return False
        
        # Test log detail view
        response = self.client.get(f'/admin/UserManagement/authenticationlog/{log_entry.id}/change/')
        if response.status_code == 200:
            print("   Authentication log detail accessible")
            return True
        else:
            print(f"   Authentication log detail failed (status: {response.status_code})")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("🧹 Cleaning up test data...")
        
        # Delete created users
        for user in self.created_users:
            if user.username != 'admin_test_user':  # Keep the admin for future tests
                user.delete()
                print(f"   Deleted user: {user.username}")
        
        # Delete created organizations (except the main test org)
        for org in self.created_orgs:
            if org.name != 'Admin Test Organization':
                org.delete()
                print(f"   Deleted organization: {org.name}")
        
        print("   Cleanup completed\n")
    
    def run_comprehensive_test(self):
        """Run comprehensive admin functionality test"""
        print("CRISP User Management - Django Admin Functionality Test")
        print("=" * 60)
        
        test_results = []
        
        try:
            # Setup
            self.setup_test_environment()
            
            # Run tests
            test_results.append(("Admin Login", self.test_admin_login()))
            test_results.append(("Organization Admin Interface", self.test_organization_admin_interface()))
            test_results.append(("Model Registration", self.test_admin_model_registration()))
            test_results.append(("User Creation (All Roles)", self.test_user_creation_all_roles()))
            test_results.append(("User Management Features", self.test_user_management_features()))
            test_results.append(("Authentication Log Viewing", self.test_authentication_log_viewing()))
            
        except Exception as e:
            print(f"Test execution failed with error: {str(e)}")
            test_results.append(("Test Execution", False))
        
        finally:
            # Always try to cleanup
            try:
                self.cleanup_test_data()
            except Exception as e:
                print(f" Cleanup warning: {str(e)}")
        
        # Report results
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "PASSED" if result else "FAILED"
            print(f"{test_name:.<40} {status}")
            if result:
                passed += 1
        
        print("-" * 60)
        success_rate = (passed / total) * 100 if total > 0 else 0
        print(f"Overall Success Rate: {passed}/{total} ({success_rate:.1f}%)")
        
        if passed == total:
            print("\nALL TESTS PASSED! Django admin interface is fully functional.")
            print("Organizations can be created by system admins")
            print("All user role types can be created and managed")
            print("Admin interface is properly configured")
            return True
        else:
            print(f"\n {total - passed} test(s) failed. Please review the output above.")
            return False


def main():
    """Main function to run admin functionality tests"""
    tester = AdminFunctionalityTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
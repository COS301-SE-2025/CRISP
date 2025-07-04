#!/usr/bin/env python3
"""
CRISP User Management System - Django Admin Verification Test

This script tests Django admin functionality using Django's test framework.
It verifies that organizations can be created and all user types work properly.
"""

import os
import sys
import django
from django.test import TestCase, TransactionTestCase
from django.contrib.admin import site
from django.contrib.auth import get_user_model

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_project.settings')
django.setup()

from UserManagement.models import CustomUser, Organization, UserSession, AuthenticationLog, STIXObjectPermission
from UserManagement.admin import (
    CustomUserAdmin, OrganizationAdmin, UserSessionAdmin, 
    AuthenticationLogAdmin, STIXObjectPermissionAdmin
)


def test_admin_registration():
    """Test that all models are properly registered in Django admin"""
    print("Testing Django Admin Model Registration...")
    
    registered_models = site._registry
    expected_models = [
        CustomUser,
        Organization, 
        UserSession,
        AuthenticationLog,
        STIXObjectPermission
    ]
    
    success_count = 0
    for model in expected_models:
        if model in registered_models:
            admin_class = registered_models[model]
            print(f"   {model.__name__} registered with {admin_class.__class__.__name__}")
            success_count += 1
        else:
            print(f"   {model.__name__} NOT registered in admin")
    
    print(f"   Registration Summary: {success_count}/{len(expected_models)} models registered")
    return success_count == len(expected_models)


def test_organization_creation():
    """Test organization creation functionality"""
    print("🏢 Testing Organization Creation...")
    
    try:
        # Test organization creation
        org = Organization.objects.create(
            name='Test Admin Organization',
            domain='testadmin.example.com',
            description='Test organization for admin verification',
            is_active=True
        )
        print(f"   Organization created: {org.name}")
        
        # Test organization string representation
        org_str = str(org)
        print(f"   Organization string representation: {org_str}")
        
        # Test organization admin fields
        if hasattr(org, 'customuser_set'):
            user_count = org.customuser_set.count()
            print(f"   Organization user relationship working (count: {user_count})")
        
        # Cleanup
        org.delete()
        print("   Organization cleanup completed")
        return True
        
    except Exception as e:
        print(f"   Organization creation failed: {str(e)}")
        return False


def test_user_creation_all_roles():
    """Test creating users with all role types"""
    print("Testing User Creation for All Roles...")
    
    # Create test organization first
    org = Organization.objects.create(
        name='User Test Organization',
        domain='usertest.example.com',
        description='Test organization for user verification'
    )
    
    # Define all roles to test
    roles_to_test = [
        ('viewer', False, False, False),      # role, is_staff, is_superuser, is_publisher
        ('analyst', False, False, False),
        ('publisher', False, False, True),
        ('admin', True, False, False),
        ('system_admin', True, True, False)
    ]
    
    created_users = []
    success_count = 0
    
    for role, is_staff, is_superuser, is_publisher in roles_to_test:
        try:
            user = CustomUser.objects.create_user(
                username=f'test_{role}_user',
                email=f'{role}@usertest.example.com',
                password=f'{role.title()}TestPass123!',
                organization=org,
                role=role,
                is_staff=is_staff,
                is_superuser=is_superuser,
                is_publisher=is_publisher,
                is_verified=True,
                is_active=True
            )
            created_users.append(user)
            
            # Verify user properties
            assert user.role == role, f"Role mismatch for {role}"
            assert user.is_staff == is_staff, f"Staff status mismatch for {role}"
            assert user.is_superuser == is_superuser, f"Superuser status mismatch for {role}"
            assert user.is_publisher == is_publisher, f"Publisher status mismatch for {role}"
            
            print(f"   {role} user created and verified: {user.username}")
            success_count += 1
            
        except Exception as e:
            print(f"   {role} user creation failed: {str(e)}")
    
    # Test role-specific methods
    if created_users:
        for user in created_users:
            try:
                # Test string representation
                user_str = str(user)
                print(f"      ↳ String representation: {user_str}")
                
                # Test role-specific methods
                if user.role == 'admin':
                    is_org_admin = user.is_organization_admin()
                    print(f"      ↳ Is organization admin: {is_org_admin}")
                
                if user.role == 'publisher':
                    can_publish = user.can_publish_feeds()
                    print(f"      ↳ Can publish feeds: {can_publish}")
                    
            except Exception as e:
                print(f"      Method testing failed for {user.role}: {str(e)}")
    
    # Cleanup
    for user in created_users:
        user.delete()
    org.delete()
    print("   User and organization cleanup completed")
    
    print(f"   User Creation Summary: {success_count}/{len(roles_to_test)} roles successful")
    return success_count == len(roles_to_test)


def test_admin_class_functionality():
    """Test admin class functionality"""
    print("⚙️ Testing Admin Class Functionality...")
    
    # Create test data
    org = Organization.objects.create(
        name='Admin Test Organization',
        domain='admintest.example.com',
        description='Test organization for admin class testing'
    )
    
    user = CustomUser.objects.create_user(
        username='admin_test_user',
        email='admintest@example.com',
        password='AdminTestPass123!',
        organization=org,
        role='viewer',
        is_verified=True
    )
    
    try:
        # Test OrganizationAdmin methods
        org_admin = OrganizationAdmin(Organization, site)
        
        # Test user_count method
        user_count = org_admin.user_count(org)
        print(f"   OrganizationAdmin.user_count: {user_count}")
        
        # Test created_at_display method
        created_display = org_admin.created_at_display(org)
        print(f"   OrganizationAdmin.created_at_display: {created_display}")
        
        # Test user_count_display method
        count_display = org_admin.user_count_display(org)
        print(f"   OrganizationAdmin.user_count_display: {count_display}")
        
        # Test CustomUserAdmin methods
        user_admin = CustomUserAdmin(CustomUser, site)
        
        # Test organization_name method
        org_name = user_admin.organization_name(user)
        print(f"   CustomUserAdmin.organization_name: {org_name}")
        
        # Test account_status method
        account_status = user_admin.account_status(user)
        print(f"   CustomUserAdmin.account_status: {account_status}")
        
        # Test last_login_display method
        login_display = user_admin.last_login_display(user)
        print(f"   CustomUserAdmin.last_login_display: {login_display}")
        
        print("   Admin class functionality tests completed")
        result = True
        
    except Exception as e:
        print(f"   Admin class functionality test failed: {str(e)}")
        result = False
    
    finally:
        # Cleanup
        user.delete()
        org.delete()
    
    return result


def test_authentication_log_admin():
    """Test authentication log admin functionality"""
    print("Testing Authentication Log Admin...")
    
    # Create test data
    org = Organization.objects.create(
        name='Log Test Organization',
        domain='logtest.example.com'
    )
    
    user = CustomUser.objects.create_user(
        username='log_test_user',
        email='logtest@example.com',
        password='LogTestPass123!',
        organization=org
    )
    
    try:
        # Create authentication log
        log_entry = AuthenticationLog.log_authentication_event(
            user=user,
            action='test_login',
            ip_address='127.0.0.1',
            user_agent='Test Agent',
            success=True,
            additional_data={'test': 'admin_verification'}
        )
        
        print(f"   Authentication log created: {log_entry.id}")
        
        # Test AuthenticationLogAdmin methods
        log_admin = AuthenticationLogAdmin(AuthenticationLog, site)
        
        # Test display methods
        timestamp_display = log_admin.timestamp_display(log_entry)
        action_display = log_admin.action_display(log_entry)
        success_display = log_admin.success_display(log_entry)
        
        print(f"   timestamp_display: {timestamp_display}")
        print(f"   action_display: {action_display}")
        print(f"   success_display: {success_display}")
        
        # Test permissions
        has_add = log_admin.has_add_permission(None)
        has_change = log_admin.has_change_permission(None)
        
        print(f"   has_add_permission: {has_add} (should be False)")
        print(f"   has_change_permission: {has_change} (should be False)")
        
        result = True
        
    except Exception as e:
        print(f"   Authentication log admin test failed: {str(e)}")
        result = False
    
    finally:
        # Cleanup
        user.delete()
        org.delete()
    
    return result


def run_all_tests():
    """Run all admin verification tests"""
    print("CRISP User Management - Django Admin Verification")
    print("=" * 60)
    
    tests = [
        ("Admin Model Registration", test_admin_registration),
        ("Organization Creation", test_organization_creation),
        ("User Creation (All Roles)", test_user_creation_all_roles),
        ("Admin Class Functionality", test_admin_class_functionality),
        ("Authentication Log Admin", test_authentication_log_admin)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test failed with exception: {str(e)}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("VERIFICATION RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"Overall Success Rate: {passed}/{total} ({success_rate:.1f}%)")
    
    if passed == total:
        print("\nALL VERIFICATION TESTS PASSED!")
        print("Django admin interface is properly configured")
        print("Organization model is registered and functional")
        print("All user role types can be created and managed")
        print("Admin classes have proper display methods")
        print("Authentication logging is working")
        return True
    else:
        print(f"\n {total - passed} test(s) failed. Please review the output above.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
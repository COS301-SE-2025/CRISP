#!/usr/bin/env python3
"""
Test script to verify that all role updates are working correctly
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
django.setup()

from UserManagement.models import CustomUser, Organization, USER_ROLE_CHOICES
from UserManagement.permissions import IsSystemAdmin, IsOrganizationAdmin, IsPublisher
from UserManagement.factories.user_factory import UserFactory
from django.test import RequestFactory

def test_role_updates():
    """Test that all role updates are working correctly"""
    
    print("Testing Role Structure Updates")
    print("=" * 50)
    
    # Test 1: Check USER_ROLE_CHOICES
    print("1. Testing USER_ROLE_CHOICES...")
    expected_roles = ['viewer', 'publisher', 'BlueVisionAdmin']
    actual_roles = [choice[0] for choice in USER_ROLE_CHOICES]
    
    print(f"   Expected roles: {expected_roles}")
    print(f"   Actual roles: {actual_roles}")
    
    if set(actual_roles) == set(expected_roles):
        print("   USER_ROLE_CHOICES correctly updated")
    else:
        print("   USER_ROLE_CHOICES not updated correctly")
        return False
    
    # Test 2: Create test organization
    print("\n2. Creating test organization...")
    org, created = Organization.objects.get_or_create(
        name='Test Role Organization',
        defaults={
            'description': 'Test organization for role testing',
            'domain': 'roletest.com'
        }
    )
    print("   Test organization created")
    
    # Test 3: Create users with new roles
    print("\n3. Testing user creation with new roles...")
    
    test_users = {}
    
    try:
        # Clean up any existing users first
        CustomUser.objects.filter(username__in=['blueadmin', 'testviewer', 'testpublisher']).delete()
        
        # Create BlueVision Admin first (needed to create other users)
        blue_admin = CustomUser.objects.create_user(
            username='blueadmin',
            email='blueadmin@roletest.com',
            password='BlueAdminPass123!',
            organization=org,
            role='BlueVisionAdmin',
            is_verified=True
        )
        test_users['BlueVisionAdmin'] = blue_admin
        print("   BlueVisionAdmin user created")
        
        # Create viewer
        viewer = UserFactory.create_user('viewer', {
            'username': 'testviewer',
            'email': 'viewer@roletest.com',
            'password': 'ViewerPass123!',
            'organization': org
        }, blue_admin)
        test_users['viewer'] = viewer
        print("   Viewer user created")
        
        # Create publisher
        publisher = UserFactory.create_user('publisher', {
            'username': 'testpublisher',
            'email': 'publisher@roletest.com',
            'password': 'PublisherPass123!',
            'first_name': 'Test',
            'last_name': 'Publisher',
            'organization': org
        }, blue_admin)
        test_users['publisher'] = publisher
        print("   Publisher user created")
        
    except Exception as e:
        print(f"   Error creating users: {e}")
        return False
    
    # Test 4: Test permissions
    print("\n4. Testing permission classes...")
    
    factory = RequestFactory()
    request = factory.get('/')
    
    # Test IsSystemAdmin (now checks for BlueVisionAdmin)
    is_system_admin = IsSystemAdmin()
    
    request.user = test_users['BlueVisionAdmin']
    if is_system_admin.has_permission(request, None):
        print("   BlueVisionAdmin passes IsSystemAdmin check")
    else:
        print("   BlueVisionAdmin fails IsSystemAdmin check")
        return False
    
    request.user = test_users['publisher']
    if not is_system_admin.has_permission(request, None):
        print("   Publisher correctly fails IsSystemAdmin check")
    else:
        print("   Publisher incorrectly passes IsSystemAdmin check")
        return False
    
    # Test IsOrganizationAdmin
    is_org_admin = IsOrganizationAdmin()
    
    request.user = test_users['BlueVisionAdmin']
    if is_org_admin.has_permission(request, None):
        print("   BlueVisionAdmin passes IsOrganizationAdmin check")
    else:
        print("   BlueVisionAdmin fails IsOrganizationAdmin check")
        return False
    
    # Test IsPublisher
    is_publisher = IsPublisher()
    
    # Make sure publisher has is_publisher flag set
    test_users['publisher'].is_publisher = True
    test_users['publisher'].save()
    
    request.user = test_users['publisher']
    if is_publisher.has_permission(request, None):
        print("   Publisher passes IsPublisher check")
    else:
        print("   Publisher fails IsPublisher check")
        return False
    
    request.user = test_users['viewer']
    if not is_publisher.has_permission(request, None):
        print("   Viewer correctly fails IsPublisher check")
    else:
        print("   Viewer incorrectly passes IsPublisher check")
        return False
    
    # Test 5: Test model methods
    print("\n5. Testing model methods...")
    
    # Test can_publish_feeds
    test_users['BlueVisionAdmin'].is_publisher = True
    test_users['BlueVisionAdmin'].save()
    
    if test_users['BlueVisionAdmin'].can_publish_feeds():
        print("   BlueVisionAdmin can publish feeds")
    else:
        print("   BlueVisionAdmin cannot publish feeds")
        return False
    
    if test_users['publisher'].can_publish_feeds():
        print("   Publisher can publish feeds")
    else:
        print("   Publisher cannot publish feeds")
        return False
    
    if not test_users['viewer'].can_publish_feeds():
        print("   Viewer correctly cannot publish feeds")
    else:
        print("   Viewer incorrectly can publish feeds")
        return False
    
    # Test is_organization_admin
    if test_users['BlueVisionAdmin'].is_organization_admin():
        print("   BlueVisionAdmin is organization admin")
    else:
        print("   BlueVisionAdmin is not organization admin")
        return False
    
    if not test_users['publisher'].is_organization_admin():
        print("   Publisher correctly is not organization admin")
    else:
        print("   Publisher incorrectly is organization admin")
        return False
    
    # Test 6: Clean up
    print("\n6. Cleaning up test data...")
    for user in test_users.values():
        user.delete()
    org.delete()
    print("   Test data cleaned up")
    
    print("\n" + "=" * 50)
    print("All role update tests passed!")
    print("\nSummary of changes verified:")
    print("- USER_ROLE_CHOICES updated to 3 roles")
    print("- UserFactory supports new role structure")
    print("- Permission classes work with BlueVisionAdmin")
    print("- Model methods updated for new roles")
    print("- Role hierarchy correctly implemented")
    
    return True

if __name__ == "__main__":
    success = test_role_updates()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Quick script to create admin test user with correct role
"""

import os
import sys

def create_admin_user():
    """Create admin test user with correct permissions"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
    
    import django
    django.setup()
    
    from UserManagement.models import CustomUser, Organization
    
    # Create test organization
    test_org, created = Organization.objects.get_or_create(
        name='Admin Test Organization',
        defaults={
            'description': 'Test organization for admin functionality testing',
            'domain': 'admintest.example.com',
            'is_active': True
        }
    )
    
    # Create admin test user
    admin_user, created = CustomUser.objects.get_or_create(
        username='admin_test_user',
        defaults={
            'email': 'admin@admintest.example.com',
            'organization': test_org,
            'role': 'BlueVisionAdmin',
            'is_verified': True,
            'is_active': True,
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # Always update to ensure correct settings
    admin_user.role = 'BlueVisionAdmin'
    admin_user.set_password('AdminTestPass123!')
    admin_user.account_locked_until = None
    admin_user.login_attempts = 0
    admin_user.failed_login_attempts = 0
    admin_user.is_verified = True
    admin_user.is_active = True
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    
    print(f"✅ Admin user created/updated:")
    print(f"   Username: {admin_user.username}")
    print(f"   Role: {admin_user.role}")
    print(f"   Email: {admin_user.email}")
    print(f"   Active: {admin_user.is_active}")
    print(f"   Verified: {admin_user.is_verified}")
    print(f"   Staff: {admin_user.is_staff}")
    print(f"   Superuser: {admin_user.is_superuser}")
    print(f"   Organization: {admin_user.organization.name}")

if __name__ == "__main__":
    create_admin_user()

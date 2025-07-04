#!/usr/bin/env python3
"""
Prepare test environment by clearing caches and setting up test users
"""

import os
import sys
import time

def prepare_test_environment():
    """Prepare the test environment"""
    print("🧹 Preparing test environment...")
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
    import django
    django.setup()
    
    from django.core.cache import cache
    from UserManagement.models import CustomUser, Organization
    
    # Clear all caches
    cache.clear()
    print("   Cleared Django cache")
    
    # Clear specific rate limit keys
    current_time = int(time.time())
    time_window = current_time // 300  # 5 minute windows
    
    # Clear multiple time windows to ensure no residual rate limiting
    for i in range(-5, 6):  # Clear 5 windows before and after current
        window = time_window + i
        keys_to_clear = [
            f'ratelimit:login:127.0.0.1:{window}',
            f'ratelimit:api:127.0.0.1:{window}',
            f'ratelimit:password_reset:127.0.0.1:{window}',
            f'rl:login:127.0.0.1:{window}',
            f'rl:api:127.0.0.1:{window}',
            f'rl:password_reset:127.0.0.1:{window}',
        ]
        for key in keys_to_clear:
            cache.delete(key)
    
    print("   Cleared rate limiting keys")
    
    # Setup test organization
    test_org, created = Organization.objects.get_or_create(
        name='Admin Test Organization',
        defaults={
            'description': 'Test organization for admin functionality testing',
            'domain': 'admintest.example.com',
            'is_active': True
        }
    )
    
    if created:
        print("   Created test organization")
    else:
        print("   Using existing test organization")
    
    # Setup admin test user
    admin_user, created = CustomUser.objects.get_or_create(
        username='admin_test_user',
        defaults={
            'email': 'admin@admintest.example.com',
            'organization': test_org,
            'role': 'BlueVisionAdmin',  # Use the correct system admin role
            'is_verified': True,
            'is_active': True,
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # Always update the user to ensure correct role and permissions
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
    
    if created:
        print("   Created admin test user")
    else:
        print("   Updated admin test user")
    
    # Setup regular test user
    regular_user, created = CustomUser.objects.get_or_create(
        username='regular_test_user',
        defaults={
            'email': 'regular@test.example.com',
            'organization': test_org,
            'role': 'user',
            'is_verified': True,
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        }
    )
    
    regular_user.set_password('RegularTestPass123!')
    regular_user.account_locked_until = None
    regular_user.login_attempts = 0
    regular_user.failed_login_attempts = 0
    regular_user.save()
    
    if created:
        print("   Created regular test user")
    else:
        print("   Updated regular test user")
    
    print("✅ Test environment prepared successfully!")
    print("   Admin User: admin_test_user (password: AdminTestPass123!)")
    print("   Regular User: regular_test_user (password: RegularTestPass123!)")
    
    return True

if __name__ == "__main__":
    try:
        prepare_test_environment()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to prepare test environment: {e}")
        sys.exit(1)

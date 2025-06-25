#!/usr/bin/env python3
"""
Test using the same pattern as successful integration test
"""
import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings for testing (same as integration test)
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'UserManagement',
            'crisp_threat_intel',
            'trust_management_app',
        ],
        SECRET_KEY='test-secret-key-for-integration-testing',
        USE_TZ=True,
        TIME_ZONE='UTC',
        AUTH_USER_MODEL='UserManagement.CustomUser',
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
    )

# Setup Django
django.setup()

# Now run tests
def run_test():
    print("🔄 Running basic model and serializer test...")
    
    # Import after Django setup
    from UserManagement.models import Organization, CustomUser
    from UserManagement.serializers import OrganizationSerializer
    
    # Create database tables
    from django.core.management import call_command
    call_command('migrate', verbosity=0, interactive=False)
    
    # Create organization
    org = Organization.objects.create(
        name='Test Organization',
        domain='test.com'
    )
    print(f"✅ Organization created: {org}")
    
    # Test serializer
    serializer = OrganizationSerializer(instance=org)
    data = serializer.data
    
    if 'domain' not in data:
        print("❌ Domain field missing from serializer")
        return False
    
    print(f"✅ Organization serializer: {data}")
    
    # Create user
    user = CustomUser.objects.create_user(
        username='testuser',
        email='testuser@test.com',
        password='TestPassword123!',
        organization=org,
        role='viewer'
    )
    print(f"✅ User created: {user}")
    
    print("🎉 Basic test PASSED!")
    return True

if __name__ == '__main__':
    try:
        success = run_test()
        if not success:
            sys.exit(1)
        print("✅ All tests completed successfully!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

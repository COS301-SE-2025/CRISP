#!/usr/bin/env python3
"""
Minimal test runner to check specific functionality
"""
import os
import sys
import django

# Set up environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_project.settings')

# Override to use in-memory SQLite to avoid database issues
import crisp_project.settings as settings_module
settings_module.DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Setup Django
django.setup()

# Now run tests
from django.test import TestCase
from django.test.utils import setup_test_environment, teardown_test_environment
from django.db import connection
from django.db.models import get_models
from django.apps import apps

# Test imports
try:
    from UserManagement.models import CustomUser, Organization
    from UserManagement.factories.user_factory import UserFactory
    from UserManagement.serializers import OrganizationSerializer
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test basic functionality
def test_basic_functionality():
    """Test basic model creation and serialization"""
    print("\n🔄 Testing basic functionality...")
    
    try:
        # Create organization
        org = Organization.objects.create(
            name='Test Organization',
            domain='test.com'
        )
        print(f"✅ Organization created: {org}")
        
        # Test organization serializer
        serializer = OrganizationSerializer(instance=org)
        data = serializer.data
        print(f"✅ Organization serializer works: {data}")
        
        # Test user creation  
        user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='TestPassword123!',
            organization=org,
            role='viewer'
        )
        print(f"✅ User created: {user}")
        
        print("\n🎉 Basic functionality test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    setup_test_environment()
    
    # Create database tables
    from django.core.management import call_command
    call_command('migrate', verbosity=0, interactive=False)
    
    # Run test
    success = test_basic_functionality()
    
    teardown_test_environment()
    
    if not success:
        sys.exit(1)
    
    print("\n✅ All basic tests passed!")

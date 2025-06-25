#!/usr/bin/env python3
"""
Direct Django model test without test framework
"""
import os
import sys
import django

# Force environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_project.settings')

try:
    # Configure Django settings before setup
    from django.conf import settings
    
    # Override to use SQLite for testing
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    
    # Force disable cache
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    
    # Setup Django
    django.setup()
    
    print("Django setup complete")
    
    # Import models and create tables
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate', '--verbosity=0', '--no-input'])
    
    print("Database migration complete")
    
    # Test basic model creation
    from UserManagement.models import Organization, CustomUser
    
    # Create test data
    org = Organization.objects.create(name='Test Org', domain='test.com')
    print(f"Organization created: {org}")
    
    user = CustomUser.objects.create_user(
        username='testuser',
        email='test@test.com',
        password='TestPass123!',
        organization=org,
        role='viewer'
    )
    print(f"User created: {user}")
    
    # Test serializer
    from UserManagement.serializers import OrganizationSerializer
    serializer = OrganizationSerializer(instance=org)
    print(f"Serializer data: {serializer.data}")
    
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

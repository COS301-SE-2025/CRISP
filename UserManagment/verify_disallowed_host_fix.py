#!/usr/bin/env python3
"""
Quick verification that DisallowedHost errors are fixed
"""

import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_project.settings')
django.setup()

from django.test import Client
from django.conf import settings

def test_disallowed_host_fix():
    """Test that testserver is now allowed"""
    print("🔍 Testing DisallowedHost Fix")
    print("=" * 40)
    
    # Check settings
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    if 'testserver' in settings.ALLOWED_HOSTS:
        print("✅ 'testserver' found in ALLOWED_HOSTS")
    else:
        print("❌ 'testserver' NOT found in ALLOWED_HOSTS")
        return False
    
    # Test with Django test client
    try:
        client = Client()
        response = client.get('/admin/')
        print(f"✅ Admin interface test: Status {response.status_code}")
        print("✅ SUCCESS: No DisallowedHost error!")
        return True
    except Exception as e:
        if "DisallowedHost" in str(e):
            print(f"❌ DisallowedHost error still occurring: {e}")
            return False
        else:
            print(f"✅ No DisallowedHost error (other error: {e})")
            return True

if __name__ == "__main__":
    success = test_disallowed_host_fix()
    if success:
        print("\n🎉 DisallowedHost fix verified!")
    else:
        print("\n⚠️ DisallowedHost fix needs attention")

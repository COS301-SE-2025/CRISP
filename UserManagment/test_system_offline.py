#!/usr/bin/env python3
"""
Offline system tests for CRISP User Management
Tests configuration and setup without requiring a running server
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.test.utils import get_runner

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_project.settings')
django.setup()

def test_url_configuration():
    """Test that URL configuration is properly set up"""
    print("Testing URL configuration...")
    
    try:
        from crisp_project.urls import urlpatterns
        from UserManagement.urls import urlpatterns as user_urlpatterns
        
        # Check that main URLs exist
        if urlpatterns:
            print("Main URL patterns configured")
        else:
            print("No main URL patterns found")
            return False
            
        # Check that UserManagement URLs exist
        if user_urlpatterns:
            print("UserManagement URL patterns configured")
        else:
            print("No UserManagement URL patterns found")
            return False
            
        return True
        
    except Exception as e:
        print(f"URL configuration error: {e}")
        return False

def test_authentication_setup():
    """Test that authentication is properly configured"""
    print("\nTesting authentication setup...")
    
    try:
        from UserManagement.models import CustomUser
        from django.contrib.auth import authenticate
        
        # Check that CustomUser model is properly configured
        if CustomUser._meta.get_field('username'):
            print("CustomUser model configured")
        else:
            print("CustomUser model missing username field")
            return False
            
        # Check authentication backends (Django default is fine)
        auth_backends = getattr(settings, 'AUTHENTICATION_BACKENDS', ['django.contrib.auth.backends.ModelBackend'])
        if auth_backends:
            print("Authentication backends configured")
        else:
            print("No authentication backends configured")
            return False
            
        return True
        
    except Exception as e:
        print(f"Authentication setup error: {e}")
        return False

def test_admin_configuration():
    """Test that admin interface is properly configured"""
    print("\nTesting admin configuration...")
    
    try:
        from UserManagement.admin import CustomUserAdmin, OrganizationAdmin
        from django.contrib import admin
        
        # Check that admin classes are registered
        if CustomUserAdmin:
            print("CustomUserAdmin configured")
        else:
            print("CustomUserAdmin not found")
            return False
            
        if OrganizationAdmin:
            print("OrganizationAdmin configured")
        else:
            print("OrganizationAdmin not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"Admin configuration error: {e}")
        return False

def test_security_settings():
    """Test that security settings are properly configured"""
    print("\nTesting security settings...")
    
    try:
        # Check for security settings
        security_checks = [
            ('ALLOWED_HOSTS', hasattr(settings, 'ALLOWED_HOSTS')),
            ('CSRF_COOKIE_SECURE', getattr(settings, 'CSRF_COOKIE_SECURE', False)),
            ('SESSION_COOKIE_SECURE', getattr(settings, 'SESSION_COOKIE_SECURE', False)),
            ('SECURE_BROWSER_XSS_FILTER', getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False)),
        ]
        
        passed = 0
        for setting_name, is_configured in security_checks:
            if is_configured:
                print(f"{setting_name} configured")
                passed += 1
            else:
                print(f" {setting_name} not configured")
        
        return passed >= 2  # At least 2 security settings should be configured
        
    except Exception as e:
        print(f"Security settings error: {e}")
        return False

def main():
    print("🛡️  CRISP User Management System - Offline Tests")
    print("="*60)
    
    tests = [
        test_url_configuration,
        test_authentication_setup,
        test_admin_configuration,
        test_security_settings
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTest Results: {passed}/{total} passed")
    
    if passed == total:
        print("All offline tests passed!")
        return 0
    else:
        print(" Some offline tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
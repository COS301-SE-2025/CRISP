#!/usr/bin/env python3
"""
Debug script to test user creation through Django admin
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from UserManagement.models import Organization
from django.urls import reverse
import re

CustomUser = get_user_model()

def debug_user_creation():
    """Debug user creation process"""
    print("CRISP User Management - Debug User Creation")
    print("=" * 60)
    
    # Setup client and login
    client = Client()
    
    # Get admin user
    admin_user = CustomUser.objects.filter(username='admin').first()
    if not admin_user:
        print("❌ Admin user not found.")
        return
    
    # Login
    login_success = client.login(username='admin', password='AdminPassword123!')
    if not login_success:
        print("❌ Failed to login as admin")
        return
    
    print("✅ Logged in successfully")
    
    # Get organization
    org = Organization.objects.first()
    if not org:
        print("❌ No organization found")
        return
    
    print(f"✅ Using organization: {org.name}")
    
    # Test user creation
    add_user_url = reverse('admin:UserManagement_customuser_add')
    print(f"📝 Testing user creation at: {add_user_url}")
    
    # Get the form first
    response = client.get(add_user_url)
    print(f"📋 Form GET status: {response.status_code}")
    
    if response.status_code == 200:
        # Extract CSRF token
        csrf_token = None
        if hasattr(response, 'context') and response.context:
            csrf_token = response.context.get('csrf_token')
        
        if not csrf_token:
            # Try to extract from content
            content = response.content.decode('utf-8')
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
            if csrf_match:
                csrf_token = csrf_match.group(1)
        
        print(f"🔑 CSRF token found: {'Yes' if csrf_token else 'No'}")
        
        # Test data for a viewer user
        test_data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': 'debug_viewer_user',
            'email': 'debug_viewer@example.com',
            'first_name': 'Debug',
            'last_name': 'Viewer',
            'role': 'viewer',
            'organization': str(org.id),
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
            'is_active': 'on',
            '_save': 'Save',
        }
        
        print("📝 Submitting user creation form...")
        print(f"   Data: {test_data}")
        
        # Submit form
        response = client.post(add_user_url, test_data, follow=True)
        print(f"📤 POST response status: {response.status_code}")
        if hasattr(response, 'redirect_chain'):
            print(f"📤 Redirect chain: {[f'{r[0]} ({r[1]})' for r in response.redirect_chain]}")
        else:
            print(f"📤 No redirect chain")
        
        # Check if user was created
        created_user = CustomUser.objects.filter(username='debug_viewer_user').first()
        if created_user:
            print(f"✅ User created successfully: {created_user.username} (role: {created_user.role})")
            # Clean up
            created_user.delete()
            print("🧹 Cleaned up test user")
        else:
            print("❌ User was not created")
            
            # Debug form errors
            if hasattr(response, 'context') and response.context:
                print("🔍 Debugging form context...")
                
                for key in response.context.keys():
                    if 'form' in key.lower():
                        print(f"   Found context key: {key}")
                        form_obj = response.context[key]
                        if hasattr(form_obj, 'errors'):
                            print(f"   Errors in {key}: {form_obj.errors}")
                        if hasattr(form_obj, 'form') and hasattr(form_obj.form, 'errors'):
                            print(f"   Nested form errors in {key}: {form_obj.form.errors}")
            
            # Check HTML content for errors
            content = response.content.decode('utf-8')
            if 'errorlist' in content:
                print("🔍 Found errorlist in HTML content")
                error_pattern = r'<ul class="errorlist[^>]*"><li>([^<]+)</li></ul>'
                errors = re.findall(error_pattern, content)
                for error in errors:
                    print(f"   Error: {error}")
            
            # Check for specific field errors
            field_error_pattern = r'<div class="form-row[^>]*errors[^>]*">.*?<div class="errors">.*?<ul class="errorlist"><li>([^<]+)</li></ul>'
            field_errors = re.findall(field_error_pattern, content, re.DOTALL)
            for error in field_errors:
                print(f"   Field error: {error}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    debug_user_creation()

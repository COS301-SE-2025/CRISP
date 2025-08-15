#!/usr/bin/env python3
"""
Create specific test users for system testing
"""

import os
import sys
import django

# Setup Django
sys.path.append('/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/Capstone-Unified')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_settings.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models.models import Organization
from core_ut.user_management.models import UserProfile

def create_test_users():
    """Create specific test users with known credentials"""
    User = get_user_model()
    
    # Test users to create
    test_users = [
        {
            'username': 'admin_test',
            'email': 'admin@crisp.test',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
            'role': 'Administrator'
        },
        {
            'username': 'analyst_test',
            'email': 'analyst@crisp.test', 
            'password': 'analyst123',
            'first_name': 'Threat',
            'last_name': 'Analyst',
            'is_staff': False,
            'is_superuser': False,
            'role': 'Threat Analyst'
        },
        {
            'username': 'manager_test',
            'email': 'manager@crisp.test',
            'password': 'manager123', 
            'first_name': 'Security',
            'last_name': 'Manager',
            'is_staff': True,
            'is_superuser': False,
            'role': 'Security Manager'
        },
        {
            'username': 'viewer_test',
            'email': 'viewer@crisp.test',
            'password': 'viewer123',
            'first_name': 'Intel',
            'last_name': 'Viewer', 
            'is_staff': False,
            'is_superuser': False,
            'role': 'Intelligence Viewer'
        }
    ]
    
    print("🔐 Creating Test Users for CRISP System")
    print("=" * 50)
    
    created_users = []
    
    for user_data in test_users:
        username = user_data['username']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            print(f"✅ User '{username}' already exists")
        else:
            # Create new user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            user.is_staff = user_data['is_staff']
            user.is_superuser = user_data['is_superuser']
            user.save()
            
            print(f"✅ Created user '{username}'")
        
        # Create or update user profile
        try:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': f"{user_data['role']} with access to CRISP threat intelligence platform",
                    'location': 'Test Environment',
                    'phone_number': '+1-555-0123',
                    'department': 'Cybersecurity',
                    'job_title': user_data['role']
                }
            )
            if created:
                print(f"   📝 Created profile for {username}")
            else:
                print(f"   📝 Profile exists for {username}")
        except Exception as e:
            print(f"   ⚠️ Profile creation failed for {username}: {e}")
        
        created_users.append({
            'username': username,
            'email': user_data['email'],
            'password': user_data['password'],
            'role': user_data['role'],
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        })
    
    print(f"\n📋 Test User Credentials:")
    print("=" * 50)
    
    for user in created_users:
        print(f"👤 {user['role']}")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")
        print(f"   Password: {user['password']}")
        print(f"   Staff: {user['is_staff']}")
        print(f"   Superuser: {user['is_superuser']}")
        print()
    
    print(f"🎯 How to Test:")
    print("=" * 50)
    print("1. Frontend Login (React):")
    print("   - Go to: http://localhost:5173")
    print("   - Use any username/password above")
    print()
    print("2. Django Admin:")
    print("   - Go to: http://localhost:8000/admin/")
    print("   - Use admin_test/admin123 or manager_test/manager123")
    print()
    print("3. API Testing:")
    print("   - Use the provided test scripts")
    print("   - Login with different users to test RBAC")
    print()
    print("4. Threat Feed Testing:")
    print("   - Login as admin_test or manager_test")
    print("   - Access threat feeds management")
    print("   - Test feed consumption and data viewing")

if __name__ == '__main__':
    create_test_users()
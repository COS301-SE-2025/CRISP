#!/usr/bin/env python
import os
import sys
import django

# Add the project root to the Python path
sys.path.insert(0, '/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone')
sys.path.insert(0, '/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/crisp')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TrustManagement.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.user_management.models import Organization

User = get_user_model()

# Create a test organization
org = Organization.objects.create(
    name="Test Org",
    domain="test.edu",
    contact_email="test@test.edu",
    organization_type="educational"
)

print("Creating user...")
user = User.objects.create_user(
    username='debuguser',
    email='debug@test.edu',
    password='testpass123',
    organization=org
)

print(f"User created: {user}")
print(f"Username: {user.username}")
print(f"Email: {user.email}")
print(f"Password field: {user.password}")
print(f"Password check result: {user.check_password('testpass123')}")

# Try setting password manually
print("\nSetting password manually...")
user.set_password('testpass123')
user.save()
print(f"Password field after manual set: {user.password}")
print(f"Password check result after manual set: {user.check_password('testpass123')}")
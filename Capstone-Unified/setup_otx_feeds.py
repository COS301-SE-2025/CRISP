#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
sys.path.append('/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/Capstone-Unified')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_settings.settings')
django.setup()

from core.models.models import ThreatFeed, Organization
from django.contrib.auth import get_user_model

def setup_otx_feeds():
    """Setup AlienVault OTX threat feeds"""
    
    # Get or create a default organization
    User = get_user_model()
    users = User.objects.all()
    if not users.exists():
        print('No users found. Creating a default admin user...')
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f'Created admin user: {user.username}')
    else:
        user = users.first()
        print(f'Using existing user: {user.username}')

    # Get or create AlienVault organization
    org, created = Organization.objects.get_or_create(
        name='AlienVault OTX',
        defaults={
            'description': 'AlienVault Open Threat Exchange',
            'identity_class': 'organization',
            'organization_type': 'private-sector',
            'contact_email': 'otx@alienvault.com',
            'website': 'https://otx.alienvault.com',
            'created_by': user
        }
    )
    status = 'created' if created else 'existing'
    print(f'Organization: {org.name} ({status})')

    # Create AlienVault OTX threat feed
    feed, created = ThreatFeed.objects.get_or_create(
        name='AlienVault OTX Feed',
        defaults={
            'description': 'Real threat intelligence from AlienVault Open Threat Exchange',
            'taxii_server_url': 'https://otx.alienvault.com',
            'taxii_collection_id': 'default',  # Will be discovered dynamically
            'owner': org,
            'is_external': True,
            'is_public': True,
            'is_active': True,
            'sync_interval_hours': 24
        }
    )
    
    status = 'created' if created else 'existing'
    print(f'Threat Feed: {feed.name} ({status})')
    print(f'Feed ID: {feed.id}')
    
    print(f'\nTotal threat feeds in database: {ThreatFeed.objects.count()}')
    print(f'Total organizations: {Organization.objects.count()}')
    print(f'Total users: {User.objects.count()}')
    
    return feed

if __name__ == '__main__':
    try:
        feed = setup_otx_feeds()
        print(f'\nSuccess! AlienVault OTX feed setup complete.')
        print(f'You can now consume threat data using:')
        print(f'python3 manage.py taxii_operations consume --feed-id {feed.id}')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
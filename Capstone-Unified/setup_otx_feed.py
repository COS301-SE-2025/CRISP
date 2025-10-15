#!/usr/bin/env python
"""
Setup AlienVault OTX threat feed
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django.setup()

from core.models.models import ThreatFeed, Organization
from django.contrib.auth import get_user_model

User = get_user_model()

def setup_otx_feed():
    """Create AlienVault OTX threat feed"""
    
    # Get BlueVision ITM organization
    org = Organization.objects.filter(name='BlueVision ITM').first()
    if not org:
        print('❌ BlueVision ITM organization not found')
        print('   Available organizations:')
        for o in Organization.objects.all():
            print(f'   - {o.name}')
        return False
    
    # Create AlienVault OTX feed
    feed, created = ThreatFeed.objects.get_or_create(
        name='AlienVault OTX',
        defaults={
            'description': 'AlienVault Open Threat Exchange - Community threat intelligence',
            'owner': org,
            'is_external': True,
            'is_active': True,
            'taxii_server_url': 'https://otx.alienvault.com',
            'taxii_api_root': 'taxii',
            'taxii_collection_id': 'user_AlienVault',
            'sync_interval_hours': 24,
            'is_public': True
        }
    )
    
    if created:
        print(f'✅ Created AlienVault OTX feed')
        print(f'   ID: {feed.id}')
        print(f'   Name: {feed.name}')
        print(f'   Owner: {feed.owner.name}')
        print(f'   Active: {feed.is_active}')
        print(f'   External: {feed.is_external}')
        print(f'   TAXII URL: {feed.taxii_server_url}')
        print(f'   API Root: {feed.taxii_api_root}')
        print(f'   Collection: {feed.taxii_collection_id}')
        print(f'   Sync Interval: {feed.sync_interval_hours} hours')
    else:
        print(f'ℹ️  AlienVault OTX feed already exists')
        print(f'   ID: {feed.id}')
        print(f'   Active: {feed.is_active}')
        
        # Make sure it's active
        if not feed.is_active:
            feed.is_active = True
            feed.save()
            print(f'   ✅ Activated feed')
    
    return True

if __name__ == '__main__':
    print('🔧 Setting up AlienVault OTX threat feed...\n')
    
    if setup_otx_feed():
        print('\n✅ Setup complete!')
        sys.exit(0)
    else:
        print('\n❌ Setup failed')
        sys.exit(1)

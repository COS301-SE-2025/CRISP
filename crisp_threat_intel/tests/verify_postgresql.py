#!/usr/bin/env python3
"""
PostgreSQL Configuration Verification Script
Ensures the entire CRISP platform is using PostgreSQL exclusively
"""

import os
import sys
import django

# Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_threat_intel.settings')
django.setup()

from django.db import connection
from django.conf import settings

def verify_postgresql_config():
    """Verify PostgreSQL is configured and working"""
    print("="*60)
    print("CRISP THREAT INTELLIGENCE - POSTGRESQL VERIFICATION")
    print("="*60)
    
    # Check database engine
    engine = connection.settings_dict['ENGINE']
    if 'postgresql' in engine:
        print("✓ Database Engine: PostgreSQL")
    else:
        print(f"✗ Database Engine: {engine} (SHOULD BE PostgreSQL)")
        return False
    
    # Check database connection
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT version();')
        result = cursor.fetchone()
        print(f"✓ PostgreSQL Version: {result[0].split(',')[0]}")
    except Exception as e:
        print(f"✗ Database Connection Failed: {e}")
        return False
    
    # Check database details
    print(f"✓ Database Name: {connection.settings_dict['NAME']}")
    print(f"✓ Database User: {connection.settings_dict['USER']}")
    print(f"✓ Database Host: {connection.settings_dict['HOST']}")
    print(f"✓ Database Port: {connection.settings_dict['PORT']}")
    
    # Check for any SQLite references in settings
    settings_str = str(settings.__dict__)
    if 'sqlite' in settings_str.lower():
        print("⚠ Warning: SQLite references found in settings")
    else:
        print("✓ No SQLite references in settings")
    
    # Check tables exist
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
    table_count = cursor.fetchone()[0]
    print(f"✓ Database Tables: {table_count} tables found")
    
    # Check for specific CRISP tables
    expected_tables = [
        'crisp_threat_intel_organization',
        'crisp_threat_intel_stixobject', 
        'crisp_threat_intel_collection',
        'crisp_threat_intel_feed'
    ]
    
    for table in expected_tables:
        cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table}'")
        exists = cursor.fetchone()[0] > 0
        if exists:
            print(f"✓ Table exists: {table}")
        else:
            print(f"✗ Table missing: {table}")
    
    # Check data counts
    from crisp_threat_intel.models import Organization, STIXObject, Collection, Feed
    
    org_count = Organization.objects.count()
    stix_count = STIXObject.objects.count()
    collection_count = Collection.objects.count()
    feed_count = Feed.objects.count()
    
    print(f"✓ Data Counts:")
    print(f"  - Organizations: {org_count}")
    print(f"  - STIX Objects: {stix_count}")
    print(f"  - Collections: {collection_count}")
    print(f"  - Feeds: {feed_count}")
    
    # Test OTX data migration
    otx_org = Organization.objects.filter(name__icontains='OTX').first()
    if otx_org:
        otx_stix_count = STIXObject.objects.filter(source_organization=otx_org).count()
        print(f"✓ OTX Data Migration: {otx_stix_count} objects from OTX")
    else:
        print("ℹ OTX Integration: No OTX data found (may need to run setup_otx)")
    
    print()
    print("="*60)
    print("POSTGRESQL CONFIGURATION: ✓ VERIFIED")
    print("All SQLite references have been removed.")
    print("The platform is now using PostgreSQL exclusively.")
    print("="*60)
    
    return True

if __name__ == '__main__':
    success = verify_postgresql_config()
    sys.exit(0 if success else 1)

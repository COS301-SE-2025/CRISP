#!/usr/bin/env python3
"""
CRISP Database Inspector - Check database contents and structure
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_threat_intel.settings')

import django
django.setup()

from django.db import connection
from crisp_threat_intel.models import Organization, STIXObject, Collection, Feed, Identity

def inspect_database():
    print("🛡️ CRISP Threat Intelligence Platform - Database Inspector")
    print("=" * 70)
    
    # Database connection info
    db_settings = connection.settings_dict
    print(f"📊 Database: {db_settings['NAME']} @ {db_settings['HOST']}:{db_settings['PORT']}")
    print(f"👤 User: {db_settings['USER']}")
    print()
    
    # Test connection and get version
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"🐘 PostgreSQL Version: {version.split(',')[0]}")
        print()
    
    # Model counts
    print("📈 Data Summary:")
    print(f"  Organizations: {Organization.objects.count()}")
    print(f"  STIX Objects:  {STIXObject.objects.count()}")
    print(f"  Collections:   {Collection.objects.count()}")
    print(f"  Feeds:         {Feed.objects.count()}")
    print(f"  Identities:    {Identity.objects.count()}")
    print()
    
    # Organizations detail
    print("🏢 Organizations:")
    for org in Organization.objects.all():
        stix_count = org.stix_objects.count()
        collections_count = org.owned_collections.count()
        print(f"  - {org.name}")
        print(f"    STIX Objects: {stix_count}")
        print(f"    Collections: {collections_count}")
        if org.stix_id:
            print(f"    STIX ID: {org.stix_id}")
        print()
    
    # Collections detail
    print("📦 Collections:")
    for collection in Collection.objects.all():
        obj_count = collection.stix_objects.count()
        feeds_count = collection.feeds.count()
        print(f"  - {collection.title} (Owner: {collection.owner.name})")
        print(f"    Objects: {obj_count}")
        print(f"    Feeds: {feeds_count}")
        print()
    
    # STIX Object types breakdown
    print("🎯 STIX Object Types:")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT stix_type, COUNT(*) as count
            FROM crisp_threat_intel_stixobject 
            GROUP BY stix_type 
            ORDER BY count DESC;
        """)
        for stix_type, count in cursor.fetchall():
            print(f"  - {stix_type}: {count}")
    print()
    
    # Recent objects
    print("🕐 Recent STIX Objects (Last 10):")
    recent_objects = STIXObject.objects.order_by('-created_at')[:10]
    for obj in recent_objects:
        source_org = obj.source_organization.name if obj.source_organization else "Unknown"
        print(f"  - {obj.stix_type}: {obj.stix_id[:40]}... ({source_org})")
    print()
    
    # Table sizes
    print("📊 Database Table Information:")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation
            FROM pg_stats 
            WHERE schemaname = 'public' 
            AND tablename LIKE 'crisp_threat_intel_%'
            ORDER BY tablename, attname;
        """)
        
        current_table = None
        for schema, table, column, distinct, correlation in cursor.fetchall():
            if table != current_table:
                if current_table is not None:
                    print()
                print(f"  📋 {table}:")
                current_table = table
            print(f"    - {column}: {distinct} distinct values")
    print()
    
    # Index information
    print("🔍 Database Indexes:")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename LIKE 'crisp_threat_intel_%'
            ORDER BY tablename, indexname;
        """)
        
        current_table = None
        for schema, table, index_name, index_def in cursor.fetchall():
            if table != current_table:
                if current_table is not None:
                    print()
                print(f"  📋 {table}:")
                current_table = table
            print(f"    - {index_name}")
    print()
    
    # Check for any foreign key relationships
    print("🔗 Foreign Key Relationships:")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_name LIKE 'crisp_threat_intel_%'
            ORDER BY tc.table_name;
        """)
        
        for table, column, foreign_table, foreign_column in cursor.fetchall():
            print(f"  {table}.{column} → {foreign_table}.{foreign_column}")
    
    print("\n✅ Database inspection complete!")

if __name__ == "__main__":
    try:
        inspect_database()
    except Exception as e:
        print(f"❌ Error inspecting database: {e}")
        sys.exit(1)
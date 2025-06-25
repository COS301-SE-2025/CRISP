#!/usr/bin/env python
"""
PostgreSQL Configuration Verification Test
Ensures PostgreSQL is properly configured and accessible.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')

import django
django.setup()

from django.db import connection, connections
from django.core.management import call_command
from django.test.utils import setup_test_environment, teardown_test_environment
import psycopg2
from psycopg2 import sql


def test_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    
    try:
        from django.db import connection
        db_vendor = connection.vendor
        
        # Test PostgreSQL database connection only
        with connection.cursor() as cursor:
            if db_vendor != 'postgresql':
                raise Exception(f"Expected PostgreSQL but got {db_vendor}")
            
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ PostgreSQL connection successful: {version}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_database_creation():
    """Test database creation and basic operations"""
    print("Testing database creation and operations...")
    
    try:
        # Test creating a simple table
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert test data
            cursor.execute("INSERT INTO test_table (name) VALUES (%s);", ["test_entry"])
            
            # Query test data
            cursor.execute("SELECT * FROM test_table WHERE name = %s;", ["test_entry"])
            result = cursor.fetchone()
            
            # Clean up
            cursor.execute("DROP TABLE test_table;")
            
            if result:
                print("✅ Database operations successful")
                return True
            else:
                print("❌ Database operations failed")
                return False
    except Exception as e:
        print(f"❌ Database operations failed: {e}")
        return False


def test_trust_management_models():
    """Test Trust Management models"""
    print("Testing Trust Management models...")
    
    try:
        from django.core.management import call_command
        from TrustManagement.models import TrustLevel, TrustGroup, TrustRelationship
        
        # Ensure migrations are applied
        call_command('migrate', verbosity=0, interactive=False)
        
        # Test model creation
        trust_level = TrustLevel.objects.create(
            name="Test Trust Level",
            level="test",
            description="Test trust level for database verification",
            numerical_value=50,
            created_by="test_user"
        )
        
        # Test model query
        retrieved_level = TrustLevel.objects.get(name="Test Trust Level")
        
        # Test model deletion
        trust_level.delete()
        
        print("✅ Trust Management models work correctly")
        return True
    except Exception as e:
        print(f"❌ Trust Management models failed: {e}")
        return False


def test_database_features():
    """Test database-specific features"""
    print("Testing database features...")
    
    try:
        from django.db import connection
        db_vendor = connection.vendor
        
        with connection.cursor() as cursor:
            if db_vendor != 'postgresql':
                raise Exception(f"Expected PostgreSQL but got {db_vendor}")
            
            # Test PostgreSQL JSON field support
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_json (
                    id SERIAL PRIMARY KEY,
                    data JSONB
                );
            """)
            
            cursor.execute(
                "INSERT INTO test_json (data) VALUES (%s);",
                ['{"test": "value", "number": 42}']
            )
            
            # Test JSON querying
            cursor.execute("SELECT data->>'test' FROM test_json;")
            result = cursor.fetchone()[0]
            
            # Clean up
            cursor.execute("DROP TABLE test_json;")
            
            if result == "value":
                print("✅ PostgreSQL JSON features working")
                return True
            else:
                print("❌ PostgreSQL JSON features failed")
                return False
    except Exception as e:
        print(f"❌ Database features test failed: {e}")
        return False


def test_database_indexes():
    """Test database indexes are working"""
    print("Testing database indexes...")
    
    try:
        from django.db import connection
        db_vendor = connection.vendor
        
        with connection.cursor() as cursor:
            if db_vendor != 'postgresql':
                raise Exception(f"Expected PostgreSQL but got {db_vendor}")
            
            # Check if indexes exist on Trust Management tables
            cursor.execute("""
                SELECT indexname, tablename 
                FROM pg_indexes 
                WHERE schemaname = 'public' 
                AND tablename LIKE '%trust%'
                LIMIT 5;
            """)
            
            indexes = cursor.fetchall()
            
            if indexes:
                print(f"✅ Found {len(indexes)} PostgreSQL indexes on trust management tables")
                for index_name, table_name in indexes:
                    print(f"  - {index_name} on {table_name}")
                return True
            else:
                print("⚠️  No PostgreSQL indexes found (tables may not be created yet)")
                return True  # Not necessarily an error
    except Exception as e:
        print(f"❌ Index test failed: {e}")
        return False


def main():
    """Run all database verification tests"""
    from django.db import connection
    db_vendor = connection.vendor.upper()
    
    print("=" * 60)
    print(f"{db_vendor} DATABASE CONFIGURATION VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Database Operations", test_database_creation),
        ("Trust Management Models", test_trust_management_models),
        ("Database Features", test_database_features),
        ("Database Schema", test_database_indexes),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        success = test_func()
        results.append((test_name, success))
        print()
    
    # Print summary
    print("=" * 60)
    print(f"{db_vendor} VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print()
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    
    if failed > 0:
        print(f"\n❌ Some {db_vendor} tests failed!")
        print(f"Please check your {db_vendor} configuration.")
        return False
    else:
        print(f"\n✅ All {db_vendor} tests passed!")
        print(f"{db_vendor} is properly configured and ready for use.")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
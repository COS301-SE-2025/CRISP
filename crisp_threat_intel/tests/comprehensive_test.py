#!/usr/bin/env python3
"""
CRISP Threat Intelligence Platform - Comprehensive Test Suite
Tests all functionality: Database, Models, STIX, Collections, Feeds, OTX, TAXII, Security
"""

import os
import sys
import json
import requests
import time
from datetime import datetime
import subprocess

# Django setup
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_threat_intel.settings')
django.setup()

from django.test.utils import get_runner
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection
from crisp_threat_intel.models import Organization, STIXObject, Collection, CollectionObject, Feed
from crisp_threat_intel.factories.stix_factory import STIXObjectFactory
from crisp_threat_intel.utils import generate_bundle_from_collection, publish_feed
from crisp_threat_intel.services.otx_service import OTXClient

class ComprehensiveTestSuite:
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.errors = []
        self.start_time = datetime.now()
        
    def log_success(self, test_name, details=""):
        print(f"✓ {test_name}")
        if details:
            print(f"  {details}")
        self.passed_tests += 1
        
    def log_error(self, test_name, error=None, details=""):
        error_msg = f"✗ {test_name}"
        if error:
            error_msg += f": {str(error)}"
        if details:
            error_msg += f" ({details})"
        print(error_msg)
        self.errors.append(error_msg)
        self.failed_tests += 1
        
    def test_database_connectivity(self):
        """Test PostgreSQL database connectivity and configuration"""
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT version();')
            result = cursor.fetchone()
            
            # Verify it's PostgreSQL
            if 'PostgreSQL' in result[0]:
                self.log_success("Database Connectivity", f"PostgreSQL version: {result[0].split(',')[0]}")
            else:
                self.log_error("Database Type", f"Expected PostgreSQL, got: {result[0]}")
                
            # Test database settings
            db_settings = connection.settings_dict
            if 'postgresql' in db_settings['ENGINE']:
                self.log_success("Database Engine", "PostgreSQL configured correctly")
            else:
                self.log_error("Database Engine", f"Wrong engine: {db_settings['ENGINE']}")
                
        except Exception as e:
            self.log_error("Database Connectivity", e)
            
    def test_model_operations(self):
        """Test Django model operations"""
        try:
            # Test data counts
            org_count = Organization.objects.count()
            stix_count = STIXObject.objects.count()
            collection_count = Collection.objects.count()
            feed_count = Feed.objects.count()
            user_count = User.objects.count()
            
            if org_count > 0:
                self.log_success("Organizations Model", f"{org_count} organizations found")
            else:
                self.log_error("Organizations Model", "No organizations found")
                
            if stix_count > 0:
                self.log_success("STIX Objects Model", f"{stix_count} STIX objects found")
            else:
                self.log_error("STIX Objects Model", "No STIX objects found")
                
            if collection_count > 0:
                self.log_success("Collections Model", f"{collection_count} collections found")
            else:
                self.log_error("Collections Model", "No collections found")
                
            if feed_count > 0:
                self.log_success("Feeds Model", f"{feed_count} feeds found")
            else:
                self.log_error("Feeds Model", "No feeds found")
                
            if user_count > 0:
                self.log_success("Users Model", f"{user_count} users found")
            else:
                self.log_error("Users Model", "No users found")
                
        except Exception as e:
            self.log_error("Model Operations", e)
            
    def test_stix_object_creation(self):
        """Test STIX object creation and validation"""
        try:
            # Test indicator creation
            indicator = STIXObjectFactory.create_object('indicator', {
                'pattern': "[domain-name:value = 'test-comprehensive.example.com']",
                'labels': ['malicious-activity'],
                'name': 'Comprehensive Test Indicator'
            })
            
            # Validate indicator structure
            required_fields = ['id', 'type', 'pattern', 'labels', 'created', 'modified']
            for field in required_fields:
                if field not in indicator:
                    self.log_error("STIX Indicator Creation", f"Missing field: {field}")
                    return
                    
            if indicator['type'] == 'indicator':
                self.log_success("STIX Indicator Creation", f"ID: {indicator['id']}")
            else:
                self.log_error("STIX Indicator Creation", f"Wrong type: {indicator['type']}")
                
            # Test attack pattern creation
            attack_pattern = STIXObjectFactory.create_object('attack-pattern', {
                'name': 'Comprehensive Test Attack Pattern',
                'description': 'Test attack pattern for comprehensive testing'
            })
            
            if attack_pattern['type'] == 'attack-pattern':
                self.log_success("STIX Attack Pattern Creation", f"ID: {attack_pattern['id']}")
            else:
                self.log_error("STIX Attack Pattern Creation", f"Wrong type: {attack_pattern['type']}")
                
            # Test malware creation
            malware = STIXObjectFactory.create_object('malware', {
                'name': 'Test Malware',
                'malware_types': ['trojan'],
                'is_family': False
            })
            
            if malware['type'] == 'malware':
                self.log_success("STIX Malware Creation", f"ID: {malware['id']}")
            else:
                self.log_error("STIX Malware Creation", f"Wrong type: {malware['type']}")
                
        except Exception as e:
            self.log_error("STIX Object Creation", e)
            
    def test_collection_operations(self):
        """Test collection and bundle operations"""
        try:
            # Get a collection with data
            collection = Collection.objects.annotate(
                object_count=models.Count('stix_objects')
            ).filter(object_count__gt=0).first()
            
            if not collection:
                self.log_error("Collection Operations", "No collections with data found")
                return
                
            # Test bundle generation
            bundle = generate_bundle_from_collection(collection)
            
            if isinstance(bundle, dict) and bundle.get('type') == 'bundle':
                object_count = len(bundle.get('objects', []))
                self.log_success("Bundle Generation", f"Generated bundle with {object_count} objects")
            else:
                self.log_error("Bundle Generation", "Invalid bundle structure")
                
            # Test collection object count
            db_count = collection.stix_objects.count()
            bundle_count = len([obj for obj in bundle['objects'] if obj['type'] != 'identity'])
            
            if db_count > 0:
                self.log_success("Collection Object Count", f"Collection has {db_count} objects")
            else:
                self.log_error("Collection Object Count", "Collection is empty")
                
        except Exception as e:
            self.log_error("Collection Operations", e)
            
    def test_feed_publishing(self):
        """Test feed publishing functionality"""
        try:
            # Get a feed
            feed = Feed.objects.first()
            if not feed:
                self.log_error("Feed Publishing", "No feeds found")
                return
                
            # Test feed publishing
            result = publish_feed(feed)
            
            if isinstance(result, dict) and result.get('status') == 'success':
                self.log_success("Feed Publishing", f"Published feed with {result.get('object_count', 0)} objects")
            else:
                self.log_error("Feed Publishing", f"Publishing failed: {result}")
                
            # Verify feed was updated
            feed.refresh_from_db()
            if feed.publish_count > 0:
                self.log_success("Feed Update", f"Publish count: {feed.publish_count}")
            else:
                self.log_error("Feed Update", "Feed publish count not updated")
                
        except Exception as e:
            self.log_error("Feed Publishing", e)
            
    def test_otx_integration(self):
        """Test OTX integration"""
        try:
            # Check OTX configuration
            from django.conf import settings
            if hasattr(settings, 'OTX_SETTINGS'):
                otx_config = settings.OTX_SETTINGS
                if otx_config.get('ENABLED'):
                    self.log_success("OTX Configuration", "OTX is enabled")
                else:
                    self.log_error("OTX Configuration", "OTX is disabled")
                    return
            else:
                self.log_error("OTX Configuration", "OTX settings not found")
                return
                
            # Test OTX API connection
            api_key = otx_config.get('API_KEY')
            if api_key:
                client = OTXClient(api_key)
                user_info = client.get_user_info()
                if user_info and 'username' in user_info:
                    self.log_success("OTX API Connection", f"Connected as: {user_info['username']}")
                else:
                    self.log_error("OTX API Connection", "Failed to get user info")
            else:
                self.log_error("OTX API Key", "No API key configured")
                
            # Check OTX data
            otx_org = Organization.objects.filter(name__icontains='OTX').first()
            if otx_org:
                otx_stix_count = STIXObject.objects.filter(source_organization=otx_org).count()
                if otx_stix_count > 0:
                    self.log_success("OTX Data Integration", f"{otx_stix_count} objects from OTX")
                else:
                    self.log_error("OTX Data Integration", "No OTX data found")
            else:
                self.log_error("OTX Organization", "OTX organization not found")
                
        except Exception as e:
            self.log_error("OTX Integration", e)
            
    def test_taxii_api(self):
        """Test TAXII API endpoints"""
        try:
            # Start a test server
            import subprocess
            import time
            import signal
            
            # Check if server is already running
            try:
                response = requests.get('http://127.0.0.1:8000/', timeout=2)
                server_running = True
            except:
                server_running = False
                
            if not server_running:
                # Start server in background
                server_process = subprocess.Popen(
                    ['python3', 'manage.py', 'runserver', '--noreload'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(5)  # Wait for server to start
                
                # Test if server started
                try:
                    response = requests.get('http://127.0.0.1:8000/', timeout=2)
                    server_running = True
                except:
                    server_running = False
                    if 'server_process' in locals():
                        server_process.terminate()
                    self.log_error("TAXII Server", "Failed to start test server")
                    return
            else:
                server_process = None
                
            try:
                # Test TAXII discovery
                response = requests.get(
                    'http://127.0.0.1:8000/taxii2/',
                    auth=('admin', 'admin123'),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_success("TAXII Discovery", f"Title: {data.get('title', 'Unknown')}")
                else:
                    self.log_error("TAXII Discovery", f"HTTP {response.status_code}")
                    
                # Test collections endpoint
                response = requests.get(
                    'http://127.0.0.1:8000/taxii2/collections/',
                    auth=('admin', 'admin123'),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    collection_count = len(data.get('collections', []))
                    self.log_success("TAXII Collections", f"{collection_count} collections available")
                else:
                    self.log_error("TAXII Collections", f"HTTP {response.status_code}")
                    
                # Test objects endpoint for first collection
                if response.status_code == 200 and data.get('collections'):
                    first_collection_id = data['collections'][0]['id']
                    response = requests.get(
                        f'http://127.0.0.1:8000/taxii2/collections/{first_collection_id}/objects/',
                        auth=('admin', 'admin123'),
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        objects_data = response.json()
                        object_count = len(objects_data.get('objects', []))
                        self.log_success("TAXII Objects", f"{object_count} objects in first collection")
                    else:
                        self.log_error("TAXII Objects", f"HTTP {response.status_code}")
                        
            finally:
                # Clean up server process if we started it
                if server_process:
                    server_process.terminate()
                    time.sleep(2)
                    
        except Exception as e:
            self.log_error("TAXII API Testing", e)
            
    def test_data_integrity(self):
        """Test data integrity and relationships"""
        try:
            # Test organization-collection relationships
            orgs_with_collections = Organization.objects.filter(owned_collections__isnull=False).distinct().count()
            total_orgs = Organization.objects.count()
            
            if orgs_with_collections > 0:
                self.log_success("Organization-Collection Relationships", f"{orgs_with_collections}/{total_orgs} orgs have collections")
            else:
                self.log_error("Organization-Collection Relationships", "No organizations have collections")
                
            # Test collection-object relationships
            collections_with_objects = Collection.objects.filter(stix_objects__isnull=False).distinct().count()
            total_collections = Collection.objects.count()
            
            if collections_with_objects > 0:
                self.log_success("Collection-Object Relationships", f"{collections_with_objects}/{total_collections} collections have objects")
            else:
                self.log_error("Collection-Object Relationships", "No collections have objects")
                
            # Test feed-collection relationships
            feeds_with_collections = Feed.objects.filter(collection__isnull=False).count()
            total_feeds = Feed.objects.count()
            
            if feeds_with_collections == total_feeds and total_feeds > 0:
                self.log_success("Feed-Collection Relationships", f"All {total_feeds} feeds have collections")
            else:
                self.log_error("Feed-Collection Relationships", f"Only {feeds_with_collections}/{total_feeds} feeds have collections")
                
            # Test STIX object data integrity
            stix_objects_with_org = STIXObject.objects.filter(source_organization__isnull=False).count()
            total_stix = STIXObject.objects.count()
            
            if stix_objects_with_org > 0:
                self.log_success("STIX Object Integrity", f"{stix_objects_with_org}/{total_stix} objects have source organizations")
            else:
                self.log_error("STIX Object Integrity", "No STIX objects have source organizations")
                
        except Exception as e:
            self.log_error("Data Integrity", e)
            
    def test_security_configuration(self):
        """Test security configuration"""
        try:
            from django.conf import settings
            
            # Test database security
            db_settings = connection.settings_dict
            if db_settings['PASSWORD']:
                self.log_success("Database Security", "Database password is configured")
            else:
                self.log_error("Database Security", "No database password configured")
                
            # Test SECRET_KEY
            if settings.SECRET_KEY and len(settings.SECRET_KEY) > 20:
                self.log_success("Django Security", "SECRET_KEY is configured")
            else:
                self.log_error("Django Security", "SECRET_KEY is weak or missing")
                
            # Test DEBUG setting
            if settings.DEBUG:
                self.log_success("Debug Mode", "DEBUG=True (development)")
            else:
                self.log_success("Debug Mode", "DEBUG=False (production)")
                
            # Test allowed hosts
            if settings.ALLOWED_HOSTS:
                self.log_success("Allowed Hosts", f"{len(settings.ALLOWED_HOSTS)} hosts configured")
            else:
                self.log_error("Allowed Hosts", "No allowed hosts configured")
                
        except Exception as e:
            self.log_error("Security Configuration", e)
            
    def run_django_tests(self):
        """Run Django unit tests"""
        try:
            from django.test.utils import get_runner
            
            # Configure test runner
            TestRunner = get_runner(settings)
            test_runner = TestRunner(verbosity=1, interactive=False)
            
            # Run tests
            failures = test_runner.run_tests(['crisp_threat_intel.tests'])
            
            if failures == 0:
                self.log_success("Django Unit Tests", "All Django tests passed")
            else:
                self.log_error("Django Unit Tests", f"{failures} test(s) failed")
                
        except Exception as e:
            self.log_error("Django Unit Tests", e)
            
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("="*80)
        print("CRISP THREAT INTELLIGENCE PLATFORM - COMPREHENSIVE TEST SUITE")
        print("="*80)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all test categories
        print("🔍 Testing Database Connectivity...")
        self.test_database_connectivity()
        print()
        
        print("🏗️  Testing Model Operations...")
        self.test_model_operations()
        print()
        
        print("📊 Testing STIX Object Creation...")
        self.test_stix_object_creation()
        print()
        
        print("📦 Testing Collection Operations...")
        self.test_collection_operations()
        print()
        
        print("📡 Testing Feed Publishing...")
        self.test_feed_publishing()
        print()
        
        print("🌐 Testing OTX Integration...")
        self.test_otx_integration()
        print()
        
        print("🔗 Testing TAXII API...")
        self.test_taxii_api()
        print()
        
        print("🔐 Testing Data Integrity...")
        self.test_data_integrity()
        print()
        
        print("🛡️  Testing Security Configuration...")
        self.test_security_configuration()
        print()
        
        print("🧪 Running Django Unit Tests...")
        self.run_django_tests()
        print()
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print("="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {self.passed_tests + self.failed_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/(self.passed_tests+self.failed_tests)*100):.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if self.errors:
            print("\n❌ FAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")
        else:
            print("\n✅ ALL TESTS PASSED!")
            
        print(f"\nCompleted: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        return self.failed_tests == 0

if __name__ == '__main__':
    # Import django models here to avoid import issues
    from django.db import models
    
    test_suite = ComprehensiveTestSuite()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
CRISP Threat Intelligence Platform - Functionality Verification Test
This script verifies that all core functionality works correctly:
1. STIX Object Creation
2. Collection Management
3. Feed Publishing
4. TAXII API
5. OTX Integration
"""

import os
import sys
import json
import requests
from datetime import datetime

# Django setup
import django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_threat_intel.settings')
django.setup()

from django.contrib.auth.models import User
from crisp_threat_intel.models import Organization, STIXObject, Collection, CollectionObject, Feed
from crisp_threat_intel.utils import get_or_create_identity, generate_bundle_from_collection
from crisp_threat_intel.factories.stix_factory import STIXObjectFactory

class CRISPFunctionalityTest:
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.errors = []
        
    def log_success(self, message):
        print(f"✓ {message}")
        self.passed_tests += 1
        
    def log_error(self, message, error=None):
        error_msg = f"✗ {message}"
        if error:
            error_msg += f": {str(error)}"
        print(error_msg)
        self.errors.append(error_msg)
        self.failed_tests += 1
        
    def test_stix_object_creation(self):
        """Test STIX object creation using factory"""
        try:
            # Test indicator creation
            indicator = STIXObjectFactory.create_object('indicator', {
                'pattern': "[domain-name:value = 'test-malicious.example.com']",
                'labels': ['malicious-activity'],
                'name': 'Test Indicator'
            })
            
            assert indicator['type'] == 'indicator'
            assert 'test-malicious.example.com' in indicator['pattern']
            assert indicator['labels'] == ['malicious-activity']
            
            self.log_success("STIX Indicator creation")
            
            # Test attack pattern creation
            attack_pattern = STIXObjectFactory.create_object('attack-pattern', {
                'name': 'Test Attack Pattern',
                'description': 'Test attack pattern for verification'
            })
            
            assert attack_pattern['type'] == 'attack-pattern'
            assert attack_pattern['name'] == 'Test Attack Pattern'
            
            self.log_success("STIX Attack Pattern creation")
            
        except Exception as e:
            self.log_error("STIX object creation", e)
            
    def test_database_operations(self):
        """Test database operations with STIX objects"""
        try:
            # Get or create test organization
            admin_user = User.objects.filter(username='admin').first()
            if not admin_user:
                self.log_error("Admin user not found. Run setup_crisp first.")
                return
                
            # Create test organization
            org, created = Organization.objects.get_or_create(
                name='Test Verification Org',
                defaults={
                    'description': 'Test organization for verification',
                    'identity_class': 'organization',
                    'sectors': ['education'],
                    'contact_email': 'test@example.com',
                    'created_by': admin_user
                }
            )
            
            self.log_success(f"Organization {'created' if created else 'retrieved'}: {org.name}")
            
            # Create test collection
            collection, created = Collection.objects.get_or_create(
                title='Test Verification Collection',
                defaults={
                    'description': 'Test collection for verification',
                    'alias': 'test-verify',
                    'owner': org,
                    'can_read': True,
                    'can_write': True
                }
            )
            
            self.log_success(f"Collection {'created' if created else 'retrieved'}: {collection.title}")
            
            # Create STIX object in database
            stix_data = STIXObjectFactory.create_object('indicator', {
                'pattern': "[file:hashes.SHA256 = 'abcd1234567890abcdef']",
                'labels': ['malicious-activity'],
                'name': 'Test Verification Indicator'
            })
            
            db_stix_object, created = STIXObject.objects.get_or_create(
                stix_id=stix_data['id'],
                defaults={
                    'stix_type': stix_data['type'],
                    'spec_version': stix_data['spec_version'],
                    'created': stix_data['created'],
                    'modified': stix_data['modified'],
                    'labels': stix_data['labels'],
                    'raw_data': stix_data,
                    'source_organization': org,
                    'created_by': admin_user
                }
            )
            
            self.log_success(f"STIX Object {'created' if created else 'retrieved'}: {db_stix_object.stix_id}")
            
            # Add to collection
            collection_obj, created = CollectionObject.objects.get_or_create(
                collection=collection,
                stix_object=db_stix_object
            )
            
            self.log_success(f"Collection Object {'created' if created else 'exists'}")
            
            return org, collection, db_stix_object
            
        except Exception as e:
            self.log_error("Database operations", e)
            return None, None, None
            
    def test_bundle_generation(self, collection):
        """Test bundle generation from collection"""
        if not collection:
            return None
            
        try:
            bundle = generate_bundle_from_collection(collection)
            
            assert isinstance(bundle, dict)
            assert bundle['type'] == 'bundle'
            assert 'objects' in bundle
            assert len(bundle['objects']) > 0
            
            object_types = [obj['type'] for obj in bundle['objects']]
            
            self.log_success(f"Bundle generation: {len(bundle['objects'])} objects")
            self.log_success(f"Object types: {', '.join(set(object_types))}")
            
            return bundle
            
        except Exception as e:
            self.log_error("Bundle generation", e)
            return None
            
    def test_feed_creation(self, collection):
        """Test feed creation and basic operations"""
        if not collection:
            return None
            
        try:
            admin_user = User.objects.filter(username='admin').first()
            
            feed, created = Feed.objects.get_or_create(
                name='Test Verification Feed',
                defaults={
                    'description': 'Test feed for verification',
                    'collection': collection,
                    'update_interval': 3600,
                    'status': 'active',
                    'created_by': admin_user
                }
            )
            
            self.log_success(f"Feed {'created' if created else 'retrieved'}: {feed.name}")
            
            # Test feed metadata
            assert feed.collection == collection
            assert feed.status == 'active'
            
            self.log_success("Feed validation")
            
            return feed
            
        except Exception as e:
            self.log_error("Feed creation", e)
            return None
            
    def test_data_counts(self):
        """Test data counts in database"""
        try:
            org_count = Organization.objects.count()
            stix_count = STIXObject.objects.count()
            collection_count = Collection.objects.count()
            feed_count = Feed.objects.count()
            
            self.log_success(f"Database counts: {org_count} orgs, {stix_count} STIX objects, {collection_count} collections, {feed_count} feeds")
            
            # Check OTX data
            otx_org = Organization.objects.filter(name__icontains='OTX').first()
            if otx_org:
                otx_stix_count = STIXObject.objects.filter(source_organization=otx_org).count()
                self.log_success(f"OTX Integration: {otx_stix_count} objects from OTX")
            else:
                self.log_error("OTX organization not found - OTX integration may not be set up")
                
        except Exception as e:
            self.log_error("Data count verification", e)
            
    def test_taxii_endpoints(self):
        """Test TAXII endpoints (if server is running)"""
        try:
            import subprocess
            import time
            
            # Check if server is running
            try:
                response = requests.get('http://127.0.0.1:8000/', timeout=2)
                server_running = True
            except:
                server_running = False
                
            if not server_running:
                self.log_error("Django server not running - start with 'python manage.py runserver' to test TAXII endpoints")
                return
                
            # Test TAXII discovery
            try:
                response = requests.get(
                    'http://127.0.0.1:8000/taxii2/',
                    auth=('admin', 'admin123'),
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_success(f"TAXII Discovery: {data.get('title', 'Unknown')}")
                else:
                    self.log_error(f"TAXII Discovery failed: {response.status_code}")
                    
            except Exception as e:
                self.log_error("TAXII Discovery", e)
                
            # Test collections endpoint
            try:
                response = requests.get(
                    'http://127.0.0.1:8000/taxii2/collections/',
                    auth=('admin', 'admin123'),
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    collection_count = len(data.get('collections', []))
                    self.log_success(f"TAXII Collections: {collection_count} collections available")
                else:
                    self.log_error(f"TAXII Collections failed: {response.status_code}")
                    
            except Exception as e:
                self.log_error("TAXII Collections", e)
                
        except Exception as e:
            self.log_error("TAXII endpoint testing", e)
            
    def run_all_tests(self):
        """Run all functionality tests"""
        print("="*60)
        print("CRISP Threat Intelligence Platform - Functionality Test")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run tests
        self.test_stix_object_creation()
        org, collection, stix_obj = self.test_database_operations()
        bundle = self.test_bundle_generation(collection)
        feed = self.test_feed_creation(collection)
        self.test_data_counts()
        self.test_taxii_endpoints()
        
        # Summary
        print()
        print("="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/(self.passed_tests+self.failed_tests)*100):.1f}%")
        
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  {error}")
                
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return self.failed_tests == 0

if __name__ == '__main__':
    test = CRISPFunctionalityTest()
    success = test.run_all_tests()
    sys.exit(0 if success else 1)

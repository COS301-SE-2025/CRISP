#!/usr/bin/env python3
"""
Script to publish threat intelligence from local machine to Pi Django server
Uses the existing threat_intel_service models and APIs
"""
import os
import sys
import requests
import json
from datetime import datetime
import uuid

# Add the threat_intel_service to Python path
sys.path.insert(0, 'threat_intel_service')

# Django setup for local threat intel service
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'threat_intel.settings')

import django
django.setup()

# Import your existing threat intel models
from core.models import Organization, STIXObject, Collection, Feed
from trust.models import TrustRelationship

# Pi server configuration
PI_BASE_URL = 'http://100.117.251.119:8001'
PI_USERNAME = 'datadefenders'
PI_PASSWORD = 'DataDefenders123!'

class ThreatIntelPublisher:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        
    def authenticate(self):
        """Authenticate with Pi server"""
        login_data = {
            'username': PI_USERNAME,
            'password': PI_PASSWORD
        }
        
        try:
            response = self.session.post(f'{PI_BASE_URL}/api/auth/login/', json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('token')
                if self.access_token:
                    self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
                    print(f"✅ Authenticated as {data.get('user', {}).get('username', 'unknown')}")
                    return True
            
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def create_organization_on_pi(self, local_org):
        """Create organization on Pi via auth_api"""
        org_data = {
            'name': local_org.name,
            'description': local_org.description or '',
            'location': '',  # Add if you have location data
            'trust_level': 50,  # Default trust level
            'is_active': True
        }
        
        try:
            # Check if organization exists first
            response = self.session.get(f'{PI_BASE_URL}/api/organizations/')
            if response.status_code == 200:
                existing_orgs = response.json()
                if isinstance(existing_orgs, dict) and 'results' in existing_orgs:
                    existing_orgs = existing_orgs['results']
                
                for org in existing_orgs:
                    if org.get('name') == local_org.name:
                        print(f"✅ Found existing organization: {org['name']}")
                        return org['id']
            
            # Create new organization
            response = self.session.post(f'{PI_BASE_URL}/api/organizations/', json=org_data)
            if response.status_code == 201:
                org = response.json()
                print(f"✅ Created organization: {org['name']}")
                return org['id']
            else:
                print(f"❌ Failed to create organization: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating organization: {e}")
            return None
    
    def create_threat_feed_on_pi(self, org_id, feed_name, description=""):
        """Create threat feed on Pi"""
        feed_data = {
            'name': feed_name,
            'description': description,
            'feed_type': 'stix_taxii',
            'url': '',
            'api_key': '',
            'is_active': True
        }
        
        try:
            response = self.session.post(f'{PI_BASE_URL}/api/threat-feeds/', json=feed_data)
            if response.status_code == 201:
                feed = response.json()
                print(f"✅ Created threat feed: {feed['name']}")
                return feed['id']
            else:
                print(f"❌ Failed to create threat feed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error creating threat feed: {e}")
            return None
    
    def publish_stix_objects(self, feed_id, stix_objects):
        """Publish STIX objects as IoCs to Pi server"""
        if not stix_objects:
            print("⚠️ No STIX objects to publish")
            return False
        
        # Convert STIX objects to IoCs for the Pi server
        indicators_created = 0
        
        for obj in stix_objects:
            try:
                # Extract indicator data from STIX object
                raw_data = obj.raw_data if hasattr(obj, 'raw_data') else {}
                
                # Create IoC data
                ioc_data = {
                    'indicator_type': self._map_stix_type_to_ioc_type(obj.stix_type),
                    'value': self._extract_indicator_value(raw_data),
                    'description': raw_data.get('description', obj.stix_id),
                    'confidence': raw_data.get('confidence', 50),
                    'severity': 'medium',  # Default severity
                    'source': 'Threat Intel Service',
                    'tags': raw_data.get('labels', []),
                    'first_seen': obj.created.isoformat() if hasattr(obj, 'created') else datetime.now().isoformat(),
                    'is_active': True
                }
                
                # Only create if we have a valid indicator value
                if ioc_data['value']:
                    response = self.session.post(f'{PI_BASE_URL}/api/indicators/', json=ioc_data)
                    if response.status_code == 201:
                        indicators_created += 1
                    else:
                        print(f"⚠️ Failed to create IoC for {obj.stix_id}: {response.status_code}")
                
            except Exception as e:
                print(f"⚠️ Error processing STIX object {obj.stix_id}: {e}")
                continue
        
        print(f"✅ Created {indicators_created} indicators from {len(stix_objects)} STIX objects")
        return indicators_created > 0
    
    def _map_stix_type_to_ioc_type(self, stix_type):
        """Map STIX types to IoC types"""
        mapping = {
            'indicator': 'hash',
            'malware': 'malware',
            'attack-pattern': 'technique',
            'threat-actor': 'actor',
            'vulnerability': 'vulnerability'
        }
        return mapping.get(stix_type, 'other')
    
    def _extract_indicator_value(self, raw_data):
        """Extract indicator value from STIX raw data"""
        if 'pattern' in raw_data:
            # Try to extract value from STIX pattern
            pattern = raw_data['pattern']
            if 'file:hashes.MD5' in pattern:
                return pattern.split("'")[1] if "'" in pattern else pattern
            elif 'domain-name:value' in pattern:
                return pattern.split("'")[1] if "'" in pattern else pattern
            elif 'ipv4-addr:value' in pattern:
                return pattern.split("'")[1] if "'" in pattern else pattern
            else:
                return pattern
        
        # Fallback to other fields
        for field in ['value', 'name', 'id']:
            if field in raw_data:
                return raw_data[field]
        
        return None
    
    def sync_collection(self, collection_name):
        """Sync a specific collection from local to Pi"""
        try:
            collection = Collection.objects.get(title=collection_name)
            print(f"🔄 Syncing collection: {collection.title}")
            
            # Create organization on Pi
            org_id = self.create_organization_on_pi(collection.owner)
            if not org_id:
                return False
            
            # Create threat feed
            feed_id = self.create_threat_feed_on_pi(
                org_id, 
                f"{collection.title} Feed",
                f"Threat feed for {collection.title} collection"
            )
            if not feed_id:
                return False
            
            # Get STIX objects from collection
            stix_objects = STIXObject.objects.filter(
                collections__collection=collection
            ).distinct()
            
            print(f"📊 Found {stix_objects.count()} STIX objects in collection")
            
            # Publish objects
            return self.publish_stix_objects(feed_id, stix_objects)
            
        except Collection.DoesNotExist:
            print(f"❌ Collection '{collection_name}' not found")
            return False
        except Exception as e:
            print(f"❌ Error syncing collection: {e}")
            return False
    
    def sync_all_collections(self):
        """Sync all collections from local to Pi"""
        try:
            collections = Collection.objects.all()
            print(f"🔄 Found {collections.count()} collections to sync...")
            
            if collections.count() == 0:
                print("⚠️ No collections found in local threat intel service")
                return False
            
            success_count = 0
            for collection in collections:
                try:
                    if self.sync_collection(collection.title):
                        success_count += 1
                except Exception as e:
                    print(f"❌ Failed to sync collection {collection.title}: {e}")
                    continue
            
            print(f"✅ Successfully synced {success_count}/{collections.count()} collections")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Error in sync_all_collections: {e}")
            return False

def main():
    print("🚀 Starting threat intelligence migration to Pi...")
    print(f"   Local DB: {os.path.join(os.getcwd(), 'threat_intel_service')}")
    print(f"   Pi Server: {PI_BASE_URL}")
    
    publisher = ThreatIntelPublisher()
    
    # Authenticate
    if not publisher.authenticate():
        print("❌ Migration failed - authentication error")
        return False
    
    # Sync all collections
    success = publisher.sync_all_collections()
    
    if success:
        print("🎉 Migration completed successfully!")
        print(f"   Pi Server: {PI_BASE_URL}")
        print(f"   Admin: {PI_BASE_URL}/admin/")
        print(f"   Login: {PI_USERNAME} / {PI_PASSWORD}")
    else:
        print("❌ Migration completed with errors")
    
    return success

if __name__ == '__main__':
    main()

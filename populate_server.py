#!/usr/bin/env python3
"""
CRISP Server Population Script
Populates the server with comprehensive sample data
"""
import os
import sys
import django
from django.db import transaction
from datetime import datetime, timedelta
from django.utils import timezone
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.settings')
sys.path.append('.')
django.setup()

from core.models.auth import Organization, CustomUser
from core.models.stix_object import STIXObject, Collection, Feed
from core.models.indicator import Indicator
from core.models.ttp_data import TTPData
from core.models.threat_feed import ThreatFeed
from core.models.trust_models.models import TrustLevel, TrustRelationship
from core.models.institution import Institution

def create_organizations():
    """Create sample organizations"""
    orgs_data = [
        {
            'name': 'FBI Cyber Division',
            'description': 'Federal Bureau of Investigation Cyber Crime Division',
            'domain': 'fbi.gov',
            'contact_email': 'cyber@fbi.gov',
            'website': 'https://www.fbi.gov/investigate/cyber',
            'sectors': ['government', 'law-enforcement']
        },
        {
            'name': 'Microsoft Security',
            'description': 'Microsoft Threat Intelligence Unit',
            'domain': 'microsoft.com',
            'contact_email': 'security@microsoft.com',
            'website': 'https://www.microsoft.com/security',
            'sectors': ['technology', 'software']
        },
        {
            'name': 'Symantec Research',
            'description': 'Symantec Threat Intelligence Research',
            'domain': 'symantec.com',
            'contact_email': 'research@symantec.com',
            'website': 'https://www.symantec.com',
            'sectors': ['cybersecurity', 'technology']
        },
        {
            'name': 'University of Pretoria',
            'description': 'University of Pretoria Cybersecurity Research Unit',
            'domain': 'up.ac.za',
            'contact_email': 'cyber@up.ac.za',
            'website': 'https://www.up.ac.za',
            'sectors': ['education', 'research']
        },
        {
            'name': 'SANS Institute',
            'description': 'SANS Internet Storm Center',
            'domain': 'sans.org',
            'contact_email': 'isc@sans.org',
            'website': 'https://isc.sans.edu',
            'sectors': ['education', 'cybersecurity']
        }
    ]
    
    organizations = []
    for org_data in orgs_data:
        org, created = Organization.objects.get_or_create(
            name=org_data['name'],
            defaults=org_data
        )
        organizations.append(org)
        print(f"{'Created' if created else 'Found'} organization: {org.name}")
    
    return organizations

def create_users(organizations):
    """Create sample users for each organization"""
    users_data = [
        {'username': 'fbi_analyst', 'email': 'analyst@fbi.gov', 'first_name': 'John', 'last_name': 'Smith', 'role': 'analyst', 'org_index': 0},
        {'username': 'fbi_admin', 'email': 'admin@fbi.gov', 'first_name': 'Sarah', 'last_name': 'Johnson', 'role': 'admin', 'org_index': 0},
        {'username': 'ms_researcher', 'email': 'researcher@microsoft.com', 'first_name': 'David', 'last_name': 'Chen', 'role': 'publisher', 'org_index': 1},
        {'username': 'ms_analyst', 'email': 'analyst@microsoft.com', 'first_name': 'Lisa', 'last_name': 'Williams', 'role': 'analyst', 'org_index': 1},
        {'username': 'symantec_lead', 'email': 'lead@symantec.com', 'first_name': 'Michael', 'last_name': 'Brown', 'role': 'admin', 'org_index': 2},
        {'username': 'up_student', 'email': 'student@up.ac.za', 'first_name': 'Thabo', 'last_name': 'Mthembu', 'role': 'viewer', 'org_index': 3},
        {'username': 'up_professor', 'email': 'prof@up.ac.za', 'first_name': 'Marie', 'last_name': 'Van Der Merwe', 'role': 'admin', 'org_index': 3},
        {'username': 'sans_instructor', 'email': 'instructor@sans.org', 'first_name': 'Robert', 'last_name': 'Davis', 'role': 'publisher', 'org_index': 4},
    ]
    
    users = []
    for user_data in users_data:
        org = organizations[user_data['org_index']]
        user, created = CustomUser.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role'],
                'organization': org,
                'is_verified': True,
                'is_publisher': user_data['role'] in ['publisher', 'admin']
            }
        )
        if created:
            user.set_password('password123')
            user.save()
        users.append(user)
        print(f"{'Created' if created else 'Found'} user: {user.username} ({org.name})")
    
    return users

def create_trust_levels():
    """Create trust levels"""
    trust_levels_data = [
        {'name': 'Verified Government', 'level': 'complete', 'numerical_value': 95, 'description': 'Verified government agencies'},
        {'name': 'Trusted Commercial', 'level': 'high', 'numerical_value': 85, 'description': 'Established commercial security vendors'},
        {'name': 'Academic Institution', 'level': 'high', 'numerical_value': 75, 'description': 'Universities and research institutions'},
        {'name': 'Community Contributor', 'level': 'medium', 'numerical_value': 65, 'description': 'Verified community contributors'},
        {'name': 'Unknown Source', 'level': 'low', 'numerical_value': 30, 'description': 'Unverified or unknown sources'},
    ]
    
    trust_levels = []
    for tl_data in trust_levels_data:
        tl, created = TrustLevel.objects.get_or_create(
            name=tl_data['name'],
            defaults=tl_data
        )
        trust_levels.append(tl)
        print(f"{'Created' if created else 'Found'} trust level: {tl.name}")
    
    return trust_levels

def create_threat_feeds(organizations, institutions):
    """Create threat feeds"""
    feeds_data = [
        {
            'name': 'FBI Cyber Threat Feed',
            'description': 'Official FBI cyber threat indicators',
            'taxii_server_url': 'https://fbi.gov/taxii/feeds/cyber',
            'taxii_collection_id': 'fbi-cyber-collection',
            'is_external': True,
            'org_index': 0
        },
        {
            'name': 'Microsoft Threat Intelligence',
            'description': 'Microsoft threat intelligence indicators',
            'taxii_server_url': 'https://microsoft.com/api/threat-intel',
            'taxii_collection_id': 'ms-threat-intel',
            'is_external': True,
            'org_index': 1
        },
        {
            'name': 'Symantec Research Feed',
            'description': 'Symantec research threat indicators',
            'taxii_server_url': 'https://symantec.com/feeds/research',
            'taxii_collection_id': 'symantec-research',
            'is_external': True,
            'org_index': 2
        },
        {
            'name': 'UP Research Collection',
            'description': 'University research threat data',
            'taxii_server_url': 'https://up.ac.za/cyber/feeds',
            'taxii_collection_id': 'up-research',
            'is_external': False,
            'org_index': 3
        },
        {
            'name': 'SANS ISC Feed',
            'description': 'SANS Internet Storm Center data',
            'taxii_server_url': 'https://isc.sans.edu/feeds/all',
            'taxii_collection_id': 'sans-isc',
            'is_external': True,
            'org_index': 4
        }
    ]
    
    feeds = []
    for feed_data in feeds_data:
        institution = institutions[feed_data['org_index']]
        feed, created = ThreatFeed.objects.get_or_create(
            name=feed_data['name'],
            defaults={
                'description': feed_data['description'],
                'taxii_server_url': feed_data['taxii_server_url'],
                'taxii_collection_id': feed_data['taxii_collection_id'],
                'is_external': feed_data['is_external'],
                'owner': institution,
                'is_public': True,
                'last_sync': timezone.now() - timedelta(hours=1)
            }
        )
        feeds.append(feed)
        print(f"{'Created' if created else 'Found'} threat feed: {feed.name}")
    
    return feeds

def create_collections(organizations):
    """Create STIX collections"""
    collections_data = [
        {'title': 'Malware Indicators', 'alias': 'malware-indicators', 'description': 'Collection of malware indicators', 'org_index': 0},
        {'title': 'APT Campaign Data', 'alias': 'apt-campaigns', 'description': 'Advanced Persistent Threat campaign information', 'org_index': 1},
        {'title': 'Network Indicators', 'alias': 'network-indicators', 'description': 'Network-based threat indicators', 'org_index': 2},
        {'title': 'Research Artifacts', 'alias': 'research-artifacts', 'description': 'Academic research threat artifacts', 'org_index': 3},
        {'title': 'Incident Response Data', 'alias': 'incident-response', 'description': 'Incident response and forensic data', 'org_index': 4},
    ]
    
    collections = []
    for coll_data in collections_data:
        org = organizations[coll_data['org_index']]
        collection, created = Collection.objects.get_or_create(
            title=coll_data['title'],
            defaults={
                'alias': coll_data['alias'],
                'description': coll_data['description'],
                'owner': org,
                'can_read': True,
                'can_write': False,
                'media_types': ['application/vnd.oasis.stix+json']
            }
        )
        collections.append(collection)
        print(f"{'Created' if created else 'Found'} collection: {collection.title}")
    
    return collections

def create_indicators(threat_feeds):
    """Create sample indicators"""
    indicators_data = [
        {
            'value': '192.168.1.100',
            'indicator_type': 'ip',
            'description': 'Suspicious IP address from malware C&C',
            'confidence': 85,
            'feed_index': 0
        },
        {
            'value': 'malware.example.com',
            'indicator_type': 'domain',
            'description': 'Known malware distribution domain',
            'confidence': 90,
            'feed_index': 1
        },
        {
            'value': 'c99465aa419b42254ebe4a4b1b6f26e8',
            'indicator_type': 'file_hash',
            'hash_type': 'md5',
            'description': 'MD5 hash of known malware sample',
            'confidence': 95,
            'feed_index': 2
        },
        {
            'value': 'https://phishing.badsite.com/login',
            'indicator_type': 'url',
            'description': 'Phishing URL targeting banking credentials',
            'confidence': 88,
            'feed_index': 3
        },
        {
            'value': 'user@suspicious.email.com',
            'indicator_type': 'email',
            'description': 'Email address used in spear phishing campaign',
            'confidence': 80,
            'feed_index': 4
        }
    ]
    
    indicators = []
    for ind_data in indicators_data:
        feed = threat_feeds[ind_data['feed_index']]
        indicator, created = Indicator.objects.get_or_create(
            value=ind_data['value'],
            type=ind_data['indicator_type'],
            defaults={
                'description': ind_data['description'],
                'confidence': ind_data['confidence'],
                'threat_feed': feed,
                'stix_id': f"indicator--{uuid.uuid4()}",
                'first_seen': timezone.now() - timedelta(days=7),
                'last_seen': timezone.now() - timedelta(hours=2),
                'hash_type': ind_data.get('hash_type')
            }
        )
        indicators.append(indicator)
        print(f"{'Created' if created else 'Found'} indicator: {indicator.value}")
    
    return indicators

def create_ttp_data(threat_feeds):
    """Create TTP (Tactics, Techniques, Procedures) data"""
    ttp_data_list = [
        {
            'name': 'Spear Phishing Attachment',
            'description': 'Adversaries may send spear phishing emails with malicious attachments',
            'tactic': 'Initial Access',
            'technique': 'T1566.001',
            'feed_index': 0
        },
        {
            'name': 'PowerShell Execution',
            'description': 'Adversaries may abuse PowerShell commands for execution',
            'tactic': 'Execution',
            'technique': 'T1059.001',
            'feed_index': 1
        },
        {
            'name': 'Registry Run Keys',
            'description': 'Adding entries to registry run keys for persistence',
            'tactic': 'Persistence',
            'technique': 'T1547.001',
            'feed_index': 2
        },
        {
            'name': 'Process Injection',
            'description': 'Injecting code into legitimate processes to evade detection',
            'tactic': 'Defense Evasion',
            'technique': 'T1055',
            'feed_index': 3
        },
        {
            'name': 'Data from Local System',
            'description': 'Collecting data from local system before exfiltration',
            'tactic': 'Collection',
            'technique': 'T1005',
            'feed_index': 4
        }
    ]
    
    ttps = []
    for ttp_data in ttp_data_list:
        feed = threat_feeds[ttp_data['feed_index']]
        ttp, created = TTPData.objects.get_or_create(
            name=ttp_data['name'],
            mitre_technique_id=ttp_data['technique'],
            defaults={
                'description': ttp_data['description'],
                'mitre_tactic': ttp_data['tactic'],
                'threat_feed': feed,
                'stix_id': f"attack-pattern--{uuid.uuid4()}"
            }
        )
        ttps.append(ttp)
        print(f"{'Created' if created else 'Found'} TTP: {ttp.name}")
    
    return ttps

def create_trust_relationships(organizations, trust_levels):
    """Create trust relationships between organizations"""
    relationships_data = [
        # FBI trusts Microsoft (government trusts commercial)
        {'trustor_index': 0, 'trustee_index': 1, 'trust_level_index': 1, 'relationship_type': 'partnership'},
        # Microsoft trusts Symantec (commercial partnership)
        {'trustor_index': 1, 'trustee_index': 2, 'trust_level_index': 1, 'relationship_type': 'vendor'},
        # University trusts SANS (academic relationship)
        {'trustor_index': 3, 'trustee_index': 4, 'trust_level_index': 2, 'relationship_type': 'educational'},
        # FBI trusts University research
        {'trustor_index': 0, 'trustee_index': 3, 'trust_level_index': 2, 'relationship_type': 'research'},
        # SANS trusts FBI data
        {'trustor_index': 4, 'trustee_index': 0, 'trust_level_index': 0, 'relationship_type': 'institutional'},
    ]
    
    relationships = []
    for rel_data in relationships_data:
        trustor = organizations[rel_data['trustor_index']]
        trustee = organizations[rel_data['trustee_index']]
        trust_level = trust_levels[rel_data['trust_level_index']]
        
        relationship, created = TrustRelationship.objects.get_or_create(
            source_organization=trustor,
            target_organization=trustee,
            defaults={
                'trust_level': trust_level,
                'relationship_type': rel_data['relationship_type'],
                'is_active': True,
                'created_by': 'System',
                'notes': f'Trust relationship between {trustor.name} and {trustee.name}'
            }
        )
        relationships.append(relationship)
        print(f"{'Created' if created else 'Found'} trust relationship: {trustor.name} -> {trustee.name}")
    
    return relationships

def create_institutions(organizations):
    """Create institution records"""
    institutions = []
    for org in organizations:
        institution, created = Institution.objects.get_or_create(
            name=org.name,
            defaults={
                'description': org.description,
                'contact_email': org.contact_email or '',
                'contact_name': 'Admin Contact'
            }
        )
        institutions.append(institution)
        print(f"{'Created' if created else 'Found'} institution: {institution.name}")
    
    return institutions

def main():
    """Main population function"""
    print("🚀 Starting CRISP Server Population...")
    print("=" * 50)
    
    try:
        with transaction.atomic():
            # Create all the data
            print("\n📊 Creating Organizations...")
            organizations = create_organizations()
            
            print("\n🏢 Creating Institutions...")
            institutions = create_institutions(organizations)
            
            print("\n👥 Creating Users...")
            users = create_users(organizations)
            
            print("\n🛡️ Creating Trust Levels...")
            trust_levels = create_trust_levels()
            
            print("\n📡 Creating Threat Feeds...")
            threat_feeds = create_threat_feeds(organizations, institutions)
            
            print("\n📚 Creating Collections...")
            collections = create_collections(organizations)
            
            print("\n🚨 Creating Indicators...")
            indicators = create_indicators(threat_feeds)
            
            print("\n⚔️ Creating TTP Data...")
            ttps = create_ttp_data(threat_feeds)
            
            print("\n🤝 Creating Trust Relationships...")
            relationships = create_trust_relationships(organizations, trust_levels)
            
        print("\n" + "=" * 50)
        print("✅ CRISP Server Population Complete!")
        print("=" * 50)
        print(f"📊 Summary:")
        print(f"   • {len(organizations)} Organizations")
        print(f"   • {len(users)} Users")
        print(f"   • {len(trust_levels)} Trust Levels")
        print(f"   • {len(threat_feeds)} Threat Feeds")
        print(f"   • {len(collections)} Collections")
        print(f"   • {len(indicators)} Indicators")
        print(f"   • {len(ttps)} TTP Records")
        print(f"   • {len(relationships)} Trust Relationships")
        print(f"   • {len(institutions)} Institutions")
        print("\n🌐 Access your populated server at: http://127.0.0.1:8000/admin/")
        print("🔑 Login with: admin / admin")
        
    except Exception as e:
        print(f"❌ Error during population: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
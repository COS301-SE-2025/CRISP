"""
Setup CRISP Platform Management Command
Complete platform setup with demo data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from crisp_threat_intel.models import Organization, Collection, Feed, STIXObject, CollectionObject
from crisp_threat_intel.utils import get_or_create_identity
from crisp_threat_intel.factories.stix_factory import STIXObjectFactory
import uuid


class Command(BaseCommand):
    help = 'Set up the CRISP platform with initial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-superuser',
            action='store_true',
            help='Skip creating superuser',
        )
        parser.add_argument(
            '--skip-demo',
            action='store_true', 
            help='Skip creating demo data',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up CRISP Threat Intelligence Platform...'))
        
        # Create superuser
        if not options['skip_superuser']:
            self.create_superuser()
        
        # Create sample organizations
        self.create_organizations()
        
        # Create sample collections
        self.create_collections()
        
        # Create demo data
        if not options['skip_demo']:
            self.create_demo_data()
        
        self.stdout.write(self.style.SUCCESS('CRISP platform setup completed successfully!'))

    def create_superuser(self):
        """Create default superuser if not exists"""
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(f'Created superuser: admin/admin123')
        else:
            self.stdout.write('Superuser already exists')

    def create_organizations(self):
        """Create sample organizations"""
        orgs_data = [
            {
                'name': 'University of Pretoria',
                'description': 'Leading South African university',
                'identity_class': 'organization',
                'sectors': ['education'],
                'contact_email': 'security@up.ac.za',
                'website': 'https://www.up.ac.za'
            },
            {
                'name': 'Stellenbosch University', 
                'description': 'Premier research university',
                'identity_class': 'organization',
                'sectors': ['education'],
                'contact_email': 'security@sun.ac.za',
                'website': 'https://www.sun.ac.za'
            },
            {
                'name': 'CRISP Threat Intel Consortium',
                'description': 'Educational threat intelligence sharing consortium',
                'identity_class': 'organization', 
                'sectors': ['education', 'cybersecurity'],
                'contact_email': 'info@crisp-threatintel.org',
                'website': 'https://crisp-threatintel.org'
            }
        ]
        
        admin_user = User.objects.filter(username='admin').first()
        
        for org_data in orgs_data:
            org, created = Organization.objects.get_or_create(
                name=org_data['name'],
                defaults={
                    **org_data,
                    'created_by': admin_user,
                    'stix_id': f"identity--{uuid.uuid4()}"
                }
            )
            if created:
                # Create STIX identity
                get_or_create_identity(org)
                self.stdout.write(f'Created organization: {org.name}')
            else:
                self.stdout.write(f'Organization already exists: {org.name}')

    def create_collections(self):
        """Create sample collections"""
        collections_data = [
            {
                'title': 'Educational Sector Threats',
                'description': 'Threat intelligence focused on educational institutions',
                'alias': 'edu-threats',
                'can_read': True,
                'can_write': True,
                'media_types': ['application/stix+json;version=2.1']
            },
            {
                'title': 'Ransomware Indicators',
                'description': 'Indicators of compromise for ransomware campaigns',
                'alias': 'ransomware-iocs',
                'can_read': True,
                'can_write': True,
                'media_types': ['application/stix+json;version=2.1']
            },
            {
                'title': 'Phishing Campaigns',
                'description': 'Phishing campaign data and indicators',
                'alias': 'phishing-campaigns',
                'can_read': True,
                'can_write': True,
                'media_types': ['application/stix+json;version=2.1']
            }
        ]
        
        # Use first organization as owner
        owner_org = Organization.objects.first()
        if not owner_org:
            self.stdout.write(self.style.ERROR('No organization found. Create organizations first.'))
            return
        
        for collection_data in collections_data:
            collection, created = Collection.objects.get_or_create(
                alias=collection_data['alias'],
                defaults={
                    **collection_data,
                    'owner': owner_org
                }
            )
            if created:
                self.stdout.write(f'Created collection: {collection.title}')
                
                # Create a feed for this collection
                feed, feed_created = Feed.objects.get_or_create(
                    name=f"{collection.title} Feed",
                    collection=collection,
                    defaults={
                        'description': f'Automated feed for {collection.title}',
                        'update_interval': 3600,  # 1 hour
                        'status': 'active'
                    }
                )
                if feed_created:
                    self.stdout.write(f'Created feed: {feed.name}')
            else:
                self.stdout.write(f'Collection already exists: {collection.title}')

    def create_demo_data(self):
        """Create demo STIX objects"""
        collection = Collection.objects.filter(alias='edu-threats').first()
        if not collection:
            self.stdout.write(self.style.ERROR('No collection found for demo data'))
            return
        
        demo_indicators = [
            {
                'pattern': "[domain-name:value = 'malicious-edu-phishing.com']",
                'labels': ['malicious-activity'],
                'name': 'Malicious Educational Phishing Domain',
                'description': 'Domain used in phishing campaigns targeting educational institutions'
            },
            {
                'pattern': "[ipv4-addr:value = '192.168.100.50']",
                'labels': ['malicious-activity'],
                'name': 'C2 Server IP',
                'description': 'Command and control server IP address'
            },
            {
                'pattern': "[file:hashes.SHA256 = 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456']",
                'labels': ['malicious-activity'],
                'name': 'Ransomware Sample',
                'description': 'SHA256 hash of ransomware targeting educational institutions'
            }
        ]
        
        created_count = 0
        for indicator_data in demo_indicators:
            try:
                # Create STIX indicator using factory
                stix_indicator = STIXObjectFactory.create_object('indicator', indicator_data)
                
                # Store in database
                stix_obj = STIXObject.objects.create(
                    stix_id=stix_indicator['id'],
                    stix_type=stix_indicator['type'],
                    spec_version=stix_indicator['spec_version'],
                    created=stix_indicator['created'],
                    modified=stix_indicator['modified'],
                    labels=stix_indicator['labels'],
                    raw_data=stix_indicator,
                    source_organization=collection.owner
                )
                
                # Add to collection
                CollectionObject.objects.get_or_create(
                    collection=collection,
                    stix_object=stix_obj
                )
                
                created_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to create indicator: {e}'))
        
        self.stdout.write(f'Created {created_count} demo indicators')
        
        # Create demo attack pattern
        try:
            attack_pattern_data = {
                'name': 'Spear Phishing via Email',
                'description': 'Targeted phishing attacks via email against educational staff',
                'external_references': [
                    {
                        'source_name': 'mitre-attack',
                        'external_id': 'T1566.001',
                        'url': 'https://attack.mitre.org/techniques/T1566/001'
                    }
                ]
            }
            
            stix_attack_pattern = STIXObjectFactory.create_object('attack-pattern', attack_pattern_data)
            
            stix_obj = STIXObject.objects.create(
                stix_id=stix_attack_pattern['id'],
                stix_type=stix_attack_pattern['type'],
                spec_version=stix_attack_pattern['spec_version'],
                created=stix_attack_pattern['created'],
                modified=stix_attack_pattern['modified'],
                raw_data=stix_attack_pattern,
                source_organization=collection.owner
            )
            
            CollectionObject.objects.get_or_create(
                collection=collection,
                stix_object=stix_obj
            )
            
            self.stdout.write('Created demo attack pattern')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to create attack pattern: {e}'))

        self.stdout.write(f'Demo data created in collection: {collection.title}')
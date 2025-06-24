"""
Setup OTX Integration Management Command
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from crisp_threat_intel.models import Organization, Collection
from crisp_threat_intel.services.otx_service import OTXClient, OTXProcessor
import uuid


class Command(BaseCommand):
    help = 'Set up OTX integration and test connectivity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api-key',
            type=str,
            help='OTX API key (if not set in environment)',
        )
        parser.add_argument(
            '--test-only',
            action='store_true',
            help='Only test connection, do not create collection',
        )
        parser.add_argument(
            '--fetch-data',
            action='store_true',
            help='Fetch recent data from OTX after setup',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up OTX integration...'))
        
        # Get API key
        api_key = options.get('api_key') or settings.OTX_SETTINGS.get('API_KEY')
        if not api_key:
            self.stdout.write(self.style.ERROR('No OTX API key found. Set OTX_API_KEY in environment or use --api-key'))
            return
        
        # Test connection
        if not self.test_connection(api_key):
            return
        
        if options['test_only']:
            self.stdout.write(self.style.SUCCESS('OTX connection test completed successfully!'))
            return
        
        # Create OTX organization
        otx_org = self.create_otx_organization()
        
        # Create OTX collection
        otx_collection = self.create_otx_collection(otx_org)
        
        # Fetch data if requested
        if options['fetch_data']:
            self.fetch_otx_data(otx_org, otx_collection, api_key)
        
        self.stdout.write(self.style.SUCCESS('OTX integration setup completed successfully!'))

    def test_connection(self, api_key):
        """Test OTX API connection"""
        try:
            client = OTXClient(api_key)
            
            self.stdout.write('Testing OTX API connection...')
            if client.test_connection():
                self.stdout.write(self.style.SUCCESS('✓ OTX API connection successful'))
                
                # Get user info
                user_info = client.get_user_info()
                self.stdout.write(f'✓ Connected as: {user_info.get("username", "Unknown")}')
                
                return True
            else:
                self.stdout.write(self.style.ERROR('✗ OTX API connection failed'))
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ OTX API connection error: {e}'))
            return False

    def create_otx_organization(self):
        """Create or get OTX organization"""
        otx_org, created = Organization.objects.get_or_create(
            name='AlienVault OTX',
            defaults={
                'description': 'AlienVault Open Threat Exchange',
                'identity_class': 'organization',
                'sectors': ['cybersecurity'],
                'contact_email': 'support@alienvault.com',
                'website': 'https://otx.alienvault.com',
                'stix_id': f"identity--{uuid.uuid4()}"
            }
        )
        
        if created:
            self.stdout.write(f'✓ Created OTX organization: {otx_org.name}')
        else:
            self.stdout.write(f'✓ Using existing OTX organization: {otx_org.name}')
        
        return otx_org

    def create_otx_collection(self, otx_org):
        """Create or get OTX collection"""
        otx_collection, created = Collection.objects.get_or_create(
            alias='otx-threats',
            defaults={
                'title': 'OTX Threat Intelligence',
                'description': 'Threat intelligence data from AlienVault OTX',
                'owner': otx_org,
                'can_read': True,
                'can_write': True,
                'media_types': ['application/stix+json;version=2.1']
            }
        )
        
        if created:
            self.stdout.write(f'✓ Created OTX collection: {otx_collection.title}')
        else:
            self.stdout.write(f'✓ Using existing OTX collection: {otx_collection.title}')
        
        return otx_collection

    def fetch_otx_data(self, otx_org, otx_collection, api_key):
        """Fetch recent data from OTX"""
        try:
            self.stdout.write('Fetching recent data from OTX...')
            
            processor = OTXProcessor(otx_org, otx_collection)
            results = processor.fetch_and_process_recent_pulses(days_back=7)
            
            if 'error' in results:
                self.stdout.write(self.style.ERROR(f'✗ Failed to fetch OTX data: {results["error"]}'))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Successfully processed {results["processed_pulses"]}/{results["total_pulses"]} pulses'
                ))
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Created {results["created_objects"]} STIX objects'
                ))
                
                if results["errors"]:
                    self.stdout.write(self.style.WARNING(f'⚠ {len(results["errors"])} errors occurred'))
                    for error in results["errors"][:3]:  # Show first 3 errors
                        self.stdout.write(f'  - {error}')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error fetching OTX data: {e}'))

    def show_setup_info(self):
        """Show setup information"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('OTX Integration Setup Complete')
        self.stdout.write('='*50)
        self.stdout.write('Next steps:')
        self.stdout.write('1. Set up periodic OTX data fetching with Celery')
        self.stdout.write('2. Configure trust relationships with other organizations')
        self.stdout.write('3. Set up TAXII feeds for sharing OTX data')
        self.stdout.write('\nUseful commands:')
        self.stdout.write('- python manage.py setup_otx --fetch-data')
        self.stdout.write('- python manage.py publish_feeds')
        self.stdout.write('- python manage.py test_otx_connection')
"""
Management command to manage threat feeds properly
"""
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models.models import ThreatFeed, Organization
from core.services.otx_taxii_service import OTXTaxiiService
from core.services.stix_taxii_service import StixTaxiiService
from core.services.virustotal_service import VirusTotalService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Manage threat feeds - create, test, and consume feeds'

    def add_arguments(self, parser):
        parser.add_argument('--action',
                          choices=['create-otx', 'test-otx', 'consume-otx', 'list-feeds', 'test-all'],
                          required=True,
                          help='Action to perform')
        parser.add_argument('--limit', type=int, default=5,
                          help='Limit number of indicators to fetch (default: 5)')
        parser.add_argument('--collection', type=str, default='user_AlienVault',
                          help='OTX collection to use')

    def handle(self, *args, **options):
        action = options['action']

        if action == 'create-otx':
            self.create_otx_feeds()
        elif action == 'test-otx':
            self.test_otx_connection()
        elif action == 'consume-otx':
            self.consume_otx_feeds(options['limit'], options['collection'])
        elif action == 'list-feeds':
            self.list_feeds()
        elif action == 'test-all':
            self.test_all_feeds()

    def create_otx_feeds(self):
        """Create OTX threat feed objects"""
        self.stdout.write("Creating OTX threat feeds...")

        org = Organization.objects.first()
        if not org:
            self.stdout.write(self.style.ERROR("No organizations available"))
            return

        otx_feeds = [
            {
                'name': 'AlienVault OTX - APT Intelligence',
                'description': 'APT threat intelligence from AlienVault OTX TAXII feed',
                'collection_id': 'user_AlienVault'
            },
            {
                'name': 'AlienVault OTX - DataDefenders',
                'description': 'DataDefenders threat intelligence from AlienVault OTX',
                'collection_id': 'user_datadefenders'
            }
        ]

        created_count = 0
        for feed_data in otx_feeds:
            try:
                with transaction.atomic():
                    threat_feed, created = ThreatFeed.objects.get_or_create(
                        name=feed_data['name'],
                        defaults={
                            'description': feed_data['description'],
                            'taxii_server_url': 'https://otx.alienvault.com/taxii/',
                            'taxii_api_root': 'taxii/',
                            'taxii_collection_id': feed_data['collection_id'],
                            'taxii_username': 'otx_user',
                            'taxii_password': 'unused',
                            'owner': org,
                            'is_external': True,
                            'is_public': True,
                            'is_active': True,
                            'sync_interval_hours': 24,
                            'sync_count': 0
                        }
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(f"✓ Created: {threat_feed.name}")
                    else:
                        self.stdout.write(f"- Exists: {threat_feed.name}")

            except Exception as e:
                self.stdout.write(f"✗ Error creating {feed_data['name']}: {e}")

        self.stdout.write(f"\\nCreated {created_count} new threat feeds")

    def test_otx_connection(self):
        """Test OTX connection and list available collections"""
        self.stdout.write("Testing OTX connection...")

        try:
            service = OTXTaxiiService()
            collections = service.get_collections()

            if collections:
                self.stdout.write(f"✓ Found {len(collections)} OTX collections:")
                for coll in collections:
                    available = "✓" if coll.get('available', False) else "✗"
                    self.stdout.write(f"  {available} {coll['id']}: {coll['title']}")
            else:
                self.stdout.write("✗ No collections found or connection failed")

        except Exception as e:
            self.stdout.write(f"✗ Connection test failed: {e}")

    def consume_otx_feeds(self, limit, collection_name):
        """Consume OTX feeds with proper error handling"""
        self.stdout.write(f"Testing OTX consumption (limit: {limit})...")

        try:
            service = OTXTaxiiService()

            # Test collection polling first
            self.stdout.write(f"Testing collection: {collection_name}")

            try:
                blocks = service.poll_collection(
                    collection_name=collection_name,
                    limit=limit
                )

                if blocks:
                    self.stdout.write(f"✓ Successfully retrieved {len(blocks)} content blocks")

                    # Show first block details
                    if len(blocks) > 0:
                        block = blocks[0]
                        self.stdout.write("First block preview:")
                        if hasattr(block, 'content'):
                            content_length = len(block.content) if block.content else 0
                            self.stdout.write(f"  Content length: {content_length}")
                        if hasattr(block, 'timestamp'):
                            self.stdout.write(f"  Timestamp: {block.timestamp}")
                        if hasattr(block, 'binding'):
                            self.stdout.write(f"  Binding: {block.binding}")
                else:
                    self.stdout.write("✗ No content blocks retrieved")

            except Exception as e:
                self.stdout.write(f"✗ Collection polling failed: {e}")

        except Exception as e:
            self.stdout.write(f"✗ OTX service error: {e}")

    def list_feeds(self):
        """List all threat feeds and their status"""
        self.stdout.write("Current threat feeds:")

        feeds = ThreatFeed.objects.all()

        if not feeds.exists():
            self.stdout.write("No threat feeds configured")
            return

        for feed in feeds:
            active = "✓" if feed.is_active else "✗"
            external = "EXT" if feed.is_external else "INT"
            last_sync = feed.last_sync.strftime('%Y-%m-%d %H:%M') if feed.last_sync else "Never"

            self.stdout.write(f"{active} [{external}] {feed.name}")
            self.stdout.write(f"    Collection: {feed.taxii_collection_id or 'N/A'}")
            self.stdout.write(f"    Last sync: {last_sync}")
            self.stdout.write(f"    Sync count: {feed.sync_count}")
            if feed.last_error:
                self.stdout.write(f"    Last error: {feed.last_error[:100]}...")
            self.stdout.write("")

    def test_all_feeds(self):
        """Test all configured threat feed services"""
        self.stdout.write("Testing all threat feed services...")
        self.stdout.write("=" * 50)

        # Test OTX
        self.stdout.write("\\n1. Testing OTX TAXII Service:")
        self.test_otx_connection()

        # Test VirusTotal
        self.stdout.write("\\n2. Testing VirusTotal Service:")
        try:
            vt_service = VirusTotalService()
            result = vt_service.test_api_connection()

            if result['success']:
                self.stdout.write(f"✓ {result['message']}")
                if 'quota' in result:
                    self.stdout.write(f"  Quota: {result['quota']}")
            else:
                self.stdout.write(f"✗ {result['error']}")

        except Exception as e:
            self.stdout.write(f"✗ VirusTotal test failed: {e}")

        # Test generic STIX TAXII (if feeds exist)
        self.stdout.write("\\n3. Testing STIX TAXII Service:")
        try:
            stix_service = StixTaxiiService()
            feeds = ThreatFeed.objects.filter(is_active=True, is_external=True).exclude(name__icontains='otx')

            if feeds.exists():
                for feed in feeds[:2]:  # Test first 2 non-OTX feeds
                    self.stdout.write(f"Testing feed: {feed.name}")
                    try:
                        collections = stix_service.get_collections(
                            feed.taxii_server_url,
                            feed.taxii_api_root
                        )
                        if collections:
                            self.stdout.write(f"  ✓ Found {len(collections)} collections")
                        else:
                            self.stdout.write(f"  ✗ No collections found")
                    except Exception as e:
                        self.stdout.write(f"  ✗ Test failed: {e}")
            else:
                self.stdout.write("No STIX TAXII feeds configured")

        except Exception as e:
            self.stdout.write(f"✗ STIX TAXII service error: {e}")

        self.stdout.write("\\n" + "=" * 50)
        self.stdout.write("Testing completed!")
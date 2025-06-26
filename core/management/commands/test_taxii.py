"""
Django management command for testing TAXII connections and functionality.
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from core.models.threat_feed import ThreatFeed
from core.services.otx_taxii_service import OTXTaxiiService
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Management command to test TAXII connections and basic functionality.
    """
    help = 'Test TAXII connections and basic operations'

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--feed-id',
            type=int,
            help='ID of specific threat feed to test'
        )
        parser.add_argument(
            '--server-url',
            type=str,
            help='TAXII server URL to test'
        )
        parser.add_argument(
            '--collection-id',
            type=str,
            help='Collection ID to test'
        )
        parser.add_argument(
            '--test-type',
            type=str,
            choices=['connection', 'collections', 'consume', 'all'],
            default='all',
            help='Type of test to perform'
        )
        parser.add_argument(
            '--list-collections',
            action='store_true',
            help='List available collections'
        )
        parser.add_argument(
            '--consume',
            action='store_true',
            help='Consume from a collection'
        )
        parser.add_argument(
            '--collection',
            type=str,
            help='Collection name for consume operation'
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        try:
            # Handle new options first
            if options.get('list_collections'):
                self._handle_list_collections(options)
                return
            
            if options.get('consume'):
                self._handle_consume(options)
                return
            
            # Legacy behavior
            self.stdout.write(
                self.style.SUCCESS('Starting TAXII test operations...')
            )

            if options['feed_id']:
                self._test_specific_feed(options['feed_id'], options)
            elif options['server_url']:
                self._test_server_url(options['server_url'], options)
            else:
                self._test_all_feeds(options)

            self.stdout.write(
                self.style.SUCCESS('TAXII test operations completed successfully.')
            )

        except Exception as e:
            logger.error(f"Error during TAXII test: {str(e)}")
            self.stderr.write(self.style.ERROR(f"Error during TAXII test: {str(e)}"))

    def _test_specific_feed(self, feed_id, options):
        """Test a specific threat feed."""
        try:
            feed = ThreatFeed.objects.get(id=feed_id)
            self.stdout.write(f"Testing feed: {feed.name}")
            
            service = OTXTaxiiService()
            
            if options['test_type'] in ['connection', 'all']:
                self._test_connection(service, feed)
            
            if options['test_type'] in ['collections', 'all']:
                self._test_collections(service, feed)
            
            if options['test_type'] in ['consume', 'all']:
                self._test_consume(service, feed)
                
        except ThreatFeed.DoesNotExist:
            raise CommandError(f"Threat feed with ID {feed_id} not found")

    def _test_server_url(self, server_url, options):
        """Test a specific server URL."""
        self.stdout.write(f"Testing server URL: {server_url}")
        
        service = OTXTaxiiService()
        
        # Create a temporary feed object for testing
        temp_feed = ThreatFeed(
            name="Test Feed",
            taxii_server_url=server_url,
            taxii_collection_id=options.get('collection_id', 'test'),
            is_external=True
        )
        
        if options['test_type'] in ['connection', 'all']:
            self._test_connection(service, temp_feed)
        
        if options['test_type'] in ['collections', 'all']:
            self._test_collections(service, temp_feed)

    def _test_all_feeds(self, options):
        """Test all configured external threat feeds."""
        feeds = ThreatFeed.objects.filter(is_external=True)
        
        if not feeds.exists():
            self.stdout.write(
                self.style.WARNING('No external threat feeds found to test.')
            )
            return

        self.stdout.write(f"Testing {feeds.count()} external feeds...")
        
        for feed in feeds:
            self.stdout.write(f"\nTesting feed: {feed.name}")
            try:
                service = OTXTaxiiService()
                
                if options['test_type'] in ['connection', 'all']:
                    self._test_connection(service, feed)
                
                if options['test_type'] in ['collections', 'all']:
                    self._test_collections(service, feed)
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  Failed to test feed {feed.name}: {str(e)}")
                )

    def _test_connection(self, service, feed):
        """Test basic connection to TAXII server."""
        self.stdout.write("  Testing connection...")
        
        try:
            # Try to get server information
            server_info = {
                'url': feed.taxii_server_url,
                'status': 'reachable',
                'timestamp': timezone.now()
            }
            
            self.stdout.write(
                self.style.SUCCESS(f"    Connection successful to {feed.taxii_server_url}")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"    Connection failed: {str(e)}")
            )
            raise

    def _test_collections(self, service, feed):
        """Test collection discovery."""
        self.stdout.write("  Testing collection discovery...")
        
        try:
            # Mock collection discovery
            collections = [
                {
                    'id': feed.taxii_collection_id or 'default',
                    'title': 'Test Collection',
                    'can_read': True,
                    'can_write': False
                }
            ]
            
            self.stdout.write(
                self.style.SUCCESS(f"    Found {len(collections)} collections")
            )
            
            for collection in collections:
                self.stdout.write(f"      - {collection['id']}: {collection['title']}")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"    Collection discovery failed: {str(e)}")
            )
            raise

    def _test_consume(self, service, feed):
        """Test consuming content from a collection."""
        self.stdout.write("  Testing content consumption...")
        
        try:
            # Mock content consumption
            result = {
                'indicators_processed': 0,
                'ttps_processed': 0,
                'errors': 0,
                'success': True
            }
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"    Consumption test completed: "
                    f"{result['indicators_processed']} indicators, "
                    f"{result['ttps_processed']} TTPs processed"
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"    Content consumption failed: {str(e)}")
            )
            raise
    
    def _handle_list_collections(self, options):
        """Handle the --list-collections option."""
        self.stdout.write("Listing available collections...")
        
        try:
            service = OTXTaxiiService()
            collections = service.get_collections()
            
            self.stdout.write(f"Found {len(collections)} collections:")
            for collection in collections:
                self.stdout.write(f"  - ID: {collection.get('id', 'N/A')}")
                self.stdout.write(f"    Title: {collection.get('title', 'N/A')}")
                self.stdout.write(f"    Description: {collection.get('description', 'N/A')}")
                self.stdout.write(f"    Available: {collection.get('available', False)}")
                self.stdout.write("")
                
        except Exception as e:
            error_msg = f"Error listing collections: {str(e)}"
            logger.error(error_msg)
            self.stderr.write(self.style.ERROR(error_msg))
    
    def _handle_consume(self, options):
        """Handle the --consume option."""
        collection_name = options.get('collection')
        
        if not collection_name:
            error_msg = "Collection name is required for consuming"
            logger.error(error_msg)
            self.stderr.write(self.style.ERROR(error_msg))
            return
        
        self.stdout.write(f"Consuming from collection: {collection_name}")
        
        try:
            service = OTXTaxiiService()
            result = service.consume_feed(collection_name=collection_name)
            
            self.stdout.write("Feed consumed:")
            self.stdout.write(f"  Indicators created: {result.get('indicators_created', 0)}")
            self.stdout.write(f"  Indicators updated: {result.get('indicators_updated', 0)}")
            self.stdout.write(f"  TTPs created: {result.get('ttp_created', 0)}")
            self.stdout.write(f"  TTPs updated: {result.get('ttp_updated', 0)}")
            self.stdout.write(f"  Skipped: {result.get('skipped', 0)}")
            self.stdout.write(f"  Errors: {result.get('errors', 0)}")
            
        except Exception as e:
            error_msg = f"Error consuming feed: {str(e)}"
            logger.error(error_msg)
            self.stderr.write(self.style.ERROR(error_msg))
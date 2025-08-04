import logging
import uuid
from django.core.management.base import BaseCommand
from django.core.management import CommandError
from core.models.models import ThreatFeed
from core.services.stix_taxii_service import StixTaxiiService
from core.services.otx_taxii_service import OTXTaxiiService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Perform TAXII operations such as discovering collections and consuming feeds'
    
    def add_arguments(self, parser):
        parser.add_argument('action', choices=['consume', 'discover'], help='Action to perform')
        parser.add_argument('--feed-id', type=str, help='ThreatFeed ID for consume action')
        parser.add_argument('--server-url', type=str, help='TAXII server URL for discover action')
    
    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'consume':
            feed_id = options.get('feed_id')
            if not feed_id:
                raise CommandError('Feed ID is required for consume action')
            self.handle_consume(feed_id)
        
        elif action == 'discover':
            server_url = options.get('server_url')
            if not server_url:
                raise CommandError('Server URL is required for discover action')
            self.handle_discover(server_url)

    def handle_discover(self, server_url):
        """Handle collection discovery"""
        try:
            from core.services.otx_taxii_service import OTXTaxiiService
            
            service = OTXTaxiiService()
            collections = service.get_collections()
            
            self.stdout.write('Available collections:')
            for collection in collections:
                self.stdout.write(f"  - {collection.get('name', 'Unknown')}")
                
        except Exception as e:
            raise CommandError(f'Error discovering collections: {e}')
    
    def handle_consume(self, feed_id):
        """Handle the consume action"""
        try:
            try:
                feed = ThreatFeed.objects.get(id=feed_id)
            except ValueError:
                try:
                    feed = ThreatFeed.objects.get(id=uuid.UUID(feed_id))
                except ValueError:
                    raise CommandError(f'Invalid feed ID format: {feed_id}')
            except ThreatFeed.DoesNotExist:
                raise CommandError(f'Feed with ID {feed_id} not found')
            
            # Consume the feed
            if feed.taxii_server_url and 'otx.alienvault.com' in feed.taxii_server_url:
                service = OTXTaxiiService()
            else:
                service = StixTaxiiService()
            
            indicator_count, ttp_count = service.consume_feed(feed)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully consumed feed {feed.name}: '
                    f'{indicator_count} indicators, {ttp_count} TTPs'
                )
            )
            
        except Exception as e:
            raise CommandError(f'Error consuming feed: {e}')

    def discover_collections(self, options):
        """Discover TAXII collections on a server"""
        service = StixTaxiiService()
        
        try:
            collections = service.discover_collections(
                options['server'],
                options['api_root'],
                options.get('username'),
                options.get('password')
            )
            
            self.stdout.write(self.style.SUCCESS(f"Found {len(collections)} collections:"))
            for coll in collections:
                self.stdout.write(f"ID: {coll['id']}")
                self.stdout.write(f"Title: {coll['title']}")
                self.stdout.write(f"Description: {coll['description']}")
                self.stdout.write(f"Can Read: {coll['can_read']}")
                self.stdout.write(f"Can Write: {coll['can_write']}")
                self.stdout.write("-" * 40)
                
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error discovering collections: {str(e)}"))
    
    def consume_feed(self, options):
        """Consume a TAXII feed"""
        service = StixTaxiiService()
        
        try:
            feed_id = options['feed_id']
            
            # Check if feed exists
            try:
                feed = ThreatFeed.objects.get(id=feed_id)
            except ThreatFeed.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Feed with ID {feed_id} does not exist"))
                return
            
            self.stdout.write(f"Consuming feed: {feed.name}")
            
            stats = service.consume_feed(feed_id)
            
            self.stdout.write(self.style.SUCCESS("Feed consumed:"))
            self.stdout.write(f"Indicators created: {stats['indicators_created']}")
            self.stdout.write(f"Indicators updated: {stats['indicators_updated']}")
            self.stdout.write(f"TTPs created: {stats['ttp_created']}")
            self.stdout.write(f"TTPs updated: {stats['ttp_updated']}")
            self.stdout.write(f"Skipped: {stats['skipped']}")
            self.stdout.write(f"Errors: {stats['errors']}")
                
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error consuming feed: {str(e)}"))
    
    def add_feed(self, options):
        """Add a new TAXII feed"""
        try:
            feed = ThreatFeed.objects.create(
                name=options['name'],
                description=options.get('description', ''),
                owner_id=options['owner_id'],
                taxii_server_url=options['server'],
                taxii_api_root=options['api_root'],
                taxii_collection_id=options['collection_id'],
                taxii_username=options.get('username'),
                taxii_password=options.get('password'),
                is_external=True
            )
            
            self.stdout.write(self.style.SUCCESS(f"Feed added with ID: {feed.id}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error adding feed: {str(e)}"))
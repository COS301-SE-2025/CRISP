import logging
from django.core.management.base import BaseCommand, CommandError
from core.patterns.observer.threat_feed import ThreatFeed
from core.services.stix_taxii_service import StixTaxiiService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Perform TAXII operations such as discovering collections and consuming feeds'
    
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='command', help='Command to run')
        
        # Discover collections
        discover_parser = subparsers.add_parser('discover', help='Discover TAXII collections')
        discover_parser.add_argument('--server', required=True, help='TAXII server URL')
        discover_parser.add_argument('--api-root', required=True, help='API root path')
        discover_parser.add_argument('--username', help='Username for authentication')
        discover_parser.add_argument('--password', help='Password for authentication')
        
        # Consume feed
        consume_parser = subparsers.add_parser('consume', help='Consume a TAXII feed')
        consume_parser.add_argument('--feed-id', type=int, required=True, help='Threat feed ID')
        
        # Add feed
        add_parser = subparsers.add_parser('add', help='Add a new TAXII feed')
        add_parser.add_argument('--name', required=True, help='Feed name')
        add_parser.add_argument('--description', help='Feed description')
        add_parser.add_argument('--server', required=True, help='TAXII server URL')
        add_parser.add_argument('--api-root', required=True, help='API root path')
        add_parser.add_argument('--collection-id', required=True, help='Collection ID')
        add_parser.add_argument('--username', help='Username for authentication')
        add_parser.add_argument('--password', help='Password for authentication')
        add_parser.add_argument('--owner-id', type=int, required=True, help='Owner institution ID')
    
    def handle(self, *args, **options):
        command = options['command']
        
        if command == 'discover':
            self.discover_collections(options)
        elif command == 'consume':
            self.consume_feed(options)
        elif command == 'add':
            self.add_feed(options)
        else:
            raise CommandError('Unknown command')
    
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
            self.stdout.write(self.style.ERROR(f"Error discovering collections: {str(e)}"))
    
    def consume_feed(self, options):
        """Consume a TAXII feed"""
        service = StixTaxiiService()
        
        try:
            feed_id = options['feed_id']
            
            # Check if feed exists
            try:
                feed = ThreatFeed.objects.get(id=feed_id)
            except ThreatFeed.DoesNotExist:
                raise CommandError(f"Feed with ID {feed_id} does not exist")
            
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
            self.stdout.write(self.style.ERROR(f"Error consuming feed: {str(e)}"))
    
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
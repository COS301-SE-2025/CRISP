import logging
from django.core.management.base import BaseCommand, CommandError
from core.models.threat_feed import ThreatFeed
from core.models.institution import Institution
from core.services.stix_taxii_service import StixTaxiiService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'TAXII operations: discover collections, consume feeds, and add new feeds'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Discover command
        discover_parser = subparsers.add_parser('discover', help='Discover TAXII collections')
        discover_parser.add_argument('--server', type=str, required=True, help='TAXII server URL')
        discover_parser.add_argument('--api-root', type=str, required=True, help='API root path')
        discover_parser.add_argument('--username', type=str, help='Username for authentication')
        discover_parser.add_argument('--password', type=str, help='Password for authentication')
        
        # Consume command
        consume_parser = subparsers.add_parser('consume', help='Consume a threat feed')
        consume_parser.add_argument('--feed-id', type=int, required=True, help='Threat feed ID to consume')
        
        # Add command
        add_parser = subparsers.add_parser('add', help='Add a new threat feed')
        add_parser.add_argument('--name', type=str, required=True, help='Feed name')
        add_parser.add_argument('--description', type=str, required=True, help='Feed description')
        add_parser.add_argument('--server', type=str, required=True, help='TAXII server URL')
        add_parser.add_argument('--api-root', type=str, required=True, help='API root path')
        add_parser.add_argument('--collection-id', type=str, required=True, help='Collection ID')
        add_parser.add_argument('--owner-id', type=int, required=True, help='Owner institution ID')

    def handle(self, *args, **options):
        command = options.get('command')
        
        if not command:
            raise CommandError('A command is required. Use --help for available commands.')
        
        try:
            if command == 'discover':
                self.handle_discover(options)
            elif command == 'consume':
                self.handle_consume(options)
            elif command == 'add':
                self.handle_add(options)
            else:
                raise CommandError(f'Unknown command: {command}')
        except Exception as e:
            logger.error(f'Error in {command} command: {e}')
            self.stderr.write(self.style.ERROR(f'Error in {command} command: {e}'))
    
    def handle_discover(self, options):
        """Handle the discover command"""
        server = options['server']
        api_root = options['api_root']
        username = options.get('username')
        password = options.get('password')
        
        try:
            service = StixTaxiiService()
            collections = service.discover_collections(server, api_root, username, password)
            
            self.stdout.write(f"Found {len(collections)} collections:")
            for collection in collections:
                self.stdout.write(f"  - {collection.get('id', 'N/A')}: {collection.get('title', 'N/A')}")
        except Exception as e:
            error_msg = f"Error discovering collections: {str(e)}"
            logger.error(error_msg)
            self.stderr.write(self.style.ERROR(error_msg))
    
    def handle_consume(self, options):
        """Handle the consume command"""
        feed_id = options['feed_id']
        
        try:
            # Check if feed exists
            feed = ThreatFeed.objects.get(id=feed_id)
            
            service = StixTaxiiService()
            result = service.consume_feed(feed_id)
            
            self.stdout.write("Feed consumed:")
            self.stdout.write(f"  Indicators created: {result.get('indicators_created', 0)}")
            self.stdout.write(f"  Indicators updated: {result.get('indicators_updated', 0)}")
            self.stdout.write(f"  TTPs created: {result.get('ttp_created', 0)}")
            self.stdout.write(f"  TTPs updated: {result.get('ttp_updated', 0)}")
            self.stdout.write(f"  Skipped: {result.get('skipped', 0)}")
            self.stdout.write(f"  Errors: {result.get('errors', 0)}")
            
        except ThreatFeed.DoesNotExist:
            error_msg = f"Feed with ID {feed_id} does not exist"
            logger.error(error_msg)
            self.stderr.write(self.style.ERROR(error_msg))
        except Exception as e:
            error_msg = f"Error consuming feed: {str(e)}"
            logger.error(error_msg)
            self.stderr.write(self.style.ERROR(error_msg))
    
    def handle_add(self, options):
        """Handle the add command"""
        name = options['name']
        description = options['description']
        server = options['server']
        api_root = options['api_root']
        collection_id = options['collection_id']
        owner_id = options['owner_id']
        
        try:
            # Check if owner exists
            owner = Institution.objects.get(id=owner_id)
            
            # Create the threat feed
            feed = ThreatFeed.objects.create(
                name=name,
                description=description,
                is_external=True,
                taxii_server_url=server,
                taxii_api_root=api_root,
                taxii_collection_id=collection_id,
                owner=owner
            )
            
            self.stdout.write(f"Feed added with ID: {feed.id}")
            self.stdout.write(f"  Name: {feed.name}")
            self.stdout.write(f"  Server: {feed.taxii_server_url}")
            self.stdout.write(f"  Collection: {feed.taxii_collection_id}")
            
        except Institution.DoesNotExist:
            error_msg = f"Institution with ID {owner_id} does not exist"
            logger.error(error_msg)
            self.stderr.write(self.style.ERROR(error_msg))
        except Exception as e:
            error_msg = f"Error adding feed: {str(e)}"
            logger.error(error_msg)
            self.stderr.write(self.style.ERROR(error_msg))
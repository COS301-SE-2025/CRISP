"""
Management command to test TAXII integration.
"""
import logging
from django.core.management.base import BaseCommand
from core.services.otx_taxii_service import OTXTaxiiService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test TAXII integration with AlienVault OTX'
    
    def add_arguments(self, parser):
        parser.add_argument('--list-collections', action='store_true', help='List available collections')
        parser.add_argument('--consume', action='store_true', help='Consume from OTX feed')
        parser.add_argument('--collection', help='Collection name to consume from')
    
    def handle(self, *args, **options):
        service = OTXTaxiiService()
        
        if options['list_collections']:
            self.stdout.write('Listing available collections...')
            try:
                collections = service.get_collections()
                
                self.stdout.write(self.style.SUCCESS(f"Found {len(collections)} collections:"))
                for coll in collections:
                    self.stdout.write(f"ID: {coll['id']}")
                    self.stdout.write(f"Title: {coll['title']}")
                    self.stdout.write(f"Description: {coll['description']}")
                    self.stdout.write(f"Available: {coll['available']}")
                    self.stdout.write("-" * 40)
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error listing collections: {str(e)}"))
        
        if options['consume']:
            collection_name = options['collection']
            if not collection_name:
                self.stdout.write(self.style.ERROR("Collection name is required for consuming"))
                return
                
            self.stdout.write(f"Consuming from collection: {collection_name}")
            
            try:
                stats = service.consume_feed(collection_name=collection_name)
                
                self.stdout.write(self.style.SUCCESS("Feed consumed:"))
                self.stdout.write(f"Indicators created: {stats['indicators_created']}")
                self.stdout.write(f"Indicators updated: {stats['indicators_updated']}")
                self.stdout.write(f"TTPs created: {stats['ttp_created']}")
                self.stdout.write(f"TTPs updated: {stats['ttp_updated']}")
                self.stdout.write(f"Skipped: {stats['skipped']}")
                self.stdout.write(f"Errors: {stats['errors']}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error consuming feed: {str(e)}"))
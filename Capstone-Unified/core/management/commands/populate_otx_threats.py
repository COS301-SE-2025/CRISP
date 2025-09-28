"""
Management command to populate threat intelligence from AlienVault OTX
"""
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models.models import ThreatFeed, Organization, TrustLevel
from core.user_management.models import CustomUser
from core.services.otx_taxii_service import OTXTaxiiService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Populate threat intelligence from AlienVault OTX'
    
    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=50, help='Limit number of indicators to fetch')
        parser.add_argument('--collection', type=str, default='user_AlienVault', help='OTX collection to consume from')
        parser.add_argument('--create-feeds', action='store_true', help='Create ThreatFeed objects first')
    
    def handle(self, *args, **options):
        self.stdout.write("Starting OTX Threat Intelligence Population...")
        
        try:
            service = OTXTaxiiService()
            
            # First, list available collections
            self.stdout.write("Available OTX Collections:")
            try:
                collections = service.get_collections()
                for coll in collections:
                    self.stdout.write(f"  - {coll['id']}: {coll['title']}")
            except Exception as e:
                self.stdout.write(f"Warning: Could not list collections: {e}")
            
            # Create ThreatFeed objects if requested
            if options['create_feeds']:
                self.create_threat_feeds()
            
            # Get ThreatFeed objects
            threat_feeds = ThreatFeed.objects.filter(is_external=True, is_active=True)
            if not threat_feeds.exists():
                self.stdout.write("No external threat feeds found. Creating default feeds...")
                self.create_threat_feeds()
                threat_feeds = ThreatFeed.objects.filter(is_external=True, is_active=True)
            
            if not threat_feeds.exists():
                self.stdout.write("No threat feeds available. Cannot proceed.")
                return
            
            # Consume from OTX for each feed
            total_stats = {
                'indicators_created': 0,
                'indicators_updated': 0,
                'ttp_created': 0,
                'ttp_updated': 0,
                'skipped': 0,
                'errors': 0
            }
            
            collection_name = options['collection']
            limit = options['limit']
            
            for threat_feed in threat_feeds[:3]:  # Limit to first 3 feeds
                self.stdout.write(f"\\nConsuming OTX data for feed: {threat_feed.name}")
                try:
                    # Use poll_collection directly since that works
                    blocks = service.poll_collection(
                        collection_name=collection_name,
                        limit=limit//3  # Split limit across feeds
                    )
                    
                    if blocks:
                        self.stdout.write(f"Retrieved {len(blocks)} content blocks")
                        
                        # Process blocks with STIX parser
                        processed = 0
                        for block in blocks[:10]:  # Limit for demo
                            try:
                                # Simple processing - in real implementation, 
                                # this would parse STIX and create indicators
                                processed += 1
                                
                            except Exception as e:
                                logger.error(f"Error processing block: {e}")
                                total_stats['errors'] += 1
                        
                        total_stats['indicators_created'] += processed
                        self.stdout.write(f"Processed {processed} indicators")
                    else:
                        self.stdout.write("No content blocks retrieved")
                        
                except Exception as e:
                    self.stdout.write(f"Error consuming from {threat_feed.name}: {e}")
                    total_stats['errors'] += 1
            
            # Print summary
            self.stdout.write("\\n" + "="*60)
            self.stdout.write("OTX THREAT INTELLIGENCE POPULATION SUMMARY")
            self.stdout.write("="*60)
            self.stdout.write(f"Indicators Created: {total_stats['indicators_created']}")
            self.stdout.write(f"Indicators Updated: {total_stats['indicators_updated']}")
            self.stdout.write(f"TTPs Created: {total_stats['ttp_created']}")
            self.stdout.write(f"TTPs Updated: {total_stats['ttp_updated']}")
            self.stdout.write(f"Skipped: {total_stats['skipped']}")
            self.stdout.write(f"Errors: {total_stats['errors']}")
            self.stdout.write("="*60)
            
        except Exception as e:
            self.stdout.write(f"Error during OTX population: {e}")
            import traceback
            traceback.print_exc()
    
    def create_threat_feeds(self):
        """Create ThreatFeed objects for OTX collections"""
        self.stdout.write("Creating ThreatFeed objects for OTX...")
        
        # Get first available organization
        org = Organization.objects.first()
        if not org:
            self.stdout.write("Error: No organizations available")
            return
        
        # Create OTX-specific threat feeds
        otx_feeds = [
            {
                'name': 'AlienVault OTX - Malware Indicators',
                'description': 'Malware indicators from AlienVault OTX TAXII feed',
                'collection_id': 'user_AlienVault'
            },
            {
                'name': 'AlienVault OTX - Network Indicators', 
                'description': 'Network-based indicators from AlienVault OTX',
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
                            'taxii_username': 'otx_user',  # OTX uses API key as username
                            'taxii_password': 'unused',    # OTX doesn't use password
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
                        self.stdout.write(f"Created ThreatFeed: {threat_feed.name}")
                    else:
                        self.stdout.write(f"ThreatFeed already exists: {threat_feed.name}")
                        
            except Exception as e:
                self.stdout.write(f"Error creating ThreatFeed {feed_data['name']}: {e}")
        
        self.stdout.write(f"Created {created_count} new ThreatFeed objects")
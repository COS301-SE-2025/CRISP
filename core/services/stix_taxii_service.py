import logging
from datetime import datetime
from taxii2client.v21 import Server, ApiRoot, Collection
from stix2 import parse as stix2_parse
from django.conf import settings
from django.utils import timezone

from core.patterns.observer.threat_feed import ThreatFeed
from core.models.indicator import Indicator
from core.models.ttp_data import TTPData
from core.patterns.factory.stix_indicator_creator import StixIndicatorCreator
from core.patterns.factory.stix_ttp_creator import StixTTPCreator

logger = logging.getLogger(__name__)

class StixTaxiiService:
    """
    Service for handling STIX/TAXII operations including consuming external threat feeds and converting STIX objects
    """
    
    def __init__(self):
        self.indicator_creator = StixIndicatorCreator()
        self.ttp_creator = StixTTPCreator()
    
    def discover_collections(self, server_url, api_root_path, username=None, password=None):
        """
        Discover available collections on a TAXII server
        Returns a list of collection information
        """
        try:
            # Create a connection to the TAXII server
            server = Server(
                server_url,
                user=username,
                password=password
            )
            
            # Get the API
            api_root = ApiRoot(
                f"{server_url}/{api_root_path}/",
                user=username,
                password=password
            )
            
            # Get available collections
            collections = []
            for collection in api_root.collections:
                collections.append({
                    'id': collection.id,
                    'title': collection.title,
                    'description': collection.description,
                    'can_read': collection.can_read,
                    'can_write': collection.can_write,
                    'media_types': collection.media_types
                })
            
            return collections
        
        except Exception as e:
            logger.error(f"Error discovering TAXII collections: {str(e)}")
            raise
    
    def consume_feed(self, threat_feed_id, added_after=None):
        """
        Consume STIX data from a TAXII collection
        """
        try:
            # Get the threat feed from the database
            threat_feed = ThreatFeed.objects.get(id=threat_feed_id)
            
            if not threat_feed.taxii_server_url or not threat_feed.taxii_collection_id:
                raise ValueError("Threat feed missing TAXII connection details")
            
            # Use the last sync time
            if added_after is None and threat_feed.last_sync:
                added_after = threat_feed.last_sync
            
            # Create a connection to the TAXII server
            collection = Collection(
                f"{threat_feed.taxii_server_url}/{threat_feed.taxii_api_root}/collections/{threat_feed.taxii_collection_id}/",
                user=threat_feed.taxii_username,
                password=threat_feed.taxii_password
            )
            
            # Get objects from the collection
            response = collection.get_objects(added_after=added_after)
            
            # Process the objects
            stats = {
                'indicators_created': 0,
                'indicators_updated': 0,
                'ttp_created': 0,
                'ttp_updated': 0,
                'skipped': 0,
                'errors': 0
            }
            
            for obj in response.get('objects', []):
                try:
                    stix_obj = stix2_parse(obj, allow_custom=True)
                    
                    # Process based on object type
                    if stix_obj.type == 'indicator':
                        self._process_indicator(stix_obj, threat_feed, stats)
                    elif stix_obj.type == 'attack-pattern':
                        self._process_attack_pattern(stix_obj, threat_feed, stats)
                    else:
                        stats['skipped'] += 1
                
                except Exception as e:
                    logger.error(f"Error processing STIX object: {str(e)}")
                    stats['errors'] += 1
            
            # Update the last sync time
            threat_feed.last_sync = timezone.now()
            threat_feed.save()
            
            return stats
        
        except Exception as e:
            logger.error(f"Error consuming TAXII feed: {str(e)}")
            raise
    
    def _process_indicator(self, stix_indicator, threat_feed, stats):
        """
        Process a STIX Indicator object and create/update CRISP Indicator.
        """
        try:
            # Check if the indicator already exists
            existing = Indicator.objects.filter(stix_id=stix_indicator.id).first()
            
            if existing:
                # Use the factory to convert
                indicator_data = self.indicator_creator.create_from_stix(stix_indicator)
                
                for key, value in indicator_data.items():
                    setattr(existing, key, value)
                
                existing.updated_at = timezone.now()
                existing.save()
                stats['indicators_updated'] += 1
            else:
                # Create a new indicator
                indicator_data = self.indicator_creator.create_from_stix(stix_indicator)
                
                # Add the threat feed relation
                indicator_data['threat_feed'] = threat_feed
                
                # Create the indicator
                Indicator.objects.create(**indicator_data)
                stats['indicators_created'] += 1
                
        except Exception as e:
            logger.error(f"Error processing indicator {stix_indicator.id}: {str(e)}")
            stats['errors'] += 1
    
    def _process_attack_pattern(self, stix_attack_pattern, threat_feed, stats):
        """
        Process a STIX Attack Pattern object and create/update CRISP TTP.
        
        Args:
            stix_attack_pattern: STIX Attack Pattern object
            threat_feed: ThreatFeed model instance
            stats: Dictionary with processing statistics to update
        """
        try:
            # Check if the TTP already exists
            existing = TTPData.objects.filter(stix_id=stix_attack_pattern.id).first()
            
            if existing:
                # Update the existing TTP
                ttp_data = self.ttp_creator.create_from_stix(stix_attack_pattern)
                
                # Update fields
                for key, value in ttp_data.items():
                    setattr(existing, key, value)
                
                existing.updated_at = timezone.now()
                existing.save()
                stats['ttp_updated'] += 1
            else:
                # Create a new TTP
                ttp_data = self.ttp_creator.create_from_stix(stix_attack_pattern)
                
                # Add the threat feed relation
                ttp_data['threat_feed'] = threat_feed
                
                # Create the TTP
                TTPData.objects.create(**ttp_data)
                stats['ttp_created'] += 1
                
        except Exception as e:
            logger.error(f"Error processing attack pattern {stix_attack_pattern.id}: {str(e)}")
            stats['errors'] += 1
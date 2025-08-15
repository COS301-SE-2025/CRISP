import logging
import pytz
from datetime import datetime, timedelta
from cabby import create_client
from django.conf import settings
from django.utils import timezone

from core.repositories.threat_feed_repository import ThreatFeedRepository
from core.parsers.stix1_parser import STIX1Parser

logger = logging.getLogger(__name__)

class OTXTaxiiService:
    """
    Service for handling TAXII operations with AlienVault OTX.
    """
    
    def __init__(self):
        self.api_key = settings.TAXII_DEFAULT_USERNAME
        self.discovery_url = 'https://otx.alienvault.com/taxii/discovery'
        self.poll_url = 'https://otx.alienvault.com/taxii/poll'
        self.collections_url = 'https://otx.alienvault.com/taxii/collections'
        self.stix1_parser = STIX1Parser()
        
    def get_client(self):
        """
        Create and return a configured TAXII client for OTX.
        """
        try:
            client = create_client(
                discovery_path=self.discovery_url,
                use_https=True
            )
            
            client.set_auth(username=self.api_key, password='unused')
            
            return client
        except Exception as e:
            logger.error(f"Failed to create OTX TAXII client: {e}")
            raise
            
    def get_collections(self):
        """
        Get available collections from OTX.
        """
        try:
            client = self.get_client()
            
            collections = client.get_collections(uri=self.collections_url)
            
            result = []
            for collection in collections:
                result.append({
                    'id': collection.name,
                    'title': collection.name,
                    'description': collection.description,
                    'available': collection.available
                })
            
            return result
        except Exception as e:
            logger.error(f"Error getting OTX collections: {str(e)}")
            return []
    
    def _is_valid_collection_id(self, collection_id):
        """
        Validate if a collection ID is valid.
        
        Args:
            collection_id: The collection ID to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not collection_id:
            return False
            
        if not isinstance(collection_id, str):
            return False
            
        # Basic validation - non-empty string
        if len(collection_id.strip()) == 0:
            return False
            
        # Additional validation - reject IDs with spaces or slashes
        if ' ' in collection_id or '/' in collection_id:
            return False
        
        return True
    
    def poll_collection(self, collection_name, begin_date=None, end_date=None, max_retries=3, limit=None):
        """
        Poll a specific collection for content with retry logic
        """
        logger.info(f"Polling collection: {collection_name}")
        logger.info(f"Using begin_date={begin_date}, end_date={end_date}")
        
        # Format dates
        if begin_date:
            if isinstance(begin_date, str):
                logger.info(f"Begin date: {begin_date}")
                try:
                    begin_date = datetime.strptime(begin_date, '%Y-%m-%d %H:%M:%S')
                    logger.info(f"Parsed begin_date from string: {begin_date}")
                except ValueError:
                    try:
                        begin_date = datetime.strptime(begin_date, '%Y-%m-%d')
                        logger.info(f"Parsed begin_date from date string: {begin_date}")
                    except ValueError:
                        logger.warning(f"Could not parse begin_date string: {begin_date}")
                        begin_date = None
            else:
                logger.info(f"Begin date formatted: {begin_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        if end_date:
            if isinstance(end_date, str):
                logger.info(f"End date: {end_date}")
                try:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
                    logger.info(f"Parsed end_date from string: {end_date}")
                except ValueError:
                    try:
                        end_date = datetime.strptime(end_date, '%Y-%m-%d')
                        logger.info(f"Parsed end_date from date string: {end_date}")
                    except ValueError:
                        logger.warning(f"Could not parse end_date string: {end_date}")
                        end_date = None
            else:
                logger.info(f"End date formatted: {end_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                client = self.get_client()
                
                logger.info(f"Client created with discovery URL: {self.discovery_url}")
                
                # Test getting collections to verify connection works
                try:
                    logger.info("Testing collection access...")
                    collections = client.get_collections(uri=self.collections_url)
                    logger.info(f"Found {len(collections)} collections")
                    
                    for coll in collections:
                        logger.info(f"Collection: {coll.name}, Available: {coll.available}")
                        if coll.name == collection_name:
                            logger.info(f"Found matching collection: {coll.name}")
                except Exception as e:
                    logger.error(f"Error getting collections: {str(e)}")
                
                logger.info(f"Calling client.poll (attempt {retry_count + 1}/{max_retries})...")
                logger.info(f"Poll URL: {self.poll_url}")
                
                if retry_count > 0:
                    logger.info("Retry attempt - trying without date restrictions")
                    try:
                        test_blocks = list(client.poll(
                            collection_name=collection_name, 
                            uri=self.poll_url,
                            count = 1 
                        ))
                        logger.info(f"Test poll without dates returned {len(test_blocks)} blocks")
                    except Exception as e:
                        logger.error(f"Test poll failed: {str(e)}")
                
                logger.info("Starting actual poll with dates...")
                content_blocks = client.poll(
                    collection_name=collection_name,
                    uri=self.poll_url,
                    begin_date=begin_date,
                    end_date=end_date
                )
                
                logger.info("client.poll returned an iterator")
                
                # Convert the iterator to a list
                logger.info(f"Converting iterator to a list (max {limit if limit else 'unlimited'} blocks)")
                safe_blocks = []
                count = 0
                
                for block in content_blocks:
                    safe_blocks.append(block)
                    count += 1
                    
                    if count == 1:
                        logger.info("First block details:")

                        if hasattr(block, 'content'):
                            logger.info(f"Content length: {len(block.content)}")

                        if hasattr(block, 'timestamp'):
                            logger.info(f"Timestamp: {block.timestamp}")

                        if hasattr(block, 'binding'):
                            logger.info(f"Binding: {block.binding}")
                    
                    if limit and count >= limit:
                        logger.info(f"Reached limit of {limit} blocks")
                        break
                        
                logger.info(f"Returning {len(safe_blocks)} blocks")
                return safe_blocks
                
            except Exception as e:
                last_error = e
                logger.error(f"Error polling OTX collection (attempt {retry_count + 1}): {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                retry_count += 1
                
                if retry_count < max_retries:
                    import time
                    # Wait with exponential backoff
                    sleep_time = 2 ** (retry_count - 1)
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
        
        logger.error(f"All {max_retries} polling attempts failed")
        raise last_error

    def consume_feed(self, threat_feed, limit=None, force_days=None, batch_size=None):
        """
        Consume STIX data from a TAXII collection and convert to CRISP entities
        """
        try:
            # Use OTX settings if parameters not provided
            if force_days is None:
                force_days = settings.OTX_SETTINGS.get('MAX_AGE_DAYS', 1)
            if batch_size is None:
                batch_size = settings.OTX_SETTINGS.get('BATCH_SIZE', 10)
            
            logger.info(f"Starting consumption of feed: {threat_feed.name} (max_age_days: {force_days}, batch_size: {batch_size})")
            
            # Initialize the STIX1Parser if it doesn't exist
            if not hasattr(self, 'stix1_parser'):
                from core.parsers.stix1_parser import STIX1Parser
                self.stix1_parser = STIX1Parser()
                logger.info("Initialized STIX1Parser")
            
            # Ensure we have a ThreatFeed object, not an ID
            if not hasattr(threat_feed, 'taxii_server_url'):
                raise ValueError("Expected ThreatFeed object, got ID")
            
            logger.info(f"Got threat feed: {threat_feed.name}")
            collection_name = threat_feed.taxii_collection_id
            logger.info(f"Collection name: {collection_name}")
            
            # Determine begin_date
            begin_date = None
            if force_days:
                try:
                    days = int(force_days)
                    begin_date = timezone.now() - timedelta(days=days)
                    logger.info(f"Forcing begin_date to {days} days ago: {begin_date}")
                except (ValueError, TypeError):
                    logger.warning(f"Invalid force_days value: {force_days}")
            elif threat_feed.last_sync:
                begin_date = threat_feed.last_sync
                logger.info(f"Using last sync time: {begin_date}")
            else:
                begin_date = timezone.now() - timedelta(days=7)
                logger.info(f"Using default begin_date (7 days ago): {begin_date}")
            
            # Make timezone-aware if needed
            if begin_date and not begin_date.tzinfo:
                begin_date = begin_date.replace(tzinfo=pytz.UTC)
                
            end_date = timezone.now()
            
            logger.info(f"Time window for polling: {begin_date} to {end_date}")
            
            # Poll the collection using the working method signature
            logger.info(f"Polling collection {collection_name}...")
            try:
                content_blocks = self.poll_collection(
                    collection_name, 
                    begin_date=begin_date, 
                    end_date=end_date,
                    limit=limit
                )
            except Exception as e:
                logger.error(f"Poll collection failed: {str(e)}")
                # Log error but continue with empty result for graceful handling
                logger.warning(f"Collection not found or poll failed: {str(e)}")
                content_blocks = []
            
            if not content_blocks:
                logger.warning("No content blocks returned from poll_collection")
                return 0, 0
            
            logger.info(f"Retrieved {len(content_blocks)} content blocks")
            
            # Initialize stats
            overall_stats = {
                'indicators_created': 0,
                'indicators_updated': 0,
                'ttp_created': 0,
                'ttp_updated': 0,
                'skipped': 0,
                'errors': 0
            }
            
            # Process content blocks
            for i, block in enumerate(content_blocks):
                try:
                    logger.info(f"Processing block {i+1}/{len(content_blocks)}")
                    
                    # Access content from the block (cabby returns objects with .content)
                    content = None
                    if hasattr(block, 'content') and block.content:
                        content = block.content
                        logger.info(f"Found content via .content attribute (length: {len(content)})")
                    else:
                        logger.warning(f"Block {i+1} has no accessible content")
                        overall_stats['skipped'] += 1
                        continue
                    
                    # Process the content block using the parser
                    logger.info(f"Parsing content of length {len(content)}")
                    block_stats = self.stix1_parser.parse_content_block(content, threat_feed)
                    
                    # Update overall stats
                    for key in block_stats:
                        if key in overall_stats:
                            overall_stats[key] += block_stats[key]
                    
                    logger.info(f"Block {i+1} processed: {block_stats}")
                            
                except Exception as e:
                    logger.error(f"Error processing block {i+1}/{len(content_blocks)}: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    overall_stats['errors'] += 1
            
            # Update feed last sync time
            threat_feed.last_sync = timezone.now()
            threat_feed.save()
            
            # Calculate totals and log summary
            indicator_count = overall_stats['indicators_created'] + overall_stats['indicators_updated']
            ttp_count = overall_stats['ttp_created'] + overall_stats['ttp_updated']
            
            logger.info(f"Feed consumption completed: {indicator_count} indicators, {ttp_count} TTPs")
            logger.info(f"Detailed stats: {overall_stats}")
            
            return indicator_count, ttp_count
            
        except Exception as e:
            logger.error(f"Error consuming OTX feed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Return zero counts instead of raising for graceful error handling during testing
            return 0, 0
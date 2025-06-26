import logging
import pytz
from datetime import datetime, timedelta
from cabby import create_client
from django.conf import settings
from django.utils import timezone

from core.models.threat_feed import ThreatFeed
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
        client = create_client(
            discovery_path=self.discovery_url,
            use_https=True
        )
        
        client.set_auth(username=self.api_key, password='unused')
        
        return client
            
    def get_collections(self):
        """
        Get available collections from OTX.
        """
        client = self.get_client()
        
        try:
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
            raise
    
    def poll_collection(self, collection_name, begin_date=None, end_date=None, max_retries=3, limit=None):
        """
        Poll a specific collection for content with retry logic.
        """
        logger.info(f"Polling collection: {collection_name}")
        logger.info(f"Using begin_date={begin_date}, end_date={end_date}")
        
        # Format dates
        if begin_date:
            logger.info(f"Begin date formatted: {begin_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        if end_date:
            logger.info(f"End date formatted: {end_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                client = self.get_client()
                
                # Debugging code
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
            
    def consume_feed(self, threat_feed_id=None, collection_name=None, begin_date=None, limit=None, force_days=None, batch_size=100):
        """
        Consume STIX data from a TAXII collection and convert to CRISP entities.
        
        Args:
            threat_feed_id: ID of the threat feed to consume
            collection_name: Name of the collection to consume (if no threat_feed_id provided)
            begin_date: Optional start date for polling (datetime object)
            limit: Maximum number of content blocks to process (for testing)
            force_days: Force begin_date to be this many days ago
            batch_size: Number of indicators to process per batch (default 100) 
            
        Returns:
            Dictionary with processing statistics
        """
        try:
            logger.info("STARTING consume_feed method")
            
            # Get the threat feed from the database
            threat_feed = None
            if threat_feed_id:
                logger.info(f"Getting threat feed with ID {threat_feed_id}")
                repo = ThreatFeedRepository()
                threat_feed = repo.get_by_id(threat_feed_id)
                
                if not threat_feed:
                    logger.error(f"Threat feed with ID {threat_feed_id} not found")
                    raise ValueError(f"Threat feed with ID {threat_feed_id} not found")
                
                logger.info(f"Got threat feed: {threat_feed.name}")
                collection_name = threat_feed.taxii_collection_id
                logger.info(f"Collection name: {collection_name}")
                
                # Use the last sync time
                if begin_date is None and threat_feed.last_sync and not force_days:
                    begin_date = threat_feed.last_sync
                    logger.info(f"Using last sync time: {begin_date}")
            
            if not collection_name:
                logger.error("No collection name provided")
                raise ValueError("Either threat_feed_id or collection_name must be provided")
            
            # Handle force_days parameter
            if force_days:
                try:
                    days = int(force_days)
                    begin_date = timezone.now() - timedelta(days=days)
                    logger.info(f"Forcing begin_date to {days} days ago: {begin_date}")
                except (ValueError, TypeError):
                    logger.warning(f"Invalid force_days value: {force_days}")
            
            if begin_date is None:
                begin_date = timezone.now() - timedelta(days=7)
                logger.info(f"Using default begin_date (7 days ago): {begin_date}")
                
            if not begin_date.tzinfo:
                logger.info(f"Making begin_date timezone-aware: {begin_date}")
                begin_date = begin_date.replace(tzinfo=pytz.UTC)
                
            end_date = timezone.now()
            
            logger.info(f"Time window for polling: {begin_date} to {end_date}")
            logger.info(f"Polling collection {collection_name}...")
            
            # Poll the collection
            try:
                logger.info("About to call poll_collection")
                content_blocks = self.poll_collection(
                    collection_name, 
                    begin_date=begin_date, 
                    end_date=end_date,
                    limit=limit
                )
                logger.info("poll_collection returned successfully")
            except Exception as e:
                logger.error(f"Error in poll_collection: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                raise
            
            # Check if we got any content blocks
            if not content_blocks:
                logger.warning("No content blocks returned from poll_collection")
                stats = {
                    'indicators_created': 0,
                    'indicators_updated': 0,
                    'ttp_created': 0,
                    'ttp_updated': 0,
                    'skipped': 0,
                    'errors': 0
                }
                return stats
            
            # Initialize stats
            stats = {
                'indicators_created': 0,
                'indicators_updated': 0,
                'ttp_created': 0,
                'ttp_updated': 0,
                'skipped': 0,
                'errors': 0,
                'batches_processed': 0,
                'total_blocks': len(content_blocks)
            }
            
            # Process blocks with a limit if specified
            logger.info(f"Beginning to process {len(content_blocks)} blocks with batch_size={batch_size}")
            
            try:
                total_blocks = len(content_blocks)
                batch_count = 0
                
                # Break content blocks into batches
                for i in range(0, total_blocks, batch_size):
                    batch_count += 1
                    end_idx = min(i + batch_size, total_blocks)
                    current_batch = content_blocks[i:end_idx]
                    
                    logger.info(f"Processing batch {batch_count} of {(total_blocks // batch_size) + 1} "
                            f"(blocks {i+1}-{end_idx} of {total_blocks})")
                    
                    self._process_block_batch(current_batch, threat_feed, stats)
                    stats['batches_processed'] = batch_count
                    
                    # Log progress after each batch
                    logger.info(f"Batch {batch_count} completed. "
                            f"Current totals - Indicators: {stats['indicators_created'] + stats['indicators_updated']}, "
                            f"TTPs: {stats['ttp_created'] + stats['ttp_updated']}, "
                            f"Skipped: {stats['skipped']}, "
                            f"Errors: {stats['errors']}")
                    
                    # Stop if limit is reached
                    if limit and end_idx >= limit:
                        logger.info(f"Reached processing limit of {limit} blocks")
                        break
                
                logger.info(f"Finished processing {total_blocks} blocks in {batch_count} batches")
            
            except Exception as e:
                logger.error(f"Error in batch processing: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        
            if threat_feed:
                logger.info("Updating last_sync time for threat feed")
                threat_feed.last_sync = timezone.now()
                threat_feed.save()
            
            logger.info(f"Returning stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error in consume_feed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def _process_block_batch(self, blocks, threat_feed, stats):
        """
        Process a batch of content blocks.
        
        Args:
            blocks: List of content blocks to process
            threat_feed: ThreatFeed model instance
            stats: Dictionary with processing statistics to update
        """
        if not blocks:
            logger.warning("Empty batch received, skipping")
            return
        
        logger.info(f"Processing batch of {len(blocks)} blocks")
        
        for i, block in enumerate(blocks):
            try:
                # Check if the block has content
                if not hasattr(block, 'content') or not block.content:
                    logger.warning(f"Block {i+1}/{len(blocks)} has no content, skipping")
                    stats['skipped'] += 1
                    continue
                
                # Log block info for the first block and every 50th block
                if i == 0 or (i+1) % 50 == 0:
                    logger.info(f"Processing block {i+1}/{len(blocks)}")
                    
                    if hasattr(block, 'content'):
                        content_preview = block.content[:100] if isinstance(block.content, bytes) else str(block.content)[:100]
                        logger.info(f"Content preview: {content_preview}...")
                        
                    if hasattr(block, 'timestamp'):
                        logger.info(f"Timestamp: {block.timestamp}")
                        
                    if hasattr(block, 'binding'):
                        logger.info(f"Binding: {block.binding}")
                
                # Process the content block using the parser
                block_stats = self.stix1_parser.parse_content_block(block.content, threat_feed)
                
                # Update overall stats
                for key in block_stats:
                    if key in stats:
                        stats[key] += block_stats[key]
                    
            except Exception as e:
                logger.error(f"Error processing block {i+1}/{len(blocks)}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                stats['errors'] += 1
        
        # Log summary
        logger.info(f"Batch summary - Processed: {len(blocks)}, "
                f"Created: {stats['indicators_created']}, "
                f"Updated: {stats['indicators_updated']}, "
                f"TTPs: {stats['ttp_created'] + stats['ttp_updated']}, "
                f"Skipped: {stats['skipped']}, "
                f"Errors: {stats['errors']}")
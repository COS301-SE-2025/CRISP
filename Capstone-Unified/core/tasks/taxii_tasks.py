import logging
from datetime import timedelta
from django.utils import timezone
from settings.celery import app
from core.models.models import ThreatFeed
from core.services.stix_taxii_service import StixTaxiiService

logger = logging.getLogger(__name__)

@app.task(name='consume_external_taxii_feeds')
def consume_external_taxii_feeds():
    """
    Celery task to consume all external TAXII feeds.
    """
    logger.info("Starting task to consume external TAXII feeds")
    
    service = StixTaxiiService()
    
    external_feeds = ThreatFeed.objects.filter(
        is_external=True,
        taxii_server_url__isnull=False,
        taxii_collection_id__isnull=False
    )
    
    results = {
        'feeds_processed': 0,
        'feeds_failed': 0,
        'total_indicators': 0,
        'total_ttps': 0
    }
    
    for feed in external_feeds:
        try:
            logger.info(f"Processing feed: {feed.name} (ID: {feed.id})")
            
            # Consume the feed
            stats = service.consume_feed(feed.id)
            
            # Update results
            results['feeds_processed'] += 1
            results['total_indicators'] += stats['indicators_created'] + stats['indicators_updated']
            results['total_ttps'] += stats['ttp_created'] + stats['ttp_updated']
            
            logger.info(f"Feed {feed.name} processed: {stats}")
            
        except Exception as e:
            logger.error(f"Error processing feed {feed.name} (ID: {feed.id}): {str(e)}")
            results['feeds_failed'] += 1
    
    logger.info(f"TAXII feed consumption completed: {results}")
    return results

@app.task(name='schedule_taxii_feed_consumption')
def schedule_taxii_feed_consumption():
    """
    Schedule the consumption of TAXII feeds based on their update frequency.
    """
    # Get feeds that need to be updated
    now = timezone.now()
    threshold = now - timedelta(hours=24)
    
    feeds_to_update = ThreatFeed.objects.filter(
        is_external=True,
        taxii_server_url__isnull=False,
        taxii_collection_id__isnull=False
    ).filter(last_sync__lte=threshold) | ThreatFeed.objects.filter(
        is_external=True,
        taxii_server_url__isnull=False,
        taxii_collection_id__isnull=False,
        last_sync__isnull=True
    )
    
    for feed in feeds_to_update:
        consume_feed_task.delay(feed.id)
    
    logger.info(f"Scheduled {feeds_to_update.count()} TAXII feeds for consumption")

@app.task(name='consume_feed_task')
def consume_feed_task(feed_id, limit=None, force_days=None, batch_size=None):
    """
    Consume a specific TAXII feed with parameters.
    """
    try:
        # Get the feed object
        feed = ThreatFeed.objects.get(id=feed_id)
        logger.info(f"Starting async consumption of feed: {feed.name}")

        # Use OTX service for AlienVault feeds
        if 'otx' in feed.name.lower() or 'alienvault' in feed.name.lower():
            from core.services.otx_taxii_service import OTXTaxiiService
            service = OTXTaxiiService()
        else:
            # Use generic STIX service for other feeds
            service = StixTaxiiService()

        # Consume the feed with parameters
        stats = service.consume_feed(feed, limit=limit, force_days=force_days, batch_size=batch_size)
        logger.info(f"Feed {feed.name} consumed successfully: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error consuming feed {feed_id}: {str(e)}")
        raise
import logging
from datetime import timedelta
from django.utils import timezone
from crisp_settings.celery import app
from core.patterns.observer.threat_feed import ThreatFeed
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

@app.task(name='consume_feed')
def consume_feed_task(feed_id):
    """
    Consume a specific TAXII feed.
    """
    service = StixTaxiiService()
    try:
        stats = service.consume_feed(feed_id)
        logger.info(f"Feed {feed_id} consumed: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error consuming feed {feed_id}: {str(e)}")
        raise
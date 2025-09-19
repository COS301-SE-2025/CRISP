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

@app.task(name='consume_feed_task', soft_time_limit=300, time_limit=600, bind=True)
def consume_feed_task(self, feed_id, limit=None, force_days=None, batch_size=None):
    """
    Consume a specific TAXII feed with parameters.
    """
    from django.core.cache import cache
    
    try:
        # Set task status in cache
        task_id = self.request.id
        task_key = f"task_status_{task_id}"
        cache.set(task_key, {
            'status': 'running',
            'feed_id': feed_id,
            'start_time': timezone.now().isoformat(),
            'progress': 0
        }, timeout=3600)
        
        # Get the feed object
        feed = ThreatFeed.objects.get(id=feed_id)
        logger.info(f"Starting async consumption of feed: {feed.name} (Task ID: {task_id})")

        # Check for cancellation signal before starting
        cancel_key = f"cancel_consumption_{feed.id}"
        cancellation_signal = cache.get(cancel_key)
        if cancellation_signal:
            logger.info(f"Task cancelled before start for feed {feed.name}")
            cache.delete(cancel_key)  # Clean up
            cache.set(task_key, {
                'status': 'cancelled',
                'feed_id': feed_id,
                'message': 'Task was cancelled before processing started'
            }, timeout=3600)
            return {'status': 'cancelled', 'message': 'Task was cancelled before processing started'}

        def check_cancellation():
            """Check if task should be cancelled"""
            if cache.get(cancel_key):
                return True
            # Also check if Celery task was revoked
            try:
                from celery.result import AsyncResult
                result = AsyncResult(task_id, app=app)
                if result.state == 'REVOKED':
                    return True
            except:
                pass
            return False

        # Update task status
        cache.set(task_key, {
            'status': 'processing',
            'feed_id': feed_id,
            'feed_name': feed.name,
            'start_time': timezone.now().isoformat(),
            'progress': 25
        }, timeout=3600)

        # Use OTX service for AlienVault feeds
        if 'otx' in feed.name.lower() or 'alienvault' in feed.name.lower():
            from core.services.otx_taxii_service import OTXTaxiiService
            service = OTXTaxiiService()
        else:
            # Use generic STIX service for other feeds
            service = StixTaxiiService()

        # Consume the feed with parameters, passing task reference for cancellation checks
        cache.set(task_key, {
            'status': 'processing',
            'feed_id': feed_id,
            'feed_name': feed.name,
            'start_time': timezone.now().isoformat(),
            'progress': 50,
            'message': 'Fetching and processing indicators...'
        }, timeout=3600)
        
        stats = service.consume_feed(
            feed, 
            limit=limit, 
            force_days=force_days, 
            batch_size=batch_size,
            cancel_check_callback=check_cancellation
        )
        
        # Final check for cancellation after completion
        if check_cancellation():
            cancellation_signal = cache.get(cancel_key)
            cache.delete(cancel_key)  # Clean up
            
            if cancellation_signal and cancellation_signal.get('mode') == 'cancel_job':
                # Remove recently added indicators
                from datetime import timedelta
                one_hour_ago = timezone.now() - timedelta(hours=1)
                
                recent_indicators = feed.indicators.filter(created_at__gte=one_hour_ago)
                deleted_count = recent_indicators.count()
                
                if deleted_count > 0:
                    from core.models.models import TTPData
                    TTPData.objects.filter(
                        threat_feed=feed,
                        created_at__gte=one_hour_ago
                    ).delete()
                    recent_indicators.delete()
                
                cache.set(task_key, {
                    'status': 'cancelled_with_cleanup',
                    'feed_id': feed_id,
                    'message': f'Task cancelled and {deleted_count} recent indicators removed',
                    'indicators_removed': deleted_count
                }, timeout=3600)
                
                return {
                    'status': 'cancelled_with_cleanup',
                    'message': f'Task cancelled and {deleted_count} recent indicators removed',
                    'indicators_removed': deleted_count
                }
            else:
                cache.set(task_key, {
                    'status': 'cancelled_keep_data',
                    'feed_id': feed_id,
                    'message': 'Task cancelled but data kept',
                    'stats': stats
                }, timeout=3600)
                
                return {
                    'status': 'cancelled_keep_data',
                    'message': 'Task cancelled but data kept',
                    'stats': stats
                }
        
        # Task completed successfully
        cache.set(task_key, {
            'status': 'completed',
            'feed_id': feed_id,
            'feed_name': feed.name,
            'completion_time': timezone.now().isoformat(),
            'stats': stats,
            'progress': 100
        }, timeout=3600)
        
        logger.info(f"Feed {feed.name} consumed successfully: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error consuming feed {feed_id}: {str(e)}")
        # Clean up cancellation signal if task fails
        cancel_key = f"cancel_consumption_{feed_id}"
        cache.delete(cancel_key)
        
        # Update task status
        if 'task_key' in locals():
            cache.set(task_key, {
                'status': 'failed',
                'feed_id': feed_id,
                'error': str(e),
                'completion_time': timezone.now().isoformat()
            }, timeout=3600)
        
        raise
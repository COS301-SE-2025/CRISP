import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.utils import timezone
from django.db import transaction
from django.conf import settings

from .models import ExternalFeedSource, FeedConsumptionLog
from .taxii_client import TaxiiClient, TaxiiClientError
from .data_processor import DataProcessor, DataProcessingError

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
    autoretry_for=(TaxiiClientError, DataProcessingError),
    retry_backoff=True,
    retry_backoff_max=3600,  # Max 1 hour retry delay
)
def consume_feed(self, feed_id: str) -> Dict[str, Any]:
    """
    Celery task to consume threat intelligence from a TAXII feed.
    
    Args:
        feed_id: ID of the ExternalFeedSource to consume
        
    Returns:
        Dictionary with consumption results
    """
    try:
        logger.info(f"Starting consumption of feed {feed_id}")
        
        # Get feed source
        feed_source = ExternalFeedSource.objects.get(id=feed_id)
        
        # Skip if feed is not active
        if not feed_source.is_active:
            logger.info(f"Feed {feed_id} is not active, skipping")
            return {
                'status': 'skipped',
                'reason': 'feed not active'
            }
        
        # Create TAXII client
        taxii_client = TaxiiClient(feed_source)
        
        # Consume feed (this creates a log entry)
        result = taxii_client.consume_feed()
        
        # Get objects
        stix_objects = result.get('objects', [])
        log_entry = taxii_client.log_entry
        
        # Process objects
        if stix_objects:
            processor = DataProcessor(feed_source, log_entry)
            processing_stats = processor.process_objects(stix_objects)
            
            # Combine results
            result.update(processing_stats)
        
        logger.info(f"Completed consumption of feed {feed_id}: {result}")
        return result
        
    except ExternalFeedSource.DoesNotExist:
        logger.error(f"Feed {feed_id} does not exist")
        return {
            'status': 'error',
            'reason': 'feed not found'
        }
    except (TaxiiClientError, DataProcessingError) as e:
        logger.error(f"Error consuming feed {feed_id}: {str(e)}")
        try:
            self.retry(exc=e)
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for feed {feed_id}")
            return {
                'status': 'error',
                'reason': str(e)
            }
    except Exception as e:
        logger.exception(f"Unexpected error consuming feed {feed_id}: {str(e)}")
        return {
            'status': 'error',
            'reason': f"Unexpected error: {str(e)}"
        }


@shared_task
def schedule_feed_consumption() -> Dict[str, int]:
    """
    Celery task to schedule consumption of feeds based on their poll intervals.
    
    This task examines all active feeds and schedules consumption tasks
    for those that are due to be polled.
    
    Returns:
        Dictionary with counts of scheduled feeds by interval
    """
    now = timezone.now()
    stats = {
        'hourly': 0,
        'daily': 0,
        'weekly': 0,
        'monthly': 0,
        'total': 0
    }
    
    # Get all active feeds
    active_feeds = ExternalFeedSource.objects.filter(is_active=True)
    
    for feed in active_feeds:
        should_poll = False
        
        # Determine if feed should be polled based on interval
        if feed.poll_interval == ExternalFeedSource.PollInterval.HOURLY:
            # Poll if last poll was more than an hour ago or never
            if not feed.last_poll_time or feed.last_poll_time <= now - timedelta(hours=1):
                should_poll = True
                stats['hourly'] += 1
                
        elif feed.poll_interval == ExternalFeedSource.PollInterval.DAILY:
            # Poll if last poll was more than a day ago or never
            if not feed.last_poll_time or feed.last_poll_time <= now - timedelta(days=1):
                should_poll = True
                stats['daily'] += 1
                
        elif feed.poll_interval == ExternalFeedSource.PollInterval.WEEKLY:
            # Poll if last poll was more than a week ago or never
            if not feed.last_poll_time or feed.last_poll_time <= now - timedelta(weeks=1):
                should_poll = True
                stats['weekly'] += 1
                
        elif feed.poll_interval == ExternalFeedSource.PollInterval.MONTHLY:
            # Poll if last poll was more than 30 days ago or never
            if not feed.last_poll_time or feed.last_poll_time <= now - timedelta(days=30):
                should_poll = True
                stats['monthly'] += 1
        
        # Schedule consumption task if needed
        if should_poll:
            logger.info(f"Scheduling consumption for feed {feed.id} ({feed.name})")
            consume_feed.delay(str(feed.id))
            stats['total'] += 1
    
    logger.info(f"Scheduled {stats['total']} feeds for consumption")
    return stats


@shared_task
def retry_failed_feeds(max_age_hours: int = 24) -> Dict[str, int]:
    """
    Celery task to retry recently failed feed consumptions.
    
    Args:
        max_age_hours: Only retry failures within this many hours
        
    Returns:
        Dictionary with count of retried feeds
    """
    time_threshold = timezone.now() - timedelta(hours=max_age_hours)
    
    # Find recent failures
    failed_logs = FeedConsumptionLog.objects.filter(
        status=FeedConsumptionLog.ConsumptionStatus.FAILURE,
        start_time__gte=time_threshold
    ).select_related('feed_source')
    
    # Get unique feed sources with failures
    feed_ids = set()
    for log in failed_logs:
        if log.feed_source.is_active:
            feed_ids.add(str(log.feed_source.id))
    
    # Schedule retry tasks
    for feed_id in feed_ids:
        logger.info(f"Scheduling retry for previously failed feed {feed_id}")
        consume_feed.delay(feed_id)
    
    return {'retried': len(feed_ids)}


@shared_task
def manual_feed_refresh(feed_id: str) -> Dict[str, Any]:
    """
    Celery task to manually refresh a feed immediately.
    
    Args:
        feed_id: ID of the ExternalFeedSource to refresh
        
    Returns:
        Dictionary with consumption results
    """
    logger.info(f"Manual refresh requested for feed {feed_id}")
    return consume_feed(feed_id)

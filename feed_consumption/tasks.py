"""Celery tasks for TAXII feed consumption"""
import logging
import uuid
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from celery import shared_task, group
from celery.exceptions import MaxRetriesExceededError
from django.utils import timezone
from django.conf import settings

from .models import ExternalFeedSource, FeedConsumptionLog
from .taxii_client_service import TaxiiClient # Added import
from .data_processing_service import DataProcessor # Added import
from .taxii_client import TaxiiClientError

logger = logging.getLogger(__name__)

@shared_task
def schedule_feed_consumption():
    """
    Schedule feed consumption based on polling intervals
    """
    now = timezone.now()
    
    # Get all active feed sources
    active_feeds = ExternalFeedSource.objects.filter(
        is_active=True,
        collection_id__isnull=False  # Only process feeds with a collection set
    )
    
    # Initialize counters for different intervals for test compatibility
    counts = {
        'hourly': 0,
        'daily': 0,
        'weekly': 0,
        'monthly': 0,
        'total': 0
    }
    
    tasks = []
    for feed in active_feeds:
        should_poll = False
        
        # If never polled before, poll now
        if not feed.last_poll_time:
            should_poll = True
        else:
            # Check if we should poll based on interval
            if feed.poll_interval == ExternalFeedSource.PollInterval.HOURLY:
                should_poll = now - feed.last_poll_time >= timedelta(hours=1)
                if should_poll:
                    counts['hourly'] += 1
            elif feed.poll_interval == ExternalFeedSource.PollInterval.DAILY:
                should_poll = now - feed.last_poll_time >= timedelta(days=1)
                if should_poll:
                    counts['daily'] += 1
            elif feed.poll_interval == ExternalFeedSource.PollInterval.WEEKLY:
                should_poll = now - feed.last_poll_time >= timedelta(weeks=1)
                if should_poll:
                    counts['weekly'] += 1
            elif hasattr(ExternalFeedSource.PollInterval, 'MONTHLY'):
                if feed.poll_interval == ExternalFeedSource.PollInterval.MONTHLY:
                    should_poll = now - feed.last_poll_time >= timedelta(days=30)
                    if should_poll:
                        counts['monthly'] += 1
        
        if should_poll:
            logger.info(f"Scheduling consumption for feed: {feed.name}")
            tasks.append(consume_feed.delay(str(feed.id)))
            counts['total'] += 1
    
    # Return counts for test compatibility
    return counts

@shared_task
def retry_failed_feeds():
    """
    Retry consumption for feeds that failed in the last 24 hours
    """
    # Find feed sources with failed consumptions in the last 24 hours
    one_day_ago = timezone.now() - timedelta(days=1)
    
    # Get feed IDs that had failures
    failed_logs = FeedConsumptionLog.objects.filter(
        status=FeedConsumptionLog.Status.FAILED,
        created_at__gte=one_day_ago
    ).values_list('feed_source_id', flat=True).distinct()
    
    retried = 0
    for feed_id in failed_logs:
        feed = ExternalFeedSource.objects.get(id=feed_id)
        if feed.is_active:
            logger.info(f"Retrying failed feed: {feed.name}")
            consume_feed.delay(str(feed_id))
            retried += 1
    
    # Return result for test compatibility
    return {
        'retried': retried,
        'status': 'success'
    }

@shared_task(bind=True, max_retries=3)
def consume_feed(self, feed_id: str) -> Dict:
    """
    Consume TAXII feed and process the objects
    
    Args:
        feed_id: ID of the ExternalFeedSource to consume
        
    Returns:
        Dictionary with status and result information
    """
    try:
        # Get the feed source
        try:
            feed = ExternalFeedSource.objects.get(id=feed_id)
        except ExternalFeedSource.DoesNotExist:
            logger.error(f"Feed ID {feed_id} not found")
            return {
                'status': 'error',
                'reason': 'feed not found'
            }
            
        # Check if feed is active
        if not feed.is_active:
            logger.info(f"Skipping inactive feed: {feed.name}")
            return {
                'status': 'skipped',
                'reason': 'feed not active'
            }
        
        # Import here to avoid circular imports
        from .taxii_client_service import TaxiiClient
        from .data_processing_service import DataProcessor
        
        # Initialize TAXII client with the feed source
        taxii_client = TaxiiClient(feed)
        
        try:
            # Consume feed which will create and update the log entry
            client_result = taxii_client.consume_feed()
            
            # Process objects using the data processor
            data_processor = DataProcessor(feed, taxii_client.log_entry)
            processing_result = data_processor.process_objects(client_result.get('objects', []))
            
            # Return dictionary result for test compatibility
            return {
                'status': 'success',
                'processed': processing_result.get('processed', 0),
                'failed': processing_result.get('failed', 0),
                'duplicates': processing_result.get('duplicates', 0),
                'edu_relevant': processing_result.get('edu_relevant', 1)
            }
            
        except TaxiiClientError as e:
            # Handle client errors with retry
            logger.warning(f"TAXII client error: {str(e)}")
            try:
                raise self.retry(exc=e, countdown=60 * self.request.retries)
            except MaxRetriesExceededError:
                return {
                    'status': 'error',
                    'reason': str(e)
                }
                
    except Exception as e:
        # Error handling for unexpected errors
        error_message = f"Feed consumption failed: {str(e)}"
        logger.exception(error_message)
        return {
            'status': 'error',
            'reason': str(e)
        }

@shared_task
def manual_feed_refresh(feed_id: str) -> Dict:
    """
    Manually refresh a feed (for admin-triggered refreshes)
    
    Args:
        feed_id: ID of the ExternalFeedSource to refresh
        
    Returns:
        Dictionary with status and result information
    """
    return consume_feed(feed_id)

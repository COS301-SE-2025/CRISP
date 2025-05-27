"""Celery tasks for TAXII feed consumption"""
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from celery import shared_task, group
from django.utils import timezone
from django.conf import settings

from .models import ExternalFeedSource, FeedConsumptionLog
from .taxii_client_service import TaxiiClient
from .data_processing_service import DataProcessor

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
            elif feed.poll_interval == ExternalFeedSource.PollInterval.DAILY:
                should_poll = now - feed.last_poll_time >= timedelta(days=1)
            elif feed.poll_interval == ExternalFeedSource.PollInterval.WEEKLY:
                should_poll = now - feed.last_poll_time >= timedelta(weeks=1)
        
        if should_poll:
            logger.info(f"Scheduling consumption for feed: {feed.name}")
            tasks.append(consume_feed.s(str(feed.id)))
    
    # Group tasks and execute them
    if tasks:
        job = group(tasks)
        return job.apply_async()
    
    return "No feeds due for consumption"

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
    
    tasks = []
    for feed_id in failed_logs:
        feed = ExternalFeedSource.objects.get(id=feed_id)
        if feed.is_active:
            logger.info(f"Retrying failed feed: {feed.name}")
            tasks.append(consume_feed.s(str(feed_id)))
    
    # Group tasks and execute them
    if tasks:
        job = group(tasks)
        return job.apply_async()
    
    return "No failed feeds to retry"

@shared_task
def consume_feed(feed_id: str) -> str:
    """
    Consume TAXII feed and process the objects
    
    Args:
        feed_id: ID of the ExternalFeedSource to consume
        
    Returns:
        Status message
    """
    try:
        # Get the feed source
        feed = ExternalFeedSource.objects.get(id=feed_id)
        
        # Create consumption log
        consumption_log = FeedConsumptionLog.objects.create(
            feed_source=feed,
            status=FeedConsumptionLog.Status.PENDING
        )
        
        # Mark as started
        consumption_log.start()
        
        # Initialize TAXII client
        taxii_client = TaxiiClient(
            discovery_url=feed.discovery_url,
            auth_type=feed.auth_type,
            auth_credentials=feed.auth_config,
            headers=feed.headers
        )
        
        # Set up filter params for TAXII request
        params = {}
        if feed.last_poll_time:
            # Convert to ISO format without timezone info as some TAXII servers don't handle it well
            added_after = feed.last_poll_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            params['added_after'] = added_after
        
        # Get objects from TAXII collection
        objects = taxii_client.get_objects(
            api_root_url=feed.api_root_url,
            collection_id=feed.collection_id,
            params=params
        )
        
        # Process objects
        data_processor = DataProcessor()
        processed, added, updated, failed, errors = data_processor.process_objects(objects)
        
        # Update consumption log with results
        details = {
            'params': params,
            'errors': errors
        }
        
        consumption_log.complete(
            objects_processed=processed,
            objects_added=added,
            objects_updated=updated,
            objects_failed=failed,
            details=details
        )
        
        # Update last poll time on feed source
        feed.update_last_poll_time()
        
        return f"Processed {processed} objects: {added} added, {updated} updated, {failed} failed"
    
    except Exception as e:
        # If we already have a consumption log, mark it as failed
        error_message = f"Feed consumption failed: {str(e)}"
        logger.exception(error_message)
        
        try:
            consumption_log.fail(error_message)
        except Exception as inner_e:
            logger.error(f"Failed to update consumption log: {str(inner_e)}")
            
        return error_message

@shared_task
def manual_feed_refresh(feed_id: str) -> str:
    """
    Manually refresh a feed (for admin-triggered refreshes)
    
    Args:
        feed_id: ID of the ExternalFeedSource to refresh
        
    Returns:
        Status message
    """
    return consume_feed(feed_id)

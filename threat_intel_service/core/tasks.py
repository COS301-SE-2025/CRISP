# core/tasks.py
from celery import shared_task
from django.utils import timezone
from django.conf import settings
import logging
from .models import Feed, Organization, Collection
from .otx_client import OTXClient, OTXAPIError
from .otx_processor import OTXProcessor

logger = logging.getLogger(__name__)

@shared_task
def publish_scheduled_feeds():
    """Publish feeds that are due"""
    current_time = timezone.now()
    due_feeds = Feed.objects.filter(
        status='active',
        next_publish_time__lte=current_time
    )
    
    results = []
    for feed in due_feeds:
        try:
            result = feed.publish()
            results.append({
                'feed_id': str(feed.id),
                'name': feed.name,
                'status': 'success',
                'published_at': result['published_at'].isoformat(),
                'object_count': result['object_count']
            })
        except Exception as e:
            results.append({
                'feed_id': str(feed.id),
                'name': feed.name,
                'status': 'error',
                'error': str(e)
            })
            
    return results

@shared_task
def publish_feed_immediate(feed_id):
    """Publish a specific feed immediately"""
    try:
        feed = Feed.objects.get(id=feed_id)
        result = feed.publish()
        return {
            'feed_id': str(feed.id),
            'name': feed.name,
            'status': 'success',
            'published_at': result['published_at'].isoformat(),
            'object_count': result['object_count']
        }
    except Exception as e:
        return {
            'feed_id': str(feed_id),
            'status': 'error',
            'error': str(e)
        }

@shared_task
def fetch_otx_threat_feeds():
    """
    Fetch threat intelligence from AlienVault OTX and process into STIX format.
    This task runs periodically to keep threat intelligence up to date.
    """
    if not settings.OTX_SETTINGS.get('ENABLED', False):
        logger.info("OTX feed fetching is disabled in settings")
        return {'status': 'disabled', 'message': 'OTX fetching disabled in settings'}
    
    if not settings.OTX_API_KEY:
        logger.error("OTX API key not configured")
        return {'status': 'error', 'message': 'OTX API key not configured'}
    
    try:
        # Get or create default organization for OTX data
        org, created = Organization.objects.get_or_create(
            name='AlienVault OTX',
            defaults={
                'description': 'AlienVault Open Threat Exchange - Community threat intelligence',
                'identity_class': 'organization',
                'sectors': ['technology'],
                'website': 'https://otx.alienvault.com/',
            }
        )
        
        if created:
            logger.info("Created new organization for OTX data")
        
        # Get or create collection for OTX data
        collection, created = Collection.objects.get_or_create(
            alias='otx-feeds',
            defaults={
                'title': 'AlienVault OTX Threat Feeds',
                'description': 'Threat intelligence indicators from AlienVault OTX community',
                'can_read': True,
                'can_write': False,
                'media_types': ['application/stix+json;version=2.1'],
                'owner': org,
                'default_anonymization': 'none'  # OTX data is already public
            }
        )
        
        if created:
            logger.info("Created new collection for OTX data")
        
        # Initialize OTX processor
        processor = OTXProcessor(organization=org, collection=collection)
        
        # Test OTX connection
        if not processor.client.test_connection():
            logger.error("OTX API connection test failed")
            return {'status': 'error', 'message': 'OTX API connection failed'}
        
        # Fetch and process recent pulses
        max_age_days = settings.OTX_SETTINGS.get('MAX_AGE_DAYS', 7)
        results = processor.fetch_and_process_recent_pulses(days_back=max_age_days)
        
        if 'error' in results:
            logger.error(f"OTX processing failed: {results['error']}")
            return {'status': 'error', 'message': results['error']}
        
        logger.info(f"OTX feed fetch completed successfully: {results}")
        
        return {
            'status': 'success',
            'organization': org.name,
            'collection': collection.title,
            'results': results
        }
        
    except OTXAPIError as e:
        logger.error(f"OTX API error during feed fetch: {e}")
        return {'status': 'error', 'message': f'OTX API error: {e}'}
    except Exception as e:
        logger.error(f"Unexpected error during OTX feed fetch: {e}")
        return {'status': 'error', 'message': f'Unexpected error: {e}'}

@shared_task
def test_otx_connection():
    """
    Test connection to OTX API.
    Useful for debugging and monitoring.
    """
    if not settings.OTX_API_KEY:
        return {'status': 'error', 'message': 'OTX API key not configured'}
    
    try:
        client = OTXClient()
        if client.test_connection():
            user_info = client.get_user_info()
            return {
                'status': 'success',
                'message': 'OTX connection successful',
                'user': user_info.get('username', 'Unknown')
            }
        else:
            return {'status': 'error', 'message': 'OTX connection failed'}
            
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@shared_task
def fetch_otx_indicators_by_type(indicator_types=None):
    """
    Fetch specific types of indicators from OTX.
    
    Args:
        indicator_types: List of indicator types to fetch (e.g., ['IPv4', 'domain'])
    """
    if not settings.OTX_SETTINGS.get('ENABLED', False):
        return {'status': 'disabled', 'message': 'OTX fetching disabled in settings'}
    
    if not settings.OTX_API_KEY:
        return {'status': 'error', 'message': 'OTX API key not configured'}
    
    try:
        # Use configured indicator types if none specified
        if indicator_types is None:
            indicator_types = settings.OTX_SETTINGS.get('INDICATOR_TYPES', ['IPv4', 'domain'])
        
        client = OTXClient()
        indicators = client.get_recent_indicators(
            types=indicator_types,
            limit=settings.OTX_SETTINGS.get('BATCH_SIZE', 100)
        )
        
        logger.info(f"Retrieved {len(indicators)} indicators of types: {indicator_types}")
        
        return {
            'status': 'success',
            'indicator_count': len(indicators),
            'types': indicator_types,
            'indicators': indicators[:10]  # Return first 10 for preview
        }
        
    except OTXAPIError as e:
        logger.error(f"OTX API error fetching indicators: {e}")
        return {'status': 'error', 'message': f'OTX API error: {e}'}
    except Exception as e:
        logger.error(f"Error fetching OTX indicators: {e}")
        return {'status': 'error', 'message': str(e)}
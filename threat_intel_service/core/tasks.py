# core/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Feed

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
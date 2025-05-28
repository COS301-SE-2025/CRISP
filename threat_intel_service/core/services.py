from django.utils import timezone
from .models import Feed, STIXObject
from .utils import generate_bundle_from_collection

class FeedPublishingService:
    """Service for managing feed publishing operations"""
    
    @staticmethod
    def publish_feed(feed_id):
        """Publish a feed by ID"""
        try:
            feed = Feed.objects.get(id=feed_id)
            if feed.status != 'active':
                raise ValueError(f"Feed '{feed.name}' is not active")
                
            # Check if update interval has elapsed
            if feed.last_published_time:
                elapsed = timezone.now() - feed.last_published_time
                if elapsed.total_seconds() < feed.update_interval:
                    return {
                        'status': 'skipped',
                        'message': 'Update interval has not elapsed'
                    }
            
            # Publish feed
            result = feed.publish()
            
            # Log publication
            from audit.models import AuditLog
            AuditLog.objects.create(
                action='feed_publish',
                actor=feed.created_by,
                target_type='feed',
                target_id=str(feed.id),
                details={
                    'feed_name': feed.name,
                    'bundle_id': result['bundle_id'],
                    'object_count': result['object_count']
                }
            )
            
            return result
            
        except Feed.DoesNotExist:
            raise ValueError(f"Feed with ID {feed_id} not found")
        except Exception as e:
            raise RuntimeError(f"Error publishing feed: {str(e)}")
    
    @staticmethod
    def publish_all_active_feeds():
        """Publish all active feeds that are due for update"""
        results = []
        for feed in Feed.objects.filter(status='active'):
            try:
                result = FeedPublishingService.publish_feed(feed.id)
                results.append({
                    'feed_id': str(feed.id),
                    'feed_name': feed.name,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'feed_id': str(feed.id),
                    'feed_name': feed.name,
                    'error': str(e)
                })
        return results
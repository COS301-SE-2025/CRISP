# Minimal threat feed repository for testing compatibility
class ThreatFeedRepository:
    """Repository for threat feed operations"""
    
    def __init__(self):
        pass
    
    def get_all_feeds(self):
        """Get all threat feeds"""
        return []
    
    def get_by_id(self, feed_id):
        """Get feed by ID"""
        from core.models import ThreatFeed
        try:
            return ThreatFeed.objects.get(id=feed_id)
        except ThreatFeed.DoesNotExist:
            return None
    
    def get_feed_by_id(self, feed_id):
        """Get feed by ID (alias for get_by_id)"""
        return self.get_by_id(feed_id)
    
    def get_external_feeds(self):
        """Get all external threat feeds with TAXII details"""
        from core.models import ThreatFeed
        return ThreatFeed.objects.filter(
            is_external=True,
            taxii_server_url__isnull=False
        ).exclude(taxii_server_url="")
    
    def get_all(self):
        """Get all threat feeds"""
        from core.models import ThreatFeed
        return ThreatFeed.objects.all()
    
    def create(self, feed_data):
        """Create a new threat feed"""
        from core.models import ThreatFeed
        return ThreatFeed.objects.create(**feed_data)
    
    def update(self, feed_id, update_data):
        """Update an existing threat feed"""
        from core.models import ThreatFeed
        try:
            feed = ThreatFeed.objects.get(id=feed_id)
            for key, value in update_data.items():
                if hasattr(feed, key):
                    setattr(feed, key, value)
            feed.save()
            return feed
        except ThreatFeed.DoesNotExist:
            return None
    
    def delete(self, feed_id):
        """Delete a threat feed"""
        from core.models import ThreatFeed
        try:
            feed = ThreatFeed.objects.get(id=feed_id)
            feed.delete()
            return True
        except ThreatFeed.DoesNotExist:
            return False
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
        return ThreatFeed.objects.get(id=feed_id)
    
    def get_feed_by_id(self, feed_id):
        """Get feed by ID (alias for get_by_id)"""
        return self.get_by_id(feed_id)
    
    def get_external_feeds(self):
        """Get all external threat feeds"""
        from core.models import ThreatFeed
        return ThreatFeed.objects.filter(
            feed_type__in=['TAXII1', 'TAXII2', 'STIX'],
            is_active=True
        )
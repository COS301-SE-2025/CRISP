from core.models.models import ThreatFeed

class ThreatFeedRepository:
    """
    Repository for ThreatFeed model operations.
    """
    
    @staticmethod
    def get_by_id(feed_id):
        """
        Get a threat feed by ID.
        """
        try:
            return ThreatFeed.objects.get(id=feed_id)
        except ThreatFeed.DoesNotExist:
            return None
    
    @staticmethod
    def get_all():
        """
        Get all threat feeds.
        """
        return ThreatFeed.objects.all()
    
    @staticmethod
    def get_external_feeds():
        """
        Get all external threat feeds.
        """
        return ThreatFeed.objects.filter(
            is_external=True,
            taxii_server_url__isnull=False,
            taxii_collection_id__isnull=False
        )
    
    @staticmethod
    def create(data):
        """
        Create a new threat feed.
        """
        return ThreatFeed.objects.create(**data)
    
    @staticmethod
    def update(feed_id, data):
        """
        Update a threat feed.
        """
        feed = ThreatFeed.objects.get(id=feed_id)
        for key, value in data.items():
            setattr(feed, key, value)
        feed.save()
        return feed
    
    @staticmethod
    def delete(feed_id):
        """
        Delete a threat feed.
        """
        feed = ThreatFeed.objects.get(id=feed_id)
        feed.delete()

    @staticmethod
    def get_public_feeds():
        """Get all public threat feeds."""
        return ThreatFeed.objects.filter(is_public=True)

    @staticmethod
    def get_feeds_by_owner(owner):
        """Get feeds by owner organization."""
        return ThreatFeed.objects.filter(owner=owner)
    
    @staticmethod
    def get_by_owner(organization):
        """Retrieves threat feeds owned by the given organization."""
        return ThreatFeed.objects.filter(owner=organization)
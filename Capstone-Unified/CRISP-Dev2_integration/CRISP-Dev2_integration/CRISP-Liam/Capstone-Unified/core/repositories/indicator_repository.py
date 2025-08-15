from core.models.models import Indicator

class IndicatorRepository:
    """
    Repository for Indicator model operations.
    """
    
    @staticmethod
    def get_by_id(indicator_id):
        """
        Get an indicator by ID.
        """
        try:
            return Indicator.objects.get(id=indicator_id)
        except Indicator.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_stix_id(stix_id):
        """
        Get an indicator by STIX ID.
        """
        try:
            return Indicator.objects.get(stix_id=stix_id)
        except Indicator.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_feed(feed):
        """
        Get indicators by feed - handle both feed object and feed ID.
        """
        if hasattr(feed, 'id'):
            # feed is a ThreatFeed object
            return Indicator.objects.filter(threat_feed=feed)
        else:
            # feed is an ID
            return Indicator.objects.filter(threat_feed_id=feed)
    
    @staticmethod
    def get_by_type(indicator_type):
        """
        Get indicators by type.
        """
        return Indicator.objects.filter(type=indicator_type)
    
    @staticmethod
    def get_high_confidence(min_confidence):
        """
        Get indicators with confidence >= min_confidence.
        """
        return Indicator.objects.filter(confidence__gte=min_confidence)
    
    @staticmethod
    def create(data):
        """
        Create a new indicator.
        """
        return Indicator.objects.create(**data)
    
    @staticmethod
    def update(indicator_id, data):
        """
        Update an indicator.
        """
        try:
            indicator = Indicator.objects.get(id=indicator_id)
            for key, value in data.items():
                setattr(indicator, key, value)
            indicator.save()
            return indicator
        except Indicator.DoesNotExist:
            return None
    
    @staticmethod
    def delete(indicator_id):
        """
        Delete an indicator.
        """
        try:
            indicator = Indicator.objects.get(id=indicator_id)
            indicator.delete()
            return True
        except Indicator.DoesNotExist:
            return False

    @staticmethod    
    def get_all():
        """Retrieves all indicators from the database."""
        return Indicator.objects.all()
    
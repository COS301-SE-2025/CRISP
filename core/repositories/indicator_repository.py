from core.models.indicator import Indicator

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
    def get_by_feed(feed_id):
        """
        Get indicators by feed ID.
        """
        return Indicator.objects.filter(threat_feed_id=feed_id)
    
    @staticmethod
    def get_by_type(indicator_type):
        """
        Get indicators by type.
        """
        return Indicator.objects.filter(type=indicator_type)
    
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
        indicator = Indicator.objects.get(id=indicator_id)
        for key, value in data.items():
            setattr(indicator, key, value)
        indicator.save()
        return indicator
    
    @staticmethod
    def delete(indicator_id):
        """
        Delete an indicator.
        """
        indicator = Indicator.objects.get(id=indicator_id)
        indicator.delete()
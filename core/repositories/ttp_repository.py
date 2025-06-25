from core.models.ttp_data import TTPData

class TTPRepository:
    """
    Repository for TTPData model operations.
    """
    
    @staticmethod
    def get_by_id(ttp_id):
        """
        Get a TTP by ID.
        """
        try:
            return TTPData.objects.get(id=ttp_id)
        except TTPData.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_stix_id(stix_id):
        """
        Get a TTP by STIX ID.
        """
        try:
            return TTPData.objects.get(stix_id=stix_id)
        except TTPData.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_feed(feed_id):
        """
        Get TTPs by feed ID.
        """
        return TTPData.objects.filter(threat_feed_id=feed_id)
    
    @staticmethod
    def get_by_mitre_id(mitre_id):
        """
        Get TTPs by MITRE ATT&CK ID.
        """
        return TTPData.objects.filter(mitre_technique_id=mitre_id)
    
    @staticmethod
    def create(data):
        """
        Create a new TTP.
        """
        return TTPData.objects.create(**data)
    
    @staticmethod
    def update(ttp_id, data):
        """
        Update a TTP.
        """
        ttp = TTPData.objects.get(id=ttp_id)
        for key, value in data.items():
            setattr(ttp, key, value)
        ttp.save()
        return ttp
    
    @staticmethod
    def delete(ttp_id):
        """
        Delete a TTP.
        """
        ttp = TTPData.objects.get(id=ttp_id)
        ttp.delete()
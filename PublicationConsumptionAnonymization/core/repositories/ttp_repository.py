from core.models.models import TTPData

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
    def get_by_feed(feed):
        """
        Get TTPs by feed - handle both feed object and feed ID.
        """
        if hasattr(feed, 'id'):
            return TTPData.objects.filter(threat_feed=feed)
        else:
            return TTPData.objects.filter(threat_feed_id=feed)
    
    @staticmethod
    def get_by_mitre_id(mitre_id):
        """
        Get TTPs by MITRE ATT&CK ID.
        """
        return TTPData.objects.filter(mitre_technique_id=mitre_id)
    
    @staticmethod
    def get_by_tactic(tactic):
        """Get TTPs by MITRE tactic."""
        return TTPData.objects.filter(mitre_tactic=tactic)

    @staticmethod
    def get_by_technique_id(technique_id):
        """Get TTP by MITRE technique ID."""
        try:
            return TTPData.objects.get(mitre_technique_id=technique_id)
        except TTPData.DoesNotExist:
            return None
    
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
        try:
            ttp = TTPData.objects.get(id=ttp_id)
            for key, value in data.items():
                setattr(ttp, key, value)
            ttp.save()
            return ttp
        except TTPData.DoesNotExist:
            return None
    
    @staticmethod
    def delete(ttp_id):
        """
        Delete a TTP.
        """
        try:
            ttp = TTPData.objects.get(id=ttp_id)
            ttp.delete()
            return True
        except TTPData.DoesNotExist:
            return False

    @staticmethod    
    def get_all():
        """Retrieves all TTPs from the database."""
        return TTPData.objects.all()
    
    @staticmethod
    def get_by_technique(technique_id):
        """Retrieves TTPs by MITRE ATT&CK technique ID."""
        return TTPData.objects.filter(mitre_technique_id=technique_id)

    @staticmethod
    def search_by_name(name_query):
        """Searches for TTPs by name containing the given query."""
        return TTPData.objects.filter(name__icontains=name_query)
    
  
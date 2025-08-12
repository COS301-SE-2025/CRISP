import logging
from typing import Optional, Dict, Any
from core.models.models import TTPData
from core.repositories.ttp_repository import TTPRepository

logger = logging.getLogger(__name__)

class TTPService:
    """
    Service for handling TTP (Tactics, Techniques, and Procedures) operations.
    Acts as an intermediary between the STIX/TAXII service and the repository.
    Integrates with anonymization strategies using the Strategy pattern.
    """
    
    def __init__(self, anonymization_context=None):
        """
        Initialize the service with a repository and optional anonymization context.
        
        Args:
            anonymization_context: AnonymizationContext for anonymizing data (optional)
        """
        self.repository = TTPRepository()
        self.anonymization_context = anonymization_context
    
    def create_ttp(self, ttp_data, anonymize=False):
        """
        Create a new TTP with optional anonymization.
        
        Args:
            ttp_data: Dictionary containing TTP data
            anonymize: Boolean indicating whether to anonymize the data
            
        Returns:
            TTPData: The created TTP
        """
        # Placeholder for anonymization strategy
        if anonymize:
            # This will be implemented later to use the strategy pattern
            ttp_data = self._anonymize_ttp(ttp_data)
        
        # Create the TTP using the repository
        return self.repository.create(ttp_data)
    
    def update_ttp(self, ttp_id, ttp_data, anonymize=False):
        """
        Update an existing TTP with optional anonymization.
        
        Args:
            ttp_id: ID of the TTP to update
            ttp_data: Dictionary containing updated TTP data
            anonymize: Boolean indicating whether to anonymize the data
            
        Returns:
            TTPData: The updated TTP
        """
        # Placeholder for anonymization strategy
        if anonymize:
            # This will be implemented later to use the strategy pattern
            ttp_data = self._anonymize_ttp(ttp_data)
        
        # Update the TTP using the repository
        return self.repository.update(ttp_id, ttp_data)
    
    def get_ttp_by_id(self, ttp_id):
        """
        Get a TTP by ID.
        
        Args:
            ttp_id: ID of the TTP to retrieve
            
        Returns:
            TTPData: The retrieved TTP or None if not found
        """
        return self.repository.get_by_id(ttp_id)
    
    def get_ttp_by_stix_id(self, stix_id):
        """
        Get a TTP by STIX ID.
        
        Args:
            stix_id: STIX ID of the TTP to retrieve
            
        Returns:
            TTPData: The retrieved TTP or None if not found
        """
        return self.repository.get_by_stix_id(stix_id)
    
    def get_ttps_by_feed(self, feed_id):
        """
        Get TTPs by feed ID.
        
        Args:
            feed_id: ID of the feed
            
        Returns:
            QuerySet: TTPs belonging to the feed
        """
        return self.repository.get_by_feed(feed_id)
    
    def get_ttps_by_mitre_id(self, mitre_id):
        """
        Get TTPs by MITRE ATT&CK technique ID.
        
        Args:
            mitre_id: MITRE technique ID
            
        Returns:
            QuerySet: TTPs with the specified MITRE technique ID
        """
        return self.repository.get_by_mitre_id(mitre_id)
    
    def delete_ttp(self, ttp_id):
        """
        Delete a TTP by ID.
        
        Args:
            ttp_id: ID of the TTP to delete
        """
        self.repository.delete(ttp_id)
    
    def _anonymize_ttp(self, ttp_data):
        """
        Use the anonymization context to anonymize TTP data.
        
        Args:
            ttp_data: Dictionary containing TTP data
            
        Returns:
            dict: Anonymized TTP data
        """
        if self.anonymization_context:
            return self.anonymization_context.anonymize_ttp(ttp_data)
        return ttp_data
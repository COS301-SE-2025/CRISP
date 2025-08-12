import logging
from typing import Optional, Dict, Any
from core.models.models import Indicator
from core.repositories.indicator_repository import IndicatorRepository

logger = logging.getLogger(__name__)

class IndicatorService:
    """
    Service for handling Indicator operations.
    Acts as an intermediary between the STIX/TAXII service and the repository.
    Integrates with anonymization strategies using the Strategy pattern.
    """
    
    def __init__(self, anonymization_context=None):
        """
        Initialize the service with a repository and optional anonymization context.
        
        Args:
            anonymization_context: AnonymizationContext for anonymizing data (optional)
        """
        self.repository = IndicatorRepository()
        self.anonymization_context = anonymization_context
    
    def create_indicator(self, indicator_data, anonymize=False):
        """
        Create a new indicator with optional anonymization.
        
        Args:
            indicator_data: Dictionary containing indicator data
            anonymize: Boolean indicating whether to anonymize the data
            
        Returns:
            Indicator: The created indicator
        """
        # Placeholder for anonymization strategy
        if anonymize:
            indicator_data = self._anonymize_indicator(indicator_data)
        
        # Create the indicator using the repository
        return self.repository.create(indicator_data)
    
    def update_indicator(self, indicator_id, indicator_data, anonymize=False):
        """
        Update an existing indicator with optional anonymization
        """
        # Placeholder for anonymization strategy
        if anonymize:
            indicator_data = self._anonymize_indicator(indicator_data)
        
        # Update the indicator using the repository
        return self.repository.update(indicator_id, indicator_data)
    
    def get_indicator_by_id(self, indicator_id):
        """
        Get an indicator by ID.
        
        Args:
            indicator_id: ID of the indicator to retrieve
            
        Returns:
            Indicator: The retrieved indicator or None if not found
        """
        return self.repository.get_by_id(indicator_id)
    
    def get_indicator_by_stix_id(self, stix_id):
        """
        Get an indicator by STIX ID.
        
        Args:
            stix_id: STIX ID of the indicator to retrieve
            
        Returns:
            Indicator: The retrieved indicator or None if not found
        """
        return self.repository.get_by_stix_id(stix_id)
    
    def get_indicators_by_feed(self, feed_id):
        """
        Get indicators by feed ID.
        
        Args:
            feed_id: ID of the feed
            
        Returns:
            QuerySet: Indicators belonging to the feed
        """
        return self.repository.get_by_feed(feed_id)
    
    def get_indicators_by_type(self, indicator_type):
        """
        Get indicators by type.
        
        Args:
            indicator_type: Type of indicators to retrieve
            
        Returns:
            QuerySet: Indicators of the specified type
        """
        return self.repository.get_by_type(indicator_type)
    
    def delete_indicator(self, indicator_id):
        """
        Delete an indicator by ID.
        
        Args:
            indicator_id: ID of the indicator to delete
        """
        self.repository.delete(indicator_id)
    
    def _anonymize_indicator(self, indicator_data):
        """
        Use the anonymization context to anonymize indicator data.
        
        Args:
            indicator_data: Dictionary containing indicator data
            
        Returns:
            dict: Anonymized indicator data
        """
        if self.anonymization_context:
            return self.anonymization_context.anonymize_indicator(indicator_data)
        return indicator_data
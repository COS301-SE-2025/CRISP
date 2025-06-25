"""
Service for handling Indicator operations with proper Strategy pattern integration.
"""
import logging
from typing import Optional, Dict, Any
from copy import deepcopy

from core.models.indicator import Indicator
from core.repositories.indicator_repository import IndicatorRepository
from core.patterns.strategy.context import AnonymizationContext
from core.patterns.strategy.enums import AnonymizationLevel, DataType

logger = logging.getLogger(__name__)


class IndicatorService:
    """
    Service for handling Indicator operations.
    Acts as an intermediary between the STIX/TAXII service and the repository.
    Integrates with anonymization strategies using the Strategy pattern.
    """
    
    def __init__(self, repository: IndicatorRepository = None, anonymization_context: AnonymizationContext = None):
        """
        Initialize the service with a repository and optional anonymization context.
        
        Args:
            repository: IndicatorRepository for data persistence
            anonymization_context: AnonymizationContext for anonymizing data (optional)
        """
        self.repository = repository or IndicatorRepository()
        self.anonymization_context = anonymization_context or AnonymizationContext()
    
    def create_indicator(self, indicator_data: Dict[str, Any], anonymize: bool = False) -> Indicator:
        """
        Create a new indicator with optional anonymization.
        
        Args:
            indicator_data: Dictionary containing indicator data
            anonymize: Boolean indicating whether to anonymize the data
            
        Returns:
            Indicator: The created indicator
        """

        if anonymize:
            indicator_data = self._anonymize_indicator_data(indicator_data)

        return self.repository.create(indicator_data)
    
    def create_anonymized(self, indicator_data: Dict[str, Any], level: AnonymizationLevel) -> Indicator:
        """
        Create a new indicator with anonymization at the specified level.
        
        Args:
            indicator_data: Dictionary containing indicator data
            level: The anonymization level to apply
            
        Returns:
            Indicator: The created anonymized indicator
        """
        # Create a copy to avoid modifying the original
        anonymized_data = deepcopy(indicator_data)
        
        # Anonymize the value based on indicator type
        if 'value' in anonymized_data and 'type' in anonymized_data:
            anonymized_data['value'] = self._anonymize_value_by_type(
                anonymized_data['value'], 
                anonymized_data['type'], 
                level
            )
        
        # Also anonymize the description if present
        if 'description' in anonymized_data:
            anonymized_data['description'] = self._anonymize_description(
                anonymized_data['description'], 
                level
            )
        
        anonymized_data['is_anonymized'] = True
        
        return self.repository.create(anonymized_data)
    
    def update_indicator(self, indicator_id: int, indicator_data: Dict[str, Any], anonymize: bool = False) -> Indicator:
        """
        Update an existing indicator with optional anonymization.
        
        Args:
            indicator_id: ID of the indicator to update
            indicator_data: Dictionary containing updated indicator data
            anonymize: Boolean indicating whether to anonymize the data
            
        Returns:
            Indicator: The updated indicator
        """
        if anonymize:
            indicator_data = self._anonymize_indicator_data(indicator_data)
        
        return self.repository.update(indicator_id, indicator_data)
    
    def share_with_anonymization(self, indicator_id: int, level: AnonymizationLevel) -> Indicator:
        """
        Share an indicator with anonymization by creating a new anonymized copy.
        
        Args:
            indicator_id: ID of the indicator to share
            level: The anonymization level to apply
            
        Returns:
            Indicator: A new anonymized indicator suitable for sharing
        """
        # Get the original indicator
        original = self.repository.get_by_id(indicator_id)
        if not original:
            raise ValueError(f"Indicator with ID {indicator_id} not found")
        
        # Create anonymized data from the original
        anonymized_data = {
            'threat_feed': original.threat_feed,
            'type': original.type,
            'value': self._anonymize_value_by_type(original.value, original.type, level),
            'description': self._anonymize_description(original.description, level),
            'confidence': original.confidence,
            'stix_id': f"{original.stix_id}-shared-{level.value}",
            'is_anonymized': True
        }
        
        return self.repository.create(anonymized_data)
    
    def anonymize_description(self, indicator_id: int, level: AnonymizationLevel) -> Indicator:
        """
        Anonymize the description of an existing indicator.
        
        Args:
            indicator_id: ID of the indicator to update
            level: The anonymization level to apply
            
        Returns:
            Indicator: The updated indicator with anonymized description
        """
        indicator = self.repository.get_by_id(indicator_id)
        if not indicator:
            raise ValueError(f"Indicator with ID {indicator_id} not found")
        
        anonymized_description = self._anonymize_description(indicator.description, level)
        
        update_data = {
            'description': anonymized_description,
            'is_anonymized': True
        }
        
        return self.repository.update(indicator_id, update_data)
    
    def get_indicator_by_id(self, indicator_id: int) -> Optional[Indicator]:
        """
        Get an indicator by ID.
        
        Args:
            indicator_id: ID of the indicator to retrieve
            
        Returns:
            Indicator: The retrieved indicator or None if not found
        """
        return self.repository.get_by_id(indicator_id)
    
    def get_indicator_by_stix_id(self, stix_id: str) -> Optional[Indicator]:
        """
        Get an indicator by STIX ID.
        
        Args:
            stix_id: STIX ID of the indicator to retrieve
            
        Returns:
            Indicator: The retrieved indicator or None if not found
        """
        return self.repository.get_by_stix_id(stix_id)
    
    def get_indicators_by_feed(self, feed_id: int):
        """
        Get indicators by feed ID.
        
        Args:
            feed_id: ID of the feed
            
        Returns:
            QuerySet: Indicators belonging to the feed
        """
        return self.repository.get_by_feed(feed_id)
    
    def get_indicators_by_type(self, indicator_type: str):
        """
        Get indicators by type.
        
        Args:
            indicator_type: Type of indicators to retrieve
            
        Returns:
            QuerySet: Indicators of the specified type
        """
        return self.repository.get_by_type(indicator_type)
    
    def delete_indicator(self, indicator_id: int):
        """
        Delete an indicator by ID.
        
        Args:
            indicator_id: ID of the indicator to delete
        """
        self.repository.delete(indicator_id)
    
    def _anonymize_indicator_data(self, indicator_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize indicator data using the default anonymization level.
        
        Args:
            indicator_data: Dictionary containing indicator data
            
        Returns:
            dict: Anonymized indicator data
        """
        return self._anonymize_indicator_data_with_level(indicator_data, AnonymizationLevel.MEDIUM)
    
    def _anonymize_indicator_data_with_level(self, indicator_data: Dict[str, Any], level: AnonymizationLevel) -> Dict[str, Any]:
        """
        Anonymize indicator data using the specified anonymization level.
        
        Args:
            indicator_data: Dictionary containing indicator data
            level: The anonymization level to apply
            
        Returns:
            dict: Anonymized indicator data
        """
        # Create a copy to avoid modifying the original
        anonymized_data = deepcopy(indicator_data)
        
        # Anonymize the value based on the indicator type
        if 'value' in anonymized_data and 'type' in anonymized_data:
            anonymized_data['value'] = self._anonymize_value_by_type(
                anonymized_data['value'], 
                anonymized_data['type'], 
                level
            )
        
        # Anonymize the description if present
        if 'description' in anonymized_data:
            anonymized_data['description'] = self._anonymize_description(
                anonymized_data['description'], 
                level
            )
        
        return anonymized_data
    
    def _anonymize_value_by_type(self, value: str, indicator_type: str, level: AnonymizationLevel) -> str:
        """
        Anonymize a value based on its indicator type.
        
        Args:
            value: The value to anonymize
            indicator_type: The type of the indicator ('ip', 'domain', 'email', etc.)
            level: The anonymization level to apply
            
        Returns:
            str: The anonymized value
        """
        # Map indicator types to DataType enum values
        type_mapping = {
            'ip': DataType.IP_ADDRESS,
            'ipv4': DataType.IP_ADDRESS,
            'ipv6': DataType.IP_ADDRESS,
            'domain': DataType.DOMAIN,
            'hostname': DataType.DOMAIN,
            'email': DataType.EMAIL,
            'email-addr': DataType.EMAIL,
            'url': DataType.URL,
            'uri': DataType.URL,
            'file': DataType.FILENAME,
            'filename': DataType.FILENAME,
            'hash': DataType.HASH,
            'md5': DataType.HASH,
            'sha1': DataType.HASH,
            'sha256': DataType.HASH,
        }
        
        data_type = type_mapping.get(indicator_type.lower())
        
        if data_type:
            try:
                return self.anonymization_context.execute_anonymization(value, data_type, level)
            except Exception as e:
                logger.warning(f"Failed to anonymize {indicator_type} value '{value}': {e}")
                # Fallback to auto-detection
                return self.anonymization_context.auto_detect_and_anonymize(value, level)
        else:
            # Use auto-detection for unknown types
            return self.anonymization_context.auto_detect_and_anonymize(value, level)
    
    def bulk_anonymize(self, indicator_ids: list, level: AnonymizationLevel) -> list:
        """
        Bulk anonymize multiple indicators.
        
        Args:
            indicator_ids: List of indicator IDs to anonymize
            level: The anonymization level to apply
            
        Returns:
            list: List of anonymized indicators
        """
        anonymized_indicators = []
        
        for indicator_id in indicator_ids:
            try:
                anonymized_indicator = self.share_with_anonymization(indicator_id, level)
                anonymized_indicators.append(anonymized_indicator)
            except Exception as e:
                logger.error(f"Failed to anonymize indicator {indicator_id}: {e}")
        
        return anonymized_indicators
    
    def _anonymize_description(self, description: str, level: AnonymizationLevel) -> str:
        """
        Anonymize a description by auto-detecting and anonymizing sensitive data within it.
        
        Args:
            description: The description to anonymize
            level: The anonymization level to apply
            
        Returns:
            str: The anonymized description
        """
        if not description:
            return description
        
        try:
            return self.anonymization_context.auto_detect_and_anonymize(description, level)
        except Exception as e:
            logger.warning(f"Failed to anonymize description: {e}")
            return f"[anonymized-description-{hash(description) % 10000}]"
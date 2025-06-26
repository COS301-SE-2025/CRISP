"""
Service for handling TTP (Tactics, Techniques, and Procedures) operations with proper Strategy pattern integration.
"""
import logging
from typing import Optional, Dict, Any
from copy import deepcopy

from core.models.ttp_data import TTPData
from core.repositories.ttp_repository import TTPRepository
from core.strategies.context import AnonymizationContext
from core.strategies.enums import AnonymizationLevel, DataType

logger = logging.getLogger(__name__)


class TTPService:
    """
    Service for handling TTP (Tactics, Techniques, and Procedures) operations.
    Acts as an intermediary between the STIX/TAXII service and the repository.
    Integrates with anonymization strategies using the Strategy pattern.
    """
    
    def __init__(self, repository: TTPRepository = None, anonymization_context: AnonymizationContext = None):
        """
        Initialize the service with a repository and optional anonymization context.
        
        Args:
            repository: TTPRepository for data persistence
            anonymization_context: AnonymizationContext for anonymizing data (optional)
        """
        self.repository = repository or TTPRepository()
        self.anonymization_context = anonymization_context or AnonymizationContext()
    
    def create_ttp(self, ttp_data: Dict[str, Any], anonymize: bool = False) -> TTPData:
        """
        Create a new TTP with optional anonymization.
        
        Args:
            ttp_data: Dictionary containing TTP data
            anonymize: Boolean indicating whether to anonymize the data
            
        Returns:
            TTPData: The created TTP
        """
        if anonymize:
            ttp_data = self._anonymize_ttp_data(ttp_data)
        
        return self.repository.create(ttp_data)
    
    def create_anonymized(self, ttp_data: Dict[str, Any], level: AnonymizationLevel) -> TTPData:
        """
        Create a new TTP with anonymization at the specified level.
        
        Args:
            ttp_data: Dictionary containing TTP data
            level: The anonymization level to apply
            
        Returns:
            TTPData: The created anonymized TTP
        """
        anonymized_data = self._anonymize_ttp_data_with_level(ttp_data, level)
        anonymized_data['is_anonymized'] = True
        
        return self.repository.create(anonymized_data)
    
    def update_ttp(self, ttp_id: int, ttp_data: Dict[str, Any], anonymize: bool = False) -> TTPData:
        """
        Update an existing TTP with optional anonymization.
        
        Args:
            ttp_id: ID of the TTP to update
            ttp_data: Dictionary containing updated TTP data
            anonymize: Boolean indicating whether to anonymize the data
            
        Returns:
            TTPData: The updated TTP
        """

        if anonymize:
            ttp_data = self._anonymize_ttp_data(ttp_data)
          
        return self.repository.update(ttp_id, ttp_data)
    
    def share_with_anonymization(self, ttp_id: int, level: AnonymizationLevel) -> TTPData:
        """
        Share a TTP with anonymization by creating a new anonymized copy.
        
        Args:
            ttp_id: ID of the TTP to share
            level: The anonymization level to apply
            
        Returns:
            TTPData: A new anonymized TTP suitable for sharing
        """
        # Get the original TTP
        original = self.repository.get_by_id(ttp_id)
        if not original:
            raise ValueError(f"TTP with ID {ttp_id} not found")
        
        # Create anonymized data from the original
        anonymized_data = {
            'threat_feed': original.threat_feed,
            'name': original.name,
            'description': self._anonymize_description(original.description, level),
            'mitre_technique_id': original.mitre_technique_id,
            'mitre_tactic': original.mitre_tactic,
            'stix_id': f"{original.stix_id}-shared-{level.value}",
            'is_anonymized': True
        }
        
        # Copy other fields that might exist
        for field in ['confidence', 'severity', 'tags', 'references']:
            if hasattr(original, field):
                anonymized_data[field] = getattr(original, field)
        
        return self.repository.create(anonymized_data)
    
    def anonymize_description(self, ttp_id: int, level: AnonymizationLevel) -> TTPData:
        """
        Anonymize the description of an existing TTP.
        
        Args:
            ttp_id: ID of the TTP to update
            level: The anonymization level to apply
            
        Returns:
            TTPData: The updated TTP with anonymized description
        """
        ttp = self.repository.get_by_id(ttp_id)
        if not ttp:
            raise ValueError(f"TTP with ID {ttp_id} not found")
        
        anonymized_description = self._anonymize_description(ttp.description, level)
        
        update_data = {
            'description': anonymized_description,
            'is_anonymized': True
        }
        
        return self.repository.update(ttp_id, update_data)
    
    def get_ttp_by_id(self, ttp_id: int) -> Optional[TTPData]:
        """
        Get a TTP by ID.
        
        Args:
            ttp_id: ID of the TTP to retrieve
            
        Returns:
            TTPData: The retrieved TTP or None if not found
        """
        return self.repository.get_by_id(ttp_id)
    
    def get_ttp_by_stix_id(self, stix_id: str) -> Optional[TTPData]:
        """
        Get a TTP by STIX ID.
        
        Args:
            stix_id: STIX ID of the TTP to retrieve
            
        Returns:
            TTPData: The retrieved TTP or None if not found
        """
        return self.repository.get_by_stix_id(stix_id)
    
    def get_ttps_by_feed(self, feed_id: int):
        """
        Get TTPs by feed ID.
        
        Args:
            feed_id: ID of the feed
            
        Returns:
            QuerySet: TTPs belonging to the feed
        """
        return self.repository.get_by_feed(feed_id)
    
    def get_ttps_by_mitre_id(self, mitre_id: str):
        """
        Get TTPs by MITRE ATT&CK ID.
        
        Args:
            mitre_id: MITRE technique ID
            
        Returns:
            QuerySet: TTPs with the specified MITRE ID
        """
        return self.repository.get_by_mitre_id(mitre_id)
    
    def delete_ttp(self, ttp_id: int):
        """
        Delete a TTP by ID.
        
        Args:
            ttp_id: ID of the TTP to delete
        """
        self.repository.delete(ttp_id)
    
    def _anonymize_ttp_data(self, ttp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize TTP data using the default anonymization level.
        
        Args:
            ttp_data: Dictionary containing TTP data
            
        Returns:
            dict: Anonymized TTP data
        """
        return self._anonymize_ttp_data_with_level(ttp_data, AnonymizationLevel.MEDIUM)
    
    def _anonymize_ttp_data_with_level(self, ttp_data: Dict[str, Any], level: AnonymizationLevel) -> Dict[str, Any]:
        """
        Anonymize TTP data using the specified anonymization level.
        
        Args:
            ttp_data: Dictionary containing TTP data
            level: The anonymization level to apply
            
        Returns:
            dict: Anonymized TTP data
        """
        # Create a copy to avoid modifying the original
        anonymized_data = deepcopy(ttp_data)
        
        # Anonymize the description if present
        if 'description' in anonymized_data:
            anonymized_data['description'] = self._anonymize_description(
                anonymized_data['description'], 
                level
            )
        
        # Anonymize other text fields that might contain sensitive information
        text_fields = ['name', 'notes', 'details', 'references']
        for field in text_fields:
            if field in anonymized_data and anonymized_data[field]:
                anonymized_data[field] = self._anonymize_text_field(
                    anonymized_data[field], 
                    level
                )
        
        return anonymized_data
    
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
    
    def _anonymize_text_field(self, text: str, level: AnonymizationLevel) -> str:
        """
        Anonymize a text field by auto-detecting and anonymizing sensitive data within it.
        
        Args:
            text: The text to anonymize
            level: The anonymization level to apply
            
        Returns:
            str: The anonymized text
        """
        if not text:
            return text
        
        try:
            return self.anonymization_context.auto_detect_and_anonymize(text, level)
        except Exception as e:
            logger.warning(f"Failed to anonymize text field: {e}")
            return f"[anonymized-text-{hash(text) % 10000}]"
    
    def bulk_anonymize(self, ttp_ids: list, level: AnonymizationLevel) -> list:
        """
        Bulk anonymize multiple TTPs.
        
        Args:
            ttp_ids: List of TTP IDs to anonymize
            level: The anonymization level to apply
            
        Returns:
            list: List of anonymized TTPs
        """
        anonymized_ttps = []
        
        for ttp_id in ttp_ids:
            try:
                anonymized_ttp = self.share_with_anonymization(ttp_id, level)
                anonymized_ttps.append(anonymized_ttp)
            except Exception as e:
                logger.error(f"Failed to anonymize TTP {ttp_id}: {e}")
        
        return anonymized_ttps
    
    def _anonymize_by_data_type(self, value: str, data_type: DataType, level: AnonymizationLevel) -> str:
        """
        Anonymize a value using a specific data type strategy.
        
        Args:
            value: The value to anonymize
            data_type: The data type to use for anonymization
            level: The anonymization level to apply
            
        Returns:
            str: The anonymized value
        """
        try:
            return self.anonymization_context.execute_anonymization(value, data_type, level)
        except Exception as e:
            logger.warning(f"Failed to anonymize {data_type} value '{value}': {e}")
            # Fallback to auto-detection
            return self.anonymization_context.auto_detect_and_anonymize(value, level)
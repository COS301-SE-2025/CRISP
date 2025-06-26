"""
Context for anonymization strategies using the Strategy pattern.
"""
import logging
from typing import Optional, Dict, Any

from .enums import AnonymizationLevel, DataType

logger = logging.getLogger(__name__)


class AnonymizationContext:
    """Context class for anonymization strategies"""
    
    def __init__(self, level: AnonymizationLevel = AnonymizationLevel.NONE):
        """
        Initialize anonymization context
        
        Args:
            level: The anonymization level to apply
        """
        self.level = level
        self.strategies = {}
    
    def set_level(self, level: AnonymizationLevel):
        """Set the anonymization level"""
        self.level = level
    
    def anonymize_data(self, data: Dict[str, Any], data_type: DataType) -> Dict[str, Any]:
        """
        Anonymize data based on the current level and data type
        
        Args:
            data: The data to anonymize
            data_type: The type of data being anonymized
            
        Returns:
            Anonymized data dictionary
        """
        if self.level == AnonymizationLevel.NONE:
            return data
        
        # Simple anonymization implementation
        anonymized = data.copy()
        
        if self.level in [AnonymizationLevel.BASIC, AnonymizationLevel.FULL]:
            # Basic anonymization - remove or hash sensitive fields
            sensitive_fields = ['ip_address', 'domain', 'url', 'email']
            
            for field in sensitive_fields:
                if field in anonymized:
                    if self.level == AnonymizationLevel.BASIC:
                        # Basic: replace with placeholder
                        anonymized[field] = f"[REDACTED_{field.upper()}]"
                    else:
                        # Full: remove completely
                        del anonymized[field]
        
        return anonymized
    
    def should_anonymize(self, data_type: DataType) -> bool:
        """Check if data of given type should be anonymized"""
        return self.level != AnonymizationLevel.NONE
    
    def auto_detect_and_anonymize(self, data: str) -> str:
        """
        Auto-detect data type and apply appropriate anonymization.
        
        Args:
            data: The string data to anonymize
            
        Returns:
            Anonymized string
        """
        if self.level == AnonymizationLevel.NONE:
            return data
        
        # Import strategies here to avoid circular imports
        from .strategies import (
            IPAddressAnonymizationStrategy,
            DomainAnonymizationStrategy,
            EmailAnonymizationStrategy,
            URLAnonymizationStrategy,
            FileHashAnonymizationStrategy
        )
        
        # Try to detect data type and apply appropriate strategy
        strategies = [
            IPAddressAnonymizationStrategy(),
            EmailAnonymizationStrategy(),
            URLAnonymizationStrategy(),
            DomainAnonymizationStrategy(),
            FileHashAnonymizationStrategy()
        ]
        
        for strategy in strategies:
            if strategy.validate_data(data):
                try:
                    return strategy.anonymize(data, self.level)
                except Exception as e:
                    logger.warning(f"Failed to anonymize data with {strategy.__class__.__name__}: {e}")
                    continue
        
        # If no specific strategy matched, apply basic anonymization
        if self.level == AnonymizationLevel.BASIC:
            return f"[REDACTED]"
        elif self.level == AnonymizationLevel.PARTIAL:
            # Show first 3 characters
            return data[:3] + "..." if len(data) > 3 else "[REDACTED]"
        elif self.level == AnonymizationLevel.FULL:
            return "[FULLY_REDACTED]"
        
        return data
    
    def execute_anonymization(self, data: str, data_type: Optional[DataType] = None) -> str:
        """
        Execute anonymization on data using appropriate strategy.
        
        Args:
            data: The data to anonymize
            data_type: Optional data type hint
            
        Returns:
            Anonymized data
        """
        return self.auto_detect_and_anonymize(data)
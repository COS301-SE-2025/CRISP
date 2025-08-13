"""
Anonymization Strategy Factory
Creates appropriate anonymization strategies based on strategy type.
"""

from .strategies import (
    IPAddressAnonymizationStrategy,
    DomainAnonymizationStrategy, 
    EmailAnonymizationStrategy,
    URLAnonymizationStrategy
)
from .enums import AnonymizationLevel


class AnonymizationStrategyFactory:
    """Factory for creating anonymization strategies"""
    
    _strategies = {
        'none': None,  # No anonymization strategy
        'ip': IPAddressAnonymizationStrategy(),
        'domain': DomainAnonymizationStrategy(), 
        'email': EmailAnonymizationStrategy(),
        'url': URLAnonymizationStrategy(),
    }
    
    @classmethod
    def get_strategy(cls, strategy_type: str):
        """
        Get anonymization strategy by type
        
        Args:
            strategy_type: Type of strategy ('none', 'ip', 'domain', 'email', 'url')
            
        Returns:
            AnonymizationStrategy instance or None for 'none' type
            
        Raises:
            ValueError: If strategy type is not supported
        """
        if strategy_type not in cls._strategies:
            raise ValueError(f"Unsupported strategy type: {strategy_type}")
        
        if strategy_type == 'none':
            return NoAnonymizationStrategy()
        
        return cls._strategies[strategy_type]
    
    @classmethod
    def register_strategy(cls, strategy_type: str, strategy_instance):
        """Register a new strategy type"""
        cls._strategies[strategy_type] = strategy_instance
    
    @classmethod
    def list_strategies(cls):
        """List all available strategy types"""
        return list(cls._strategies.keys())


class NoAnonymizationStrategy:
    """Strategy that performs no anonymization"""
    
    def anonymize(self, data, trust_level=1.0):
        """Return data unchanged"""
        return data
    
    def can_handle(self, data_type):
        """Can handle any data type by doing nothing"""
        return True
    
    def validate(self, data):
        """Always valid since we don't modify anything"""
        return True
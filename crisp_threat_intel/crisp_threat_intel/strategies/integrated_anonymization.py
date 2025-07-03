"""
Integrated Anonymization Strategy Pattern Implementation
Bridges crisp_threat_intel and crisp_anonymization systems for unified anonymization.
"""

import sys
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional
import json
import re
import logging

# Add the core patterns strategy package to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'core', 'patterns', 'strategy'))

try:
    # Import from core/patterns/strategy package
    from core.patterns.strategy.context import AnonymizationContext as BaseAnonymizationContext
    from core.patterns.strategy.enums import AnonymizationLevel, DataType
    from core.patterns.strategy.strategies import (
        IPAddressAnonymizationStrategy as BaseIPStrategy,
        DomainAnonymizationStrategy as BaseDomainStrategy,
        EmailAnonymizationStrategy as BaseEmailStrategy,
        URLAnonymizationStrategy as BaseURLStrategy
    )
except ImportError:
    # Fallback: try direct import from core directory
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'core', 'patterns', 'strategy'))
        from context import AnonymizationContext as BaseAnonymizationContext
        from enums import AnonymizationLevel, DataType
        from strategies import (
            IPAddressAnonymizationStrategy as BaseIPStrategy,
            DomainAnonymizationStrategy as BaseDomainStrategy,
            EmailAnonymizationStrategy as BaseEmailStrategy,
            URLAnonymizationStrategy as BaseURLStrategy
        )
    except ImportError:
        # Final fallback: create minimal implementations
        logger.warning("Could not import core strategy patterns, using minimal implementations")
        
        class AnonymizationLevel:
            NONE = "none"
            LOW = "low"
            MEDIUM = "medium"
            HIGH = "high"
            FULL = "full"
        
        class DataType:
            IP_ADDRESS = "ip_address"
            DOMAIN = "domain"
            EMAIL = "email"
            URL = "url"
        
        class BaseAnonymizationContext:
            def execute_anonymization(self, data, data_type, level):
                return f"[ANONYMIZED:{level}]{data}"
            
            def auto_detect_and_anonymize(self, data, level):
                return f"[AUTO-ANON:{level}]{data}"
        
        class BaseIPStrategy:
            def anonymize(self, data, level):
                return f"[IP-ANON:{level}]{data}"
        
        class BaseDomainStrategy:
            def anonymize(self, data, level):
                return f"[DOMAIN-ANON:{level}]{data}"
        
        class BaseEmailStrategy:
            def anonymize(self, data, level):
                return f"[EMAIL-ANON:{level}]{data}"
        
        class BaseURLStrategy:
            def anonymize(self, data, level):
                return f"[URL-ANON:{level}]{data}"

# Import existing STIX-focused strategies
from .anonymization import (
    AnonymizationStrategy as STIXAnonymizationStrategy,
    DomainAnonymizationStrategy as STIXDomainStrategy,
    IPAddressAnonymizationStrategy as STIXIPStrategy,
    EmailAnonymizationStrategy as STIXEmailStrategy,
    AnonymizationStrategyFactory as STIXStrategyFactory
)

logger = logging.getLogger(__name__)


class TrustLevel:
    """Helper class for trust level management"""
    HIGH = 0.8
    MEDIUM = 0.5
    LOW = 0.2
    
    @staticmethod
    def to_anonymization_level(trust_level: float) -> AnonymizationLevel:
        """Convert trust level to anonymization level"""
        if trust_level >= TrustLevel.HIGH:
            return AnonymizationLevel.NONE
        elif trust_level >= TrustLevel.MEDIUM:
            return AnonymizationLevel.LOW
        elif trust_level >= TrustLevel.LOW:
            return AnonymizationLevel.MEDIUM
        else:
            return AnonymizationLevel.FULL


class IntegratedAnonymizationStrategy(ABC):
    """
    Abstract base class for integrated anonymization strategies that work with both
    STIX objects (threat intel) and raw data types (anonymization).
    """
    
    @abstractmethod
    def anonymize_stix_object(self, stix_object: Dict[str, Any], trust_level: float) -> Dict[str, Any]:
        """Anonymize STIX object based on trust level"""
        pass
    
    @abstractmethod
    def anonymize_raw_data(self, data: str, data_type: DataType, anonymization_level: AnonymizationLevel) -> str:
        """Anonymize raw data based on type and level"""
        pass
    
    @abstractmethod
    def can_handle_stix_type(self, stix_type: str) -> bool:
        """Check if strategy can handle STIX object type"""
        pass
    
    @abstractmethod
    def can_handle_data_type(self, data_type: DataType) -> bool:
        """Check if strategy can handle data type"""
        pass


class IntegratedDomainAnonymizationStrategy(IntegratedAnonymizationStrategy):
    """
    Integrated strategy for domain anonymization that works with both STIX objects and raw domains.
    """
    
    def __init__(self):
        self.stix_strategy = STIXDomainStrategy()
        self.data_strategy = BaseDomainStrategy()
    
    def anonymize_stix_object(self, stix_object: Dict[str, Any], trust_level: float) -> Dict[str, Any]:
        """Anonymize domain indicators in STIX objects"""
        return self.stix_strategy.anonymize(stix_object, trust_level)
    
    def anonymize_raw_data(self, data: str, data_type: DataType, anonymization_level: AnonymizationLevel) -> str:
        """Anonymize raw domain data"""
        if data_type != DataType.DOMAIN:
            raise ValueError(f"Strategy cannot handle data type: {data_type}")
        return self.data_strategy.anonymize(data, anonymization_level)
    
    def can_handle_stix_type(self, stix_type: str) -> bool:
        """Check if strategy can handle STIX object containing domain indicators"""
        return stix_type == 'indicator'  # Domain indicators are in indicator objects
    
    def can_handle_data_type(self, data_type: DataType) -> bool:
        """Check if strategy can handle domain data type"""
        return data_type == DataType.DOMAIN
    
    def anonymize_mixed(self, data: Union[str, Dict], trust_level: Optional[float] = None, 
                       anonymization_level: Optional[AnonymizationLevel] = None) -> Union[str, Dict]:
        """
        Unified method to anonymize either STIX objects or raw data
        """
        if isinstance(data, dict) and 'type' in data:
            # STIX object
            if trust_level is None:
                raise ValueError("Trust level required for STIX object anonymization")
            return self.anonymize_stix_object(data, trust_level)
        elif isinstance(data, str):
            # Raw domain string
            if anonymization_level is None and trust_level is not None:
                anonymization_level = TrustLevel.to_anonymization_level(trust_level)
            elif anonymization_level is None:
                anonymization_level = AnonymizationLevel.MEDIUM
            return self.anonymize_raw_data(data, DataType.DOMAIN, anonymization_level)
        else:
            raise ValueError(f"Cannot handle data type: {type(data)}")


class IntegratedIPAnonymizationStrategy(IntegratedAnonymizationStrategy):
    """
    Integrated strategy for IP address anonymization that works with both STIX objects and raw IPs.
    """
    
    def __init__(self):
        self.stix_strategy = STIXIPStrategy()
        self.data_strategy = BaseIPStrategy()
    
    def anonymize_stix_object(self, stix_object: Dict[str, Any], trust_level: float) -> Dict[str, Any]:
        """Anonymize IP indicators in STIX objects"""
        return self.stix_strategy.anonymize(stix_object, trust_level)
    
    def anonymize_raw_data(self, data: str, data_type: DataType, anonymization_level: AnonymizationLevel) -> str:
        """Anonymize raw IP data"""
        if data_type != DataType.IP_ADDRESS:
            raise ValueError(f"Strategy cannot handle data type: {data_type}")
        return self.data_strategy.anonymize(data, anonymization_level)
    
    def can_handle_stix_type(self, stix_type: str) -> bool:
        """Check if strategy can handle STIX object containing IP indicators"""
        return stix_type == 'indicator'
    
    def can_handle_data_type(self, data_type: DataType) -> bool:
        """Check if strategy can handle IP data type"""
        return data_type == DataType.IP_ADDRESS
    
    def anonymize_mixed(self, data: Union[str, Dict], trust_level: Optional[float] = None, 
                       anonymization_level: Optional[AnonymizationLevel] = None) -> Union[str, Dict]:
        """
        Unified method to anonymize either STIX objects or raw data
        """
        if isinstance(data, dict) and 'type' in data:
            # STIX object
            if trust_level is None:
                raise ValueError("Trust level required for STIX object anonymization")
            return self.anonymize_stix_object(data, trust_level)
        elif isinstance(data, str):
            # Raw IP string
            if anonymization_level is None and trust_level is not None:
                anonymization_level = TrustLevel.to_anonymization_level(trust_level)
            elif anonymization_level is None:
                anonymization_level = AnonymizationLevel.MEDIUM
            return self.anonymize_raw_data(data, DataType.IP_ADDRESS, anonymization_level)
        else:
            raise ValueError(f"Cannot handle data type: {type(data)}")


class IntegratedEmailAnonymizationStrategy(IntegratedAnonymizationStrategy):
    """
    Integrated strategy for email anonymization that works with both STIX objects and raw emails.
    """
    
    def __init__(self):
        self.stix_strategy = STIXEmailStrategy()
        self.data_strategy = BaseEmailStrategy()
    
    def anonymize_stix_object(self, stix_object: Dict[str, Any], trust_level: float) -> Dict[str, Any]:
        """Anonymize email indicators in STIX objects"""
        return self.stix_strategy.anonymize(stix_object, trust_level)
    
    def anonymize_raw_data(self, data: str, data_type: DataType, anonymization_level: AnonymizationLevel) -> str:
        """Anonymize raw email data"""
        if data_type != DataType.EMAIL:
            raise ValueError(f"Strategy cannot handle data type: {data_type}")
        return self.data_strategy.anonymize(data, anonymization_level)
    
    def can_handle_stix_type(self, stix_type: str) -> bool:
        """Check if strategy can handle STIX object containing email indicators"""
        return stix_type == 'indicator'
    
    def can_handle_data_type(self, data_type: DataType) -> bool:
        """Check if strategy can handle email data type"""
        return data_type == DataType.EMAIL
    
    def anonymize_mixed(self, data: Union[str, Dict], trust_level: Optional[float] = None, 
                       anonymization_level: Optional[AnonymizationLevel] = None) -> Union[str, Dict]:
        """
        Unified method to anonymize either STIX objects or raw data
        """
        if isinstance(data, dict) and 'type' in data:
            # STIX object
            if trust_level is None:
                raise ValueError("Trust level required for STIX object anonymization")
            return self.anonymize_stix_object(data, trust_level)
        elif isinstance(data, str):
            # Raw email string
            if anonymization_level is None and trust_level is not None:
                anonymization_level = TrustLevel.to_anonymization_level(trust_level)
            elif anonymization_level is None:
                anonymization_level = AnonymizationLevel.MEDIUM
            return self.anonymize_raw_data(data, DataType.EMAIL, anonymization_level)
        else:
            raise ValueError(f"Cannot handle data type: {type(data)}")


class IntegratedURLAnonymizationStrategy(IntegratedAnonymizationStrategy):
    """
    Integrated strategy for URL anonymization that works with both STIX objects and raw URLs.
    """
    
    def __init__(self):
        # Note: No STIX URL strategy exists yet, so we'll create it
        self.data_strategy = BaseURLStrategy()
    
    def anonymize_stix_object(self, stix_object: Dict[str, Any], trust_level: float) -> Dict[str, Any]:
        """Anonymize URL indicators in STIX objects"""
        if trust_level >= 0.8:
            return stix_object
        
        anonymized_obj = stix_object.copy()
        
        # Anonymize URL patterns in indicators
        if anonymized_obj.get('type') == 'indicator' and 'pattern' in anonymized_obj:
            pattern = anonymized_obj['pattern']
            
            # Find URL patterns: [url:value = 'https://example.com/path']
            url_pattern = r"\[url:value\s*=\s*'([^']+)'\]"
            matches = re.findall(url_pattern, pattern)
            
            for url in matches:
                anonymization_level = TrustLevel.to_anonymization_level(trust_level)
                anonymized_url = self.data_strategy.anonymize(url, anonymization_level)
                pattern = pattern.replace(f"'{url}'", f"'{anonymized_url}'")
            
            anonymized_obj['pattern'] = pattern
        
        # Mark as anonymized
        anonymized_obj['x_crisp_anonymized'] = True
        anonymized_obj['x_crisp_trust_level'] = trust_level
        
        return anonymized_obj
    
    def anonymize_raw_data(self, data: str, data_type: DataType, anonymization_level: AnonymizationLevel) -> str:
        """Anonymize raw URL data"""
        if data_type != DataType.URL:
            raise ValueError(f"Strategy cannot handle data type: {data_type}")
        return self.data_strategy.anonymize(data, anonymization_level)
    
    def can_handle_stix_type(self, stix_type: str) -> bool:
        """Check if strategy can handle STIX object containing URL indicators"""
        return stix_type == 'indicator'
    
    def can_handle_data_type(self, data_type: DataType) -> bool:
        """Check if strategy can handle URL data type"""
        return data_type == DataType.URL
    
    def anonymize_mixed(self, data: Union[str, Dict], trust_level: Optional[float] = None, 
                       anonymization_level: Optional[AnonymizationLevel] = None) -> Union[str, Dict]:
        """
        Unified method to anonymize either STIX objects or raw data
        """
        if isinstance(data, dict) and 'type' in data:
            # STIX object
            if trust_level is None:
                raise ValueError("Trust level required for STIX object anonymization")
            return self.anonymize_stix_object(data, trust_level)
        elif isinstance(data, str):
            # Raw URL string
            if anonymization_level is None and trust_level is not None:
                anonymization_level = TrustLevel.to_anonymization_level(trust_level)
            elif anonymization_level is None:
                anonymization_level = AnonymizationLevel.MEDIUM
            return self.anonymize_raw_data(data, DataType.URL, anonymization_level)
        else:
            raise ValueError(f"Cannot handle data type: {type(data)}")


class IntegratedAnonymizationContext:
    """
    Unified context for managing anonymization across both STIX objects and raw data.
    This is the main interface for the integrated anonymization system.
    """
    
    def __init__(self):
        # Initialize integrated strategies
        self.strategies = {
            'domain': IntegratedDomainAnonymizationStrategy(),
            'ip': IntegratedIPAnonymizationStrategy(),
            'email': IntegratedEmailAnonymizationStrategy(),
            'url': IntegratedURLAnonymizationStrategy(),
        }
        
        # Also maintain access to the base anonymization context
        self.base_context = BaseAnonymizationContext()
        
        logger.info("Integrated anonymization context initialized")
    
    def anonymize_stix_object(self, stix_object: Dict[str, Any], trust_level: float) -> Dict[str, Any]:
        """
        Anonymize a STIX object based on trust level.
        
        Args:
            stix_object: STIX object to anonymize
            trust_level: Trust level between organizations (0.0-1.0)
            
        Returns:
            Anonymized STIX object
        """
        if not isinstance(stix_object, dict) or 'type' not in stix_object:
            raise ValueError("Invalid STIX object format")
        
        # Determine appropriate strategy based on object content
        strategy = self._select_stix_strategy(stix_object, trust_level)
        
        if strategy:
            return strategy.anonymize_stix_object(stix_object, trust_level)
        else:
            # If no specific strategy found, return object with minimal marking
            anonymized_obj = stix_object.copy()
            anonymized_obj['x_crisp_anonymized'] = True
            anonymized_obj['x_crisp_trust_level'] = trust_level
            return anonymized_obj
    
    def anonymize_raw_data(self, data: str, data_type: DataType, 
                          anonymization_level: AnonymizationLevel) -> str:
        """
        Anonymize raw data based on type and level.
        
        Args:
            data: Raw data to anonymize
            data_type: Type of data
            anonymization_level: Level of anonymization
            
        Returns:
            Anonymized data string
        """
        strategy = self._get_strategy_for_data_type(data_type)
        if strategy:
            return strategy.anonymize_raw_data(data, data_type, anonymization_level)
        else:
            # Fallback to base context
            return self.base_context.execute_anonymization(data, data_type, anonymization_level)
    
    def anonymize_mixed(self, data: Union[str, Dict, List], 
                       trust_level: Optional[float] = None,
                       anonymization_level: Optional[AnonymizationLevel] = None) -> Union[str, Dict, List]:
        """
        Universal anonymization method that handles STIX objects, raw data, or lists.
        
        Args:
            data: Data to anonymize (STIX object, raw string, or list)
            trust_level: Trust level for STIX objects
            anonymization_level: Anonymization level for raw data
            
        Returns:
            Anonymized data in same format as input
        """
        if isinstance(data, list):
            # Handle list of items
            return [self.anonymize_mixed(item, trust_level, anonymization_level) for item in data]
        
        elif isinstance(data, dict) and 'type' in data:
            # STIX object
            if trust_level is None:
                raise ValueError("Trust level required for STIX object anonymization")
            return self.anonymize_stix_object(data, trust_level)
        
        elif isinstance(data, str):
            # Raw data string - auto-detect type
            if anonymization_level is None and trust_level is not None:
                anonymization_level = TrustLevel.to_anonymization_level(trust_level)
            elif anonymization_level is None:
                anonymization_level = AnonymizationLevel.MEDIUM
            
            # Auto-detect data type and anonymize
            return self.base_context.auto_detect_and_anonymize(data, anonymization_level)
        
        else:
            raise ValueError(f"Cannot handle data type: {type(data)}")
    
    def anonymize_stix_bundle(self, bundle: Dict[str, Any], trust_level: float) -> Dict[str, Any]:
        """
        Anonymize an entire STIX bundle based on trust level.
        
        Args:
            bundle: STIX bundle to anonymize
            trust_level: Trust level between organizations
            
        Returns:
            Anonymized STIX bundle
        """
        if not isinstance(bundle, dict) or bundle.get('type') != 'bundle':
            raise ValueError("Invalid STIX bundle format")
        
        anonymized_bundle = bundle.copy()
        anonymized_objects = []
        
        for obj in bundle.get('objects', []):
            anonymized_obj = self.anonymize_stix_object(obj, trust_level)
            anonymized_objects.append(anonymized_obj)
        
        anonymized_bundle['objects'] = anonymized_objects
        anonymized_bundle['x_crisp_anonymized'] = True
        anonymized_bundle['x_crisp_trust_level'] = trust_level
        
        return anonymized_bundle
    
    def _select_stix_strategy(self, stix_object: Dict[str, Any], trust_level: float) -> Optional[IntegratedAnonymizationStrategy]:
        """Select appropriate strategy for STIX object"""
        if stix_object.get('type') != 'indicator':
            return None
        
        pattern = stix_object.get('pattern', '').lower()
        
        if 'domain-name' in pattern:
            return self.strategies['domain']
        elif 'ipv4-addr' in pattern or 'ipv6-addr' in pattern:
            return self.strategies['ip']
        elif 'email-addr' in pattern:
            return self.strategies['email']
        elif 'url' in pattern:
            return self.strategies['url']
        
        return None
    
    def _get_strategy_for_data_type(self, data_type: DataType) -> Optional[IntegratedAnonymizationStrategy]:
        """Get strategy for specific data type"""
        type_mapping = {
            DataType.DOMAIN: 'domain',
            DataType.IP_ADDRESS: 'ip',
            DataType.EMAIL: 'email',
            DataType.URL: 'url',
        }
        
        strategy_name = type_mapping.get(data_type)
        return self.strategies.get(strategy_name) if strategy_name else None
    
    def register_strategy(self, name: str, strategy: IntegratedAnonymizationStrategy):
        """Register a new anonymization strategy"""
        self.strategies[name] = strategy
        logger.info(f"Registered new strategy: {name}")
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategy names"""
        return list(self.strategies.keys())
    
    def get_anonymization_statistics(self) -> Dict[str, Any]:
        """Get statistics about anonymization usage"""
        return {
            'available_strategies': self.get_available_strategies(),
            'trust_level_mapping': {
                'high (0.8+)': 'no anonymization',
                'medium (0.5-0.8)': 'low anonymization',
                'low (0.2-0.5)': 'medium anonymization',
                'untrusted (<0.2)': 'full anonymization'
            },
            'supported_stix_types': ['indicator'],
            'supported_data_types': [dt.value for dt in DataType]
        }


# Convenience functions for easy integration
def anonymize_for_organization(data: Union[str, Dict, List], 
                              source_org_id: str, 
                              target_org_id: str) -> Union[str, Dict, List]:
    """
    Anonymize data based on trust relationship between organizations.
    
    Args:
        data: Data to anonymize
        source_org_id: Source organization ID
        target_org_id: Target organization ID
        
    Returns:
        Anonymized data
    """
    # This would integrate with the Django models to get trust level
    # For now, we'll use a default medium trust level
    context = IntegratedAnonymizationContext()
    return context.anonymize_mixed(data, trust_level=0.5)


def create_anonymized_bundle_for_collection(collection_id: str, 
                                           requesting_org_id: str) -> Dict[str, Any]:
    """
    Create an anonymized STIX bundle from a collection for a specific organization.
    
    Args:
        collection_id: Collection UUID
        requesting_org_id: Requesting organization ID
        
    Returns:
        Anonymized STIX bundle
    """
    # This would integrate with Django models to:
    # 1. Get collection objects
    # 2. Determine trust level with requesting org
    # 3. Generate and anonymize bundle
    # For now, return a placeholder
    
    context = IntegratedAnonymizationContext()
    
    # Placeholder bundle structure
    bundle = {
        'type': 'bundle',
        'id': f'bundle--{collection_id}',
        'objects': []
    }
    
    return context.anonymize_stix_bundle(bundle, trust_level=0.5)


# Factory for creating integrated strategies
class IntegratedAnonymizationFactory:
    """Factory for creating integrated anonymization strategies"""
    
    _strategies = {
        'domain': IntegratedDomainAnonymizationStrategy,
        'ip': IntegratedIPAnonymizationStrategy,
        'email': IntegratedEmailAnonymizationStrategy,
        'url': IntegratedURLAnonymizationStrategy,
    }
    
    @classmethod
    def create_strategy(cls, strategy_name: str) -> IntegratedAnonymizationStrategy:
        """Create an integrated anonymization strategy"""
        if strategy_name not in cls._strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        return cls._strategies[strategy_name]()
    
    @classmethod
    def create_context(cls) -> IntegratedAnonymizationContext:
        """Create a new integrated anonymization context"""
        return IntegratedAnonymizationContext()
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """Get list of available strategy names"""
        return list(cls._strategies.keys())
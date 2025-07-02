"""
Design Patterns Implementation

This module implements the core design patterns from the CRISP domain model:
- Factory Pattern: For STIX object creation
- Decorator Pattern: For STIX object enhancement
- Strategy Pattern: For trust-based access control and anonymization
- Observer Pattern: For trust event notifications
- Repository Pattern: For data persistence abstraction
"""

from .factory import stix_trust_factory, StixTrustFactory
from .decorator import StixTrustDecoratorChain
from .repository import trust_repository_manager
from .observer import trust_event_manager

__all__ = [
    'stix_trust_factory',
    'StixTrustFactory', 
    'StixTrustDecoratorChain',
    'trust_repository_manager',
    'trust_event_manager',
]
"""
Design Patterns Implementation

This module implements the core design patterns from the CRISP domain model:
- Factory Pattern: For trust object creation
- Decorator Pattern: For trust evaluation enhancement
- Strategy Pattern: For trust-based access control and anonymization
- Observer Pattern: For trust event notifications
- Repository Pattern: For data persistence abstraction
"""

from .factory import trust_factory, TrustFactory
from .decorator import TrustDecoratorChain
from .repository import trust_repository_manager
from .observer import trust_event_manager

__all__ = [
    'trust_factory',
    'TrustFactory', 
    'TrustDecoratorChain',
    'trust_repository_manager',
    'trust_event_manager',
]
"""
Strategy Pattern Implementation

Implements the Strategy pattern for flexible trust-based access control
and anonymization algorithms as specified in the CRISP domain model.
"""

from .access_control_strategies import (
    AccessControlStrategy,
    TrustLevelAccessStrategy,
    CommunityAccessStrategy,
    TimeBasedAccessStrategy,
    AccessControlContext,
    
    # Missing strategy classes that tests are looking for
    TrustBasedAccessControl,
    GroupBasedAccessControl,
    PolicyBasedAccessControl,
    ContextAwareAccessControl,
    AccessControlManager,
    
    AnonymizationStrategy,
    NoAnonymizationStrategy,
    MinimalAnonymizationStrategy,
    PartialAnonymizationStrategy,
    FullAnonymizationStrategy,
    CustomAnonymizationStrategy,
    AnonymizationContext,
)

__all__ = [
    'AccessControlStrategy',
    'TrustLevelAccessStrategy',
    'CommunityAccessStrategy',
    'TimeBasedAccessStrategy',
    'AccessControlContext',
    
    # Missing strategy classes that tests are looking for
    'TrustBasedAccessControl',
    'GroupBasedAccessControl',
    'PolicyBasedAccessControl',
    'ContextAwareAccessControl',
    'AccessControlManager',
    
    'AnonymizationStrategy',
    'NoAnonymizationStrategy',
    'MinimalAnonymizationStrategy',
    'PartialAnonymizationStrategy',
    'FullAnonymizationStrategy',
    'CustomAnonymizationStrategy',
    'AnonymizationContext',
]
"""
Repository Pattern Implementation

Implements the Repository pattern for data persistence abstraction
as specified in the CRISP domain model, providing clean data access
interfaces for trust management entities.
"""

from .trust_repository import (
    BaseRepository,
    TrustRelationshipRepository,
    TrustGroupRepository,
    TrustLevelRepository,
    TrustLogRepository,
    TrustRepositoryManager,
    trust_repository_manager,
)

__all__ = [
    'BaseRepository',
    'TrustRelationshipRepository',
    'TrustGroupRepository',
    'TrustLevelRepository',
    'TrustLogRepository',
    'TrustRepositoryManager',
    'trust_repository_manager',
]
# Import all models from models.py to make them available
from .models import (
    STIXObject, 
    Collection,
    CollectionObject,
    Feed,
    Identity,
    TrustNetwork,
    NetworkMembership,
    ThreatFeed,
    Indicator,
    TTPData,
    Institution,
    TrustLevel
)

# Import Organization from user_management
try:
    from core_ut.user_management.models import Organization
except ImportError:
    # Fallback during migrations
    Organization = None

# Import TrustRelationship from trust
try:
    from core_ut.trust.models import TrustRelationship
except ImportError:
    # Fallback during migrations
    TrustRelationship = None

__all__ = [
    'Organization',
    'STIXObject', 
    'Collection',
    'CollectionObject',
    'Feed',
    'Identity',
    'TrustNetwork',
    'NetworkMembership', 
    'ThreatFeed',
    'Indicator',
    'TTPData',
    'Institution',
    'TrustLevel',
    'TrustRelationship'
]
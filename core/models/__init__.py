# Ultra-clean structure - models package init
# Individual models are imported directly from their files to avoid circular imports

# Import models to ensure they are registered with Django's app registry.

# User and Organization models
from .auth import (
    Organization,
    CustomUser,
    UserSession,
    AuthenticationLog,
    STIXObjectPermission,
)

# STIX and Threat Intelligence models
from .stix_object import STIXObject, Collection, Feed, Identity
from .institution import Institution
from .threat_feed import ThreatFeed
from .indicator import Indicator
from .ttp_data import TTPData

# Trust Management models
from .trust_models.models import (
    TrustLevel,
    TrustGroup,
    TrustRelationship,
    TrustGroupMembership,
    TrustLog,
    SharingPolicy,
)


# Define __all__ for a clean public API
__all__ = [
    # auth
    'Organization', 'CustomUser', 'UserSession', 'AuthenticationLog', 'STIXObjectPermission',
    # stix
    'STIXObject', 'Collection', 'Feed', 'Identity',
    # threat_intel
    'Institution', 'ThreatFeed', 'Indicator', 'TTPData',
    # trust
    'TrustLevel', 'TrustGroup', 'TrustRelationship', 'TrustGroupMembership', 'TrustLog', 'SharingPolicy',
]
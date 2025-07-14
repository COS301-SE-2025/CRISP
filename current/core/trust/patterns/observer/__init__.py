"""
Observer Pattern Implementation

Implements the Observer pattern for trust event notifications
as specified in the CRISP domain model, enabling decoupled
event handling and monitoring.
"""

from .trust_observers import (
    TrustObserver,
    TrustNotificationObserver,
    TrustMetricsObserver,
    TrustAuditObserver,
    TrustSecurityObserver,
    TrustEventManager,
    trust_event_manager,
    notify_access_event,
    notify_trust_relationship_event,
)

__all__ = [
    'TrustObserver',
    'TrustNotificationObserver',
    'TrustMetricsObserver',
    'TrustAuditObserver',
    'TrustSecurityObserver',
    'TrustEventManager',
    'trust_event_manager',
    'notify_access_event',
    'notify_trust_relationship_event',
]
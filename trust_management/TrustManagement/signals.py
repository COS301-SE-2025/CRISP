"""
Django signals for trust management.
Connects trust events to the observer system.
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import TrustRelationship, TrustGroup, TrustGroupMembership, TrustLog

logger = logging.getLogger(__name__)


@receiver(post_save, sender=TrustRelationship)
def handle_trust_relationship_save(sender, instance, created, **kwargs):
    """
    Handle TrustRelationship save events.
    This signal is already handled in observers/trust_observers.py
    but we include it here for completeness.
    """
    pass


@receiver(post_save, sender=TrustGroup)
def handle_trust_group_save(sender, instance, created, **kwargs):
    """Handle TrustGroup save events."""
    if created:
        logger.info(f"Trust group created: {instance.name}")


@receiver(post_save, sender=TrustLog)
def handle_trust_log_save(sender, instance, created, **kwargs):
    """Handle TrustLog save events for additional processing."""
    if created and not instance.success:
        # Handle failed trust operations
        logger.warning(f"Failed trust operation logged: {instance.action} - {instance.failure_reason}")


# Custom signals for trust events
from django.dispatch import Signal

# Define custom signals
trust_relationship_approved = Signal()
trust_relationship_revoked = Signal()
trust_access_granted = Signal()
trust_access_denied = Signal()


@receiver(trust_relationship_approved)
def handle_trust_relationship_approved(sender, relationship, approving_org, user, **kwargs):
    """Handle trust relationship approval signal."""
    from .observers.trust_observers import trust_event_manager
    
    trust_event_manager.notify_observers('relationship_approved', {
        'relationship': relationship,
        'approving_organization': approving_org,
        'user': user,
        'success': True
    })


@receiver(trust_relationship_revoked)
def handle_trust_relationship_revoked(sender, relationship, revoking_org, user, reason=None, **kwargs):
    """Handle trust relationship revocation signal."""
    from .observers.trust_observers import trust_event_manager
    
    trust_event_manager.notify_observers('relationship_revoked', {
        'relationship': relationship,
        'revoking_organization': revoking_org,
        'user': user,
        'reason': reason,
        'success': True
    })


@receiver(trust_access_granted)
def handle_trust_access_granted(sender, requesting_org, target_org, resource_type, 
                               access_level, user, **kwargs):
    """Handle trust access granted signal."""
    from .observers.trust_observers import trust_event_manager
    
    trust_event_manager.notify_observers('access_granted', {
        'requesting_organization': requesting_org,
        'target_organization': target_org,
        'resource_type': resource_type,
        'access_level': access_level,
        'user': user,
        'success': True
    })


@receiver(trust_access_denied)
def handle_trust_access_denied(sender, requesting_org, target_org, resource_type, 
                              reason, user, **kwargs):
    """Handle trust access denied signal."""
    from .observers.trust_observers import trust_event_manager
    
    trust_event_manager.notify_observers('access_denied', {
        'requesting_organization': requesting_org,
        'target_organization': target_org,
        'resource_type': resource_type,
        'reason': reason,
        'user': user,
        'success': False,
        'failure_reason': reason
    })
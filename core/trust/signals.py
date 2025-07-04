"""
Django Signals for Trust Management

Signal handlers for trust-related events that integrate with the
Observer pattern implementation.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import TrustRelationship, TrustGroup, TrustGroupMembership
from .patterns.observer import trust_event_manager


@receiver(post_save, sender=TrustRelationship)
def trust_relationship_saved(sender, instance, created, **kwargs):
    """Handle trust relationship save events."""
    if created:
        trust_event_manager.notify_observers('relationship_created', {
            'relationship': instance,
            'source_organization': instance.source_organization,
            'target_organization': instance.target_organization,
            'user': instance.created_by
        })
    else:
        # Check if status changed to active
        if instance.status == 'active' and instance.activated_at:
            trust_event_manager.notify_observers('relationship_activated', {
                'relationship': instance,
                'source_organization': instance.source_organization,
                'target_organization': instance.target_organization,
                'user': instance.last_modified_by
            })


@receiver(post_save, sender=TrustGroupMembership)
def trust_group_membership_saved(sender, instance, created, **kwargs):
    """Handle trust group membership events."""
    if created:
        trust_event_manager.notify_observers('group_joined', {
            'membership': instance,
            'organization': instance.organization,
            'trust_group': instance.trust_group,
            'user': 'system'  # Would be actual user in real implementation
        })


@receiver(pre_save, sender=TrustGroupMembership)
def trust_group_membership_pre_save(sender, instance, **kwargs):
    """Handle trust group membership changes."""
    if instance.pk:  # Existing instance
        try:
            old_instance = TrustGroupMembership.objects.get(pk=instance.pk)
            if old_instance.is_active and not instance.is_active:
                # Member is leaving the group
                trust_event_manager.notify_observers('group_left', {
                    'membership': instance,
                    'organization': instance.organization,
                    'trust_group': instance.trust_group,
                    'user': 'system'
                })
        except TrustGroupMembership.DoesNotExist:
            pass
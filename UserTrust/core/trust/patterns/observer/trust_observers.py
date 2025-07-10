from abc import ABC, abstractmethod
from typing import Dict, Any, List
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from django.utils import timezone
import logging
import json

from ...models.trust_models import TrustRelationship, TrustGroup, TrustGroupMembership, TrustLog

logger = logging.getLogger(__name__)


class TrustObserver(ABC):
    """
    Abstract base class for trust relationship observers.
    Implements the Observer pattern for trust-related events.
    """
    
    @abstractmethod
    def update(self, event_type: str, event_data: Dict[str, Any]):
        """
        Handle trust-related event notifications.
        
        Args:
            event_type: Type of trust event
            event_data: Event data and context
        """
        pass


class TrustNotificationObserver(TrustObserver):
    """
    Observer that handles trust relationship notifications.
    Sends notifications to relevant parties when trust events occur.
    """
    
    def update(self, event_type: str, event_data: Dict[str, Any]):
        """
        Send notifications for trust events.
        """
        try:
            if event_type == 'relationship_created':
                self._notify_relationship_created(event_data)
            elif event_type == 'relationship_approved':
                self._notify_relationship_approved(event_data)
            elif event_type == 'relationship_activated':
                self._notify_relationship_activated(event_data)
            elif event_type == 'relationship_revoked':
                self._notify_relationship_revoked(event_data)
            elif event_type == 'group_joined':
                self._notify_group_joined(event_data)
            elif event_type == 'group_left':
                self._notify_group_left(event_data)
            elif event_type == 'access_granted':
                self._notify_access_granted(event_data)
            elif event_type == 'access_denied':
                self._notify_access_denied(event_data)
            
            logger.info(f"Notification sent for trust event: {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to send trust notification: {str(e)}")
    
    def _notify_relationship_created(self, event_data: Dict[str, Any]):
        """Notify parties about new trust relationship creation."""
        relationship = event_data.get('relationship')
        if not relationship:
            return
        
        # In a real implementation, this would send actual notifications
        # via email, webhooks, message queues, etc.
        logger.info(
            f"NOTIFICATION: Trust relationship created between "
            f"{relationship.source_organization} and {relationship.target_organization}"
        )
        
        # Log the notification
        self._log_notification('relationship_created', {
            'source_org': relationship.source_organization,
            'target_org': relationship.target_organization,
            'trust_level': relationship.trust_level.name,
            'relationship_type': relationship.relationship_type
        })
    
    def _notify_relationship_approved(self, event_data: Dict[str, Any]):
        """Notify parties about trust relationship approval."""
        relationship = event_data.get('relationship')
        approving_org = event_data.get('approving_organization')
        
        if not relationship or not approving_org:
            return
        
        logger.info(
            f"NOTIFICATION: Trust relationship approved by {approving_org} "
            f"for relationship {relationship.id}"
        )
        
        self._log_notification('relationship_approved', {
            'relationship_id': str(relationship.id),
            'approving_org': approving_org,
            'fully_approved': relationship.is_fully_approved
        })
    
    def _notify_relationship_activated(self, event_data: Dict[str, Any]):
        """Notify parties about trust relationship activation."""
        relationship = event_data.get('relationship')
        if not relationship:
            return
        
        logger.info(
            f"NOTIFICATION: Trust relationship activated between "
            f"{relationship.source_organization} and {relationship.target_organization}"
        )
        
        self._log_notification('relationship_activated', {
            'relationship_id': str(relationship.id),
            'source_org': relationship.source_organization,
            'target_org': relationship.target_organization,
            'trust_level': relationship.trust_level.name
        })
    
    def _notify_relationship_revoked(self, event_data: Dict[str, Any]):
        """Notify parties about trust relationship revocation."""
        relationship = event_data.get('relationship')
        revoking_org = event_data.get('revoking_organization')
        reason = event_data.get('reason')
        
        if not relationship or not revoking_org:
            return
        
        logger.info(
            f"NOTIFICATION: Trust relationship revoked by {revoking_org} "
            f"for relationship {relationship.id}. Reason: {reason or 'Not specified'}"
        )
        
        self._log_notification('relationship_revoked', {
            'relationship_id': str(relationship.id),
            'revoking_org': revoking_org,
            'reason': reason or 'Not specified'
        })
    
    def _notify_group_joined(self, event_data: Dict[str, Any]):
        """Notify parties about trust group membership."""
        membership = event_data.get('membership')
        if not membership:
            return
        
        logger.info(
            f"NOTIFICATION: Organization {membership.organization} "
            f"joined trust group {membership.trust_group.name}"
        )
        
        self._log_notification('group_joined', {
            'organization': membership.organization,
            'group_name': membership.trust_group.name,
            'membership_type': membership.membership_type
        })
    
    def _notify_group_left(self, event_data: Dict[str, Any]):
        """Notify parties about trust group departure."""
        membership = event_data.get('membership')
        reason = event_data.get('reason')
        
        if not membership:
            return
        
        logger.info(
            f"NOTIFICATION: Organization {membership.organization} "
            f"left trust group {membership.trust_group.name}. Reason: {reason or 'Not specified'}"
        )
        
        self._log_notification('group_left', {
            'organization': membership.organization,
            'group_name': membership.trust_group.name,
            'reason': reason or 'Not specified'
        })
    
    def _notify_access_granted(self, event_data: Dict[str, Any]):
        """Notify about intelligence access granted."""
        requesting_org = event_data.get('requesting_organization')
        target_org = event_data.get('target_organization')
        resource_type = event_data.get('resource_type')
        access_level = event_data.get('access_level')
        
        logger.info(
            f"NOTIFICATION: Access granted to {requesting_org} "
            f"for {resource_type} from {target_org} (level: {access_level})"
        )
        
        self._log_notification('access_granted', event_data)
    
    def _notify_access_denied(self, event_data: Dict[str, Any]):
        """Notify about intelligence access denied."""
        requesting_org = event_data.get('requesting_organization')
        target_org = event_data.get('target_organization')
        resource_type = event_data.get('resource_type')
        reason = event_data.get('reason')
        
        logger.info(
            f"NOTIFICATION: Access denied to {requesting_org} "
            f"for {resource_type} from {target_org}. Reason: {reason}"
        )
        
        self._log_notification('access_denied', event_data)
    
    def _log_notification(self, notification_type: str, data: Dict[str, Any]):
        """Log notification details for audit purposes."""
        try:
            # Convert complex objects to serializable format
            serializable_data = self._make_serializable(data)
            # In a real implementation, this might store notifications in a separate table
            logger.debug(f"Notification logged: {notification_type} - {json.dumps(serializable_data)}")
        except Exception as e:
            logger.error(f"Failed to log notification: {str(e)}")
    
    def _make_serializable(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert data to JSON-serializable format."""
        serializable = {}
        for key, value in data.items():
            if hasattr(value, 'id'):
                # Django model instance
                serializable[key] = str(value.id)
            elif hasattr(value, '__dict__'):
                # Other objects with attributes
                serializable[key] = str(value)
            else:
                # Basic types
                serializable[key] = value
        return serializable


class TrustMetricsObserver(TrustObserver):
    """
    Observer that collects trust relationship metrics and statistics.
    """
    
    def update(self, event_type: str, event_data: Dict[str, Any]):
        """
        Collect metrics for trust events.
        """
        try:
            metrics_data = {
                'event_type': event_type,
                'timestamp': timezone.now().isoformat(),
                'event_data': event_data
            }
            
            # In a real implementation, this would send metrics to monitoring systems
            # like Prometheus, CloudWatch, or custom analytics platforms
            self._record_metric(event_type, metrics_data)
            
        except Exception as e:
            logger.error(f"Failed to record trust metrics: {str(e)}")
    
    def _record_metric(self, metric_type: str, data: Dict[str, Any]):
        """Record metric data."""
        # Placeholder for metrics recording
        logger.debug(f"METRIC: {metric_type} - {json.dumps(data, default=str)}")


class TrustAuditObserver(TrustObserver):
    """
    Observer that maintains detailed audit logs for trust operations.
    """
    
    def update(self, event_type: str, event_data: Dict[str, Any]):
        """
        Create detailed audit logs for trust events.
        """
        try:
            self._create_audit_log(event_type, event_data)
        except Exception as e:
            logger.error(f"Failed to create trust audit log: {str(e)}")
    
    def _create_audit_log(self, event_type: str, event_data: Dict[str, Any]):
        """Create detailed audit log entry."""
        relationship = event_data.get('relationship')
        trust_group = event_data.get('trust_group')
        source_org = event_data.get('source_organization') or event_data.get('requesting_organization')
        target_org = event_data.get('target_organization')
        user = event_data.get('user')  # None for system events
        
        # Map event types to trust log actions
        action_mapping = {
            'relationship_created': 'relationship_created',
            'relationship_approved': 'relationship_approved',
            'relationship_activated': 'relationship_activated',
            'relationship_revoked': 'relationship_revoked',
            'group_joined': 'group_joined',
            'group_left': 'group_left',
            'access_granted': 'access_granted',
            'access_denied': 'access_denied',
        }
        
        action = action_mapping.get(event_type, event_type)
        
        # Create trust log entry
        TrustLog.log_trust_event(
            action=action,
            source_organization=source_org,
            target_organization=target_org,
            trust_relationship=relationship,
            trust_group=trust_group,
            user=user,
            success=event_data.get('success', True),
            failure_reason=event_data.get('failure_reason'),
            details=event_data.get('details', {})
        )
        
        logger.debug(f"Audit log created for {event_type}")


class TrustSecurityObserver(TrustObserver):
    """
    Observer that monitors trust relationships for security anomalies.
    """
    
    def update(self, event_type: str, event_data: Dict[str, Any]):
        """
        Monitor trust events for security concerns.
        """
        try:
            if event_type == 'access_denied':
                self._check_access_denial_patterns(event_data)
            elif event_type == 'relationship_revoked':
                self._check_revocation_patterns(event_data)
            elif event_type == 'multiple_failed_access':
                self._handle_suspicious_access_attempts(event_data)
        except Exception as e:
            logger.error(f"Failed to process security monitoring: {str(e)}")
    
    def _check_access_denial_patterns(self, event_data: Dict[str, Any]):
        """Check for suspicious access denial patterns."""
        requesting_org = event_data.get('requesting_organization')
        if not requesting_org:
            return
        
        # In a real implementation, this would check for patterns like:
        # - Multiple rapid access attempts
        # - Access attempts to sensitive resources
        # - Unusual access patterns
        
        logger.debug(f"Security check: Access denial for {requesting_org}")
    
    def _check_revocation_patterns(self, event_data: Dict[str, Any]):
        """Check for suspicious trust revocation patterns."""
        relationship = event_data.get('relationship')
        if not relationship:
            return
        
        # Check if this is part of a pattern of revocations
        logger.debug(f"Security check: Trust revocation for relationship {relationship.id}")
    
    def _handle_suspicious_access_attempts(self, event_data: Dict[str, Any]):
        """Handle potentially suspicious access attempts."""
        # This would trigger security alerts, rate limiting, etc.
        logger.warning(f"SECURITY ALERT: Suspicious access pattern detected - {event_data}")


# Observable Trust Event Manager
class TrustEventManager:
    """
    Manages trust event observers and notifications.
    Implements the Subject part of the Observer pattern.
    """
    
    def __init__(self):
        self._observers: List[TrustObserver] = []
        self._setup_default_observers()
    
    def _setup_default_observers(self):
        """Setup default observers."""
        self.add_observer(TrustNotificationObserver())
        self.add_observer(TrustMetricsObserver())
        self.add_observer(TrustAuditObserver())
        self.add_observer(TrustSecurityObserver())
    
    def add_observer(self, observer: TrustObserver):
        """Add an observer to the list."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: TrustObserver):
        """Remove an observer from the list."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event_type: str, event_data: Dict[str, Any]):
        """Notify all observers of a trust event."""
        for observer in self._observers:
            try:
                observer.update(event_type, event_data)
            except Exception as e:
                logger.error(f"Observer {observer.__class__.__name__} failed to handle event {event_type}: {str(e)}")


# Global event manager instance
trust_event_manager = TrustEventManager()


# Django Signal Handlers
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


def notify_access_event(event_type: str, requesting_org: str, target_org: str, 
                       resource_type: str = None, access_level: str = None,
                       reason: str = None, user: str = None, **kwargs):
    """
    Convenience function to notify access-related events.
    
    Args:
        event_type: Type of access event ('access_granted' or 'access_denied')
        requesting_org: Organization requesting access
        target_org: Organization owning the resource
        resource_type: Type of resource being accessed
        access_level: Access level granted (if applicable)
        reason: Reason for denial (if applicable)
        user: User performing the action
        **kwargs: Additional event data
    """
    event_data = {
        'requesting_organization': requesting_org,
        'target_organization': target_org,
        'resource_type': resource_type,
        'access_level': access_level,
        'reason': reason,
        'user': user,
        **kwargs
    }
    
    trust_event_manager.notify_observers(event_type, event_data)


def notify_trust_relationship_event(event_type: str, relationship: TrustRelationship,
                                   user: str = None, **kwargs):
    """
    Convenience function to notify trust relationship events.
    
    Args:
        event_type: Type of relationship event
        relationship: TrustRelationship instance
        user: User performing the action
        **kwargs: Additional event data
    """
    event_data = {
        'relationship': relationship,
        'source_organization': relationship.source_organization,
        'target_organization': relationship.target_organization,
        'user': user,
        **kwargs
    }
    
    trust_event_manager.notify_observers(event_type, event_data)
from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.conf import settings
from .services.audit_service import AuditService
from .user_management.models import CustomUser, Organization
from .trust.models import TrustRelationship, TrustGroup
import logging

logger = logging.getLogger(__name__)

# Initialize audit service
audit_service = AuditService()

def _is_test_environment():
    """Check if we're running in test environment."""
    return (hasattr(settings, 'TESTING') and settings.TESTING) or \
           'test' in settings.DATABASES.get('default', {}).get('NAME', '')

def _get_client_ip(request):
    """Extract client IP from request."""
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

@receiver(post_save, sender=CustomUser)
def log_user_changes(sender, instance, created, **kwargs):
    """Log user creation and modification events."""
    try:
        # Skip in test environment to avoid integrity issues
        if _is_test_environment():
            return
            
        # Skip if this is called during user creation by signals themselves
        if hasattr(instance, '_signal_skip'):
            return
            
        action = 'user_created' if created else 'user_modified'
        
        # Get the current user from the request context if available
        current_user = getattr(instance, '_current_user', None)
        
        # Avoid infinite recursion by using current user or system
        log_user = current_user if current_user and current_user != instance else None
        
        audit_service.log_user_event(
            user=log_user,
            action=action,
            success=True,
            additional_data={
                'target_user_id': str(instance.id),
                'target_username': instance.username,
                'target_email': instance.email,
                'target_role': instance.role,
                'target_organization': instance.organization.name if instance.organization else None
            },
            target_user=instance
        )
        
    except Exception as e:
        logger.error(f"Failed to log user change: {str(e)}")

@receiver(post_save, sender=Organization)
def log_organization_changes(sender, instance, created, **kwargs):
    """Log organization creation and modification events."""
    try:
        # Skip in test environment
        if _is_test_environment():
            return
            
        action = 'organization_created' if created else 'organization_modified'
        
        # Get the current user from the request context if available
        current_user = getattr(instance, '_current_user', None)
        
        if current_user:
            audit_service.log_user_event(
                user=current_user,
                action=action,
                success=True,
                additional_data={
                    'target_organization_id': str(instance.id),
                    'target_organization_name': instance.name,
                    'target_organization_type': instance.org_type,
                },
                target_organization=instance
            )
        
    except Exception as e:
        logger.error(f"Failed to log organization change: {str(e)}")

@receiver(post_save, sender=TrustRelationship)
def log_trust_relationship_changes(sender, instance, created, **kwargs):
    """Log trust relationship creation and modification events."""
    try:
        # Skip in test environment
        if _is_test_environment():
            return
            
        action = 'relationship_created' if created else 'relationship_modified'
        
        # Get the current user from the request context if available
        current_user = getattr(instance, '_current_user', None)
        
        if current_user:
            audit_service.log_trust_event(
                user=current_user,
                action=action,
                source_organization=instance.source_organization,
                target_organization=instance.target_organization,
                success=True,
                trust_relationship=instance,
                additional_data={
                    'relationship_id': str(instance.id),
                    'trust_level': instance.trust_level.name if instance.trust_level else None,
                    'status': instance.status
                }
            )
        
    except Exception as e:
        logger.error(f"Failed to log trust relationship change: {str(e)}")

@receiver(post_save, sender=TrustGroup)
def log_trust_group_changes(sender, instance, created, **kwargs):
    """Log trust group creation and modification events."""
    try:
        # Skip in test environment
        if _is_test_environment():
            return
            
        action = 'group_created' if created else 'group_modified'
        
        # Get the current user from the request context if available
        current_user = getattr(instance, '_current_user', None)
        
        if current_user:
            audit_service.log_trust_event(
                user=current_user,
                action=action,
                success=True,
                trust_group=instance,
                additional_data={
                    'group_id': str(instance.id),
                    'group_name': instance.name,
                    'group_type': instance.group_type,
                    'default_trust_level': instance.default_trust_level.name if instance.default_trust_level else None
                }
            )
        
    except Exception as e:
        logger.error(f"Failed to log trust group change: {str(e)}")

@receiver(user_logged_in)
def log_successful_login(sender, request, user, **kwargs):
    """Log successful login events."""
    try:
        # Skip in test environment
        if _is_test_environment():
            return
            
        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        session_key = request.session.session_key if request.session else None
        
        audit_service.log_user_event(
            user=user,
            action='login_success',
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            additional_data={
                'login_method': 'django_auth',
                'session_key': session_key
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to log login success: {str(e)}")

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Log failed login attempts."""
    try:
        # Skip in test environment
        if _is_test_environment():
            return
            
        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        audit_service.log_user_event(
            user=None,  # No user for failed login
            action='login_failure',
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason='Invalid credentials',
            additional_data={
                'attempted_username': credentials.get('username', 'Unknown'),
                'login_method': 'django_auth'
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to log login failure: {str(e)}")
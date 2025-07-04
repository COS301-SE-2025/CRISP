from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from threading import local
import logging

logger = logging.getLogger(__name__)

# Thread-local storage for tracking current user in signals
_thread_local = local()


class AuditSignalHandler:
    """
    Signal handlers for automatic audit logging of model changes.
    """
    
    @staticmethod
    def set_current_user(user):
        """Set the current user for the thread (used in middleware)."""
        _thread_local.user = user
    
    @staticmethod
    def get_current_user():
        """Get the current user for the thread."""
        return getattr(_thread_local, 'user', None)


@receiver(post_save, sender='user_management.CustomUser')
def log_user_changes(sender, instance, created, **kwargs):
    """Log user model changes."""
    try:
        from .services.audit_service import AuditService
        
        audit_service = AuditService()
        current_user = AuditSignalHandler.get_current_user()
        
        if created:
            action = 'user_created'
        else:
            action = 'user_modified'
        
        audit_service.log_user_event(
            user=current_user,
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
        logger.error(f"Failed to log user changes: {str(e)}")


@receiver(post_save, sender='user_management.Organization')
def log_organization_changes(sender, instance, created, **kwargs):
    """Log organization model changes."""
    try:
        from .services.audit_service import AuditService
        
        audit_service = AuditService()
        current_user = AuditSignalHandler.get_current_user()
        
        if created:
            action = 'organization_created'
        else:
            action = 'organization_modified'
        
        audit_service.log_user_event(
            user=current_user,
            action=action,
            success=True,
            additional_data={
                'target_organization_id': str(instance.id),
                'target_organization_name': instance.name,
                'target_organization_domain': instance.domain,
                'target_organization_type': instance.organization_type,
                'is_publisher': instance.is_publisher
            },
            target_organization=instance
        )
        
    except Exception as e:
        logger.error(f"Failed to log organization changes: {str(e)}")


@receiver(post_save, sender='trust.TrustRelationship')
def log_trust_relationship_changes(sender, instance, created, **kwargs):
    """Log trust relationship model changes."""
    try:
        from .services.audit_service import AuditService
        
        audit_service = AuditService()
        current_user = AuditSignalHandler.get_current_user()
        
        if created:
            action = 'relationship_created'
        else:
            action = 'relationship_modified'
        
        audit_service.log_trust_event(
            user=current_user,
            action=action,
            success=True,
            details=f"Trust relationship between {instance.source_organization.name} and {instance.target_organization.name}",
            trust_relationship=instance,
            additional_data={
                'source_organization': instance.source_organization.name,
                'target_organization': instance.target_organization.name,
                'trust_level': instance.trust_level.name,
                'status': instance.status,
                'relationship_type': instance.relationship_type
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to log trust relationship changes: {str(e)}")


@receiver(post_save, sender='trust.TrustGroup')
def log_trust_group_changes(sender, instance, created, **kwargs):
    """Log trust group model changes."""
    try:
        from .services.audit_service import AuditService
        
        audit_service = AuditService()
        current_user = AuditSignalHandler.get_current_user()
        
        if created:
            action = 'group_created'
        else:
            action = 'group_modified'
        
        audit_service.log_trust_event(
            user=current_user,
            action=action,
            success=True,
            details=f"Trust group: {instance.name}",
            trust_group=instance,
            additional_data={
                'group_name': instance.name,
                'group_description': instance.description,
                'is_public': instance.is_public,
                'is_active': instance.is_active,
                'trust_level': instance.trust_level.name if instance.trust_level else None
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to log trust group changes: {str(e)}")


@receiver(post_delete, sender='user_management.CustomUser')
def log_user_deletion(sender, instance, **kwargs):
    """Log user deletion."""
    try:
        from .services.audit_service import AuditService
        
        audit_service = AuditService()
        current_user = AuditSignalHandler.get_current_user()
        
        audit_service.log_user_event(
            user=current_user,
            action='user_deleted',
            success=True,
            additional_data={
                'deleted_user_id': str(instance.id),
                'deleted_username': instance.username,
                'deleted_email': instance.email,
                'deleted_role': instance.role
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to log user deletion: {str(e)}")


@receiver(post_delete, sender='trust.TrustRelationship')
def log_trust_relationship_deletion(sender, instance, **kwargs):
    """Log trust relationship deletion."""
    try:
        from .services.audit_service import AuditService
        
        audit_service = AuditService()
        current_user = AuditSignalHandler.get_current_user()
        
        audit_service.log_trust_event(
            user=current_user,
            action='relationship_deleted',
            success=True,
            details=f"Deleted trust relationship between {instance.source_organization.name} and {instance.target_organization.name}",
            additional_data={
                'deleted_relationship_id': str(instance.id),
                'source_organization': instance.source_organization.name,
                'target_organization': instance.target_organization.name,
                'trust_level': instance.trust_level.name,
                'relationship_type': instance.relationship_type
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to log trust relationship deletion: {str(e)}")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login."""
    try:
        from .services.audit_service import AuditService
        
        audit_service = AuditService()
        
        audit_service.log_user_event(
            user=user,
            action='login_success',
            ip_address=audit_service._get_client_ip(request) if hasattr(audit_service, '_get_client_ip') else None,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=True,
            additional_data={
                'login_method': 'django_auth',
                'session_key': request.session.session_key
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to log user login: {str(e)}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout."""
    try:
        from .services.audit_service import AuditService
        
        audit_service = AuditService()
        
        audit_service.log_user_event(
            user=user,
            action='logout',
            ip_address=audit_service._get_client_ip(request) if hasattr(audit_service, '_get_client_ip') else None,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=True,
            additional_data={
                'logout_method': 'django_auth',
                'session_key': request.session.session_key if hasattr(request, 'session') else None
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to log user logout: {str(e)}")


@receiver(user_login_failed)
def log_user_login_failure(sender, credentials, request, **kwargs):
    """Log failed login attempts."""
    try:
        from .services.audit_service import AuditService
        
        audit_service = AuditService()
        
        audit_service.log_user_event(
            user=None,
            action='login_failure',
            ip_address=audit_service._get_client_ip(request) if hasattr(audit_service, '_get_client_ip') else None,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=False,
            failure_reason='Invalid credentials',
            additional_data={
                'attempted_username': credentials.get('username', ''),
                'login_method': 'django_auth'
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to log login failure: {str(e)}")


# Enhanced middleware to set current user in signals
class AuditSignalMiddleware:
    """Middleware to set current user for signal handlers."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Set current user for signals
        if hasattr(request, 'user') and request.user.is_authenticated:
            AuditSignalHandler.set_current_user(request.user)
        else:
            AuditSignalHandler.set_current_user(None)
        
        response = self.get_response(request)
        
        # Clear current user after request
        AuditSignalHandler.set_current_user(None)
        
        return response
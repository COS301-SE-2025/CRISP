from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import CustomUser, AuthenticationLog
from .observers.auth_observers import auth_event_subject


@receiver(post_save, sender=CustomUser)
def user_created_signal(sender, instance, created, **kwargs):
    """Handle user creation events"""
    if created:
        # Get request data if available
        request_data = getattr(instance, '_creation_request_data', {})
        
        # Notify observers
        auth_event_subject.notify_observers(
            event_type='user_created',
            user=instance,
            event_data={
                'ip_address': request_data.get('ip_address', '127.0.0.1'),
                'user_agent': request_data.get('user_agent', 'System'),
                'created_by': request_data.get('created_by'),
                'success': True,
                'additional_data': {
                    'role': instance.role,
                    'organization': instance.organization.name if instance.organization else None
                }
            }
        )


@receiver(post_delete, sender=CustomUser)
def user_deleted_signal(sender, instance, **kwargs):
    """Handle user deletion events"""
    # Get request data if available
    request_data = getattr(instance, '_deletion_request_data', {})
    
    # Log deletion event
    AuthenticationLog.log_authentication_event(
        user=None,  # User is being deleted
        action='user_deleted',
        ip_address=request_data.get('ip_address', '127.0.0.1'),
        user_agent=request_data.get('user_agent', 'System'),
        success=True,
        additional_data={
            'deleted_user_id': str(instance.id),
            'deleted_username': instance.username,
            'deleted_by': request_data.get('deleted_by'),
            'organization': instance.organization.name if instance.organization else None
        }
    )


@receiver(user_logged_in)
def user_login_signal(sender, request, user, **kwargs):
    """Handle successful login events"""
    if isinstance(user, CustomUser):
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Notify observers
        auth_event_subject.notify_observers(
            event_type='login_success',
            user=user,
            event_data={
                'ip_address': ip_address,
                'user_agent': user_agent,
                'success': True,
                'additional_data': {
                    'session_key': request.session.session_key
                }
            }
        )


@receiver(user_logged_out)
def user_logout_signal(sender, request, user, **kwargs):
    """Handle logout events"""
    if isinstance(user, CustomUser):
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Log logout event
        AuthenticationLog.log_authentication_event(
            user=user,
            action='logout',
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip
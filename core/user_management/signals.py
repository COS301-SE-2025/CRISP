from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.utils import timezone
from .models import CustomUser, Organization, UserProfile, AuthenticationLog
import logging

logger = logging.getLogger(__name__)

def _safe_get_organization_name(instance):
    """Safely get organization name, handling deleted organizations"""
    try:
        return instance.organization.name if instance.organization else None
    except:
        return None


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create UserProfile when a new user is created
    """
    if created:
        UserProfile.objects.create(user=instance)
        logger.info(f"Created user profile for user: {instance.username}")


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    Save UserProfile when user is saved
    """
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


@receiver(pre_save, sender=CustomUser)
def user_pre_save_handler(sender, instance, **kwargs):
    """
    Handle user model changes before saving
    """
    # Auto-set is_publisher based on role
    if instance.role in ['publisher', 'BlueVisionAdmin']:
        instance.is_publisher = True
    elif instance.role == 'viewer':
        instance.is_publisher = False
    
    # Auto-verify certain roles
    if instance.role == 'BlueVisionAdmin':
        instance.is_verified = True
        instance.is_staff = True
        instance.is_superuser = True
    
    # Track password changes
    if instance.pk:  # Existing user
        try:
            old_instance = CustomUser.objects.get(pk=instance.pk)
            if old_instance.password != instance.password:
                instance.password_changed_at = timezone.now()
        except CustomUser.DoesNotExist:
            pass


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """
    Handle successful user login
    """
    # Reset failed login attempts
    if user.failed_login_attempts > 0:
        user.failed_login_attempts = 0
        user.save(update_fields=['failed_login_attempts'])
    
    # Unlock account if it was locked
    if user.is_account_locked:
        user.unlock_account()
    
    # Log the successful login
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    
    AuthenticationLog.log_authentication_event(
        user=user,
        action='login_success',
        ip_address=ip_address,
        user_agent=user_agent,
        success=True,
        additional_data={
            'login_method': 'standard',
            'session_key': request.session.session_key if hasattr(request, 'session') else None
        }
    )
    
    logger.info(f"User {user.username} logged in successfully from {ip_address}")


@receiver(user_login_failed)
def user_login_failed_handler(sender, credentials, request, **kwargs):
    """
    Handle failed user login attempts
    """
    username = credentials.get('username')
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    
    # Try to find the user
    user = None
    if username:
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(email=username)
            except CustomUser.DoesNotExist:
                pass
    
    # Increment failed login attempts if user exists
    if user:
        user.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.lock_account(duration_minutes=15)
            logger.warning(f"Account locked for user {user.username} after {user.failed_login_attempts} failed attempts")
        
        user.save(update_fields=['failed_login_attempts', 'account_locked_until'])
    
    # Log the failed login attempt
    AuthenticationLog.log_authentication_event(
        user=user,
        action='login_failure',
        ip_address=ip_address,
        user_agent=user_agent,
        success=False,
        failure_reason='Invalid credentials',
        additional_data={
            'attempted_username': username,
            'failed_attempts': user.failed_login_attempts if user else 1
        }
    )
    
    logger.warning(f"Failed login attempt for username: {username} from {ip_address}")


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    """
    Handle user logout
    """
    if user:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Log the logout
        AuthenticationLog.log_authentication_event(
            user=user,
            action='logout',
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            additional_data={
                'logout_method': 'manual',
                'session_key': request.session.session_key if hasattr(request, 'session') else None
            }
        )
        
        logger.info(f"User {user.username} logged out from {ip_address}")


@receiver(post_save, sender=Organization)
def organization_created_handler(sender, instance, created, **kwargs):
    """
    Handle organization creation
    """
    if created:
        logger.info(f"New organization created: {instance.name} (ID: {instance.id})")
        
        # Create default trust level if this is the first organization
        from core.trust.models import TrustLevel
        if Organization.objects.count() == 1:
            TrustLevel.objects.get_or_create(
                name='Default Public Trust',
                defaults={
                    'level': 'public',
                    'description': 'Default public trust level for new organizations',
                    'numerical_value': 30,
                    'is_system_default': True,
                    'created_by': 'System'
                }
            )


@receiver(post_delete, sender=CustomUser)
def user_deleted_handler(sender, instance, **kwargs):
    """
    Handle user deletion
    """
    logger.info(f"User deleted: {instance.username} (ID: {instance.id})")
    
    # Log the user deletion
    AuthenticationLog.log_authentication_event(
        user=None,  # User is being deleted
        action='user_deleted',
        ip_address='127.0.0.1',
        user_agent='System',
        success=True,
        additional_data={
            'deleted_username': instance.username,
            'deleted_user_id': str(instance.id),
            'organization': _safe_get_organization_name(instance)
        }
    )


@receiver(post_delete, sender=Organization)
def organization_deleted_handler(sender, instance, **kwargs):
    """
    Handle organization deletion
    """
    logger.info(f"Organization deleted: {instance.name} (ID: {instance.id})")
    
    # Clean up related trust relationships
    from core.trust.models import TrustRelationship
    TrustRelationship.objects.filter(
        source_organization=str(instance.id)
    ).delete()
    TrustRelationship.objects.filter(
        target_organization=str(instance.id)
    ).delete()


def get_client_ip(request):
    """
    Extract client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


# Trust-related signals for user management integration
@receiver(post_save, sender='trust.TrustRelationship')
def trust_relationship_created_handler(sender, instance, created, **kwargs):
    """
    Handle trust relationship creation/updates for user management
    """
    if created:
        # Notify users in both organizations about new trust relationship
        try:
            # source_organization and target_organization are now ForeignKey objects
            source_org = instance.source_organization
            target_org = instance.target_organization
            
            # Log trust relationship creation
            logger.info(
                f"Trust relationship created between {source_org.name} and {target_org.name}"
            )
            
            # Here you could send notifications to organization administrators
            # about the new trust relationship
            
        except Organization.DoesNotExist:
            logger.error(f"Organization not found for trust relationship {instance.id}")


@receiver(post_delete, sender='trust.TrustRelationship')
def trust_relationship_deleted_handler(sender, instance, **kwargs):
    """
    Handle trust relationship deletion
    """
    logger.info(f"Trust relationship deleted: {instance.id}")
    
    # Here you could notify users about the revoked trust relationship
    # and potentially revoke access to shared resources
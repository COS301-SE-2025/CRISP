"""
Utility functions for CRISP User Management integration
"""
import hashlib
import secrets
import string
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from datetime import timedelta

from .models import CustomUser, STIXObjectPermission, AuthenticationLog


class CRISPIntegrationUtils:
    """Utilities for integrating with existing CRISP components"""
    
    @staticmethod
    def get_user_organization_context(user: CustomUser) -> Dict[str, Any]:
        """Get user's organization context for CRISP integration"""
        if not user.organization:
            return {}
        
        return {
            'organization_id': str(user.organization.id),
            'organization_name': user.organization.name,
            'organization_sectors': getattr(user.organization, 'sectors', []),
            'organization_contact': getattr(user.organization, 'contact_email', ''),
            'user_role': user.role,
            'user_permissions': {
                'is_publisher': user.is_publisher,
                'is_admin': user.is_organization_admin(),
                'can_publish_feeds': user.can_publish_feeds()
            }
        }
    
    @staticmethod
    def check_organization_trust_relationship(org1_id: str, org2_id: str) -> bool:
        """
        Check if two organizations have a trust relationship
        This would integrate with existing organization trust model
        """
        # Placeholder implementation - would integrate with actual trust model
        try:
            # This would query the actual organization trust relationships
            # For now, assume organizations trust themselves
            return org1_id == org2_id
        except Exception:
            return False
    
    @staticmethod
    def get_user_stix_permissions(user: CustomUser) -> List[Dict[str, Any]]:
        """Get user's STIX object permissions"""
        permissions = STIXObjectPermission.objects.filter(
            user=user
        ).exclude(
            expires_at__lt=timezone.now()
        )
        
        return [
            {
                'stix_object_id': str(perm.stix_object_id),
                'permission_level': perm.permission_level,
                'granted_by': perm.granted_by.username if perm.granted_by else None,
                'expires_at': perm.expires_at,
                'is_expired': perm.is_expired
            }
            for perm in permissions
        ]
    
    @staticmethod
    def grant_stix_object_permission(
        user: CustomUser, 
        stix_object_id: str, 
        permission_level: str,
        granted_by: CustomUser,
        expires_at: Optional[timezone.datetime] = None
    ) -> STIXObjectPermission:
        """Grant STIX object permission to user"""
        permission, created = STIXObjectPermission.objects.update_or_create(
            user=user,
            stix_object_id=stix_object_id,
            defaults={
                'permission_level': permission_level,
                'granted_by': granted_by,
                'expires_at': expires_at
            }
        )
        
        # Log permission grant
        AuthenticationLog.log_authentication_event(
            user=user,
            action='stix_permission_granted',
            ip_address='127.0.0.1',  # Would get from request
            user_agent='System',
            success=True,
            additional_data={
                'stix_object_id': stix_object_id,
                'permission_level': permission_level,
                'granted_by': granted_by.username,
                'expires_at': expires_at.isoformat() if expires_at else None,
                'created': created
            }
        )
        
        return permission
    
    @staticmethod
    def revoke_stix_object_permission(
        user: CustomUser, 
        stix_object_id: str,
        revoked_by: CustomUser
    ) -> bool:
        """Revoke STIX object permission from user"""
        try:
            permission = STIXObjectPermission.objects.get(
                user=user,
                stix_object_id=stix_object_id
            )
            permission.delete()
            
            # Log permission revocation
            AuthenticationLog.log_authentication_event(
                user=user,
                action='stix_permission_revoked',
                ip_address='127.0.0.1',  # Would get from request
                user_agent='System',
                success=True,
                additional_data={
                    'stix_object_id': stix_object_id,
                    'revoked_by': revoked_by.username
                }
            )
            
            return True
        except STIXObjectPermission.DoesNotExist:
            return False
    
    @staticmethod
    def get_user_feed_permissions(user: CustomUser) -> Dict[str, Any]:
        """Get user's feed publishing permissions"""
        return {
            'can_publish': user.can_publish_feeds(),
            'can_create_feeds': user.role in ['publisher', 'admin', 'system_admin'],
            'can_manage_feeds': user.role in ['admin', 'system_admin'],
            'organization_feeds_only': user.role != 'system_admin',
            'max_feeds': None if user.role == 'system_admin' else 100  # Example limit
        }
    
    @staticmethod
    def check_taxii_access_permission(user: CustomUser, collection_id: str) -> bool:
        """Check if user has access to TAXII collection"""
        # System admins have access to all collections
        if user.role == 'system_admin':
            return True
        
        # Check if collection belongs to user's organization
        # This would integrate with actual TAXII collection model
        try:
            # Placeholder - would query actual collection ownership
            # For now, assume users can access collections from their organization
            return user.is_verified and user.is_active
        except Exception:
            return False
    
    @staticmethod
    def get_anonymization_strategy_for_user(user: CustomUser) -> str:
        """Get appropriate anonymization strategy for user"""
        if user.role == 'system_admin':
            return 'none'  # No anonymization for system admins
        elif user.role in ['admin', 'publisher']:
            return 'minimal'  # Minimal anonymization
        else:
            return 'full'  # Full anonymization for viewers
    
    @staticmethod
    def create_audit_trail_entry(
        user: CustomUser,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Dict[str, Any] = None
    ) -> None:
        """Create audit trail entry for CRISP operations"""
        AuthenticationLog.log_authentication_event(
            user=user,
            action=f'crisp_{action}',
            ip_address=details.get('ip_address', '127.0.0.1') if details else '127.0.0.1',
            user_agent=details.get('user_agent', 'System') if details else 'System',
            success=True,
            additional_data={
                'resource_type': resource_type,
                'resource_id': resource_id,
                'action_details': details or {}
            }
        )


class SecurityUtils:
    """Security utilities for CRISP User Management"""
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_sensitive_data(data: str, salt: str = None) -> str:
        """Hash sensitive data with optional salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        return hashlib.pbkdf2_hmac(
            'sha256',
            data.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        ).hex()
    
    @staticmethod
    def create_device_fingerprint(user_agent: str, accept_language: str, accept_encoding: str) -> str:
        """Create device fingerprint for trusted device tracking"""
        fingerprint_data = f"{user_agent}|{accept_language}|{accept_encoding}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    @staticmethod
    def validate_ip_address(ip_address: str) -> bool:
        """Validate IP address format"""
        import ipaddress
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def check_password_breach(password: str) -> bool:
        """Check if password has been breached (placeholder implementation)"""
        # This would integrate with services like HaveIBeenPwned
        # For now, just check against common passwords
        common_passwords = [
            'password', '123456', 'password123', 'admin', 'qwerty',
            'letmein', 'welcome', 'monkey', '1234567890'
        ]
        return password.lower() in common_passwords


class NotificationUtils:
    """Notification utilities for user management events"""
    
    @staticmethod
    def send_welcome_email(user: CustomUser, temporary_password: str = None) -> bool:
        """Send welcome email to new user"""
        try:
            subject = f'Welcome to CRISP - {user.organization.name if user.organization else "CRISP"}'
            
            message = f"""
Dear {user.first_name or user.username},

Welcome to the CRISP (Cyber Risk Information Sharing Platform)!

Your account has been created with the following details:
- Username: {user.username}
- Email: {user.email}
- Organization: {user.organization.name if user.organization else 'N/A'}
- Role: {user.get_role_display()}

{f"Your temporary password is: {temporary_password}" if temporary_password else ""}

Please log in to the CRISP platform to complete your account setup.

Best regards,
CRISP Administration Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            
            return True
        except Exception as e:
            # Log error but don't raise exception
            print(f"Failed to send welcome email: {e}")
            return False
    
    @staticmethod
    def send_password_reset_email(user: CustomUser, reset_token: str) -> bool:
        """Send password reset email"""
        try:
            subject = 'CRISP Password Reset Request'
            
            reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"
            
            message = f"""
Dear {user.first_name or user.username},

A password reset request has been made for your CRISP account.

Click the following link to reset your password:
{reset_url}

This link will expire in 1 hour.

If you did not request this password reset, please ignore this email.

Best regards,
CRISP Administration Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            
            return True
        except Exception as e:
            print(f"Failed to send password reset email: {e}")
            return False
    
    @staticmethod
    def send_account_locked_notification(user: CustomUser, ip_address: str) -> bool:
        """Send account locked notification"""
        try:
            subject = 'CRISP Account Locked - Security Alert'
            
            message = f"""
Dear {user.first_name or user.username},

Your CRISP account has been locked due to multiple failed login attempts.

Details:
- Account: {user.username}
- Time: {timezone.now()}
- IP Address: {ip_address}

Your account will be automatically unlocked after 30 minutes, or you can contact an administrator.

If this was not you, please contact your organization's CRISP administrator immediately.

Best regards,
CRISP Security Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            
            return True
        except Exception as e:
            print(f"Failed to send account locked notification: {e}")
            return False


class APIUtils:
    """API utilities for CRISP integration"""
    
    @staticmethod
    def format_api_response(success: bool, data: Any = None, message: str = None, 
                          error_code: str = None) -> Dict[str, Any]:
        """Format standardized API response"""
        response = {
            'success': success,
            'timestamp': timezone.now().isoformat()
        }
        
        if success:
            if data is not None:
                response['data'] = data
            if message:
                response['message'] = message
        else:
            response['error'] = {
                'code': error_code or 'unknown_error',
                'message': message or 'An error occurred'
            }
        
        return response
    
    @staticmethod
    def paginate_queryset(queryset, page: int, page_size: int) -> Dict[str, Any]:
        """Paginate queryset and return pagination info"""
        from django.core.paginator import Paginator
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'items': list(page_obj.object_list),
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        }
    
    @staticmethod
    def extract_client_info(request) -> Dict[str, str]:
        """Extract client information from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        return {
            'ip_address': ip,
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
            'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE', ''),
            'accept_encoding': request.META.get('HTTP_ACCEPT_ENCODING', ''),
            'referer': request.META.get('HTTP_REFERER', ''),
            'host': request.META.get('HTTP_HOST', '')
        }
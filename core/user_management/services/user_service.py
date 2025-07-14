from typing import Dict, List, Optional, Any, Tuple
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from ..models import CustomUser, Organization, AuthenticationLog, UserProfile
from ..factories.user_factory import UserFactory
from .access_control_service import AccessControlService
import logging

logger = logging.getLogger(__name__)


class UserService:
    """
    Service for managing users with trust-aware access control.
    Handles user CRUD operations, role management, and trust-based permissions.
    """
    
    def __init__(self):
        self.access_control = AccessControlService()
        # Don't instantiate factory here to avoid creating objects on import
        self.user_factory = None
    
    def create_user(self, creating_user: CustomUser, user_data: Dict) -> CustomUser:
        """
        Create a new user with role-based validation.
        
        Args:
            creating_user: User creating the new user
            user_data: User data including role, organization, etc.
            
        Returns:
            CustomUser: Created user
            
        Raises:
            PermissionDenied: If creating user doesn't have permission
            ValidationError: If user data is invalid
        """
        target_role = user_data.get('role', 'viewer')
        target_org_id = user_data.get('organization_id')
        
        if not target_org_id:
            raise ValidationError("Organization is required")
        
        try:
            target_organization = Organization.objects.get(id=target_org_id)
        except Organization.DoesNotExist:
            raise ValidationError("Invalid organization")
        
        # Check if creating user has permission to create this role
        if not self.access_control.can_create_user_with_role(
            creating_user, target_role, target_organization
        ):
            raise PermissionDenied(
                f"No permission to create {target_role} users in {target_organization.name}"
            )
        
        # Use factory to create user
        user_data['organization'] = target_organization
        user_data['created_by'] = creating_user
        user_data['created_from_ip'] = user_data.get('ip_address', '127.0.0.1')
        user_data['user_agent'] = user_data.get('user_agent', 'System')
        
        try:
            user = self.user_factory.create_user(target_role, user_data, creating_user)
            
            logger.info(
                f"User {user.username} ({target_role}) created by {creating_user.username} "
                f"in organization {target_organization.name}"
            )
            
            return user
            
        except ValidationError as e:
            logger.error(f"User creation failed: {str(e)}")
            raise
    
    def update_user(self, updating_user: CustomUser, user_id: str,
                   update_data: Dict) -> CustomUser:
        """
        Update a user's information with proper permission checks.
        
        Args:
            updating_user: User performing the update
            user_id: ID of user to update
            update_data: Data to update
            
        Returns:
            CustomUser: Updated user
            
        Raises:
            PermissionDenied: If updating user doesn't have permission
            ValidationError: If update data is invalid
        """
        try:
            target_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError("User not found")
        
        # Check permissions
        if not self.access_control.can_manage_user(updating_user, target_user):
            # Users can update their own basic profile
            if updating_user.id == target_user.id:
                allowed_fields = {'first_name', 'last_name', 'email', 'two_factor_enabled'}
                if not set(update_data.keys()).issubset(allowed_fields):
                    raise PermissionDenied("Can only update own basic profile information")
            else:
                raise PermissionDenied("No permission to update this user")
        
        # Define updatable fields based on permissions
        if updating_user.id == target_user.id:
            # Self-update: limited fields
            updatable_fields = {'first_name', 'last_name', 'email', 'two_factor_enabled'}
        elif updating_user.role in ['BlueVisionAdmin', 'admin']:
            # Admin: all fields except sensitive ones
            updatable_fields = {
                'first_name', 'last_name', 'email', 'role', 'is_publisher',
                'is_verified', 'is_active', 'organization'
            }
        elif updating_user.role == 'publisher':
            # Publisher: limited fields for users in their organization
            updatable_fields = {
                'first_name', 'last_name', 'email', 'role', 'is_verified', 'is_active'
            }
        else:
            updatable_fields = set()
        
        # Validate role changes
        if 'role' in update_data and update_data['role'] != target_user.role:
            new_role = update_data['role']
            
            # Check if updating user can assign this role
            if updating_user.role == 'publisher' and new_role not in ['viewer', 'publisher']:
                raise PermissionDenied("Publishers cannot assign admin roles")
            
            # Validate role hierarchy
            updating_level = self.access_control.get_role_hierarchy_level(updating_user.role)
            new_role_level = self.access_control.get_role_hierarchy_level(new_role)
            
            if new_role_level >= updating_level and updating_user.role not in ['BlueVisionAdmin', 'admin']:
                raise PermissionDenied("Cannot assign role equal or higher than your own")
        
        # Validate organization changes
        if 'organization' in update_data:
            if updating_user.role not in ['BlueVisionAdmin', 'admin']:
                raise PermissionDenied("Only BlueVision admins can change user organizations")
            
            try:
                new_org = Organization.objects.get(id=update_data['organization'])
                update_data['organization'] = new_org
            except Organization.DoesNotExist:
                raise ValidationError("Invalid organization")
        
        # Apply updates
        updated_fields = []
        for field, value in update_data.items():
            if field in updatable_fields and hasattr(target_user, field):
                old_value = getattr(target_user, field)
                if old_value != value:
                    setattr(target_user, field, value)
                    updated_fields.append(field)
        
        # Handle role changes
        if 'role' in updated_fields:
            # Auto-set is_publisher based on role
            if target_user.role in ['publisher', 'BlueVisionAdmin']:
                target_user.is_publisher = True
            elif target_user.role == 'viewer':
                target_user.is_publisher = False
        
        if updated_fields:
            target_user.save(update_fields=updated_fields + ['updated_at'])
            # Refresh from database to ensure changes are reflected
            target_user.refresh_from_db()
            
            # Log user update
            AuthenticationLog.log_authentication_event(
                user=updating_user,
                action='user_updated',
                ip_address=update_data.get('updated_from_ip', '127.0.0.1'),
                user_agent=update_data.get('user_agent', 'System'),
                success=True,
                additional_data={
                    'target_user_id': str(target_user.id),
                    'target_username': target_user.username,
                    'updated_fields': updated_fields,
                    'self_update': updating_user.id == target_user.id
                }
            )
            
            logger.info(
                f"User {target_user.username} updated by {updating_user.username}. "
                f"Fields: {', '.join(updated_fields)}"
            )
        
        return target_user
    
    def get_user_details(self, requesting_user: CustomUser,
                        user_id: str) -> Dict[str, Any]:
        """
        Get detailed user information with appropriate filtering.
        
        Args:
            requesting_user: User requesting the information
            user_id: ID of user to get details for
            
        Returns:
            dict: User details with appropriate filtering
            
        Raises:
            PermissionDenied: If requesting user doesn't have access
        """
        try:
            target_user = CustomUser.objects.select_related(
                'organization', 'profile'
            ).get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError("User not found")
        
        # Check if requesting user can access this user
        can_access = (
            requesting_user.id == target_user.id or  # Own profile
            self.access_control.can_manage_user(requesting_user, target_user) or  # Can manage
            self.access_control.can_access_organization(requesting_user, target_user.organization)  # Trust access
        )
        
        if not can_access:
            raise PermissionDenied("No access to this user")
        
        # Determine detail level based on relationship
        if requesting_user.id == target_user.id:
            detail_level = 'full'  # Own profile
        elif self.access_control.can_manage_user(requesting_user, target_user):
            detail_level = 'management'  # Can manage
        else:
            detail_level = 'basic'  # Trust-based access
        
        user_details = {
            'id': str(target_user.id),
            'username': target_user.username,
            'first_name': target_user.first_name,
            'last_name': target_user.last_name,
            'role': target_user.role,
            'organization': {
                'id': str(target_user.organization.id),
                'name': target_user.organization.name,
                'domain': target_user.organization.domain
            },
            'is_publisher': target_user.is_publisher,
            'is_verified': target_user.is_verified,
            'is_active': target_user.is_active,
            'date_joined': target_user.date_joined.isoformat()
        }
        
        if detail_level in ['management', 'full']:
            user_details.update({
                'email': target_user.email,
                'last_login': target_user.last_login.isoformat() if target_user.last_login else None,
                'failed_login_attempts': target_user.failed_login_attempts,
                'is_account_locked': target_user.is_account_locked,
                'two_factor_enabled': target_user.two_factor_enabled,
                'trusted_devices_count': len(target_user.trusted_devices)
            })
        
        if detail_level == 'full':
            # Add sensitive information only for own profile
            user_details.update({
                'preferences': target_user.preferences,
                'trusted_devices': [
                    {
                        'fingerprint': device.get('fingerprint', '')[:8] + '...',
                        'name': device.get('name', 'Unknown'),
                        'added_at': device.get('added_at', '')
                    }
                    for device in target_user.trusted_devices
                ],
                'permissions': list(self.access_control.get_user_permissions(target_user))
            })
            
            # Add profile information if exists
            try:
                profile = target_user.profile
                user_details['profile'] = {
                    'bio': profile.bio,
                    'department': profile.department,
                    'job_title': profile.job_title,
                    'phone_number': profile.phone_number,
                    'email_notifications': profile.email_notifications,
                    'threat_alerts': profile.threat_alerts,
                    'security_notifications': profile.security_notifications,
                    'profile_visibility': profile.profile_visibility
                }
            except UserProfile.DoesNotExist:
                user_details['profile'] = None
        
        return user_details
    
    def list_users(self, requesting_user: CustomUser,
                  filters: Optional[Dict] = None,
                  organization_id: Optional[str] = None) -> List[Dict]:
        """
        List users the requesting user can access.
        
        Args:
            requesting_user: User requesting the list
            filters: Optional filters to apply
            organization_id: Specific organization to list users from
            
        Returns:
            List[Dict]: List of users with basic information
        """
        # Determine which organizations the user can access
        if organization_id:
            try:
                target_org = Organization.objects.get(id=organization_id)
                if not self.access_control.can_access_organization(requesting_user, target_org):
                    raise PermissionDenied("No access to this organization's users")
                accessible_orgs = [target_org]
            except Organization.DoesNotExist:
                raise ValidationError("Organization not found")
        else:
            accessible_orgs = self.access_control.get_accessible_organizations(requesting_user)
        
        # Get users from accessible organizations
        users_queryset = CustomUser.objects.filter(
            organization__in=accessible_orgs
        ).select_related('organization')
        
        # Apply filters
        if filters:
            if 'role' in filters:
                users_queryset = users_queryset.filter(role=filters['role'])
            
            if 'is_active' in filters:
                users_queryset = users_queryset.filter(is_active=filters['is_active'])
            
            if 'is_verified' in filters:
                users_queryset = users_queryset.filter(is_verified=filters['is_verified'])
            
            if 'is_publisher' in filters:
                users_queryset = users_queryset.filter(is_publisher=filters['is_publisher'])
            
            if 'search' in filters:
                search_term = filters['search'].lower()
                from django.db.models import Q
                users_queryset = users_queryset.filter(
                    Q(username__icontains=search_term) |
                    Q(first_name__icontains=search_term) |
                    Q(last_name__icontains=search_term) |
                    Q(email__icontains=search_term)
                )
        
        # Format user data
        users_list = []
        for user in users_queryset.order_by('username'):
            user_data = {
                'id': str(user.id),
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'organization': {
                    'id': str(user.organization.id),
                    'name': user.organization.name
                },
                'is_publisher': user.is_publisher,
                'is_verified': user.is_verified,
                'is_active': user.is_active,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'date_joined': user.date_joined.isoformat(),
                'can_manage': self.access_control.can_manage_user(requesting_user, user),
                'is_own_profile': requesting_user.id == user.id
            }
            
            # Add email for users that can be managed
            if user_data['can_manage'] or user_data['is_own_profile']:
                user_data['email'] = user.email
            
            users_list.append(user_data)
        
        return users_list
    
    def deactivate_user(self, deactivating_user: CustomUser,
                       user_id: str, reason: str = '') -> CustomUser:
        """
        Deactivate a user account.
        
        Args:
            deactivating_user: User performing the deactivation
            user_id: ID of user to deactivate
            reason: Reason for deactivation
            
        Returns:
            CustomUser: Deactivated user
            
        Raises:
            PermissionDenied: If deactivating user doesn't have permission
        """
        try:
            target_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError("User not found")
        
        # Check permissions
        if not self.access_control.can_manage_user(deactivating_user, target_user):
            raise PermissionDenied("No permission to deactivate this user")
        
        # Prevent self-deactivation
        if deactivating_user.id == target_user.id:
            raise ValidationError("Cannot deactivate your own account")
        
        # Prevent deactivating the last admin
        if target_user.role == 'BlueVisionAdmin':
            admin_count = CustomUser.objects.filter(
                role='BlueVisionAdmin', is_active=True
            ).count()
            if admin_count <= 1:
                raise ValidationError("Cannot deactivate the last BlueVision administrator")
        
        if not target_user.is_active:
            raise ValidationError("User is already deactivated")
        
        try:
            with transaction.atomic():
                # Deactivate user
                target_user.is_active = False
                target_user.save(update_fields=['is_active', 'updated_at'])
                
                # Deactivate all user sessions
                target_user.sessions.filter(is_active=True).update(is_active=False)
                
                # Log user deactivation
                AuthenticationLog.log_authentication_event(
                    user=deactivating_user,
                    action='user_deactivated',
                    ip_address='127.0.0.1',
                    user_agent='System',
                    success=True,
                    additional_data={
                        'target_user_id': str(target_user.id),
                        'target_username': target_user.username,
                        'reason': reason,
                        'organization': target_user.organization.name
                    }
                )
                
                logger.warning(
                    f"User {target_user.username} deactivated by {deactivating_user.username}. "
                    f"Reason: {reason}"
                )
                
                return target_user
                
        except Exception as e:
            logger.error(f"Error deactivating user: {str(e)}")
            raise ValidationError(f"Failed to deactivate user: {str(e)}")
    
    def delete_user(self, deleting_user: CustomUser, user_id: str, reason: str = '') -> bool:
        """
        Delete a user account (soft delete by deactivation).
        
        Args:
            deleting_user: User performing the deletion
            user_id: ID of user to delete
            reason: Reason for deletion
            
        Returns:
            bool: True if successful
            
        Raises:
            PermissionDenied: If deleting user doesn't have permission
        """
        # Use deactivate_user for soft delete
        self.deactivate_user(deleting_user, user_id, reason)
        return True
    
    def change_user_password(self, requesting_user: CustomUser,
                           user_id: str, new_password: str,
                           current_password: Optional[str] = None) -> bool:
        """
        Change a user's password with appropriate validation.
        
        Args:
            requesting_user: User requesting the password change
            user_id: ID of user whose password to change
            new_password: New password
            current_password: Current password (required for self-change)
            
        Returns:
            bool: True if password changed successfully
            
        Raises:
            PermissionDenied: If requesting user doesn't have permission
            ValidationError: If password validation fails
        """
        try:
            target_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError("User not found")
        
        is_self_change = requesting_user.id == target_user.id
        
        # Check permissions
        if not (is_self_change or self.access_control.can_manage_user(requesting_user, target_user)):
            raise PermissionDenied("No permission to change this user's password")
        
        # For self-password change, validate current password
        if is_self_change:
            if not current_password:
                raise ValidationError("Current password is required")
            
            if not target_user.check_password(current_password):
                raise ValidationError("Current password is incorrect")
        
        # Validate new password
        try:
            validate_password(new_password, target_user)
        except ValidationError as e:
            raise ValidationError(f"Password validation failed: {'; '.join(e.messages)}")
        
        try:
            with transaction.atomic():
                # Set new password
                target_user.set_password(new_password)
                target_user.password_changed_at = timezone.now()
                target_user.save(update_fields=['password', 'password_changed_at', 'updated_at'])
                
                # Invalidate all existing sessions except current one (for self-change)
                sessions_to_deactivate = target_user.sessions.filter(is_active=True)
                if is_self_change and hasattr(requesting_user, 'current_session_id'):
                    sessions_to_deactivate = sessions_to_deactivate.exclude(
                        id=requesting_user.current_session_id
                    )
                
                sessions_to_deactivate.update(is_active=False)
                
                # Log password change
                AuthenticationLog.log_authentication_event(
                    user=requesting_user,
                    action='password_change',
                    ip_address='127.0.0.1',
                    user_agent='System',
                    success=True,
                    additional_data={
                        'target_user_id': str(target_user.id),
                        'target_username': target_user.username,
                        'self_change': is_self_change,
                        'sessions_invalidated': sessions_to_deactivate.count()
                    }
                )
                
                logger.info(
                    f"Password changed for user {target_user.username} by {requesting_user.username}"
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            raise ValidationError(f"Failed to change password: {str(e)}")
    
    def get_user_statistics(self, requesting_user: CustomUser,
                          organization_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user statistics for organization or platform.
        
        Args:
            requesting_user: User requesting statistics
            organization_id: Specific organization (optional)
            
        Returns:
            dict: User statistics
        """
        if organization_id:
            try:
                organization = Organization.objects.get(id=organization_id)
                if not self.access_control.can_access_organization(requesting_user, organization):
                    raise PermissionDenied("No access to this organization")
                users_query = CustomUser.objects.filter(organization=organization)
                scope = f"organization '{organization.name}'"
            except Organization.DoesNotExist:
                raise ValidationError("Organization not found")
        else:
            # Platform-wide statistics (admin only)
            self.access_control.require_permission(requesting_user, 'can_view_system_analytics')
            users_query = CustomUser.objects.all()
            scope = "platform"
        
        stats = {
            'scope': scope,
            'total_users': users_query.count(),
            'active_users': users_query.filter(is_active=True).count(),
            'verified_users': users_query.filter(is_verified=True).count(),
            'publishers': users_query.filter(is_publisher=True).count(),
            'by_role': {},
            'recent_registrations': [],
            'login_activity': {}
        }
        
        try:
            # Get user breakdown by role
            from django.db.models import Count
            role_breakdown = users_query.values('role').annotate(
                count=Count('id')
            )
            
            for item in role_breakdown:
                stats['by_role'][item['role']] = item['count']
            
            # Get recent registrations (last 30 days)
            from datetime import timedelta
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_users = users_query.filter(
                date_joined__gte=thirty_days_ago
            ).order_by('-date_joined')[:10]
            
            for user in recent_users:
                stats['recent_registrations'].append({
                    'id': str(user.id),
                    'username': user.username,
                    'role': user.role,
                    'organization': user.organization.name,
                    'date_joined': user.date_joined.isoformat()
                })
            
            # Get login activity stats
            seven_days_ago = timezone.now() - timedelta(days=7)
            stats['login_activity'] = {
                'logged_in_last_7_days': users_query.filter(
                    last_login__gte=seven_days_ago
                ).count(),
                'never_logged_in': users_query.filter(
                    last_login__isnull=True
                ).count(),
                'locked_accounts': users_query.filter(
                    account_locked_until__gt=timezone.now()
                ).count()
            }
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
        
        return stats
from django.core.exceptions import ValidationError
from django.db import transaction
from typing import Dict, List, Optional
from ..models import CustomUser, AuthenticationLog
from ..factories.user_factory import UserFactory
from ..observers.auth_observers import auth_event_subject


class UserManagementService:
    """Service for user management operations"""
    
    def create_user(self, role: str, user_data: Dict, created_by: CustomUser) -> Dict:
        """
        Create a new user with specified role
        
        Args:
            role: User role to create
            user_data: User information
            created_by: User creating this user
            
        Returns:
            dict: Creation result with user info or error
        """
        try:
            # Add creation context
            user_data['created_from_ip'] = user_data.get('ip_address', '127.0.0.1')
            user_data['user_agent'] = user_data.get('user_agent', 'System')
            
            # Create user using factory
            user = UserFactory.create_user(role, user_data, created_by)
            
            # Notify observers
            auth_event_subject.notify_observers(
                event_type='user_created',
                user=user,
                event_data={
                    'ip_address': user_data.get('ip_address', '127.0.0.1'),
                    'user_agent': user_data.get('user_agent', 'System'),
                    'success': True,
                    'additional_data': {
                        'created_by': created_by.username,
                        'role': role,
                        'organization': user.organization.name if user.organization else None
                    }
                }
            )
            
            return {
                'success': True,
                'user': user,
                'message': f'User {user.username} created successfully'
            }
            
        except ValidationError as e:
            return {
                'success': False,
                'message': str(e),
                'errors': e.message_dict if hasattr(e, 'message_dict') else [str(e)]
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'User creation failed: {str(e)}'
            }
    
    def create_user_with_auto_password(self, role: str, user_data: Dict, 
                                     created_by: CustomUser) -> Dict:
        """
        Create user with auto-generated password
        
        Returns:
            dict: Creation result including generated password
        """
        try:
            user_data['created_from_ip'] = user_data.get('ip_address', '127.0.0.1')
            user_data['user_agent'] = user_data.get('user_agent', 'System')
            
            # Create user with auto-generated password
            user, password = UserFactory.create_user_with_auto_password(
                role, user_data, created_by
            )
            
            # Notify observers
            auth_event_subject.notify_observers(
                event_type='user_created',
                user=user,
                event_data={
                    'ip_address': user_data.get('ip_address', '127.0.0.1'),
                    'user_agent': user_data.get('user_agent', 'System'),
                    'success': True,
                    'additional_data': {
                        'created_by': created_by.username,
                        'role': role,
                        'auto_generate_password': True,
                        'organization': user.organization.name if user.organization else None
                    }
                }
            )
            
            return {
                'success': True,
                'user': user,
                'password': password,  # Return generated password for admin to share
                'message': f'User {user.username} created with auto-generated password'
            }
            
        except ValidationError as e:
            return {
                'success': False,
                'message': str(e),
                'errors': e.message_dict if hasattr(e, 'message_dict') else [str(e)]
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'User creation failed: {str(e)}'
            }
    
    def update_user(self, user: CustomUser, update_data: Dict, 
                   updated_by: CustomUser) -> Dict:
        """
        Update user information
        
        Args:
            user: User to update
            update_data: Fields to update
            updated_by: User performing the update
            
        Returns:
            dict: Update result
        """
        try:
            with transaction.atomic():
                # Track what fields are being updated
                updated_fields = []
                
                # Update allowed fields
                allowed_fields = [
                    'first_name', 'last_name', 'email', 'role', 
                    'is_publisher', 'is_verified', 'is_active'
                ]
                
                for field in allowed_fields:
                    if field in update_data:
                        old_value = getattr(user, field)
                        new_value = update_data[field]
                        
                        if old_value != new_value:
                            setattr(user, field, new_value)
                            updated_fields.append(f"{field}: {old_value} -> {new_value}")
                
                if updated_fields:
                    user.save()
                    
                    # Log user update
                    AuthenticationLog.log_authentication_event(
                        user=user,
                        action='user_updated',
                        ip_address=update_data.get('ip_address', '127.0.0.1'),
                        user_agent=update_data.get('user_agent', 'System'),
                        success=True,
                        additional_data={
                            'updated_by': updated_by.username,
                            'updated_fields': updated_fields
                        }
                    )
                    
                    return {
                        'success': True,
                        'user': user,
                        'updated_fields': updated_fields,
                        'message': 'User updated successfully'
                    }
                else:
                    return {
                        'success': True,
                        'user': user,
                        'message': 'No changes detected'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'message': f'User update failed: {str(e)}'
            }
    
    def delete_user(self, user: CustomUser, deleted_by: CustomUser, 
                   soft_delete: bool = True) -> Dict:
        """
        Delete user (soft delete by default)
        
        Args:
            user: User to delete
            deleted_by: User performing the deletion
            soft_delete: Whether to soft delete or hard delete
            
        Returns:
            dict: Deletion result
        """
        try:
            with transaction.atomic():
                if soft_delete:
                    # Soft delete - deactivate user
                    user.is_active = False
                    user.save(update_fields=['is_active'])
                    
                    # Deactivate all user sessions
                    user.sessions.filter(is_active=True).update(is_active=False)
                    
                    action = 'user_deactivated'
                    message = f'User {user.username} deactivated successfully'
                else:
                    # Hard delete - actually delete user record
                    username = user.username
                    user.delete()
                    
                    action = 'user_deleted'
                    message = f'User {username} deleted permanently'
                
                # Log deletion
                AuthenticationLog.log_authentication_event(
                    user=user if soft_delete else None,
                    action=action,
                    ip_address='127.0.0.1',  # System action
                    user_agent='System',
                    success=True,
                    additional_data={
                        'deleted_by': deleted_by.username,
                        'soft_delete': soft_delete,
                        'username': user.username if soft_delete else username
                    }
                )
                
                return {
                    'success': True,
                    'message': message,
                    'soft_delete': soft_delete
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'User deletion failed: {str(e)}'
            }
    
    def unlock_user_account(self, user: CustomUser, unlocked_by: CustomUser) -> Dict:
        """
        Unlock a locked user account
        
        Args:
            user: User to unlock
            unlocked_by: User performing the unlock
            
        Returns:
            dict: Unlock result
        """
        try:
            if not user.is_account_locked:
                return {
                    'success': True,
                    'message': 'Account is not locked'
                }
            
            user.unlock_account()
            
            # Log account unlock
            AuthenticationLog.log_authentication_event(
                user=user,
                action='account_unlocked',
                ip_address='127.0.0.1',  # System action
                user_agent='System',
                success=True,
                additional_data={
                    'unlocked_by': unlocked_by.username
                }
            )
            
            # Notify observers
            auth_event_subject.notify_observers(
                event_type='account_unlocked',
                user=user,
                event_data={
                    'ip_address': '127.0.0.1',
                    'user_agent': 'System',
                    'success': True,
                    'additional_data': {
                        'unlocked_by': unlocked_by.username
                    }
                }
            )
            
            return {
                'success': True,
                'message': 'Account unlocked successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Account unlock failed: {str(e)}'
            }
    
    def list_users(self, organization=None, role=None, is_active=None, 
                   page=1, page_size=50) -> Dict:
        """
        List users with optional filtering
        
        Args:
            organization: Filter by organization
            role: Filter by role
            is_active: Filter by active status
            page: Page number
            page_size: Items per page
            
        Returns:
            dict: Users list with pagination info
        """
        try:
            queryset = CustomUser.objects.all()
            
            # Apply filters
            if organization:
                queryset = queryset.filter(organization=organization)
            if role:
                queryset = queryset.filter(role=role)
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active)
            
            # Order by username
            queryset = queryset.order_by('username')
            
            # Pagination
            total_count = queryset.count()
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            users = queryset[start_index:end_index]
            
            return {
                'success': True,
                'users': list(users),
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size,
                    'has_next': end_index < total_count,
                    'has_previous': page > 1
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to list users: {str(e)}'
            }
    
    def get_user_audit_log(self, user: CustomUser, limit: int = 100) -> Dict:
        """
        Get authentication audit log for a user
        
        Args:
            user: User to get logs for
            limit: Maximum number of log entries
            
        Returns:
            dict: Audit log entries
        """
        try:
            logs = AuthenticationLog.objects.filter(
                user=user
            ).order_by('-timestamp')[:limit]
            
            return {
                'success': True,
                'logs': list(logs),
                'user': user,
                'total_entries': logs.count()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get audit log: {str(e)}'
            }
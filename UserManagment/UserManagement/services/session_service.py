from django.utils import timezone
from typing import Dict, List, Optional
from datetime import timedelta
from ..models import CustomUser, UserSession, AuthenticationLog


class SessionManagementService:
    """Service for managing user sessions and JWT tokens"""
    
    def get_user_sessions(self, user: CustomUser, active_only: bool = True) -> Dict:
        """
        Get all sessions for a user
        
        Args:
            user: User to get sessions for
            active_only: Whether to return only active sessions
            
        Returns:
            dict: List of user sessions
        """
        try:
            queryset = user.sessions.all()
            
            if active_only:
                queryset = queryset.filter(is_active=True)
            
            sessions = queryset.order_by('-created_at')
            
            session_data = []
            for session in sessions:
                session_data.append({
                    'id': str(session.id),
                    'ip_address': session.ip_address,
                    'device_info': session.device_info,
                    'is_trusted_device': session.is_trusted_device,
                    'created_at': session.created_at,
                    'last_activity': session.last_activity,
                    'expires_at': session.expires_at,
                    'is_active': session.is_active,
                    'is_expired': session.is_expired
                })
            
            return {
                'success': True,
                'sessions': session_data,
                'total_count': len(session_data),
                'active_count': len([s for s in session_data if s['is_active']])
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get user sessions: {str(e)}'
            }
    
    def terminate_session(self, user: CustomUser, session_id: str, 
                         terminated_by: Optional[CustomUser] = None) -> Dict:
        """
        Terminate a specific user session
        
        Args:
            user: User who owns the session
            session_id: ID of session to terminate
            terminated_by: User terminating the session (for audit)
            
        Returns:
            dict: Termination result
        """
        try:
            session = UserSession.objects.get(
                id=session_id,
                user=user,
                is_active=True
            )
            
            session.deactivate()
            
            # Log session termination
            AuthenticationLog.log_authentication_event(
                user=user,
                action='logout',
                ip_address='127.0.0.1',  # System action
                user_agent='System',
                success=True,
                additional_data={
                    'session_id': session_id,
                    'terminated_by': terminated_by.username if terminated_by else 'user',
                    'reason': 'manual_termination'
                }
            )
            
            return {
                'success': True,
                'message': 'Session terminated successfully',
                'session_id': session_id
            }
            
        except UserSession.DoesNotExist:
            return {
                'success': False,
                'message': 'Session not found or already inactive'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to terminate session: {str(e)}'
            }
    
    def terminate_all_sessions(self, user: CustomUser, exclude_session_id: str = None,
                              terminated_by: Optional[CustomUser] = None) -> Dict:
        """
        Terminate all active sessions for a user
        
        Args:
            user: User to terminate sessions for
            exclude_session_id: Keep this session active (current session)
            terminated_by: User terminating sessions
            
        Returns:
            dict: Termination result
        """
        try:
            queryset = user.sessions.filter(is_active=True)
            
            if exclude_session_id:
                queryset = queryset.exclude(id=exclude_session_id)
            
            session_count = queryset.count()
            session_ids = list(queryset.values_list('id', flat=True))
            
            queryset.update(is_active=False)
            
            # Log bulk session termination
            AuthenticationLog.log_authentication_event(
                user=user,
                action='logout',
                ip_address='127.0.0.1',  # System action
                user_agent='System',
                success=True,
                additional_data={
                    'sessions_terminated': session_count,
                    'excluded_session': exclude_session_id,
                    'terminated_by': terminated_by.username if terminated_by else 'user',
                    'reason': 'bulk_termination',
                    'session_ids': [str(sid) for sid in session_ids]
                }
            )
            
            return {
                'success': True,
                'message': f'Terminated {session_count} active sessions',
                'sessions_terminated': session_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to terminate sessions: {str(e)}'
            }
    
    def cleanup_expired_sessions(self, user: Optional[CustomUser] = None) -> Dict:
        """
        Clean up expired sessions
        
        Args:
            user: Specific user to clean up (None for all users)
            
        Returns:
            dict: Cleanup result
        """
        try:
            queryset = UserSession.objects.filter(
                expires_at__lt=timezone.now(),
                is_active=True
            )
            
            if user:
                queryset = queryset.filter(user=user)
            
            expired_count = queryset.count()
            
            # Log expired sessions before cleanup
            for session in queryset:
                AuthenticationLog.log_authentication_event(
                    user=session.user,
                    action='session_expired',
                    ip_address=session.ip_address,
                    user_agent='System',
                    success=True,
                    additional_data={
                        'session_id': str(session.id),
                        'expired_at': session.expires_at.isoformat(),
                        'reason': 'automatic_cleanup'
                    }
                )
            
            queryset.update(is_active=False)
            
            return {
                'success': True,
                'message': f'Cleaned up {expired_count} expired sessions',
                'sessions_cleaned': expired_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to cleanup expired sessions: {str(e)}'
            }
    
    def extend_session(self, user: CustomUser, session_id: str, 
                      hours: int = 1) -> Dict:
        """
        Extend session expiration time
        
        Args:
            user: User who owns the session
            session_id: ID of session to extend
            hours: Hours to extend the session
            
        Returns:
            dict: Extension result
        """
        try:
            session = UserSession.objects.get(
                id=session_id,
                user=user,
                is_active=True
            )
            
            if session.is_expired:
                return {
                    'success': False,
                    'message': 'Cannot extend expired session'
                }
            
            old_expires_at = session.expires_at
            session.extend_session(hours)
            
            # Log session extension
            AuthenticationLog.log_authentication_event(
                user=user,
                action='session_extended',
                ip_address='127.0.0.1',  # System action
                user_agent='System',
                success=True,
                additional_data={
                    'session_id': session_id,
                    'old_expires_at': old_expires_at.isoformat(),
                    'new_expires_at': session.expires_at.isoformat(),
                    'hours_extended': hours
                }
            )
            
            return {
                'success': True,
                'message': f'Session extended by {hours} hours',
                'session_id': session_id,
                'new_expires_at': session.expires_at.isoformat()
            }
            
        except UserSession.DoesNotExist:
            return {
                'success': False,
                'message': 'Session not found or inactive'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to extend session: {str(e)}'
            }
    
    def get_session_statistics(self, user: Optional[CustomUser] = None) -> Dict:
        """
        Get session statistics
        
        Args:
            user: Specific user (None for system-wide stats)
            
        Returns:
            dict: Session statistics
        """
        try:
            queryset = UserSession.objects.all()
            
            if user:
                queryset = queryset.filter(user=user)
            
            stats = {
                'total_sessions': queryset.count(),
                'active_sessions': queryset.filter(is_active=True).count(),
                'expired_sessions': queryset.filter(
                    expires_at__lt=timezone.now(),
                    is_active=True
                ).count(),
                'trusted_device_sessions': queryset.filter(
                    is_trusted_device=True,
                    is_active=True
                ).count()
            }
            
            # Recent activity (last 24 hours)
            recent_cutoff = timezone.now() - timedelta(hours=24)
            stats['recent_logins'] = queryset.filter(
                created_at__gte=recent_cutoff
            ).count()
            
            # Top IPs (if system-wide)
            if not user:
                top_ips = queryset.filter(
                    is_active=True
                ).values('ip_address').annotate(
                    session_count=models.Count('id')
                ).order_by('-session_count')[:10]
                
                stats['top_ips'] = list(top_ips)
            
            return {
                'success': True,
                'statistics': stats,
                'generated_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get session statistics: {str(e)}'
            }
    
    def manage_trusted_devices(self, user: CustomUser, action: str, 
                              device_fingerprint: str = None) -> Dict:
        """
        Manage user's trusted devices
        
        Args:
            user: User to manage trusted devices for
            action: 'add', 'remove', 'list', or 'clear_all'
            device_fingerprint: Device fingerprint (for add/remove)
            
        Returns:
            dict: Management result
        """
        try:
            if action == 'list':
                return {
                    'success': True,
                    'trusted_devices': user.trusted_devices,
                    'device_count': len(user.trusted_devices)
                }
            
            elif action == 'add':
                if not device_fingerprint:
                    return {
                        'success': False,
                        'message': 'Device fingerprint required for add action'
                    }
                
                if device_fingerprint not in user.trusted_devices:
                    user.trusted_devices.append(device_fingerprint)
                    user.save(update_fields=['trusted_devices'])
                    
                    AuthenticationLog.log_authentication_event(
                        user=user,
                        action='trusted_device_added',
                        ip_address='127.0.0.1',
                        user_agent='System',
                        success=True,
                        additional_data={'device_fingerprint': device_fingerprint}
                    )
                    
                    return {
                        'success': True,
                        'message': 'Device added to trusted devices'
                    }
                else:
                    return {
                        'success': True,
                        'message': 'Device already trusted'
                    }
            
            elif action == 'remove':
                if not device_fingerprint:
                    return {
                        'success': False,
                        'message': 'Device fingerprint required for remove action'
                    }
                
                if device_fingerprint in user.trusted_devices:
                    user.trusted_devices.remove(device_fingerprint)
                    user.save(update_fields=['trusted_devices'])
                    
                    AuthenticationLog.log_authentication_event(
                        user=user,
                        action='trusted_device_removed',
                        ip_address='127.0.0.1',
                        user_agent='System',
                        success=True,
                        additional_data={'device_fingerprint': device_fingerprint}
                    )
                    
                    return {
                        'success': True,
                        'message': 'Device removed from trusted devices'
                    }
                else:
                    return {
                        'success': True,
                        'message': 'Device was not in trusted devices'
                    }
            
            elif action == 'clear_all':
                device_count = len(user.trusted_devices)
                user.trusted_devices = []
                user.save(update_fields=['trusted_devices'])
                
                AuthenticationLog.log_authentication_event(
                    user=user,
                    action='trusted_devices_cleared',
                    ip_address='127.0.0.1',
                    user_agent='System',
                    success=True,
                    additional_data={'devices_cleared': device_count}
                )
                
                return {
                    'success': True,
                    'message': f'Cleared {device_count} trusted devices'
                }
            
            else:
                return {
                    'success': False,
                    'message': 'Invalid action. Use: add, remove, list, or clear_all'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to manage trusted devices: {str(e)}'
            }
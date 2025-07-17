from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ValidationError, PermissionDenied
from ..services.user_service import UserService
from ..services.organization_service import OrganizationService
from ..services.trust_aware_service import TrustAwareService
from ..services.access_control_service import AccessControlService
from ...services.audit_service import AuditService
from ..models import CustomUser, AuthenticationLog
import logging

logger = logging.getLogger(__name__)


class AdminViewSet(GenericViewSet):
    """
    Administrative API endpoints for BlueVision administrators.
    """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.user_service = UserService()
            self.org_service = OrganizationService()
            self.trust_service = TrustAwareService()
            self.access_control = AccessControlService()
            self.audit_service = AuditService()
        except Exception as e:
            # Handle service initialization errors gracefully
            logger.error(f"Failed to initialize admin services: {str(e)}")
            self.user_service = None
            self.org_service = None
            self.trust_service = None
            self.access_control = None
            self.audit_service = None
    
    def _check_admin_permission(self, user, permission):
        """Check if user has admin permission"""
        if not self.access_control.has_permission(user, permission):
            raise PermissionDenied(f"Admin permission required: {permission}")
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get comprehensive admin dashboard data."""
        try:
            # Check if services are available
            if not self.user_service or not self.org_service:
                return Response({
                    'success': False,
                    'message': 'Failed to load admin dashboard'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            self._check_admin_permission(request.user, 'can_view_system_analytics')
            
            # Get platform statistics
            user_stats = self.user_service.get_user_statistics(request.user)
            org_stats = self.org_service.get_organization_statistics(request.user)
            
            # Get recent activities
            recent_logs = AuthenticationLog.objects.select_related('user').order_by('-timestamp')[:20]
            recent_activities = []
            
            for log in recent_logs:
                recent_activities.append({
                    'id': str(log.id),
                    'action': log.action,
                    'user': log.user.username if log.user else 'System',
                    'ip_address': log.ip_address,
                    'success': log.success,
                    'timestamp': log.timestamp.isoformat(),
                    'additional_data': log.additional_data
                })
            
            dashboard_data = {
                'user_statistics': user_stats,
                'organization_statistics': org_stats,
                'recent_activities': recent_activities,
                'system_health': {
                    'total_active_sessions': self._get_active_sessions_count(),
                    'failed_logins_last_24h': self._get_failed_logins_count(),
                    'locked_accounts': self._get_locked_accounts_count()
                }
            }
            
            return Response({
                'success': True,
                'data': dashboard_data
            }, status=status.HTTP_200_OK)
        
        except PermissionDenied as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Admin dashboard error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to load admin dashboard'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def system_health(self, request):
        """Get detailed system health information."""
        try:
            self._check_admin_permission(request.user, 'can_view_system_analytics')
            
            health_data = {
                'database': {
                    'status': 'healthy',  # Would implement actual health checks
                    'total_users': CustomUser.objects.count(),
                    'active_users': CustomUser.objects.filter(is_active=True).count(),
                    'total_organizations': self.org_service.get_organization_statistics(request.user)['total_organizations']
                },
                'authentication': {
                    'active_sessions': self._get_active_sessions_count(),
                    'failed_logins_24h': self._get_failed_logins_count(),
                    'locked_accounts': self._get_locked_accounts_count(),
                    'average_session_duration': self._get_average_session_duration()
                },
                'trust_system': {
                    'total_relationships': self._get_total_trust_relationships(),
                    'active_relationships': self._get_active_trust_relationships(),
                    'pending_approvals': self._get_pending_trust_approvals()
                }
            }
            
            return Response({
                'success': True,
                'data': health_data
            }, status=status.HTTP_200_OK)
        
        except PermissionDenied as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"System health error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve system health'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def audit_logs(self, request):
        """
        Get audit logs with filtering.
        
        Query parameters:
        - action: Filter by action type
        - user_id: Filter by user
        - success: Filter by success status
        - start_date: Start date filter
        - end_date: End date filter
        - limit: Number of results (default 100, max 1000)
        """
        try:
            # Check if services are available
            if not self.audit_service:
                return Response({
                    'success': False,
                    'message': 'Audit service unavailable'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            self._check_admin_permission(request.user, 'can_view_system_analytics')
            
            # Get query parameters
            action = request.query_params.get('action')
            user_id = request.query_params.get('user_id')
            success = request.query_params.get('success')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            limit = min(int(request.query_params.get('limit', 100)), 1000)
            
            # Build query
            logs_query = AuthenticationLog.objects.select_related('user').order_by('-timestamp')
            
            if action:
                logs_query = logs_query.filter(action=action)
            if user_id:
                try:
                    logs_query = logs_query.filter(user_id=user_id)
                except Exception:
                    # Skip invalid user_id values
                    pass
            if success is not None:
                success_bool = success.lower() == 'true'
                logs_query = logs_query.filter(success=success_bool)
            if start_date:
                from django.utils.dateparse import parse_datetime
                try:
                    parsed_start = parse_datetime(start_date)
                    if parsed_start:
                        logs_query = logs_query.filter(timestamp__gte=parsed_start)
                except Exception:
                    # Skip invalid date format
                    pass
            if end_date:
                from django.utils.dateparse import parse_datetime
                try:
                    parsed_end = parse_datetime(end_date)
                    if parsed_end:
                        logs_query = logs_query.filter(timestamp__lte=parsed_end)
                except Exception:
                    # Skip invalid date format
                    pass
            
            logs = logs_query[:limit]
            
            audit_data = []
            for log in logs:
                audit_data.append({
                    'id': str(log.id),
                    'action': log.action,
                    'user': {
                        'id': str(log.user.id) if log.user else None,
                        'username': log.user.username if log.user else None,
                        'organization': log.user.organization.name if log.user and log.user.organization else None
                    },
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent,
                    'success': log.success,
                    'failure_reason': log.failure_reason,
                    'timestamp': log.timestamp.isoformat(),
                    'additional_data': log.additional_data
                })
            
            return Response({
                'success': True,
                'data': {
                    'logs': audit_data,
                    'total_returned': len(audit_data),
                    'filters_applied': {
                        'action': action,
                        'user_id': user_id,
                        'success': success,
                        'start_date': start_date,
                        'end_date': end_date,
                        'limit': limit
                    }
                }
            }, status=status.HTTP_200_OK)
        
        except PermissionDenied as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Audit logs error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve audit logs'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def unlock_account(self, request, pk=None):
        """Unlock a user account."""
        try:
            self._check_admin_permission(request.user, 'can_manage_all_users')
            
            try:
                user = CustomUser.objects.get(id=pk)
            except CustomUser.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            user.unlock_account()
            
            # Log the unlock action
            AuthenticationLog.log_authentication_event(
                user=request.user,
                action='account_unlocked',
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', 'API'),
                success=True,
                additional_data={
                    'target_user_id': str(user.id),
                    'target_username': user.username,
                    'unlocked_by_admin': True
                }
            )
            
            return Response({
                'success': True,
                'data': {
                    'message': f'Account {user.username} unlocked successfully',
                    'user_id': str(user.id)
                }
            }, status=status.HTTP_200_OK)
        
        except PermissionDenied as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Unlock account error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to unlock account'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def cleanup_expired_sessions(self, request):
        """Clean up expired user sessions."""
        try:
            self._check_admin_permission(request.user, 'can_manage_system_settings')
            
            from ..services.auth_service import AuthenticationService
            auth_service = AuthenticationService()
            
            cleaned_count = auth_service.cleanup_expired_sessions()
            
            return Response({
                'success': True,
                'data': {
                    'message': f'Cleaned up {cleaned_count} expired sessions',
                    'sessions_cleaned': cleaned_count
                }
            }, status=status.HTTP_200_OK)
        
        except PermissionDenied as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Cleanup sessions error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to cleanup sessions'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def trust_overview(self, request):
        """Get trust system overview for administrators."""
        try:
            self._check_admin_permission(request.user, 'can_view_system_analytics')
            
            from core.trust.models import TrustRelationship, TrustGroup, TrustLog
            
            # Get trust statistics
            trust_stats = {
                'relationships': {
                    'total': TrustRelationship.objects.count(),
                    'active': TrustRelationship.objects.filter(status='active', is_active=True).count(),
                    'pending': TrustRelationship.objects.filter(status='pending').count(),
                    'revoked': TrustRelationship.objects.filter(status='revoked').count()
                },
                'groups': {
                    'total': TrustGroup.objects.count(),
                    'active': TrustGroup.objects.filter(is_active=True).count(),
                    'public': TrustGroup.objects.filter(is_public=True, is_active=True).count()
                },
                'recent_activities': []
            }
            
            # Get recent trust activities
            recent_trust_logs = TrustLog.objects.select_related(
                'user', 'trust_relationship', 'trust_group'
            ).order_by('-timestamp')[:10]
            
            for log in recent_trust_logs:
                trust_stats['recent_activities'].append({
                    'id': str(log.id),
                    'action': log.action,
                    'user': log.user.username if log.user else 'System',
                    'success': log.success,
                    'timestamp': log.timestamp.isoformat(),
                    'details': log.details
                })
            
            return Response({
                'success': True,
                'data': trust_stats
            }, status=status.HTTP_200_OK)
        
        except PermissionDenied as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Trust overview error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve trust overview'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_active_sessions_count(self):
        """Get count of active user sessions"""
        from ..models import UserSession
        return UserSession.objects.filter(is_active=True).count()
    
    def _get_failed_logins_count(self):
        """Get count of failed logins in last 24 hours"""
        from django.utils import timezone
        from datetime import timedelta
        
        yesterday = timezone.now() - timedelta(days=1)
        return AuthenticationLog.objects.filter(
            action='login_failure',
            timestamp__gte=yesterday
        ).count()
    
    def _get_locked_accounts_count(self):
        """Get count of currently locked accounts"""
        from django.utils import timezone
        return CustomUser.objects.filter(
            account_locked_until__gt=timezone.now()
        ).count()
    
    def _get_average_session_duration(self):
        """Get average session duration in minutes"""
        # Placeholder implementation
        return 45
    
    def _get_total_trust_relationships(self):
        """Get total trust relationships count"""
        try:
            from core.trust.models import TrustRelationship
            return TrustRelationship.objects.count()
        except:
            return 0
    
    def _get_active_trust_relationships(self):
        """Get active trust relationships count"""
        try:
            from core.trust.models import TrustRelationship
            return TrustRelationship.objects.filter(
                status='active', is_active=True
            ).count()
        except:
            return 0
    
    def _get_pending_trust_approvals(self):
        """Get pending trust approvals count"""
        try:
            from core.trust.models import TrustRelationship
            return TrustRelationship.objects.filter(status='pending').count()
        except:
            return 0
    
    @action(detail=False, methods=['get'])
    def comprehensive_audit_logs(self, request):
        """
        Get comprehensive audit logs from both user management and trust systems.
        
        Query parameters:
        - action: Filter by action type
        - user_id: Filter by user
        - success: Filter by success status
        - start_date: Start date filter (ISO format)
        - end_date: End date filter (ISO format)
        - limit: Number of results (default 100, max 1000)
        - offset: Offset for pagination
        - include_trust_logs: Include trust logs (default true)
        - include_user_logs: Include user logs (default true)
        - severity: Filter by security severity (high, medium, low, all)
        """
        try:
            self._check_admin_permission(request.user, 'can_view_system_analytics')
            
            # Parse query parameters
            filters = {}
            
            action = request.query_params.get('action')
            if action:
                filters['action'] = action
            
            user_id = request.query_params.get('user_id')
            if user_id:
                filters['user_id'] = user_id
            
            success = request.query_params.get('success')
            if success is not None:
                filters['success'] = success.lower() == 'true'
            
            start_date = request.query_params.get('start_date')
            if start_date:
                from django.utils.dateparse import parse_datetime
                filters['start_date'] = parse_datetime(start_date)
            
            end_date = request.query_params.get('end_date')
            if end_date:
                from django.utils.dateparse import parse_datetime
                filters['end_date'] = parse_datetime(end_date)
            
            limit = min(int(request.query_params.get('limit', 100)), 1000)
            offset = int(request.query_params.get('offset', 0))
            
            include_trust_logs = request.query_params.get('include_trust_logs', 'true').lower() == 'true'
            include_user_logs = request.query_params.get('include_user_logs', 'true').lower() == 'true'
            
            # Get audit logs
            audit_data = self.audit_service.get_audit_logs(
                filters=filters,
                limit=limit,
                offset=offset,
                include_trust_logs=include_trust_logs,
                include_user_logs=include_user_logs
            )
            
            return Response({
                'success': True,
                'data': audit_data
            }, status=status.HTTP_200_OK)
        
        except PermissionDenied as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Comprehensive audit logs error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve comprehensive audit logs'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def user_activity_summary(self, request, pk=None):
        """
        Get activity summary for a specific user.
        
        Query parameters:
        - days: Number of days to look back (default 30)
        """
        try:
            self._check_admin_permission(request.user, 'can_view_system_analytics')
            
            try:
                target_user = CustomUser.objects.get(id=pk)
            except CustomUser.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            days = int(request.query_params.get('days', 30))
            
            activity_summary = self.audit_service.get_user_activity_summary(
                user=target_user,
                days=days
            )
            
            return Response({
                'success': True,
                'data': activity_summary
            }, status=status.HTTP_200_OK)
        
        except PermissionDenied as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"User activity summary error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve user activity summary'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def security_events(self, request):
        """
        Get security-related events for monitoring.
        
        Query parameters:
        - severity: Security severity level (high, medium, low, all) - default 'all'
        - days: Number of days to look back (default 7)
        """
        try:
            self._check_admin_permission(request.user, 'can_view_system_analytics')
            
            severity = request.query_params.get('severity', 'all')
            days = int(request.query_params.get('days', 7))
            
            security_events = self.audit_service.get_security_events(
                severity=severity,
                days=days
            )
            
            return Response({
                'success': True,
                'data': {
                    'events': security_events,
                    'total_count': len(security_events),
                    'severity_filter': severity,
                    'days_lookback': days
                }
            }, status=status.HTTP_200_OK)
        
        except PermissionDenied as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Security events error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve security events'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def audit_statistics(self, request):
        """
        Get audit statistics and metrics.
        
        Query parameters:
        - days: Number of days to look back (default 30)
        """
        try:
            self._check_admin_permission(request.user, 'can_view_system_analytics')
            
            days = int(request.query_params.get('days', 30))
            
            from datetime import timedelta
            from django.utils import timezone
            from django.db.models import Count
            
            start_date = timezone.now() - timedelta(days=days)
            
            # Get user log statistics
            user_stats = AuthenticationLog.objects.filter(
                timestamp__gte=start_date
            ).values('action').annotate(count=Count('id'))
            
            # Get trust log statistics
            from core.trust.models import TrustLog
            trust_stats = TrustLog.objects.filter(
                timestamp__gte=start_date
            ).values('action').annotate(count=Count('id'))
            
            # Get failure statistics
            failure_stats = AuthenticationLog.objects.filter(
                timestamp__gte=start_date,
                success=False
            ).values('action').annotate(count=Count('id'))
            
            # Get top active users
            top_users = AuthenticationLog.objects.filter(
                timestamp__gte=start_date,
                user__isnull=False
            ).values('user__username').annotate(
                activity_count=Count('id')
            ).order_by('-activity_count')[:10]
            
            statistics = {
                'analysis_period_days': days,
                'user_activity_breakdown': list(user_stats),
                'trust_activity_breakdown': list(trust_stats),
                'failure_breakdown': list(failure_stats),
                'top_active_users': list(top_users),
                'total_user_logs': AuthenticationLog.objects.filter(timestamp__gte=start_date).count(),
                'total_trust_logs': TrustLog.objects.filter(timestamp__gte=start_date).count(),
                'total_failed_attempts': AuthenticationLog.objects.filter(
                    timestamp__gte=start_date, success=False
                ).count()
            }
            
            return Response({
                'success': True,
                'data': statistics
            }, status=status.HTTP_200_OK)
        
        except PermissionDenied as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Audit statistics error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve audit statistics'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from ..models import CustomUser, UserSession
from ..serializers import (
    UserProfileSerializer, UserSessionSerializer, 
    OrganizationSerializer
)
from ..permissions import IsVerifiedUser


class UserSessionListView(APIView):
    """User's own session management"""
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    
    def get(self, request):
        """Get user's active sessions"""
        sessions = UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-last_activity')
        
        serializer = UserSessionSerializer(sessions, many=True)
        
        return Response({
            'sessions': serializer.data,
            'total_count': sessions.count()
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, session_id):
        """Terminate specific session"""
        try:
            session = UserSession.objects.get(
                id=session_id,
                user=request.user,
                is_active=True
            )
            
            session.deactivate()
            
            return Response({
                'success': True,
                'message': 'Session terminated successfully'
            }, status=status.HTTP_200_OK)
            
        except UserSession.DoesNotExist:
            return Response({
                'error': 'session_not_found',
                'message': 'Session not found or already inactive'
            }, status=status.HTTP_404_NOT_FOUND)


class UserDashboardView(APIView):
    """User dashboard with overview information"""
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    
    def get(self, request):
        """Get user dashboard data"""
        user = request.user
        
        # Get user's active sessions
        active_sessions = UserSession.objects.filter(
            user=user,
            is_active=True
        ).count()
        
        # Get recent authentication logs
        recent_logins = user.auth_logs.filter(
            action='login_success'
        ).order_by('-timestamp')[:5]
        
        # Get user statistics
        stats = {
            'total_logins': user.auth_logs.filter(action='login_success').count(),
            'failed_attempts': user.failed_login_attempts,
            'active_sessions': active_sessions,
            'trusted_devices': len(user.trusted_devices),
            'account_created': user.date_joined,
            'last_login': user.last_login,
            'two_factor_enabled': user.two_factor_enabled
        }
        
        # Get organization info
        org_data = None
        if user.organization:
            org_data = {
                'id': str(user.organization.id),
                'name': user.organization.name,
                'description': getattr(user.organization, 'description', ''),
                'user_count': CustomUser.objects.filter(
                    organization=user.organization,
                    is_active=True
                ).count()
            }
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'stats': stats,
            'organization': org_data,
            'recent_logins': [
                {
                    'timestamp': log.timestamp,
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent
                }
                for log in recent_logins
            ]
        }, status=status.HTTP_200_OK)


class UserSearchView(APIView):
    """Search users within organization"""
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    
    def get(self, request):
        """Search users"""
        query = request.query_params.get('q', '').strip()
        
        if not query or len(query) < 2:
            return Response({
                'error': 'invalid_query',
                'message': 'Search query must be at least 2 characters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Base queryset - users in same organization
        queryset = CustomUser.objects.filter(
            organization=request.user.organization,
            is_active=True,
            is_verified=True
        ).exclude(id=request.user.id)
        
        # Apply search filters
        queryset = queryset.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        
        # Limit results
        queryset = queryset[:20]
        
        # Serialize results
        results = []
        for user in queryset:
            results.append({
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'role': user.role,
                'is_publisher': user.is_publisher
            })
        
        return Response({
            'results': results,
            'count': len(results),
            'query': query
        }, status=status.HTTP_200_OK)


class UserActivityView(APIView):
    """User activity and audit trail"""
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    
    def get(self, request):
        """Get user's activity logs"""
        # Get authentication logs
        auth_logs = request.user.auth_logs.order_by('-timestamp')[:50]
        
        # Apply filters
        action_filter = request.query_params.get('action')
        if action_filter:
            auth_logs = auth_logs.filter(action=action_filter)
        
        success_filter = request.query_params.get('success')
        if success_filter is not None:
            success_bool = success_filter.lower() == 'true'
            auth_logs = auth_logs.filter(success=success_bool)
        
        # Serialize logs
        activity_data = []
        for log in auth_logs:
            activity_data.append({
                'id': str(log.id),
                'action': log.action,
                'timestamp': log.timestamp,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent,
                'success': log.success,
                'failure_reason': log.failure_reason,
                'additional_data': log.additional_data
            })
        
        # Get available actions for filtering
        available_actions = request.user.auth_logs.values_list(
            'action', flat=True
        ).distinct().order_by('action')
        
        return Response({
            'activity': activity_data,
            'available_actions': list(available_actions),
            'total_count': request.user.auth_logs.count()
        }, status=status.HTTP_200_OK)


class UserStatsView(APIView):
    """User statistics and analytics"""
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    
    def get(self, request):
        """Get user statistics"""
        user = request.user
        
        # Login statistics
        login_stats = {
            'total_logins': user.auth_logs.filter(action='login_success').count(),
            'failed_logins': user.auth_logs.filter(action='login_failed').count(),
            'password_changes': user.auth_logs.filter(action='password_changed').count(),
            'password_resets': user.auth_logs.filter(action='password_reset').count()
        }
        
        # Recent activity (last 30 days)
        from django.utils import timezone
        from datetime import timedelta
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_activity = user.auth_logs.filter(
            timestamp__gte=thirty_days_ago
        ).count()
        
        # Security statistics
        security_stats = {
            'account_locked_times': user.auth_logs.filter(action='account_locked').count(),
            'trusted_devices_count': len(user.trusted_devices),
            'two_factor_enabled': user.two_factor_enabled,
            'current_failed_attempts': user.failed_login_attempts,
            'is_account_locked': user.is_account_locked
        }
        
        # Session statistics
        session_stats = {
            'active_sessions': UserSession.objects.filter(
                user=user,
                is_active=True
            ).count(),
            'total_sessions': UserSession.objects.filter(user=user).count()
        }
        
        return Response({
            'login_stats': login_stats,
            'security_stats': security_stats,
            'session_stats': session_stats,
            'recent_activity_count': recent_activity,
            'account_age_days': (timezone.now() - user.date_joined).days
        }, status=status.HTTP_200_OK)


class OrganizationUsersView(APIView):
    """View users in the same organization"""
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    
    def get(self, request):
        """Get users in same organization"""
        if not request.user.organization:
            return Response({
                'error': 'no_organization',
                'message': 'User is not associated with an organization'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get users in same organization
        org_users = CustomUser.objects.filter(
            organization=request.user.organization,
            is_active=True,
            is_verified=True
        ).exclude(id=request.user.id).order_by('username')
        
        # Apply role filter if provided
        role_filter = request.query_params.get('role')
        if role_filter:
            org_users = org_users.filter(role=role_filter)
        
        # Serialize users
        users_data = []
        for user in org_users:
            # Only show limited info for privacy
            users_data.append({
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'role': user.role,
                'is_publisher': user.is_publisher,
                'date_joined': user.date_joined,
                'last_login': user.last_login
            })
        
        # Get organization statistics
        org_stats = {
            'total_users': CustomUser.objects.filter(
                organization=request.user.organization,
                is_active=True
            ).count(),
            'verified_users': CustomUser.objects.filter(
                organization=request.user.organization,
                is_active=True,
                is_verified=True
            ).count(),
            'publishers': CustomUser.objects.filter(
                organization=request.user.organization,
                is_active=True,
                is_publisher=True
            ).count(),
            'admins': CustomUser.objects.filter(
                organization=request.user.organization,
                is_active=True,
                role__in=['admin', 'system_admin']
            ).count()
        }
        
        return Response({
            'users': users_data,
            'organization': {
                'id': str(request.user.organization.id),
                'name': request.user.organization.name
            },
            'stats': org_stats,
            'total_count': len(users_data)
        }, status=status.HTTP_200_OK)
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404

from ..models import CustomUser, UserSession
from ..serializers import (
    UserProfileSerializer, UserSessionSerializer, 
    OrganizationSerializer, AdminUserUpdateSerializer
)
from ..permissions import IsVerifiedUser, IsOrganizationAdmin


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


class UserListView(APIView):
    """General user list view - handles pagination, search, filtering"""
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    
    def get(self, request):
        """Get list of users based on permissions"""
        # Base queryset
        if request.user.role in ['system_admin', 'admin']:
            # Admins can see all users in their organization or all if system admin
            if request.user.role == 'system_admin':
                queryset = CustomUser.objects.filter(is_active=True)
            else:
                queryset = CustomUser.objects.filter(
                    organization=request.user.organization,
                    is_active=True
                )
        elif request.user.is_publisher:
            # Publishers can see users in their organization
            queryset = CustomUser.objects.filter(
                organization=request.user.organization,
                is_active=True
            )
        else:
            # Viewers can only see limited user info or just themselves
            queryset = CustomUser.objects.filter(
                id=request.user.id,
                is_active=True
            )
        
        # Apply search filter
        search = request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Apply role filter
        role = request.GET.get('role', '')
        if role:
            queryset = queryset.filter(role=role)
        
        # Apply pagination
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 20)
        
        try:
            page = int(page)
            page_size = int(page_size)
        except (ValueError, TypeError):
            page = 1
            page_size = 20
        
        # Calculate pagination
        total_count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        users = queryset[start:end]
        
        # Serialize users
        serializer = UserProfileSerializer(users, many=True)
        
        return Response({
            'users': serializer.data,
            'pagination': {
                'count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    """User detail view - get, update, delete specific user"""
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    
    def _can_access_user(self, request_user, target_user):
        """Check if request user can access target user"""
        # Users can always access their own profile
        if request_user.id == target_user.id:
            return True
            
        # System admins can access anyone
        if request_user.role == 'system_admin':
            return True
            
        # Admins can access users in their organization
        if request_user.role == 'admin' and request_user.organization == target_user.organization:
            return True
            
        # Publishers can view users in their organization
        if request_user.is_publisher and request_user.organization == target_user.organization:
            return True
            
        return False
    
    def _can_modify_user(self, request_user, target_user):
        """Check if request user can modify target user"""
        # Users can modify their own profile (limited)
        if request_user.id == target_user.id:
            return True
            
        # System admins can modify anyone
        if request_user.role == 'system_admin':
            return True
            
        # Admins can modify users in their organization (except other admins)
        if (request_user.role == 'admin' and 
            request_user.organization == target_user.organization and
            target_user.role not in ['admin', 'system_admin']):
            return True
            
        return False
    
    def get(self, request, user_id):
        """Get user details"""
        try:
            user = CustomUser.objects.get(id=user_id, is_active=True)
        except CustomUser.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not self._can_access_user(request.user, user):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, user_id):
        """Update user"""
        try:
            user = CustomUser.objects.get(id=user_id, is_active=True)
        except CustomUser.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not self._can_modify_user(request.user, user):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Use appropriate serializer based on permissions
        if request.user.role in ['system_admin', 'admin']:
            serializer = AdminUserUpdateSerializer(user, data=request.data)
        else:
            serializer = UserProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, user_id):
        """Partial update user"""
        try:
            user = CustomUser.objects.get(id=user_id, is_active=True)
        except CustomUser.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not self._can_modify_user(request.user, user):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Use appropriate serializer based on permissions
        if request.user.role in ['system_admin', 'admin']:
            serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
        else:
            serializer = UserProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_id):
        """Delete/deactivate user"""
        try:
            user = CustomUser.objects.get(id=user_id, is_active=True)
        except CustomUser.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Users cannot delete their own account
        if request.user.id == user.id:
            return Response({
                'error': 'Cannot delete your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Only admins can delete users
        if not request.user.role in ['system_admin', 'admin']:
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # System admins can delete anyone, regular admins only in their org
        if (request.user.role == 'admin' and 
            request.user.organization != user.organization):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Deactivate instead of delete
        user.is_active = False
        user.save()
        
        return Response({
            'success': True,
            'message': 'User deactivated successfully'
        }, status=status.HTTP_200_OK)
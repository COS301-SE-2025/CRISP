from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator

from ..models import CustomUser, AuthenticationLog, UserSession
from ..serializers import (
    AdminUserListSerializer, AdminUserCreateSerializer, AdminUserUpdateSerializer,
    AuthenticationLogSerializer, UserSessionSerializer, OrganizationSerializer
)
from ..factories.user_factory import UserFactory
from ..permissions import IsSystemAdmin, IsOrganizationAdmin


class AdminUserListView(APIView):
    """Admin user management - list and create users"""
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    
    def get(self, request):
        """List users with filtering and pagination"""
        # Filter users based on admin permissions
        if request.user.role == 'BlueVisionAdmin':
            # System admins can see all users
            queryset = CustomUser.objects.all()
        else:
            # Organization admins can only see users in their organization
            queryset = CustomUser.objects.filter(organization=request.user.organization)
        
        # Apply filters
        role_filter = request.query_params.get('role')
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        
        is_active_filter = request.query_params.get('is_active')
        if is_active_filter is not None:
            is_active = is_active_filter.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        
        is_verified_filter = request.query_params.get('is_verified')
        if is_verified_filter is not None:
            is_verified = is_verified_filter.lower() == 'true'
            queryset = queryset.filter(is_verified=is_verified)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Order by
        order_by = request.query_params.get('order_by', '-created_at')
        queryset = queryset.order_by(order_by)
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        serializer = AdminUserListSerializer(page_obj.object_list, many=True)
        
        return Response({
            'users': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Create new user"""
        serializer = AdminUserCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Extract data
                user_data = serializer.validated_data.copy()
                role = user_data.get('role', 'viewer')
                auto_generate_password = user_data.pop('auto_generate_password', False)
                
                # Add request context
                user_data['created_from_ip'] = self._get_client_ip(request)
                user_data['user_agent'] = request.META.get('HTTP_USER_AGENT', 'Admin Interface')
                
                # Create user using factory
                if auto_generate_password:
                    user, generated_password = UserFactory.create_user_with_auto_password(
                        role=role,
                        user_data=user_data,
                        created_by=request.user
                    )
                    
                    return Response({
                        'success': True,
                        'user': AdminUserListSerializer(user).data,
                        'generated_password': generated_password,
                        'message': 'User created successfully with auto-generated password'
                    }, status=status.HTTP_201_CREATED)
                else:
                    user = UserFactory.create_user(
                        role=role,
                        user_data=user_data,
                        created_by=request.user
                    )
                    
                    return Response({
                        'success': True,
                        'user': AdminUserListSerializer(user).data,
                        'message': 'User created successfully'
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                return Response({
                    'error': 'user_creation_failed',
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class AdminUserDetailView(APIView):
    """Admin user management - get, update, delete specific user"""
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    
    def get_user(self, request, user_id):
        """Get user if admin has permission to access"""
        try:
            user = CustomUser.objects.get(id=user_id)
            
            # Check permissions
            if request.user.role == 'BlueVisionAdmin':
                return user
            elif request.user.role == 'admin' and user.organization == request.user.organization:
                return user
            else:
                return None
                
        except CustomUser.DoesNotExist:
            return None
    
    def get(self, request, user_id):
        """Get user details"""
        user = self.get_user(request, user_id)
        
        if not user:
            return Response({
                'error': 'user_not_found',
                'message': 'User not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AdminUserListSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, user_id):
        """Update user"""
        user = self.get_user(request, user_id)
        
        if not user:
            return Response({
                'error': 'user_not_found',
                'message': 'User not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Check if user can update this role
            new_role = serializer.validated_data.get('role')
            if new_role and not self._can_assign_role(request.user, new_role):
                return Response({
                    'error': 'insufficient_permissions',
                    'message': 'Insufficient permissions to assign this role'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer.save()
            
            # Log user update
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', 'Admin Interface')
            
            AuthenticationLog.log_authentication_event(
                user=user,
                action='user_updated',
                ip_address=ip_address,
                user_agent=user_agent,
                success=True,
                additional_data={
                    'updated_by': request.user.username,
                    'fields_updated': list(request.data.keys())
                }
            )
            
            return Response({
                'success': True,
                'user': AdminUserListSerializer(user).data,
                'message': 'User updated successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_id):
        """Delete user (soft delete)"""
        user = self.get_user(request, user_id)
        
        if not user:
            return Response({
                'error': 'user_not_found',
                'message': 'User not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Prevent self-deletion
        if user.id == request.user.id:
            return Response({
                'error': 'cannot_delete_self',
                'message': 'Cannot delete your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user can delete this role
        if not self._can_delete_user(request.user, user):
            return Response({
                'error': 'insufficient_permissions',
                'message': 'Insufficient permissions to delete this user'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Soft delete
        user.is_active = False
        user.save(update_fields=['is_active'])
        
        # Deactivate all user sessions
        UserSession.objects.filter(user=user, is_active=True).update(is_active=False)
        
        # Log user deletion
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Admin Interface')
        
        AuthenticationLog.log_authentication_event(
            user=user,
            action='user_deleted',
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            additional_data={
                'deleted_by': request.user.username,
                'soft_delete': True
            }
        )
        
        return Response({
            'success': True,
            'message': 'User deleted successfully'
        }, status=status.HTTP_200_OK)
    
    def _can_assign_role(self, admin_user, role):
        """Check if admin can assign this role"""
        if admin_user.role == 'system_admin':
            return True
        elif admin_user.role == 'admin':
            # Regular admins can assign viewer, analyst, publisher roles
            return role in ['viewer', 'analyst', 'publisher']
        return False
    
    def _can_delete_user(self, admin_user, target_user):
        """Check if admin can delete this user"""
        if admin_user.role == 'system_admin':
            return True
        elif admin_user.role == 'admin':
            # Regular admins can delete non-admin users in their organization
            return (target_user.organization == admin_user.organization and 
                   target_user.role not in ['admin', 'system_admin'])
        return False
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class AdminUserUnlockView(APIView):
    """Unlock user account"""
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    
    def post(self, request, user_id):
        """Unlock user account"""
        try:
            user = CustomUser.objects.get(id=user_id)
            
            # Check permissions
            if request.user.role == 'BlueVisionAdmin':
                pass  # System admins can unlock any user
            elif (request.user.role == 'admin' and 
                  user.organization == request.user.organization):
                pass  # Organization admins can unlock users in their org
            else:
                return Response({
                    'error': 'insufficient_permissions',
                    'message': 'Insufficient permissions to unlock this user'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Unlock account
            user.unlock_account()
            
            # Log unlock
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', 'Admin Interface')
            
            AuthenticationLog.log_authentication_event(
                user=user,
                action='account_unlocked',
                ip_address=ip_address,
                user_agent=user_agent,
                success=True,
                additional_data={'unlocked_by': request.user.username}
            )
            
            return Response({
                'success': True,
                'message': 'User account unlocked successfully'
            }, status=status.HTTP_200_OK)
            
        except CustomUser.DoesNotExist:
            return Response({
                'error': 'user_not_found',
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class AdminAuthenticationLogView(APIView):
    """View authentication logs"""
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    
    def get(self, request):
        """Get authentication logs with filtering"""
        # Filter logs based on admin permissions
        if request.user.role == 'BlueVisionAdmin':
            queryset = AuthenticationLog.objects.all()
        else:
            # Organization admins can only see logs for their organization users
            org_users = CustomUser.objects.filter(organization=request.user.organization)
            queryset = AuthenticationLog.objects.filter(user__in=org_users)
        
        # Apply filters
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user__id=user_id)
        
        action = request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        success = request.query_params.get('success')
        if success is not None:
            success_bool = success.lower() == 'true'
            queryset = queryset.filter(success=success_bool)
        
        ip_address = request.query_params.get('ip_address')
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)
        
        # Date range filtering
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        if from_date:
            queryset = queryset.filter(timestamp__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(timestamp__date__lte=to_date)
        
        # Order by timestamp (newest first)
        queryset = queryset.order_by('-timestamp')
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        serializer = AuthenticationLogSerializer(page_obj.object_list, many=True)
        
        return Response({
            'logs': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        }, status=status.HTTP_200_OK)


class AdminUserSessionView(APIView):
    """View and manage user sessions"""
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    
    def get(self, request):
        """Get active user sessions"""
        # Filter sessions based on admin permissions
        if request.user.role == 'BlueVisionAdmin':
            queryset = UserSession.objects.filter(is_active=True)
        else:
            # Organization admins can only see sessions for their organization users
            org_users = CustomUser.objects.filter(organization=request.user.organization)
            queryset = UserSession.objects.filter(user__in=org_users, is_active=True)
        
        # Apply filters
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user__id=user_id)
        
        # Order by last activity
        queryset = queryset.order_by('-last_activity')
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        serializer = UserSessionSerializer(page_obj.object_list, many=True)
        
        return Response({
            'sessions': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, session_id):
        """Terminate user session"""
        try:
            session = UserSession.objects.get(id=session_id, is_active=True)
            
            # Check permissions
            if request.user.role == 'BlueVisionAdmin':
                pass  # System admins can terminate any session
            elif (request.user.role == 'admin' and 
                  session.user.organization == request.user.organization):
                pass  # Organization admins can terminate sessions in their org
            else:
                return Response({
                    'error': 'insufficient_permissions',
                    'message': 'Insufficient permissions to terminate this session'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Terminate session
            session.deactivate()
            
            # Log session termination
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', 'Admin Interface')
            
            AuthenticationLog.log_authentication_event(
                user=session.user,
                action='session_expired',
                ip_address=ip_address,
                user_agent=user_agent,
                success=True,
                additional_data={
                    'terminated_by': request.user.username,
                    'session_id': str(session.id)
                }
            )
            
            return Response({
                'success': True,
                'message': 'Session terminated successfully'
            }, status=status.HTTP_200_OK)
            
        except UserSession.DoesNotExist:
            return Response({
                'error': 'session_not_found',
                'message': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
"""
Unified Permission Decorators for CRISP Systems

These decorators provide role-based access control that works seamlessly across
both Core and Trust systems, preserving all existing functionality while adding
Trust system features.
"""

import functools
import logging
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


def unified_login_required(view_func):
    """
    Unified login requirement that works with both session and JWT authentication.
    Preserves all existing Core system functionality while adding Trust system support.
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated via any method
        if not request.user or not request.user.is_authenticated:
            # For API requests, return JSON error
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Authentication required',
                    'message': 'Please log in to access this resource'
                }, status=401)
            
            # For web requests, redirect to login (preserves Core system behavior)
            return redirect('/admin/login/?next=' + request.path)
        
        # Check if account is locked (Trust system feature)
        if hasattr(request.user, 'is_account_locked') and request.user.is_account_locked:
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Account locked',
                    'message': 'Your account is temporarily locked'
                }, status=403)
            return HttpResponseForbidden("Your account is temporarily locked")
        
        # Check if organization is active (Trust system feature)
        if (hasattr(request.user, 'organization') and 
            request.user.organization and 
            not request.user.organization.is_active):
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Organization inactive',
                    'message': 'Your organization is currently inactive'
                }, status=403)
            return HttpResponseForbidden("Your organization is currently inactive")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_role(*allowed_roles):
    """
    Require specific user roles. Works with both Core and Trust system roles.
    
    Args:
        *allowed_roles: Roles that are allowed to access the view
                       ('viewer', 'publisher', 'BlueVisionAdmin', 'admin', 'staff')
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        @unified_login_required
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            # Check Trust system roles
            if hasattr(user, 'role'):
                if user.role in allowed_roles:
                    return view_func(request, *args, **kwargs)
            
            # Check Django admin roles (Core system compatibility)
            if 'admin' in allowed_roles and user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if 'staff' in allowed_roles and user.is_staff:
                return view_func(request, *args, **kwargs)
            
            # Log access denied
            logger.warning(f"Access denied for user {user.username} to {request.path}. "
                          f"Required roles: {allowed_roles}, User role: {getattr(user, 'role', 'None')}")
            
            # Return appropriate error response
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Insufficient permissions',
                    'message': f'This action requires one of the following roles: {", ".join(allowed_roles)}',
                    'required_roles': list(allowed_roles),
                    'user_role': getattr(user, 'role', None)
                }, status=403)
            
            return HttpResponseForbidden("You don't have permission to access this resource")
        
        return wrapper
    return decorator


def require_publisher_or_admin(view_func):
    """
    Require user to be a publisher or administrator.
    Combines Trust system publisher role with Core system admin roles.
    """
    return require_role('publisher', 'BlueVisionAdmin', 'admin')(view_func)


def require_admin(view_func):
    """
    Require user to be an administrator (BlueVisionAdmin or Django superuser).
    """
    return require_role('BlueVisionAdmin', 'admin')(view_func)


def require_organization_access(view_func):
    """
    Require user to belong to an active organization.
    Preserves Core system functionality while adding Trust system validation.
    """
    @functools.wraps(view_func)
    @unified_login_required
    def wrapper(request, *args, **kwargs):
        user = request.user
        
        # Allow superusers and BlueVisionAdmins to bypass organization requirement
        if user.is_superuser or (hasattr(user, 'role') and user.role == 'BlueVisionAdmin'):
            return view_func(request, *args, **kwargs)
        
        # Check organization requirement
        if not hasattr(user, 'organization') or not user.organization:
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Organization required',
                    'message': 'You must belong to an organization to access this resource'
                }, status=403)
            return HttpResponseForbidden("You must belong to an organization to access this resource")
        
        # Check if organization is active
        if not user.organization.is_active:
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Organization inactive',
                    'message': 'Your organization is currently inactive'
                }, status=403)
            return HttpResponseForbidden("Your organization is currently inactive")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_trust_management_permission(view_func):
    """
    Require permission to manage trust relationships.
    """
    @functools.wraps(view_func)
    @unified_login_required
    def wrapper(request, *args, **kwargs):
        user = request.user
        
        # Check trust management permission
        if not hasattr(user, 'can_manage_trust_relationships') or not user.can_manage_trust_relationships:
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Trust management permission required',
                    'message': 'You need trust management permissions to perform this action',
                    'required_permission': 'can_manage_trust_relationships'
                }, status=403)
            return HttpResponseForbidden("You need trust management permissions to perform this action")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_organization_data_access(organization_id_param='organization_id'):
    """
    Require access to specific organization's data based on trust relationships.
    
    Args:
        organization_id_param: Name of the parameter containing organization ID
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        @unified_login_required
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            # Get organization ID from parameters
            org_id = kwargs.get(organization_id_param) or request.GET.get(organization_id_param)
            if not org_id:
                if request.path.startswith('/api/'):
                    return JsonResponse({
                        'error': 'Organization ID required',
                        'message': f'Parameter {organization_id_param} is required'
                    }, status=400)
                return HttpResponseForbidden("Organization ID is required")
            
            # Allow BlueVisionAdmins to access all organization data
            if hasattr(user, 'role') and user.role == 'BlueVisionAdmin':
                return view_func(request, *args, **kwargs)
            
            # Allow superusers to access all data (Core system compatibility)
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check if user can access this organization's data
            if hasattr(user, 'can_access_organization_data'):
                if user.can_access_organization_data(org_id):
                    return view_func(request, *args, **kwargs)
            
            # Fallback: check if it's user's own organization
            if (hasattr(user, 'organization') and 
                user.organization and 
                str(user.organization.id) == str(org_id)):
                return view_func(request, *args, **kwargs)
            
            # Access denied
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Access denied',
                    'message': 'You do not have access to this organization\'s data',
                    'organization_id': org_id
                }, status=403)
            return HttpResponseForbidden("You do not have access to this organization's data")
        
        return wrapper
    return decorator


def api_authentication_required(view_func):
    """
    API-specific authentication decorator that works with both JWT and session auth.
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return JsonResponse({
                'error': 'Authentication required',
                'message': 'Please provide valid authentication credentials',
                'authentication_methods': ['JWT Token', 'Session Authentication']
            }, status=401)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def preserve_core_functionality(view_func):
    """
    Decorator to ensure Core system functionality is preserved.
    This is a safety decorator that can be applied to existing Core views.
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Ensure user profile compatibility
        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            not hasattr(request.user, 'profile')):
            
            # Create compatibility profile
            class CompatibilityProfile:
                def __init__(self, user):
                    self.user = user
                    self.organization = getattr(user, 'organization', None)
            
            request.user.profile = CompatibilityProfile(request.user)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
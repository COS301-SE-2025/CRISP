"""
Unified Authentication Middleware for CRISP Systems

This middleware provides seamless authentication across both Core and Trust systems,
supporting both JWT tokens and session authentication while preserving all existing
functionality from both systems.
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.http import JsonResponse
import json

logger = logging.getLogger(__name__)


class UnifiedAuthenticationMiddleware(MiddlewareMixin):
    """
    Unified authentication middleware that supports both JWT and session authentication.
    
    This middleware:
    1. Preserves ALL existing Core system session authentication
    2. Adds JWT authentication support across both systems
    3. Maintains backward compatibility with all existing authentication flows
    4. Provides unified user context with Trust system features
    5. Ensures no authentication functionality is lost
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authenticator = JWTAuthentication()
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Process incoming requests to provide unified authentication.
        
        Priority order:
        1. Existing session authentication (preserves Core system functionality)
        2. JWT authentication (adds Trust system functionality)
        3. Anonymous users (maintains existing behavior)
        """
        # Skip authentication for certain paths to avoid conflicts
        if self._should_skip_auth(request):
            return None
        
        # If user is already authenticated via session (Core system), preserve that
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Enhance session-authenticated user with Trust system context
            self._enhance_user_with_trust_context(request.user, request)
            return None
        
        # Try JWT authentication for API endpoints
        if self._is_api_request(request):
            jwt_user = self._authenticate_jwt(request)
            if jwt_user:
                request.user = jwt_user
                # Add Trust system context to JWT-authenticated user
                self._enhance_user_with_trust_context(jwt_user, request)
                return None
        
        # Fallback to anonymous user (preserves existing behavior)
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            request.user = AnonymousUser()
        
        return None
    
    def _should_skip_auth(self, request):
        """Determine if authentication should be skipped for this request"""
        skip_paths = [
            '/admin/login/',
            '/api/v1/auth/login/',
            '/api/v1/auth/register/',
            '/static/',
            '/media/',
            '/favicon.ico'
        ]
        
        return any(request.path.startswith(path) for path in skip_paths)
    
    def _is_api_request(self, request):
        """Determine if this is an API request that should use JWT"""
        return (
            request.path.startswith('/api/') and
            not request.path.startswith('/admin/')
        )
    
    def _authenticate_jwt(self, request):
        """
        Authenticate request using JWT token.
        Returns authenticated user or None.
        """
        try:
            # Use DRF's JWT authenticator
            auth_result = self.jwt_authenticator.authenticate(request)
            if auth_result is not None:
                user, token = auth_result
                # Ensure user is active and valid
                if user and user.is_authenticated and user.is_active:
                    # Check if user account is locked
                    if hasattr(user, 'is_account_locked') and user.is_account_locked:
                        logger.warning(f"JWT authentication attempted for locked account: {user.username}")
                        return None
                    
                    # Check if user's organization is active
                    if hasattr(user, 'organization') and user.organization and not user.organization.is_active:
                        logger.warning(f"JWT authentication attempted for inactive organization: {user.organization.name}")
                        return None
                    
                    logger.debug(f"JWT authentication successful for user: {user.username}")
                    return user
                
        except (InvalidToken, TokenError) as e:
            logger.debug(f"JWT authentication failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during JWT authentication: {str(e)}")
        
        return None
    
    def _enhance_user_with_trust_context(self, user, request):
        """
        Enhance user object with Trust system context and permissions.
        This ensures both Core and Trust functionality work seamlessly.
        """
        if not user or not user.is_authenticated:
            return
        
        try:
            # Add Trust system context if user has organization
            if hasattr(user, 'organization') and user.organization:
                # Cache accessible organizations for performance
                if not hasattr(user, '_accessible_organizations'):
                    user._accessible_organizations = self._get_accessible_organizations(user)
                
                # Cache user permissions
                if not hasattr(user, '_trust_permissions'):
                    user._trust_permissions = self._get_user_permissions(user)
                
                # Cache trust context
                if not hasattr(user, '_trust_context'):
                    user._trust_context = self._get_trust_context(user)
            
            # Ensure Core system compatibility
            self._ensure_core_compatibility(user)
            
        except Exception as e:
            logger.error(f"Error enhancing user with trust context: {str(e)}")
    
    def _get_accessible_organizations(self, user):
        """Get organizations accessible to this user"""
        try:
            from core_ut.user_management.services.access_control_service import AccessControlService
            access_control = AccessControlService()
            return list(access_control.get_accessible_organizations(user))
        except Exception as e:
            logger.error(f"Error getting accessible organizations: {str(e)}")
            return []
    
    def _get_user_permissions(self, user):
        """Get user permissions from Trust system"""
        try:
            from core_ut.user_management.services.access_control_service import AccessControlService
            access_control = AccessControlService()
            return list(access_control.get_user_permissions(user))
        except Exception as e:
            logger.error(f"Error getting user permissions: {str(e)}")
            return []
    
    def _get_trust_context(self, user):
        """Get trust context for the user"""
        try:
            if not hasattr(user, 'organization') or not user.organization:
                return {}
            
            # Get basic trust metrics
            from core_ut.trust.models import TrustRelationship
            
            outgoing_relationships = TrustRelationship.objects.filter(
                source_organization=str(user.organization.id),
                is_active=True,
                status='active'
            ).count()
            
            incoming_relationships = TrustRelationship.objects.filter(
                target_organization=str(user.organization.id),
                is_active=True,
                status='active'
            ).count()
            
            return {
                'organization_id': str(user.organization.id),
                'organization_name': user.organization.name,
                'outgoing_trust_relationships': outgoing_relationships,
                'incoming_trust_relationships': incoming_relationships,
                'can_manage_trust': user.can_manage_trust_relationships,
                'trust_aware_access': True
            }
            
        except Exception as e:
            logger.error(f"Error getting trust context: {str(e)}")
            return {}
    
    def _ensure_core_compatibility(self, user):
        """
        Ensure the user object maintains compatibility with Core system expectations.
        This preserves all existing Core system functionality.
        """
        try:
            # Ensure standard Django user fields are available
            if not hasattr(user, 'is_staff'):
                user.is_staff = getattr(user, 'is_superuser', False)
            
            # Ensure backward compatibility with Core system user profile
            if not hasattr(user, 'profile'):
                # Create a compatibility profile object if needed
                class CompatibilityProfile:
                    def __init__(self, user):
                        self.user = user
                        self.organization = getattr(user, 'organization', None)
                
                user.profile = CompatibilityProfile(user)
            
            # Ensure Core system model compatibility
            self._ensure_model_compatibility(user)
            
        except Exception as e:
            logger.error(f"Error ensuring Core compatibility: {str(e)}")
    
    def _ensure_model_compatibility(self, user):
        """
        Ensure model relationships work between Core and Trust systems.
        This maintains data integrity across both systems.
        """
        try:
            # Map Trust system organization to Core system if needed
            if hasattr(user, 'organization') and user.organization:
                # Ensure Core system can reference the organization
                self._sync_organization_references(user.organization)
                
        except Exception as e:
            logger.error(f"Error ensuring model compatibility: {str(e)}")
    
    def _sync_organization_references(self, trust_org):
        """
        Ensure Trust system organization is compatible with Core system expectations.
        This maintains referential integrity across both systems.
        """
        try:
            from core.models.models import Organization as CoreOrganization
            
            # Check if Core organization exists with same ID
            try:
                core_org = CoreOrganization.objects.get(id=trust_org.id)
                # Update Core organization with Trust data if needed
                if core_org.name != trust_org.name:
                    core_org.name = trust_org.name
                    core_org.description = trust_org.description
                    core_org.domain = trust_org.domain
                    core_org.contact_email = trust_org.contact_email
                    core_org.save()
                    
            except CoreOrganization.DoesNotExist:
                # Create Core organization to maintain compatibility
                CoreOrganization.objects.create(
                    id=trust_org.id,
                    name=trust_org.name,
                    description=trust_org.description or '',
                    domain=trust_org.domain or '',
                    contact_email=trust_org.contact_email or '',
                    organization_type='educational',  # Default type
                    created_by=None
                )
                logger.info(f"Created Core organization for Trust org: {trust_org.name}")
                
        except Exception as e:
            logger.error(f"Error syncing organization references: {str(e)}")
    
    def process_exception(self, request, exception):
        """
        Handle authentication-related exceptions gracefully.
        Ensures system stability when authentication issues occur.
        """
        if isinstance(exception, (InvalidToken, TokenError)):
            if self._is_api_request(request):
                return JsonResponse({
                    'error': 'Authentication failed',
                    'message': 'Invalid or expired token'
                }, status=401)
        
        return None
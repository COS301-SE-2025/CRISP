from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ValidationError, PermissionDenied
from ..services.organization_service import OrganizationService
from ..services.trust_aware_service import TrustAwareService
from ..services.access_control_service import AccessControlService
import logging

logger = logging.getLogger(__name__)


class OrganizationViewSet(GenericViewSet):
    """
    Organization management API endpoints with trust relationship support.
    """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.org_service = OrganizationService()
        self.trust_service = TrustAwareService()
        self.access_control = AccessControlService()
    
    @action(detail=False, methods=['post'])
    def create_organization(self, request):
        """
        Create a new organization with primary publisher user.
        
        Expected payload:
        {
            "name": "string",
            "domain": "string",
            "contact_email": "string",
            "description": "string",
            "website": "string",
            "organization_type": "educational|government|private",
            "primary_user": {
                "username": "string",
                "email": "string",
                "password": "string",
                "first_name": "string",
                "last_name": "string"
            }
        }
        """
        try:
            if not self.access_control.has_permission(request.user, 'can_create_organizations'):
                return Response({
                    'success': False,
                    'message': 'No permission to create organizations'
                }, status=status.HTTP_403_FORBIDDEN)
            
            org_data = request.data.copy()
            org_data['created_from_ip'] = self._get_client_ip(request)
            org_data['user_agent'] = request.META.get('HTTP_USER_AGENT', 'API')
            
            organization, primary_user = self.org_service.create_organization(
                creating_user=request.user,
                org_data=org_data
            )
            
            org_details = self.org_service.get_organization_details(
                requesting_user=request.user,
                organization_id=str(organization.id)
            )
            
            return Response({
                'success': True,
                'data': {
                    'organization': org_details,
                    'primary_user': {
                        'id': str(primary_user.id),
                        'username': primary_user.username,
                        'email': primary_user.email
                    },
                    'message': f'Organization {organization.name} created successfully'
                }
            }, status=status.HTTP_201_CREATED)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Create organization error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to create organization'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def get_organization(self, request, pk=None):
        """Get detailed organization information."""
        try:
            org_details = self.org_service.get_organization_details(
                requesting_user=request.user,
                organization_id=pk
            )
            
            return Response({
                'success': True,
                'data': {
                    'organization': org_details
                }
            }, status=status.HTTP_200_OK)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Get organization error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve organization'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['put', 'patch'])
    def update_organization(self, request, pk=None):
        """
        Update organization information.
        
        Expected payload:
        {
            "description": "string",
            "contact_email": "string",
            "website": "string",
            "organization_type": "string"
        }
        """
        try:
            update_data = request.data.copy()
            update_data['updated_from_ip'] = self._get_client_ip(request)
            update_data['user_agent'] = request.META.get('HTTP_USER_AGENT', 'API')
            
            updated_org = self.org_service.update_organization(
                updating_user=request.user,
                organization_id=pk,
                update_data=update_data
            )
            
            org_details = self.org_service.get_organization_details(
                requesting_user=request.user,
                organization_id=str(updated_org.id)
            )
            
            return Response({
                'success': True,
                'data': {
                    'organization': org_details,
                    'message': 'Organization updated successfully'
                }
            }, status=status.HTTP_200_OK)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Update organization error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to update organization'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def list_organizations(self, request):
        """
        List organizations accessible to the user.
        
        Query parameters:
        - is_active: Filter by active status
        - is_publisher: Filter by publisher status
        - organization_type: Filter by type
        - search: Search by name or domain
        """
        try:
            filters = {
                'is_active': request.query_params.get('is_active'),
                'is_publisher': request.query_params.get('is_publisher'),
                'organization_type': request.query_params.get('organization_type'),
                'search': request.query_params.get('search')
            }
            
            # Remove None values
            filters = {k: v for k, v in filters.items() if v is not None}
            
            # Convert string booleans
            for bool_field in ['is_active', 'is_publisher']:
                if bool_field in filters:
                    filters[bool_field] = filters[bool_field].lower() == 'true'
            
            organizations = self.org_service.list_organizations(
                requesting_user=request.user,
                filters=filters
            )
            
            return Response({
                'success': True,
                'data': {
                    'organizations': organizations,
                    'total_count': len(organizations),
                    'filters_applied': filters
                }
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"List organizations error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve organizations'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def deactivate_organization(self, request, pk=None):
        """
        Deactivate an organization.
        
        Expected payload:
        {
            "reason": "string"
        }
        """
        try:
            reason = request.data.get('reason', '')
            
            deactivated_org = self.org_service.deactivate_organization(
                deactivating_user=request.user,
                organization_id=pk,
                reason=reason
            )
            
            return Response({
                'success': True,
                'data': {
                    'message': f'Organization {deactivated_org.name} deactivated successfully',
                    'organization_id': str(deactivated_org.id),
                    'reason': reason
                }
            }, status=status.HTTP_200_OK)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Deactivate organization error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to deactivate organization'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get organization statistics (admin only)."""
        try:
            stats = self.org_service.get_organization_statistics(
                requesting_user=request.user
            )
            
            return Response({
                'success': True,
                'data': {
                    'statistics': stats
                }
            }, status=status.HTTP_200_OK)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Get organization statistics error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve statistics'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def create_trust_relationship(self, request, pk=None):
        """
        Create a trust relationship with another organization.
        
        Expected payload:
        {
            "trust_level_id": "uuid",
            "relationship_type": "bilateral|community|hierarchical",
            "notes": "string"
        }
        """
        try:
            from core.trust.models import TrustLevel, Organization
            
            trust_level_id = request.data.get('trust_level_id')
            relationship_type = request.data.get('relationship_type', 'bilateral')
            notes = request.data.get('notes', '')
            
            if not trust_level_id:
                return Response({
                    'success': False,
                    'message': 'Trust level ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                target_organization = Organization.objects.get(id=pk)
                trust_level = TrustLevel.objects.get(id=trust_level_id)
            except (Organization.DoesNotExist, TrustLevel.DoesNotExist) as e:
                return Response({
                    'success': False,
                    'message': f'Invalid organization or trust level: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            trust_relationship = self.trust_service.create_trust_relationship(
                requesting_user=request.user,
                target_organization=target_organization,
                trust_level=trust_level,
                relationship_type=relationship_type,
                notes=notes
            )
            
            return Response({
                'success': True,
                'data': {
                    'trust_relationship': {
                        'id': str(trust_relationship.id),
                        'source_organization': trust_relationship.source_organization.name,
                        'target_organization': trust_relationship.target_organization.name,
                        'trust_level': trust_relationship.trust_level.name,
                        'status': trust_relationship.status,
                        'relationship_type': trust_relationship.relationship_type
                    },
                    'message': 'Trust relationship created successfully'
                }
            }, status=status.HTTP_201_CREATED)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Create trust relationship error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to create trust relationship'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def trust_metrics(self, request):
        """Get trust metrics for user's organization."""
        try:
            metrics = self.trust_service.get_organization_trust_metrics(
                user=request.user
            )
            
            return Response({
                'success': True,
                'data': {
                    'metrics': metrics
                }
            }, status=status.HTTP_200_OK)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Get trust metrics error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve trust metrics'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
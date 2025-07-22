from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ValidationError, PermissionDenied
from django.db.models import Q
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
    
    @action(detail=True, methods=['post'])
    def reactivate_organization(self, request, pk=None):
        """
        Reactivate a previously deactivated organization.
        
        Expected payload:
        {
            "reason": "string"
        }
        """
        try:
            reason = request.data.get('reason', '')
            
            reactivated_org = self.org_service.reactivate_organization(
                reactivating_user=request.user,
                organization_id=pk,
                reason=reason
            )
            
            return Response({
                'success': True,
                'data': {
                    'message': f'Organization {reactivated_org.name} reactivated successfully',
                    'organization_id': str(reactivated_org.id),
                    'reason': reason
                }
            }, status=status.HTTP_200_OK)
        
        except (ValidationError, PermissionDenied) as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Reactivate organization error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to reactivate organization'
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

    def list_trust_relationships(self, request):
        """List trust relationships for user's organization."""
        try:
            # Try to import trust models with better error handling
            try:
                from core.trust.models import TrustRelationship
                from django.db.models import Q
            except ImportError as import_error:
                logger.error(f"Failed to import trust models: {import_error}")
                return Response({
                    'success': True,
                    'data': [],
                    'message': 'Trust management system not available'
                }, status=status.HTTP_200_OK)
            
            user_org = getattr(request.user, 'organization', None)
            
            # If user has no organization, check if they're an admin who can see all relationships
            if not user_org:
                if hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin':
                    # For admin users, return all trust relationships
                    relationships = TrustRelationship.objects.all().select_related(
                        'source_organization', 'target_organization', 'trust_level'
                    )
                else:
                    return Response({
                        'success': False,
                        'message': 'User is not associated with an organization'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Get all trust relationships where this org is source or target
                relationships = TrustRelationship.objects.filter(
                    Q(source_organization=user_org) | 
                    Q(target_organization=user_org)
                ).select_related('source_organization', 'target_organization', 'trust_level')
            
            relationship_data = []
            for rel in relationships:
                # For admin users without organization, show all relationships differently
                if not user_org:
                    relationship_data.append({
                        'id': str(rel.id),
                        'source_organization_name': rel.source_organization.name,
                        'source_organization_id': str(rel.source_organization.id),
                        'target_organization_name': rel.target_organization.name,
                        'target_organization_id': str(rel.target_organization.id),
                        'trust_level': rel.trust_level.name if rel.trust_level else None,
                        'trust_score': rel.trust_level.numerical_value if rel.trust_level else 0,
                        'relationship_type': rel.relationship_type,
                        'status': rel.status,
                        'notes': rel.notes,
                        'created_at': rel.created_at.isoformat() if rel.created_at else None,
                        'is_admin_view': True
                    })
                else:
                    # Determine which is the "other" organization
                    other_org = rel.target_organization if rel.source_organization == user_org else rel.source_organization
                    
                    relationship_data.append({
                        'id': str(rel.id),
                        'target_organization_name': other_org.name,
                        'target_organization_id': str(other_org.id),
                        'trust_level': rel.trust_level.name if rel.trust_level else None,
                        'trust_score': rel.trust_level.numerical_value if rel.trust_level else 0,
                        'relationship_type': rel.relationship_type,
                        'status': rel.status,
                        'notes': rel.notes,
                        'created_at': rel.created_at.isoformat() if rel.created_at else None,
                        'is_source': rel.source_organization == user_org
                    })
            
            return Response({
                'success': True,
                'data': relationship_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"List trust relationships error: {str(e)}")
            # Return empty data instead of error to prevent frontend crashes
            return Response({
                'success': True,
                'data': [],
                'message': 'Trust relationships temporarily unavailable'
            }, status=status.HTTP_200_OK)

    def update_trust_relationship(self, request, pk=None):
        """Update a trust relationship."""
        try:
            from core.trust.models import TrustRelationship, TrustLevel
            
            user_org = request.user.organization
            if not user_org:
                return Response({
                    'success': False,
                    'message': 'User is not associated with an organization'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the relationship
            try:
                relationship = TrustRelationship.objects.filter(
                    id=pk
                ).filter(
                    Q(source_organization=user_org) | 
                    Q(target_organization=user_org)
                ).get()
            except TrustRelationship.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Trust relationship not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Update fields
            trust_level_id = request.data.get('trust_level')
            if trust_level_id:
                try:
                    trust_level = TrustLevel.objects.get(id=trust_level_id)
                    relationship.trust_level = trust_level
                except TrustLevel.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': 'Invalid trust level'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if 'notes' in request.data:
                relationship.notes = request.data.get('notes')
            
            if 'status' in request.data:
                relationship.status = request.data.get('status')
            
            relationship.save()
            
            return Response({
                'success': True,
                'message': 'Trust relationship updated successfully',
                'data': {
                    'id': str(relationship.id),
                    'status': relationship.status,
                    'trust_level': relationship.trust_level.name if relationship.trust_level else None
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Update trust relationship error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to update trust relationship'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete_trust_relationship(self, request, pk=None):
        """Delete a trust relationship."""
        try:
            from core.trust.models import TrustRelationship
            
            user_org = request.user.organization
            if not user_org:
                return Response({
                    'success': False,
                    'message': 'User is not associated with an organization'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the relationship
            try:
                relationship = TrustRelationship.objects.filter(
                    id=pk
                ).filter(
                    Q(source_organization=user_org) | 
                    Q(target_organization=user_org)
                ).get()
            except TrustRelationship.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Trust relationship not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Delete the relationship
            relationship.delete()
            
            return Response({
                'success': True,
                'message': 'Trust relationship deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Delete trust relationship error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to delete trust relationship'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list_trust_groups(self, request):
        """List trust groups."""
        try:
            # Try to import trust models with better error handling
            try:
                from core.trust.models import TrustGroup, TrustGroupMembership
            except ImportError as import_error:
                logger.error(f"Failed to import trust models: {import_error}")
                return Response({
                    'success': False,
                    'message': 'Trust management system not available',
                    'data': []
                }, status=status.HTTP_200_OK)
            
            user_org = getattr(request.user, 'organization', None)
            
            # If user has no organization, check if they're an admin who can see all groups
            if not user_org:
                if hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin':
                    try:
                        # For admin users, return all trust groups
                        groups = TrustGroup.objects.all().select_related('default_trust_level')
                        group_data = []
                        for group in groups:
                            try:
                                member_count = TrustGroupMembership.objects.filter(group=group).count()
                            except Exception:
                                member_count = 0
                            
                            group_data.append({
                                'id': str(group.id),
                                'name': group.name,
                                'description': group.description or '',
                                'default_trust_level': group.default_trust_level.name if group.default_trust_level else None,
                                'is_admin_view': True,
                                'member_count': member_count
                            })
                        return Response({
                            'success': True,
                            'data': group_data
                        }, status=status.HTTP_200_OK)
                    except Exception as db_error:
                        logger.error(f"Database error fetching trust groups for admin: {db_error}")
                        return Response({
                            'success': True,
                            'data': [],
                            'message': 'No trust groups available'
                        }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'success': False,
                        'message': 'User is not associated with an organization',
                        'data': []
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Get trust groups where this org is a member
                memberships = TrustGroupMembership.objects.filter(
                    organization=user_org
                ).select_related('group', 'group__default_trust_level')
                
                group_data = []
                for membership in memberships:
                    try:
                        group = membership.group
                        member_count = getattr(group, 'trustgroupmembership_set', None)
                        if member_count:
                            member_count = member_count.count()
                        else:
                            member_count = 0
                        
                        group_data.append({
                            'id': str(group.id),
                            'name': group.name,
                            'description': group.description or '',
                            'trust_level': group.default_trust_level.name if group.default_trust_level else None,
                            'group_type': getattr(group, 'group_type', 'community'),
                            'member_count': member_count,
                            'is_active': getattr(group, 'is_active', True),
                            'created_at': group.created_at.isoformat() if hasattr(group, 'created_at') and group.created_at else None,
                            'user_role': getattr(membership, 'membership_type', 'member')
                        })
                    except Exception as group_error:
                        logger.warning(f"Error processing trust group {group.id if 'group' in locals() else 'unknown'}: {group_error}")
                        continue
                
                return Response({
                    'success': True,
                    'data': group_data
                }, status=status.HTTP_200_OK)
                
            except Exception as query_error:
                logger.error(f"Database query error in list_trust_groups: {query_error}")
                return Response({
                    'success': True,
                    'data': [],
                    'message': 'No trust groups available'
                }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Unexpected error in list_trust_groups: {str(e)}")
            return Response({
                'success': True,
                'data': [],
                'message': 'Trust groups temporarily unavailable'
            }, status=status.HTTP_200_OK)

    def create_trust_group(self, request):
        """Create a new trust group."""
        try:
            from core.trust.models import TrustGroup, TrustLevel, TrustGroupMembership
            
            user_org = request.user.organization
            if not user_org:
                return Response({
                    'success': False,
                    'message': 'User is not associated with an organization'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get request data
            name = request.data.get('name')
            description = request.data.get('description', '')
            trust_level_name = request.data.get('trust_level')
            group_type = request.data.get('group_type', 'industry')
            
            if not name:
                return Response({
                    'success': False,
                    'message': 'Group name is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get trust level
            trust_level = None
            if trust_level_name:
                try:
                    trust_level = TrustLevel.objects.get(name=trust_level_name)
                except TrustLevel.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': 'Invalid trust level'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the group
            group = TrustGroup.objects.create(
                name=name,
                description=description,
                default_trust_level=trust_level,
                created_by=request.user,
                metadata={'group_type': group_type}
            )
            
            # Add the creator's organization as an admin member
            TrustGroupMembership.objects.create(
                group=group,
                organization=user_org,
                role='admin'
            )
            
            return Response({
                'success': True,
                'message': 'Trust group created successfully',
                'data': {
                    'id': str(group.id),
                    'name': group.name,
                    'description': group.description,
                    'trust_level': group.default_trust_level.name if group.default_trust_level else None,
                    'group_type': group_type
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Create trust group error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to create trust group'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
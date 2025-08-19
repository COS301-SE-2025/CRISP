from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models.trust_models import TrustRelationship, TrustGroup, TrustLevel, TrustGroupMembership
from .services.trust_service import TrustService
from .services.trust_group_service import TrustGroupService
import logging

logger = logging.getLogger(__name__)

class TrustRelationshipViewSet(viewsets.ViewSet):
    """ViewSet for managing trust relationships."""
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trust_service = TrustService()

    def list(self, request):
        """Get list of trust relationships."""
        try:
            # BlueVision admins can see all relationships
            if hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin':
                relationships = self.trust_service.get_all_trust_relationships()
                return Response({
                    'success': True,
                    'data': relationships
                }, status=status.HTTP_200_OK)
            
            # For regular users, use the service method which handles no-org users gracefully
            result = self.trust_service.get_trust_relationships(request.user)
            if result.get('success', False):
                return Response({
                    'success': True,
                    'data': result.get('relationships', [])
                }, status=status.HTTP_200_OK)
            else:
                # Return empty list for users with no organization or access issues
                return Response({
                    'success': True,
                    'data': []
                }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to get trust relationships: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """Create a new trust relationship."""
        try:
            relationship_data = request.data.copy()
            is_admin = hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin'
            
            # For admins, allow creation between any organizations
            if is_admin:
                # Bypass organization ownership checks for admins
                result = self.trust_service.create_trust_relationship(request.user, relationship_data)
            else:
                # Regular users follow normal validation
                result = self.trust_service.create_trust_relationship(request.user, relationship_data)
            
            if result.get('success', False):
                # Convert the relationship object to serializable data
                relationship = result.get('relationship')
                if relationship:
                    serialized_relationship = {
                        'id': str(relationship.id),
                        'source_organization': str(relationship.source_organization.id),
                        'source_organization_name': relationship.source_organization.name,
                        'target_organization': str(relationship.target_organization.id),
                        'target_organization_name': relationship.target_organization.name,
                        'trust_level': relationship.trust_level.name,
                        'relationship_type': relationship.relationship_type,
                        'status': relationship.status,
                        'notes': relationship.notes or '',
                        'created_at': relationship.created_at.isoformat()
                    }
                    return Response({
                        'success': True,
                        'data': serialized_relationship,
                        'message': 'Trust relationship created successfully'
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'success': True,
                        'message': 'Trust relationship created successfully'
                    }, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Failed to create trust relationship: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """Get a specific trust relationship."""
        try:
            relationship = TrustRelationship.objects.select_related(
                'trust_level', 'source_organization', 'target_organization'
            ).get(id=pk, is_active=True)
            
            # Check permissions
            user_org = request.user.organization
            if (hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin') or \
               (user_org and (relationship.source_organization == user_org or relationship.target_organization == user_org)):
                
                data = {
                    'id': str(relationship.id),
                    'source_organization': str(relationship.source_organization.id),
                    'source_organization_name': relationship.source_organization.name,
                    'target_organization': str(relationship.target_organization.id),
                    'target_organization_name': relationship.target_organization.name,
                    'trust_level': relationship.trust_level.name,
                    'relationship_type': relationship.relationship_type,
                    'status': relationship.status,
                    'notes': relationship.notes or '',
                    'created_at': relationship.created_at.isoformat()
                }
                
                return Response({
                    'success': True,
                    'data': data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
                
        except TrustRelationship.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Trust relationship not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to retrieve trust relationship: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        """Update a trust relationship."""
        try:
            relationship = TrustRelationship.objects.get(id=pk, is_active=True)
            
            # Check permissions - Admins can update any relationship
            user_org = request.user.organization
            is_admin = hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin'
            
            if not (is_admin or (user_org and (relationship.source_organization == user_org or relationship.target_organization == user_org))):
                return Response({
                    'success': False,
                    'message': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Update fields
            update_data = request.data
            if 'status' in update_data:
                relationship.status = update_data['status']
            if 'notes' in update_data:
                relationship.notes = update_data['notes']
            if 'trust_level' in update_data:
                try:
                    trust_level = TrustLevel.objects.get(id=update_data['trust_level'])
                    relationship.trust_level = trust_level
                except TrustLevel.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': 'Invalid trust level'
                    }, status=status.HTTP_400_BAD_REQUEST)
            if 'relationship_type' in update_data and is_admin:
                relationship.relationship_type = update_data['relationship_type']
            
            # Admins can modify approval status
            if is_admin:
                if 'source_approval_status' in update_data:
                    relationship.source_approval_status = update_data['source_approval_status']
                if 'target_approval_status' in update_data:
                    relationship.target_approval_status = update_data['target_approval_status']
            
            relationship.last_modified_by = request.user
            relationship.save()
            
            return Response({
                'success': True,
                'message': 'Trust relationship updated successfully'
            }, status=status.HTTP_200_OK)
            
        except TrustRelationship.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Trust relationship not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to update trust relationship: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        """Delete a trust relationship."""
        try:
            relationship = TrustRelationship.objects.get(id=pk, is_active=True)
            
            # Check permissions - Admins can delete any relationship
            user_org = request.user.organization
            is_admin = hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin'
            
            if is_admin:
                # Admins can hard delete any relationship
                relationship.is_active = False
                relationship.status = 'revoked'
                relationship.last_modified_by = request.user
                relationship.save()
                
                return Response({
                    'success': True,
                    'message': 'Trust relationship deleted successfully'
                }, status=status.HTTP_200_OK)
            else:
                # Regular users use the service method for proper validation
                result = self.trust_service.revoke_trust_relationship(request.user, pk, "Deleted by user")
                
                if result.get('success', False):
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except TrustRelationship.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Trust relationship not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to delete trust relationship: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def bulk_update(self, request):
        """Bulk update trust relationships (Admin only)."""
        if not (hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin'):
            return Response({
                'success': False,
                'message': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            updates = request.data.get('updates', [])
            results = []
            
            for update in updates:
                relationship_id = update.get('id')
                update_data = update.get('data', {})
                
                try:
                    relationship = TrustRelationship.objects.get(id=relationship_id, is_active=True)
                    
                    # Apply updates
                    if 'status' in update_data:
                        relationship.status = update_data['status']
                    if 'trust_level' in update_data:
                        trust_level = TrustLevel.objects.get(id=update_data['trust_level'])
                        relationship.trust_level = trust_level
                    if 'notes' in update_data:
                        relationship.notes = update_data['notes']
                    
                    relationship.last_modified_by = request.user
                    relationship.save()
                    
                    results.append({
                        'id': relationship_id,
                        'success': True,
                        'message': 'Updated successfully'
                    })
                    
                except TrustRelationship.DoesNotExist:
                    results.append({
                        'id': relationship_id,
                        'success': False,
                        'message': 'Relationship not found'
                    })
                except Exception as e:
                    results.append({
                        'id': relationship_id,
                        'success': False,
                        'message': str(e)
                    })
            
            return Response({
                'success': True,
                'results': results
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed bulk update: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def approve_multiple(self, request):
        """Approve multiple trust relationships (Admin only)."""
        if not (hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin'):
            return Response({
                'success': False,
                'message': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            relationship_ids = request.data.get('relationship_ids', [])
            results = []
            
            for rel_id in relationship_ids:
                try:
                    relationship = TrustRelationship.objects.get(id=rel_id, is_active=True)
                    relationship.status = 'active'
                    relationship.source_approval_status = 'approved'
                    relationship.target_approval_status = 'approved'
                    relationship.last_modified_by = request.user
                    relationship.save()
                    
                    results.append({
                        'id': rel_id,
                        'success': True,
                        'message': 'Approved successfully'
                    })
                    
                except TrustRelationship.DoesNotExist:
                    results.append({
                        'id': rel_id,
                        'success': False,
                        'message': 'Relationship not found'
                    })
                except Exception as e:
                    results.append({
                        'id': rel_id,
                        'success': False,
                        'message': str(e)
                    })
            
            return Response({
                'success': True,
                'results': results
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed multiple approval: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TrustGroupViewSet(viewsets.ViewSet):
    """ViewSet for managing trust groups."""
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trust_service = TrustService()

    def list(self, request):
        """Get list of trust groups."""
        try:
            # Use core models if trust_management models are empty
            from core.models.models import TrustGroup as CoreTrustGroup, TrustGroupMembership as CoreTrustGroupMembership
            
            # Always try core models first since that's where your data is
            groups = CoreTrustGroup.objects.filter(is_active=True)
            
            # For BlueVision admins, return full data
            if hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin':
                result = []
                for group in groups:
                    member_count = CoreTrustGroupMembership.objects.filter(
                        trust_group=group,
                        is_active=True
                    ).count()
                    
                    result.append({
                        'id': str(group.id),
                        'name': group.name,
                        'description': group.description,
                        'group_type': group.group_type,
                        'is_public': group.is_public,
                        'requires_approval': group.requires_approval,
                        'default_trust_level': group.default_trust_level.name if group.default_trust_level else None,
                        'member_count': member_count,
                        'status': 'active' if group.is_active else 'inactive',
                        'created_at': group.created_at.isoformat()
                    })
                
                return Response({
                    'success': True,
                    'data': result
                }, status=status.HTTP_200_OK)
            
            # For regular users, also return the groups
            result = []
            for group in groups:
                member_count = CoreTrustGroupMembership.objects.filter(
                    trust_group=group,
                    is_active=True
                ).count()
                
                result.append({
                    'id': str(group.id),
                    'name': group.name,
                    'description': group.description,
                    'group_type': group.group_type,
                    'is_public': group.is_public,
                    'requires_approval': group.requires_approval,
                    'default_trust_level': group.default_trust_level.name if group.default_trust_level else None,
                    'member_count': member_count,
                    'status': 'active' if group.is_active else 'inactive',
                    'created_at': group.created_at.isoformat()
                })
            
            return Response({
                'success': True,
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get trust groups: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """Create a new trust group."""
        try:
            # Check permissions - only BlueVisionAdmin can create trust groups
            if not (hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin'):
                return Response({
                    'success': False,
                    'message': 'Only administrators can create trust groups'
                }, status=status.HTTP_403_FORBIDDEN)
            
            group_data = request.data
            result = self.trust_service.create_trust_group(request.user, group_data)
            
            if result.get('success', False):
                # Convert the group object to serializable data
                group = result.get('group')
                if group:
                    serialized_group = {
                        'id': str(group.id),
                        'name': group.name,
                        'description': group.description,
                        'group_type': group.group_type,
                        'is_public': group.is_public,
                        'requires_approval': group.requires_approval,
                        'default_trust_level': group.default_trust_level.name if group.default_trust_level else None,
                        'status': 'active' if group.is_active else 'inactive',
                        'created_at': group.created_at.isoformat()
                    }
                    return Response({
                        'success': True,
                        'data': serialized_group,
                        'message': 'Trust group created successfully'
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'success': True,
                        'message': 'Trust group created successfully'
                    }, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Failed to create trust group: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """Get a specific trust group."""
        try:
            group = TrustGroup.objects.select_related('default_trust_level').get(id=pk, is_active=True)
            
            # Check permissions
            user_org = request.user.organization
            if hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin':
                # Admin can see all groups
                pass
            elif user_org:
                # Check if user's organization is a member
                if not TrustGroupMembership.objects.filter(
                    trust_group=group, 
                    organization=user_org, 
                    is_active=True
                ).exists():
                    return Response({
                        'success': False,
                        'message': 'Permission denied'
                    }, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({
                    'success': False,
                    'message': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get member count
            member_count = TrustGroupMembership.objects.filter(
                trust_group=group,
                is_active=True
            ).count()
            
            data = {
                'id': str(group.id),
                'name': group.name,
                'description': group.description,
                'group_type': group.group_type,
                'is_public': group.is_public,
                'requires_approval': group.requires_approval,
                'default_trust_level': group.default_trust_level.name if group.default_trust_level else None,
                'member_count': member_count,
                'status': 'active' if group.is_active else 'inactive',
                'created_at': group.created_at.isoformat()
            }
            
            return Response({
                'success': True,
                'data': data
            }, status=status.HTTP_200_OK)
                
        except TrustGroup.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Trust group not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to retrieve trust group: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        """Update a trust group."""
        try:
            group = TrustGroup.objects.get(id=pk, is_active=True)
            
            # Check permissions - only admins or group administrators
            if not (hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin'):
                return Response({
                    'success': False,
                    'message': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Update fields
            update_data = request.data
            if 'name' in update_data:
                group.name = update_data['name']
            if 'description' in update_data:
                group.description = update_data['description']
            if 'is_public' in update_data:
                group.is_public = update_data['is_public']
            if 'requires_approval' in update_data:
                group.requires_approval = update_data['requires_approval']
            if 'default_trust_level' in update_data:
                try:
                    trust_level = TrustLevel.objects.get(id=update_data['default_trust_level'])
                    group.default_trust_level = trust_level
                except TrustLevel.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': 'Invalid trust level'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            group.save()
            
            return Response({
                'success': True,
                'message': 'Trust group updated successfully'
            }, status=status.HTTP_200_OK)
            
        except TrustGroup.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Trust group not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to update trust group: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        """Delete a trust group."""
        try:
            group = TrustGroup.objects.get(id=pk, is_active=True)
            
            # Check permissions - only admins
            if not (hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin'):
                return Response({
                    'success': False,
                    'message': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Soft delete
            group.is_active = False
            group.save()
            
            return Response({
                'success': True,
                'message': 'Trust group deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except TrustGroup.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Trust group not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to delete trust group: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, pk=None):
        """Join a trust group."""
        try:
            group = TrustGroup.objects.get(id=pk, is_active=True)
            
            # Check if user has an organization
            user_org = request.user.organization
            if not user_org:
                return Response({
                    'success': False,
                    'message': 'User has no associated organization'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if already a member
            existing_membership = TrustGroupMembership.objects.filter(
                trust_group=group,
                organization=user_org,
                is_active=True
            ).exists()
            
            if existing_membership:
                return Response({
                    'success': False,
                    'message': 'Organization is already a member of this group'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create membership
            membership = TrustGroupMembership.objects.create(
                trust_group=group,
                organization=user_org,
                role='member',
                join_date=timezone.now(),
                joined_by=request.user
            )
            
            return Response({
                'success': True,
                'message': f'Successfully joined trust group: {group.name}'
            }, status=status.HTTP_201_CREATED)
            
        except TrustGroup.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Trust group not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to join trust group: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TrustMetricsViewSet(viewsets.ViewSet):
    """ViewSet for trust metrics."""
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trust_service = TrustService()

    def list(self, request):
        """Get trust metrics."""
        try:
            # BlueVision admins can see all metrics
            if hasattr(request.user, 'role') and request.user.role == 'BlueVisionAdmin':
                metrics = self.trust_service.get_all_trust_metrics()
                return Response({
                    'success': True,
                    'data': metrics
                }, status=status.HTTP_200_OK)
            
            # For regular users, get their organization metrics or return empty metrics
            organization_id = request.user.organization.id if request.user.organization else None
            if organization_id:
                result = self.trust_service.get_trust_metrics(request.user, str(organization_id))
                if result.get('success', False):
                    return Response({
                        'success': True,
                        'data': result.get('metrics', {})
                    }, status=status.HTTP_200_OK)
            
            # Return empty metrics for users without organization
            return Response({
                'success': True,
                'data': {
                    'trust_score': 0,
                    'connected_orgs': 0,
                    'total_relationships': 0,
                    'active_groups': 0
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to get trust metrics: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TrustLevelViewSet(viewsets.ViewSet):
    """ViewSet for trust levels."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Get list of available trust levels."""
        try:
            trust_levels = TrustLevel.objects.filter(is_active=True).order_by('numerical_value')
            
            levels_data = []
            for level in trust_levels:
                levels_data.append({
                    'id': str(level.id),
                    'name': level.name,
                    'level': level.level,
                    'description': level.description,
                    'numerical_value': level.numerical_value,
                    'default_anonymization_level': level.default_anonymization_level,
                    'default_access_level': level.default_access_level
                })
            
            return Response({
                'success': True,
                'data': levels_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get trust levels: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TrustGroupsView(APIView):
    """API View for trust groups."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get trust groups."""
        service = TrustService()
        result = service.get_trust_groups(request.user)
        # Always return 200 if success True, even if empty
        if result.get("success", False):
            return Response(result, status=status.HTTP_200_OK)
        # Only return 400 for real errors, not for "no org"
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
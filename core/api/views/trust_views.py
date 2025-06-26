"""
Trust Management Views

REST API views for trust relationship operations.
"""

from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.db.models import Q
from django.core.exceptions import ValidationError
from typing import Dict, Any
import django.db.models

from ...models import TrustRelationship, TrustLevel, TrustLog
from ..serializers.serializers import (
    TrustRelationshipSerializer, CreateTrustRelationshipSerializer,
    ApproveTrustRelationshipSerializer, RevokeTrustRelationshipSerializer,
    CheckTrustSerializer, TestIntelligenceAccessSerializer,
    UpdateTrustLevelSerializer, TrustLogSerializer
)
from ...core.services.trust_service import TrustService
from ..permissions.permissions import TrustRelationshipPermission
from ...core.validators.validators import validate_trust_operation


class TrustRelationshipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing trust relationships.
    Provides CRUD operations and additional trust-specific actions.
    """
    
    serializer_class = TrustRelationshipSerializer
    permission_classes = [TrustRelationshipPermission]
    
    def get_queryset(self):
        """
        Filter relationships based on user's organization.
        """
        if not self.request.user.is_authenticated:
            return TrustRelationship.objects.none()
        
        user_org = self.get_user_organization()
        if not user_org:
            return TrustRelationship.objects.none()
        
        # Return relationships where user's org is source or target
        return TrustRelationship.objects.filter(
            Q(source_organization=user_org) | Q(target_organization=user_org)
        ).select_related('trust_level', 'trust_group').order_by('-created_at')
    
    def get_user_organization(self) -> str:
        """Get the user's organization UUID."""
        if (hasattr(self.request.user, 'organization') and 
            self.request.user.organization):
            return str(self.request.user.organization.id)
        return None
    
    @action(detail=False, methods=['post'])
    def create_relationship(self, request: Request) -> Response:
        """
        Create a new trust relationship.
        """
        serializer = CreateTrustRelationshipSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_org = self.get_user_organization()
        
        # Validate the operation
        validation_result = validate_trust_operation(
            'create_relationship',
            source_org=user_org,
            target_org=str(data['target_organization']),
            trust_level_name=data['trust_level_name'],
            relationship_type=data['relationship_type']
        )
        
        if not validation_result['valid']:
            return Response({
                'errors': validation_result['errors'],
                'warnings': validation_result.get('warnings', [])
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create the relationship
            relationship = TrustService.create_trust_relationship(
                source_org=user_org,
                target_org=str(data['target_organization']),
                trust_level_name=data['trust_level_name'],
                relationship_type=data['relationship_type'],
                created_by=str(request.user.id),
                sharing_preferences=data.get('sharing_preferences', {}),
                valid_until=data.get('valid_until'),
                notes=data.get('notes', '')
            )
            
            response_serializer = TrustRelationshipSerializer(relationship)
            return Response({
                'relationship': response_serializer.data,
                'warnings': validation_result.get('warnings', [])
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Failed to create relationship: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def approve_relationship(self, request: Request) -> Response:
        """
        Approve a trust relationship.
        """
        serializer = ApproveTrustRelationshipSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_org = self.get_user_organization()
        
        # Validate the operation
        validation_result = validate_trust_operation(
            'approve_relationship',
            relationship_id=str(data['relationship_id']),
            approving_org=user_org,
            approved_by_user=str(request.user.id)
        )
        
        if not validation_result['valid']:
            return Response({
                'errors': validation_result['errors']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Approve the relationship
            activated = TrustService.approve_trust_relationship(
                relationship_id=str(data['relationship_id']),
                approving_org=user_org,
                approved_by_user=str(request.user.id)
            )
            
            # Get updated relationship
            relationship = TrustRelationship.objects.get(id=data['relationship_id'])
            response_serializer = TrustRelationshipSerializer(relationship)
            
            return Response({
                'relationship': response_serializer.data,
                'activated': activated,
                'message': 'Relationship activated' if activated else 'Approval recorded, waiting for other party'
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Failed to approve relationship: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def revoke_relationship(self, request: Request) -> Response:
        """
        Revoke a trust relationship.
        """
        serializer = RevokeTrustRelationshipSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_org = self.get_user_organization()
        
        # Validate the operation
        validation_result = validate_trust_operation(
            'revoke_relationship',
            relationship_id=str(data['relationship_id']),
            revoking_org=user_org,
            revoked_by_user=str(request.user.id),
            reason=data.get('reason')
        )
        
        if not validation_result['valid']:
            return Response({
                'errors': validation_result['errors'],
                'warnings': validation_result.get('warnings', [])
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Revoke the relationship
            success = TrustService.revoke_trust_relationship(
                relationship_id=str(data['relationship_id']),
                revoking_org=user_org,
                revoked_by_user=str(request.user.id),
                reason=data.get('reason')
            )
            
            if success:
                # Get updated relationship
                relationship = TrustRelationship.objects.get(id=data['relationship_id'])
                response_serializer = TrustRelationshipSerializer(relationship)
                
                return Response({
                    'relationship': response_serializer.data,
                    'message': 'Relationship revoked successfully',
                    'warnings': validation_result.get('warnings', [])
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Failed to revoke relationship'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except ValidationError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Failed to revoke relationship: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def check_trust(self, request: Request) -> Response:
        """
        Check trust level between organizations.
        """
        serializer = CheckTrustSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_org = self.get_user_organization()
        
        try:
            trust_info = TrustService.check_trust_level(
                source_org=user_org,
                target_org=str(data['target_organization'])
            )
            
            if trust_info:
                trust_level, relationship = trust_info
                relationship_serializer = TrustRelationshipSerializer(relationship)
                
                return Response({
                    'trust_exists': True,
                    'trust_level': {
                        'name': trust_level.name,
                        'level': trust_level.level,
                        'numerical_value': trust_level.numerical_value
                    },
                    'relationship': relationship_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'trust_exists': False,
                    'message': 'No trust relationship found'
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'error': f'Failed to check trust: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def test_intelligence_access(self, request: Request) -> Response:
        """
        Test intelligence access based on trust relationships.
        """
        serializer = TestIntelligenceAccessSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_org = self.get_user_organization()
        
        try:
            can_access, reason, relationship = TrustService.can_access_intelligence(
                requesting_org=user_org,
                intelligence_owner=str(data['intelligence_owner']),
                intelligence_type=data.get('resource_type'),
                required_access_level=data['required_access_level']
            )
            
            response_data = {
                'can_access': can_access,
                'reason': reason,
                'requested_access_level': data['required_access_level']
            }
            
            if relationship:
                relationship_serializer = TrustRelationshipSerializer(relationship)
                response_data['relationship'] = relationship_serializer.data
                response_data['effective_access_level'] = relationship.get_effective_access_level()
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Failed to test access: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def update_trust_level(self, request: Request) -> Response:
        """
        Update the trust level of an existing relationship.
        """
        serializer = UpdateTrustLevelSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user_org = self.get_user_organization()
        
        try:
            success = TrustService.update_trust_level(
                relationship_id=str(data['relationship_id']),
                new_trust_level_name=data['new_trust_level_name'],
                updated_by=str(request.user.id),
                reason=data.get('reason')
            )
            
            if success:
                # Get updated relationship
                relationship = TrustRelationship.objects.get(id=data['relationship_id'])
                response_serializer = TrustRelationshipSerializer(relationship)
                
                return Response({
                    'relationship': response_serializer.data,
                    'message': 'Trust level updated successfully'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Failed to update trust level'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except ValidationError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Failed to update trust level: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def get_sharing_organizations(self, request: Request) -> Response:
        """
        Get organizations that can receive intelligence from the user's organization.
        """
        user_org = self.get_user_organization()
        min_trust_level = request.query_params.get('min_trust_level', 'low')
        
        try:
            sharing_orgs = TrustService.get_sharing_organizations(
                source_org=user_org,
                min_trust_level=min_trust_level
            )
            
            response_data = []
            for org_id, trust_level, relationship in sharing_orgs:
                relationship_serializer = TrustRelationshipSerializer(relationship)
                response_data.append({
                    'organization_id': org_id,
                    'trust_level': {
                        'name': trust_level.name,
                        'level': trust_level.level,
                        'numerical_value': trust_level.numerical_value
                    },
                    'relationship': relationship_serializer.data
                })
            
            return Response({
                'sharing_organizations': response_data,
                'count': len(response_data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Failed to get sharing organizations: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TrustLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing trust activity logs.
    Read-only access to audit trail information.
    """
    
    serializer_class = TrustLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter logs based on user's organization and permissions.
        """
        if not self.request.user.is_authenticated:
            return TrustLog.objects.none()
        
        user_org = self.get_user_organization()
        if not user_org:
            return TrustLog.objects.none()
        
        # Filter logs related to user's organization
        queryset = TrustLog.objects.filter(
            Q(source_organization=user_org) | Q(target_organization=user_org)
        )
        
        # Additional filters from query parameters
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        success = self.request.query_params.get('success')
        if success is not None:
            queryset = queryset.filter(success=success.lower() == 'true')
        
        days = self.request.query_params.get('days')
        if days:
            try:
                from datetime import timedelta
                from django.utils import timezone
                cutoff_date = timezone.now() - timedelta(days=int(days))
                queryset = queryset.filter(timestamp__gte=cutoff_date)
            except (ValueError, TypeError):
                pass  # Ignore invalid days parameter
        
        return queryset.order_by('-timestamp')
    
    def get_user_organization(self) -> str:
        """Get the user's organization UUID."""
        if (hasattr(self.request.user, 'organization') and 
            self.request.user.organization):
            return str(self.request.user.organization.id)
        return None
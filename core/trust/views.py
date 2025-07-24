from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TrustRelationship, TrustGroup
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
            if request.user.is_bluevision_admin:
                relationships = self.trust_service.get_all_trust_relationships()
                return Response({
                    'success': True,
                    'data': relationships
                }, status=status.HTTP_200_OK)
            
            # Get organization ID from authenticated user
            organization_id = request.user.organization.id if request.user.organization else None
            if not organization_id:
                return Response({
                    'success': False,
                    'message': 'User has no associated organization'
                }, status=status.HTTP_400_BAD_REQUEST)

            relationships = self.trust_service.get_trust_relationships(request.user)
            return Response({
                'success': True,
                'data': relationships
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to get trust relationships: {str(e)}")
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
            # BlueVision admins can see all groups
            if request.user.is_bluevision_admin:
                result = self.trust_service.get_all_trust_groups()
                if not result.get('success', False):
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
                groups = result.get('groups', [])
                return Response({
                    'success': True,
                    'data': groups
                }, status=status.HTTP_200_OK)
            
            # Get organization ID from authenticated user
            organization_id = request.user.organization.id if request.user.organization else None
            if not organization_id:
                return Response({
                    'success': False,
                    'message': 'User has no associated organization'
                }, status=status.HTTP_400_BAD_REQUEST)

            result = self.trust_service.get_trust_groups(request.user)
            if not result.get('success', False):
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            groups = result.get('groups', [])
            return Response({
                'success': True,
                'data': groups
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to get trust groups: {str(e)}")
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
            if request.user.is_bluevision_admin:
                metrics = self.trust_service.get_all_trust_metrics()
                return Response({
                    'success': True,
                    'data': metrics
                }, status=status.HTTP_200_OK)
            
            # Get organization ID from authenticated user
            organization_id = request.user.organization.id if request.user.organization else None
            if not organization_id:
                return Response({
                    'success': False,
                    'message': 'User has no associated organization'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            metrics = self.trust_service.get_trust_metrics(organization_id)
            return Response({
                'success': True,
                'data': metrics
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to get trust metrics: {str(e)}")
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
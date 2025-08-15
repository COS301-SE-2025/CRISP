"""
Unified Response Utilities for CRISP API Integration

These utilities provide consistent response formatting while preserving ALL existing
response formats from both Core and Trust systems.
"""

from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import QuerySet
import logging
import uuid

logger = logging.getLogger(__name__)


class UnifiedResponseFormatter:
    """
    Unified response formatter that maintains compatibility with existing API responses
    while providing enhanced formatting for new unified endpoints.
    """
    
    @staticmethod
    def success_response(data=None, message="Success", meta=None, preserve_format=False):
        """
        Create a standardized success response.
        
        Args:
            data: Response data (can be dict, list, or any serializable object)
            message: Success message
            meta: Additional metadata
            preserve_format: If True, preserves existing API format exactly
            
        Returns:
            Response object with standardized format
        """
        if preserve_format and isinstance(data, (dict, list)):
            # For backward compatibility, return data as-is if it's already formatted
            if isinstance(data, dict) and ('success' in data or 'error' in data):
                return Response(data)
            
            # If it's a simple list or data structure, return it directly (Core system compatibility)
            return Response(data)
        
        response_data = {
            "success": True,
            "data": data,
            "message": message,
            "meta": {
                "timestamp": timezone.now().isoformat(),
                **(_format_meta(meta) if meta else {})
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @staticmethod
    def error_response(message="An error occurred", details=None, error_code=None, 
                      status_code=status.HTTP_400_BAD_REQUEST, preserve_format=False):
        """
        Create a standardized error response.
        
        Args:
            message: Error message
            details: Additional error details
            error_code: Specific error code
            status_code: HTTP status code
            preserve_format: If True, preserves existing error format
            
        Returns:
            Response object with standardized error format
        """
        if preserve_format:
            # Preserve existing error formats from both systems
            if isinstance(details, dict) and 'error' in details:
                return Response(details, status=status_code)
        
        response_data = {
            "success": False,
            "error": message,
            "message": message,  # Dual compatibility
            "meta": {
                "timestamp": timezone.now().isoformat(),
                "error_code": error_code,
            }
        }
        
        if details:
            response_data["details"] = details
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def paginated_response(queryset, request, serializer_class=None, 
                          page_size=20, meta=None, preserve_format=False):
        """
        Create a paginated response with unified format.
        
        Args:
            queryset: QuerySet to paginate
            request: Request object for pagination parameters
            serializer_class: Serializer class for data formatting
            page_size: Number of items per page
            meta: Additional metadata
            preserve_format: Preserve existing pagination format
            
        Returns:
            Paginated response with unified format
        """
        # Get page parameter
        page = request.query_params.get('page', 1)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1
        
        # Get page size from query params or use default
        size = request.query_params.get('page_size', page_size)
        try:
            size = int(size)
            size = min(size, 100)  # Maximum 100 items per page
        except (ValueError, TypeError):
            size = page_size
        
        # Paginate the queryset
        paginator = Paginator(queryset, size)
        page_obj = paginator.get_page(page)
        
        # Serialize the data
        if serializer_class:
            serializer = serializer_class(page_obj.object_list, many=True, context={'request': request})
            data = serializer.data
        else:
            # For backward compatibility, handle QuerySet directly
            data = list(page_obj.object_list.values()) if isinstance(queryset, QuerySet) else page_obj.object_list
        
        if preserve_format:
            # For existing APIs that expect simple data format
            return Response(data)
        
        response_data = {
            "success": True,
            "data": data,
            "pagination": {
                "page": page,
                "page_size": size,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "next_page": page + 1 if page_obj.has_next() else None,
                "previous_page": page - 1 if page_obj.has_previous() else None
            },
            "meta": {
                "timestamp": timezone.now().isoformat(),
                **(_format_meta(meta) if meta else {})
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class LegacyResponseHandler:
    """
    Handles responses for legacy endpoints to ensure backward compatibility.
    This ensures ALL existing API clients continue working without changes.
    """
    
    @staticmethod
    def threat_feed_response(data, action="list"):
        """Handle ThreatFeed API responses in existing format"""
        if action == "consume":
            # Preserve exact consume response format
            if isinstance(data, dict) and "indicators" in data:
                return Response(data)
        
        if action == "status":
            # Preserve exact status response format
            return Response(data)
        
        # For list/detail actions, preserve existing format
        return Response(data)
    
    @staticmethod
    def trust_system_response(data, success=True, message="Success"):
        """Handle Trust system responses in existing format"""
        # Trust system uses success/data format
        if isinstance(data, dict) and "success" in data:
            return Response(data)
        
        return Response({
            "success": success,
            "data": data,
            "message": message
        })
    
    @staticmethod
    def core_system_response(data):
        """Handle Core system responses in existing format"""
        # Core system typically returns data directly
        return Response(data)


def _format_meta(meta):
    """Format metadata for response"""
    if not meta:
        return {}
    
    formatted_meta = {}
    
    for key, value in meta.items():
        # Convert UUID objects to strings
        if isinstance(value, uuid.UUID):
            formatted_meta[key] = str(value)
        else:
            formatted_meta[key] = value
    
    return formatted_meta


def get_user_context(request):
    """
    Get user context for API responses.
    Provides unified user information across both systems.
    """
    if not request.user or not request.user.is_authenticated:
        return {}
    
    user = request.user
    context = {
        "user_id": str(user.id),
        "username": user.username,
    }
    
    # Add Trust system context
    if hasattr(user, 'role'):
        context["role"] = user.role
        
    if hasattr(user, 'organization') and user.organization:
        context["user_organization"] = {
            "id": str(user.organization.id),
            "name": user.organization.name
        }
        
    # Add Core system context
    if user.is_staff:
        context["is_staff"] = True
        
    if user.is_superuser:
        context["is_admin"] = True
    
    return context


def filter_by_organization(queryset, user, field_name="organization"):
    """
    Filter queryset by user's organization unless user is admin.
    Preserves existing organization-based filtering logic.
    """
    # BlueVisionAdmins and superusers see all data
    if (hasattr(user, 'role') and user.role == 'BlueVisionAdmin') or user.is_superuser:
        return queryset
    
    # Users with organization see their organization's data
    if hasattr(user, 'organization') and user.organization:
        filter_kwargs = {field_name: user.organization}
        return queryset.filter(**filter_kwargs)
    
    # Core system compatibility - staff users see all, others see none
    if user.is_staff:
        return queryset
    
    # Return empty queryset for users without organization
    return queryset.none()


def filter_by_source_organization(queryset, user, field_name="source_organization"):
    """
    Filter queryset by source organization for threat intelligence data.
    """
    return filter_by_organization(queryset, user, field_name)


def get_organization_accessible_data(user, model_class, field_name="organization"):
    """
    Get data accessible to user based on their organization and trust relationships.
    """
    queryset = model_class.objects.all()
    
    # Admin users see everything
    if (hasattr(user, 'role') and user.role == 'BlueVisionAdmin') or user.is_superuser:
        return queryset
    
    # Users see their organization's data plus trusted organizations
    if hasattr(user, 'organization') and user.organization:
        accessible_org_ids = [user.organization.id]
        
        # Add trusted organizations (if Trust system is available)
        try:
            from core_ut.trust.services.trust_service import TrustService
            trust_service = TrustService()
            trusted_orgs = trust_service.get_trusted_organizations(user)
            accessible_org_ids.extend([org.id for org in trusted_orgs])
        except ImportError:
            # Trust system not available, just use own organization
            pass
        
        filter_kwargs = {f"{field_name}__id__in": accessible_org_ids}
        return queryset.filter(**filter_kwargs)
    
    # Core system compatibility
    if user.is_staff:
        return queryset
    
    return queryset.none()
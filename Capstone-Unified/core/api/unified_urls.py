"""
Unified URL Configuration for CRISP API Integration

This configuration creates a unified API structure while preserving ALL existing
endpoints from both Core and Trust systems. No existing API calls will break.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Import unified views
from .unified_views import (
    UnifiedThreatFeedViewSet, 
    UnifiedDashboardViewSet,
    UnifiedCollectionViewSet
)

# Import existing views to preserve backward compatibility
from ..api.threat_feed_views import ThreatFeedViewSet
from ..simple_auth_views import login_view, system_health, alert_statistics
from ..api_extensions import (
    list_organizations, organization_types, create_organization, organization_detail,
    deactivate_organization, reactivate_organization,
    trust_groups, trust_levels, trust_metrics, trust_relationships, trust_relationships_detail, 
    trust_overview, list_users, create_user, user_detail, change_username
)

# Import Trust system views (if available)
try:
    from core_ut.user_management.views import (
        AuthenticationViewSet,
        UserViewSet, 
        OrganizationViewSet,
        AdminViewSet
    )
    from core_ut.trust.views_ut import (
        TrustRelationshipViewSet,
        TrustGroupViewSet,
        TrustMetricsViewSet,
        TrustLevelViewSet
    )
    TRUST_VIEWS_AVAILABLE = True
except ImportError:
    TRUST_VIEWS_AVAILABLE = False


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint providing navigation to all available endpoints"""
    
    base_url = request.build_absolute_uri('/api/v1/')
    
    endpoints = {
        "message": "CRISP Unified API - Threat Intelligence and Trust Management Platform",
        "version": "1.0",
        "documentation": base_url + "docs/",
        "authentication": {
            "login": base_url + "auth/login/",
            "refresh": base_url + "auth/refresh/",
            "logout": base_url + "auth/logout/"
        },
        "threat_intelligence": {
            "feeds": base_url + "threat-feeds/",
            "indicators": base_url + "indicators/",  # To be implemented
            "collections": base_url + "collections/",
            "dashboard": base_url + "dashboard/overview/"
        },
        "user_management": {
            "users": base_url + "users/",
            "organizations": base_url + "organizations/",
            "admin": base_url + "admin/"
        },
        "trust_management": {
            "relationships": base_url + "trust/relationships/",
            "groups": base_url + "trust/groups/",
            "levels": base_url + "trust/levels/",
            "metrics": base_url + "trust/metrics/"
        },
        "legacy_endpoints": {
            "note": "All existing API endpoints are preserved for backward compatibility",
            "core_threat_feeds": "/api/threat-feeds/",
            "status": "/api/status/"
        }
    }
    
    return Response(endpoints)


# Create unified router
router = DefaultRouter()

# Register unified views
router.register(r'threat-feeds', UnifiedThreatFeedViewSet, basename='unified-threat-feeds')
router.register(r'collections', UnifiedCollectionViewSet, basename='unified-collections')
router.register(r'dashboard', UnifiedDashboardViewSet, basename='unified-dashboard')

# Register Trust system views if available
if TRUST_VIEWS_AVAILABLE:
    router.register(r'auth', AuthenticationViewSet, basename='auth')
    router.register(r'users', UserViewSet, basename='users')
    router.register(r'organizations', OrganizationViewSet, basename='organizations')
    router.register(r'admin', AdminViewSet, basename='admin')
    
    # Trust management endpoints
    router.register(r'trust/relationships', TrustRelationshipViewSet, basename='trust-relationships')
    router.register(r'trust/groups', TrustGroupViewSet, basename='trust-groups')
    router.register(r'trust/levels', TrustLevelViewSet, basename='trust-levels')
    router.register(r'trust/metrics', TrustMetricsViewSet, basename='trust-metrics')


# URL patterns for unified API
unified_patterns = [
    # API root
    path('', api_root, name='api-root'),
    
    # Router-based endpoints
    path('', include(router.urls)),
    
    # Explicit endpoint mappings for better URL control
    # Authentication endpoints
    path('auth/login/', AuthenticationViewSet.as_view({'post': 'login'}), name='auth-login') if TRUST_VIEWS_AVAILABLE else path('auth/login/', api_root),
    path('auth/register/', AuthenticationViewSet.as_view({'post': 'register'}), name='auth-register') if TRUST_VIEWS_AVAILABLE else path('auth/register/', api_root),
    path('auth/logout/', AuthenticationViewSet.as_view({'post': 'logout'}), name='auth-logout') if TRUST_VIEWS_AVAILABLE else path('auth/logout/', api_root),
    path('auth/refresh/', AuthenticationViewSet.as_view({'post': 'refresh'}), name='auth-refresh') if TRUST_VIEWS_AVAILABLE else path('auth/refresh/', api_root),
    path('auth/verify/', AuthenticationViewSet.as_view({'get': 'verify'}), name='auth-verify') if TRUST_VIEWS_AVAILABLE else path('auth/verify/', api_root),
    
    # Dashboard endpoints
    path('dashboard/overview/', UnifiedDashboardViewSet.as_view({'get': 'overview'}), name='dashboard-overview'),
    
    # Threat intelligence endpoints
    path('threat-feeds/external/', UnifiedThreatFeedViewSet.as_view({'get': 'external'}), name='threat-feeds-external'),
    path('threat-feeds/collections/', UnifiedThreatFeedViewSet.as_view({'get': 'available_collections'}), name='threat-feeds-collections'),
    path('threat-feeds/<int:pk>/consume/', UnifiedThreatFeedViewSet.as_view({'post': 'consume'}), name='threat-feeds-consume'),
    path('threat-feeds/<int:pk>/status/', UnifiedThreatFeedViewSet.as_view({'get': 'status'}), name='threat-feeds-status'),
    path('threat-feeds/<int:pk>/test/', UnifiedThreatFeedViewSet.as_view({'get': 'test_connection'}), name='threat-feeds-test'),
    
    # Collection endpoints
    path('collections/<uuid:pk>/objects/', UnifiedCollectionViewSet.as_view({'get': 'objects'}), name='collections-objects'),
    path('collections/<uuid:pk>/bundle/', UnifiedCollectionViewSet.as_view({'post': 'generate_bundle'}), name='collections-bundle'),
]


# URL patterns that preserve ALL existing endpoints
urlpatterns = [
    # NEW: Unified API v1 endpoints
    path('v1/', include(unified_patterns)),
    
    # PRESERVED: Existing Core system endpoints (backward compatibility)
    path('threat-feeds/', include([
        path('', ThreatFeedViewSet.as_view({'get': 'list', 'post': 'create'}), name='core-threat-feeds-list'),
        path('<int:pk>/', ThreatFeedViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='core-threat-feeds-detail'),
        path('<int:pk>/consume/', ThreatFeedViewSet.as_view({'post': 'consume'}), name='core-threat-feeds-consume'),
        path('<int:pk>/status/', ThreatFeedViewSet.as_view({'get': 'status'}), name='core-threat-feeds-status'),
        path('<int:pk>/test_connection/', ThreatFeedViewSet.as_view({'get': 'test_connection'}), name='core-threat-feeds-test'),
        path('external/', ThreatFeedViewSet.as_view({'get': 'external'}), name='core-threat-feeds-external'),
        path('available_collections/', ThreatFeedViewSet.as_view({'get': 'available_collections'}), name='core-threat-feeds-available-collections'),
    ])),
    
    # Status endpoint
    path('status/', include('core.urls')),
]


# Additional preserved endpoints from main URL configuration
legacy_preserved_patterns = [
    # These patterns preserve the exact URLs from crisp_settings/urls.py
    
    # Simple auth endpoints for frontend (PRESERVED)
    path('v1/auth/login/', login_view, name='preserved-login'),
    
    # Organizations endpoints (PRESERVED - keep exact URLs)
    path('v1/organizations/list_organizations/', list_organizations, name='preserved-list-organizations'),
    path('v1/organizations/types/', organization_types, name='preserved-organization-types'),
    path('v1/organizations/create_organization/', create_organization, name='preserved-create-organization'),
    path('v1/organizations/<str:organization_id>/get_organization/', organization_detail, name='preserved-get-organization'),
    path('v1/organizations/<str:organization_id>/update_organization/', organization_detail, name='preserved-update-organization'),
    path('v1/organizations/<str:organization_id>/delete_organization/', organization_detail, name='preserved-delete-organization'),
    path('v1/organizations/<str:organization_id>/', organization_detail, name='preserved-organization-detail'),
    path('v1/organizations/<str:organization_id>/deactivate_organization/', deactivate_organization, name='preserved-deactivate-organization'),
    path('v1/organizations/<str:organization_id>/reactivate_organization/', reactivate_organization, name='preserved-reactivate-organization'),
    
    # Trust management endpoints (PRESERVED)
    path('v1/trust/groups/', trust_groups, name='preserved-trust-groups'),
    path('v1/trust/levels/', trust_levels, name='preserved-trust-levels'),
    path('v1/trust/metrics/', trust_metrics, name='preserved-trust-metrics'),
    path('v1/trust/relationships/', trust_relationships, name='preserved-trust-relationships'),
    path('v1/trust/relationships/<int:relationship_id>/', trust_relationships_detail, name='preserved-trust-relationship-detail'),
    
    # Admin endpoints (PRESERVED)
    path('v1/admin/trust_overview/', trust_overview, name='preserved-trust-overview'),
    path('v1/admin/system_health/', system_health, name='preserved-system-health'),
    path('v1/alerts/statistics/', alert_statistics, name='preserved-alert-statistics'),
    path('v1/users/list/', list_users, name='preserved-list-users'),
    
    # User management endpoints (PRESERVED)
    path('v1/users/create_user/', create_user, name='preserved-create-user'),
    path('v1/users/<int:user_id>/get_user/', user_detail, name='preserved-get-user'),
    path('v1/users/<int:user_id>/update_user/', user_detail, name='preserved-update-user'),
    path('v1/users/<int:user_id>/delete_user/', user_detail, name='preserved-delete-user'),
    path('v1/users/<int:user_id>/change_username/', change_username, name='preserved-change-username'),
]


# Complete URL configuration
api_urlpatterns = urlpatterns + legacy_preserved_patterns


# Export patterns for use in main URL configuration
__all__ = ['api_urlpatterns', 'router', 'unified_patterns']
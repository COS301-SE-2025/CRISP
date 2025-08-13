"""URL configuration for crisp_settings project"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework import routers
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from core.api.threat_feed_views import ThreatFeedViewSet
from core.api.indicator_views import IndicatorViewSet
from core.viewing.home import home
from core.simple_auth_views import login_view, system_health, alert_statistics, send_test_email, test_gmail_connection, send_alert_test_email, get_user_profile, get_user_statistics, get_organizations_simple
from core.api_extensions import (
    list_organizations, organization_types, create_organization, organization_detail,
    deactivate_organization, reactivate_organization,
    trust_groups, trust_levels, trust_metrics, trust_relationships, trust_relationships_detail, 
    trust_overview, list_users, create_user, user_detail, change_username
)
# Simple API endpoints
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root_v1(request):
    """API v1 root endpoint"""
    return Response({
        "message": "CRISP API v1",
        "version": "1.0",
        "endpoints": {
            "authentication": "/api/v1/auth/",
            "dashboard": "/api/v1/dashboard/",
            "threat_feeds": "/api/v1/threat-feeds/",
            "organizations": "/api/v1/organizations/",
            "users": "/api/v1/users/",
            "trust": "/api/v1/trust/",
            "admin": "/api/v1/admin/"
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """Dashboard overview endpoint"""
    return Response({
        "dashboard": "overview",
        "user": request.user.username,
        "timestamp": timezone.now().isoformat(),
        "stats": {
            "total_feeds": 1,
            "total_indicators": 13321,
            "active_users": 771
        }
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def unified_threat_feeds_external(request):
    """Unified external threat feeds endpoint"""
    return Response({
        "external_feeds": [
            {
                "id": 1,
                "name": "AlienVault OTX",
                "url": "https://otx.alienvault.com",
                "status": "active",
                "last_sync": "2025-08-13T06:54:45Z"
            }
        ]
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def unified_threat_feeds_collections(request):
    """Unified threat feeds collections endpoint"""
    return Response({
        "collections": [
            {
                "id": "user_AlienVault",
                "name": "AlienVault Collection", 
                "description": "AlienVault OTX threat intelligence",
                "objects_count": 13321
            }
        ]
    })

# Set up REST API router
router = routers.DefaultRouter()
router.register(r'threat-feeds', ThreatFeedViewSet, basename='threat-feed')
router.register(r'indicators', IndicatorViewSet, basename='indicator')

# Redirect to admin by default
def redirect_to_admin(request):
    return redirect('/admin/')

urlpatterns = [
    path('', home, name='home'),  # Home page
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/status/', include('core.urls')),
    
    # Simple auth endpoints for frontend
    path('api/v1/auth/login/', login_view, name='api-login'),
    path('api/v1/admin/system_health/', system_health, name='system-health'),
    path('api/v1/alerts/statistics/', alert_statistics, name='alert-statistics'),
    path('api/v1/alerts/test-connection/', test_gmail_connection, name='test-gmail-connection'),
    path('api/v1/alerts/test-email/', send_alert_test_email, name='send-alert-test-email'),
    path('api/v1/email/send-test/', send_test_email, name='send-test-email'),
    path('api/v1/users/profile/', get_user_profile, name='user-profile'),
    path('api/v1/users/statistics/', get_user_statistics, name='user-statistics'),
    
    # Organizations endpoints
    path('api/v1/organizations/list_organizations/', list_organizations, name='list-organizations'),
    path('api/v1/organizations/types/', organization_types, name='organization-types'),
    path('api/v1/organizations/create_organization/', create_organization, name='create-organization'),
    path('api/v1/organizations/<str:organization_id>/get_organization/', organization_detail, name='get-organization'),
    path('api/v1/organizations/<str:organization_id>/update_organization/', organization_detail, name='update-organization'),
    path('api/v1/organizations/<str:organization_id>/delete_organization/', organization_detail, name='delete-organization'),
    path('api/v1/organizations/<str:organization_id>/', organization_detail, name='organization-detail'),
    path('api/v1/organizations/<str:organization_id>/deactivate_organization/', deactivate_organization, name='deactivate-organization'),
    path('api/v1/organizations/<str:organization_id>/reactivate_organization/', reactivate_organization, name='reactivate-organization'),
    
    # Trust management endpoints
    path('api/v1/trust/groups/', trust_groups, name='trust-groups'),
    path('api/v1/trust/levels/', trust_levels, name='trust-levels'),
    path('api/v1/trust/metrics/', trust_metrics, name='trust-metrics'),
    path('api/v1/trust/relationships/', trust_relationships, name='trust-relationships'),
    path('api/v1/trust/relationships/<int:relationship_id>/', trust_relationships_detail, name='trust-relationship-detail'),
    
    # Admin endpoints
    path('api/v1/admin/trust_overview/', trust_overview, name='trust-overview'),
    path('api/v1/users/list/', list_users, name='list-users'),
    
    # User management endpoints
    path('api/v1/users/create_user/', create_user, name='create-user'),
    path('api/v1/users/<int:user_id>/get_user/', user_detail, name='get-user'),
    path('api/v1/users/<int:user_id>/update_user/', user_detail, name='update-user'),
    path('api/v1/users/<int:user_id>/delete_user/', user_detail, name='delete-user'),
    path('api/v1/users/<int:user_id>/change_username/', change_username, name='change-username'),
    
    
    # Temporarily disabled until imports are fixed  
    # path('api/v1/', include('core_ut.user_management.urls_ut')),
    path('taxii2/', include('core.taxii.urls')),
    
    # Add missing unified API endpoints
    path('api/v1/', api_root_v1, name='api-v1-root'),
    path('api/v1/dashboard/overview/', dashboard_overview, name='dashboard-overview'),
    path('api/v1/threat-feeds/external/', unified_threat_feeds_external, name='unified-threat-feeds-external'),
    path('api/v1/threat-feeds/collections/', unified_threat_feeds_collections, name='unified-threat-feeds-collections'),
]
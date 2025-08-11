"""URL configuration for crisp_settings project"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework import routers
from core.api.threat_feed_views import ThreatFeedViewSet
from core.viewing.home import home
from core.simple_auth_views import login_view, system_health, alert_statistics
from core.api_extensions import (
    list_organizations, organization_types, create_organization, organization_detail,
    deactivate_organization, reactivate_organization,
    trust_groups, trust_levels, trust_metrics, trust_relationships, trust_relationships_detail, 
    trust_overview, list_users, create_user, user_detail, change_username
)

# Import unified API configuration
from core.api.unified_urls import api_urlpatterns as unified_api_urls

# Set up REST API router for legacy endpoints
router = routers.DefaultRouter()
router.register(r'threat-feeds', ThreatFeedViewSet, basename='threat-feed')

# Redirect to admin by default
def redirect_to_admin(request):
    return redirect('/admin/')

urlpatterns = [
    path('', home, name='home'),  # Home page
    path('admin/', admin.site.urls),
    
    # NEW UNIFIED API (Primary API interface)
    path('api/', include(unified_api_urls)),
    
    # LEGACY ENDPOINTS (Preserved for backward compatibility)
    # Legacy Core API router
    path('api/', include(router.urls)),
    path('api/status/', include('core.urls')),
    
    # Legacy Simple auth endpoints for frontend
    path('api/v1/auth/login/', login_view, name='api-login'),
    path('api/v1/admin/system_health/', system_health, name='system-health'),
    path('api/v1/alerts/statistics/', alert_statistics, name='alert-statistics'),
    
    # Legacy Organizations endpoints
    path('api/v1/organizations/list_organizations/', list_organizations, name='list-organizations'),
    path('api/v1/organizations/types/', organization_types, name='organization-types'),
    path('api/v1/organizations/create_organization/', create_organization, name='create-organization'),
    path('api/v1/organizations/<str:organization_id>/get_organization/', organization_detail, name='get-organization'),
    path('api/v1/organizations/<str:organization_id>/update_organization/', organization_detail, name='update-organization'),
    path('api/v1/organizations/<str:organization_id>/delete_organization/', organization_detail, name='delete-organization'),
    path('api/v1/organizations/<str:organization_id>/', organization_detail, name='organization-detail'),
    path('api/v1/organizations/<str:organization_id>/deactivate_organization/', deactivate_organization, name='deactivate-organization'),
    path('api/v1/organizations/<str:organization_id>/reactivate_organization/', reactivate_organization, name='reactivate-organization'),
    
    # Legacy Trust management endpoints
    path('api/v1/trust/groups/', trust_groups, name='trust-groups'),
    path('api/v1/trust/levels/', trust_levels, name='trust-levels'),
    path('api/v1/trust/metrics/', trust_metrics, name='trust-metrics'),
    path('api/v1/trust/relationships/', trust_relationships, name='trust-relationships'),
    path('api/v1/trust/relationships/<int:relationship_id>/', trust_relationships_detail, name='trust-relationship-detail'),
    
    # Legacy Admin endpoints
    path('api/v1/admin/trust_overview/', trust_overview, name='trust-overview'),
    path('api/v1/users/list/', list_users, name='list-users'),
    
    # Legacy User management endpoints
    path('api/v1/users/create_user/', create_user, name='create-user'),
    path('api/v1/users/<int:user_id>/get_user/', user_detail, name='get-user'),
    path('api/v1/users/<int:user_id>/update_user/', user_detail, name='update-user'),
    path('api/v1/users/<int:user_id>/delete_user/', user_detail, name='delete-user'),
    path('api/v1/users/<int:user_id>/change_username/', change_username, name='change-username'),
    
    # Legacy Trust system authentication and user management
    path('api/v1/auth/', include('core_ut.user_management.urls_ut')),  # Authentication endpoints
    path('api/v1/trust/', include('core_ut.trust.urls_ut')),  # Trust management endpoints
    path('api/v1/alerts/', include('core_ut.alerts.alerts_urls')),  # Alert system endpoints
    
    # TAXII endpoints
    path('taxii2/', include('core.taxii.urls')),
]
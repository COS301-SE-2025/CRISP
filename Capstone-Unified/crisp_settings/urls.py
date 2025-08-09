"""URL configuration for crisp_settings project"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework import routers
from core.api.threat_feed_views import ThreatFeedViewSet
from core.viewing.home import home
from core.simple_auth_views import login_view, system_health, alert_statistics
from core.api_extensions import (
    list_organizations, organization_types, trust_groups, trust_levels, 
    trust_metrics, trust_relationships, trust_overview, list_users
)

# Set up REST API router
router = routers.DefaultRouter()
router.register(r'threat-feeds', ThreatFeedViewSet, basename='threat-feed')

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
    
    # Organizations endpoints
    path('api/v1/organizations/list_organizations/', list_organizations, name='list-organizations'),
    path('api/v1/organizations/types/', organization_types, name='organization-types'),
    
    # Trust management endpoints
    path('api/v1/trust/groups/', trust_groups, name='trust-groups'),
    path('api/v1/trust/levels/', trust_levels, name='trust-levels'),
    path('api/v1/trust/metrics/', trust_metrics, name='trust-metrics'),
    path('api/v1/trust/relationships/', trust_relationships, name='trust-relationships'),
    
    # Admin endpoints
    path('api/v1/admin/trust_overview/', trust_overview, name='trust-overview'),
    path('api/v1/users/list/', list_users, name='list-users'),
    
    # Temporarily disabled until imports are fixed
    # path('api/v1/', include('core_ut.urls_ut')),  # User management and trust APIs
    path('taxii2/', include('core.taxii.urls')),
]
"""URL configuration for crisp_settings project"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework import routers
from core.api.threat_feed_views import ThreatFeedViewSet
from core.viewing.home import home
from core.simple_auth_views import login_view, system_health, alert_statistics, send_test_email, test_gmail_connection, send_alert_test_email, get_user_profile, get_user_statistics, get_organizations_simple
from core.api_extensions import (
    list_organizations, organization_types, create_organization, organization_detail,
    deactivate_organization, reactivate_organization,
    trust_groups, trust_levels, trust_metrics, trust_relationships, trust_relationships_detail, 
    trust_overview, list_users, create_user, user_detail, change_username
)

# Import admin modules to ensure all models are registered
from . import admin as crisp_admin

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
    path('api/v1/trust/relationships/<uuid:relationship_id>/', trust_relationships_detail, name='trust-relationship-detail'),
    
    # Admin endpoints
    path('api/v1/admin/trust_overview/', trust_overview, name='trust-overview'),
    path('api/v1/users/list/', list_users, name='list-users'),
    
    # User management endpoints
    path('api/v1/users/create_user/', create_user, name='create-user'),
    path('api/v1/users/<uuid:user_id>/get_user/', user_detail, name='get-user'),
    path('api/v1/users/<uuid:user_id>/update_user/', user_detail, name='update-user'),
    path('api/v1/users/<uuid:user_id>/delete_user/', user_detail, name='delete-user'),
    path('api/v1/users/<uuid:user_id>/change_username/', change_username, name='change-username'),
    
    
    # Trust and User Management URLs
    path('api/v1/ut/', include('core_ut.urls_ut')),
    path('taxii2/', include('core.taxii.urls')),
]
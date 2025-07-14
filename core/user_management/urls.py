from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthenticationViewSet,
    UserViewSet,
    OrganizationViewSet,
    AdminViewSet
)

# Create router for API endpoints
router = DefaultRouter()

# Register viewsets with router
router.register(r'auth', AuthenticationViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='users')
router.register(r'organizations', OrganizationViewSet, basename='organizations')
router.register(r'admin', AdminViewSet, basename='admin')

# URL patterns
urlpatterns = [
    # API endpoints
    path('api/v1/', include(router.urls)),
    
    # Direct endpoint mappings for specific actions
    path('api/v1/auth/login/', AuthenticationViewSet.as_view({'post': 'login'}), name='auth-login'),
    path('api/v1/auth/logout/', AuthenticationViewSet.as_view({'post': 'logout'}), name='auth-logout'),
    path('api/v1/auth/refresh/', AuthenticationViewSet.as_view({'post': 'refresh'}), name='auth-refresh'),
    path('api/v1/auth/verify/', AuthenticationViewSet.as_view({'get': 'verify'}), name='auth-verify'),
    path('api/v1/auth/sessions/', AuthenticationViewSet.as_view({'get': 'sessions'}), name='auth-sessions'),
    path('api/v1/auth/revoke-session/', AuthenticationViewSet.as_view({'post': 'revoke_session'}), name='auth-revoke-session'),
    path('api/v1/auth/change-password/', AuthenticationViewSet.as_view({'post': 'change_password'}), name='auth-change-password'),
    path('api/v1/auth/dashboard/', AuthenticationViewSet.as_view({'get': 'dashboard'}), name='auth-dashboard'),
    
    # User management endpoints
    path('api/v1/users/create/', UserViewSet.as_view({'post': 'create_user'}), name='users-create'),
    path('api/v1/users/list/', UserViewSet.as_view({'get': 'list_users'}), name='users-list'),
    path('api/v1/users/profile/', UserViewSet.as_view({'get': 'profile', 'put': 'update_profile', 'patch': 'update_profile'}), name='users-profile'),
    path('api/v1/users/statistics/', UserViewSet.as_view({'get': 'statistics'}), name='users-statistics'),
    path('api/v1/users/<uuid:pk>/', UserViewSet.as_view({'get': 'get_user', 'put': 'update_user', 'patch': 'update_user'}), name='users-detail'),
    path('api/v1/users/<uuid:pk>/deactivate/', UserViewSet.as_view({'post': 'deactivate_user'}), name='users-deactivate'),
    
    # Organization management endpoints
    path('api/v1/organizations/create/', OrganizationViewSet.as_view({'post': 'create_organization'}), name='organizations-create'),
    path('api/v1/organizations/list/', OrganizationViewSet.as_view({'get': 'list_organizations'}), name='organizations-list'),
    path('api/v1/organizations/statistics/', OrganizationViewSet.as_view({'get': 'statistics'}), name='organizations-statistics'),
    path('api/v1/organizations/trust-metrics/', OrganizationViewSet.as_view({'get': 'trust_metrics'}), name='organizations-trust-metrics'),
    path('api/v1/organizations/<uuid:pk>/', OrganizationViewSet.as_view({'get': 'get_organization', 'put': 'update_organization', 'patch': 'update_organization'}), name='organizations-detail'),
    path('api/v1/organizations/<uuid:pk>/deactivate/', OrganizationViewSet.as_view({'post': 'deactivate_organization'}), name='organizations-deactivate'),
    path('api/v1/organizations/<uuid:pk>/trust-relationship/', OrganizationViewSet.as_view({'post': 'create_trust_relationship'}), name='organizations-trust-relationship'),
    
    # Admin endpoints
    path('api/v1/admin/dashboard/', AdminViewSet.as_view({'get': 'dashboard'}), name='admin-dashboard'),
    path('api/v1/admin/system-health/', AdminViewSet.as_view({'get': 'system_health'}), name='admin-system-health'),
    path('api/v1/admin/audit-logs/', AdminViewSet.as_view({'get': 'audit_logs'}), name='admin-audit-logs'),
    path('api/v1/admin/trust-overview/', AdminViewSet.as_view({'get': 'trust_overview'}), name='admin-trust-overview'),
    path('api/v1/admin/cleanup-sessions/', AdminViewSet.as_view({'post': 'cleanup_expired_sessions'}), name='admin-cleanup-sessions'),
    path('api/v1/admin/users/<uuid:pk>/unlock/', AdminViewSet.as_view({'post': 'unlock_account'}), name='admin-unlock-account'),
    
    # Comprehensive audit endpoints
    path('api/v1/admin/comprehensive-audit-logs/', AdminViewSet.as_view({'get': 'comprehensive_audit_logs'}), name='admin-comprehensive-audit-logs'),
    path('api/v1/admin/users/<uuid:pk>/activity-summary/', AdminViewSet.as_view({'get': 'user_activity_summary'}), name='admin-user-activity-summary'),
    path('api/v1/admin/security-events/', AdminViewSet.as_view({'get': 'security_events'}), name='admin-security-events'),
    path('api/v1/admin/audit-statistics/', AdminViewSet.as_view({'get': 'audit_statistics'}), name='admin-audit-statistics'),
]

# API documentation patterns
api_patterns = [
    path('user-management/', include(urlpatterns)),
]
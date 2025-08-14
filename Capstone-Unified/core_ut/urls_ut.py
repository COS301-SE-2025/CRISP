from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .user_management.views.auth_views import AuthenticationViewSet
from .user_management.views.admin_views import AdminViewSet
from .user_management.views.organization_views import OrganizationViewSet
from .user_management.views.user_views import UserViewSet

router = DefaultRouter()
router.register(r'auth', AuthenticationViewSet, basename='auth')
router.register(r'admin', AdminViewSet, basename='admin')
router.register(r'organizations', OrganizationViewSet, basename='organizations')
router.register(r'users', UserViewSet, basename='user')

# Main URL configuration for the core application
# All application URLs are now correctly nested under /api/v1/
urlpatterns = [
    # All viewsets are registered in this single router
    path('', include(router.urls)),
    # Trust management system URLs
    path('trust/', include('core_ut.trust.urls_ut')),
    # Alerts system URLs (temporarily disabled)  
    # path('alerts/', include('core_ut.alerts.alerts_urls')),
    # User management URLs
    path('user-management/', include('core_ut.user_management.urls_ut')),
]
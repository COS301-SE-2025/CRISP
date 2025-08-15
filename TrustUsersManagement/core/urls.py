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
    path('api/v1/', include([
        # All viewsets are now registered in this single router
        path('', include(router.urls)),
        # Trust management system URLs (e.g., /api/v1/trust/relationships/)
        path('trust/', include('core.trust.urls')),
        # Alerts system URLs (e.g., /api/v1/alerts/)
        path('alerts/', include('core.alerts.alerts_urls')),
    ])),
    # User management URLs with explicit endpoints
    path('', include('core.user_management.urls')),
]
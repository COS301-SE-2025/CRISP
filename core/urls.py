from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .user_management.views.auth_views import AuthenticationViewSet

router = DefaultRouter()
router.register(r'auth', AuthenticationViewSet, basename='auth')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]

# Main URL configuration for the core application
urlpatterns += [
    # User management system URLs
    path('', include('core.user_management.urls')),
    
    # Trust management system URLs  
    path('trust/', include('core.trust.urls')),

    # Alerts system URLs
    path('api/v1/alerts/', include('core.alerts.alerts_urls')),
]
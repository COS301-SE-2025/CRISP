"""URL configuration for crisp_settings project"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework import routers
from core.api.threat_feed_views import ThreatFeedViewSet
from core.viewing.home import home
from core.simple_auth_views import login_view, system_health, alert_statistics

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
    
    # Temporarily disabled until imports are fixed
    # path('api/v1/', include('core_ut.urls_ut')),  # User management and trust APIs
    path('taxii2/', include('core.taxii.urls')),
]
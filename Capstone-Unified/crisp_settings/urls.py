"""
URL configuration for CRISP Unified Platform
Integrates Publication System + Trust Users Management
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers

# Publication System Imports
from core.api.threat_feed_views import ThreatFeedViewSet
from core.viewing.home import home

# Set up REST API router for Publication System
router = routers.DefaultRouter()
router.register(r'threat-feeds', ThreatFeedViewSet, basename='threat-feed')

@csrf_exempt
@require_http_methods(["GET"])
def api_health_check(request):
    """Health check endpoint for the unified CRISP platform"""
    return JsonResponse({
        'status': 'healthy',
        'platform': 'CRISP Unified Platform',
        'version': '1.0.0',
        'components': {
            'publication_system': 'active',
            'trust_management': 'active',
            'user_management': 'active',
            'email_alerts': 'active'
        }
    })

@csrf_exempt
@require_http_methods(["GET"])
def api_info(request):
    """API information endpoint"""
    return JsonResponse({
        'name': 'CRISP Unified Platform API',
        'version': '1.0.0',
        'description': 'Unified API for threat intelligence sharing and trust management',
        'endpoints': {
            'publication_system': {
                'threat_feeds': '/api/threat-feeds/',
                'status': '/api/status/',
                'taxii': '/taxii2/'
            },
            'user_management': {
                'auth': '/api/v1/auth/',
                'users': '/api/v1/users/',
                'organizations': '/api/v1/organizations/'
            },
            'trust_management': {
                'relationships': '/api/v1/trust/relationships/',
                'groups': '/api/v1/trust/groups/',
                'metrics': '/api/v1/trust/metrics/',
                'levels': '/api/v1/trust/levels/'
            },
            'email_alerts': {
                'statistics': '/api/v1/alerts/statistics/',
                'test_connection': '/api/v1/alerts/test-connection/'
            },
            'admin': {
                'system_health': '/api/v1/admin/system_health/',
                'trust_overview': '/api/v1/admin/trust_overview/'
            }
        }
    })

urlpatterns = [
    # MAIN PAGES
    path('', home, name='home'),
    path('admin/', admin.site.urls),

    # API HEALTH AND INFO
    path('api/health/', api_health_check, name='api-health'),
    path('api/info/', api_info, name='api-info'),

    # PUBLICATION SYSTEM APIs (Core)
    path('api/', include(router.urls)),  # Threat feeds API
    path('api/status/', include('core.urls')),  # Core status endpoints
    path('taxii2/', include('core.taxii.urls')),  # TAXII protocol endpoints

    # TRUST USERS MANAGEMENT SYSTEM - Complete Integration
    path('api/v1/', include('core_ut.urls_ut')),  # ALL Trust Management APIs
]

# Add debug toolbar for development
try:
    from django.conf import settings
    if settings.DEBUG:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
except ImportError:
    pass
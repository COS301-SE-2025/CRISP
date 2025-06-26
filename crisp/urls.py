"""CRISP Integrated URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from core.views.home import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    
    # Core user management endpoints (for test compatibility)
    path('api/', include('core.urls')),
    
    # Additional endpoints 
    path('api/v1/', include([
        path('trust/', include('core.api.trust_api.urls')),
        path('threat-intel/', include('core.urls.threat_intel')),
    ])),
    
    # Direct routing for some test paths
    path('auth/', include('core.urls')),
    path('viewer/', include([
        path('dashboard/', home, name='viewer_dashboard'),
    ])),
    path('debug/', include([
        path('auth/', home, name='debug_auth'),
    ])),
]
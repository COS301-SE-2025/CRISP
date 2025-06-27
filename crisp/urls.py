"""CRISP Integrated URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from core.views.home import home
from core.views.auth_views import LoginPageView, ViewerDashboardView, DebugAuthView

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
    
    # Direct routing for some test paths that expect template views
    path('auth/', include([
        path('login/', LoginPageView.as_view(), name='auth_login_page'),
        path('', include('core.urls')),  # Include other auth URLs
    ])),
    path('viewer/', include([
        path('dashboard/', ViewerDashboardView.as_view(), name='viewer_dashboard'),
    ])),
    path('debug/', include([
        path('auth/', DebugAuthView.as_view(), name='debug_auth'),
    ])),
]
"""URL configuration for crisp_unified project"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from core.viewing.home import home
from core.health_check import health_check

# Redirect to admin by default
def redirect_to_admin(request):
    return redirect('/admin/')

urlpatterns = [
    path('', home, name='home'),  # Home page
    path('health/', health_check, name='health_check'),  # Health check endpoint
    path('admin/', admin.site.urls),
    
    # React Router routes - serve React app for all frontend routes
    path('dashboard/', home, name='dashboard'),
    path('login/', home, name='react-login'),
    path('user-management/', home, name='user-management'),
    path('trust-management/', home, name='trust-management'),
    path('register-user/', home, name='register-user'),
    path('forgot-password/', home, name='forgot-password'),
    path('reset-password/', home, name='reset-password'),
    path('construction/', home, name='construction'),
    
    # Unified API endpoints
    path('api/', include('core.urls')),
    
    # TAXII endpoints
    path('taxii2/', include('core.taxii.urls')),
    
    # Enhanced user management endpoints
    path('api/user-management/', include('core.user_management.urls_ut')),
    
    # Enhanced trust management endpoints
    path('api/trust-management/', include('core.trust_management.urls_ut')),
    
    # Alert management endpoints
    path('api/alerts/', include('core.alerts.alerts_urls')),
    
    # SOC (Security Operations Center) endpoints
    path('api/soc/', include('soc.urls')),
]
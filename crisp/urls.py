"""
Main URL configuration for integrated CRISP system
Combines UserManagement and TrustManagement URLs
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints for integrated system
    path('api/auth/', include('apps.user_management.urls')),
    path('api/trust/', include('apps.trust_management.urls')),
    path('api/core/', include('apps.core.urls')),
    
    # API documentation and browsable API
    path('api-auth/', include('rest_framework.urls')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add debug toolbar if available
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Customize admin
admin.site.site_header = "CRISP Administration"
admin.site.site_title = "CRISP Admin Portal"
admin.site.index_title = "Welcome to CRISP Administration"

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # User Management APIs
    path('api/auth/', include('UserManagement.urls')),
    
    # Trust Management APIs
    path('api/trust/', include('trust_management_app.urls')),
    
    # Threat Intelligence APIs
    path('api/threat-intel/', include('crisp_threat_intel.urls')),
    
    # TAXII 2.1 Server Endpoints
    path('taxii2/', include('crisp_threat_intel.taxii.urls')),
]
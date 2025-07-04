from django.urls import path, include

# Main URL configuration for the core application
urlpatterns = [
    # User management system URLs
    path('', include('core.user_management.urls')),
    
    # Trust management system URLs  
    path('trust/', include('core.trust.urls')),
]
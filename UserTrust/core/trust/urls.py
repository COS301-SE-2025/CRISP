from django.urls import path, include

# Trust management system URLs
urlpatterns = [
    # Trust system endpoints will be integrated via user management
    # This file provides a placeholder for future trust-specific endpoints
    # that are not covered by the user management integration
]

# API documentation patterns
api_patterns = [
    path('trust/', include(urlpatterns)),
]
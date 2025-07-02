"""
Trust Management URL Configuration

URL patterns for the CRISP Trust Management API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api.views import (
    TrustRelationshipViewSet,
    TrustLogViewSet,
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'relationships', TrustRelationshipViewSet, basename='trust-relationship')
router.register(r'logs', TrustLogViewSet, basename='trust-log')

# URL patterns
urlpatterns = [
    # API routes
    path('', include(router.urls)),
    
    # Additional custom endpoints can be added here
    # path('api/v1/trust/stats/', include('core.trust.api.stats_urls')),
    # path('api/v1/trust/export/', include('core.trust.api.export_urls')),
]

# Add app name for namespacing
app_name = 'trust'
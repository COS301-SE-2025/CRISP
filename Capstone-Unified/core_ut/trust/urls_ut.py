"""
URL configuration for Trust Management features
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import Trust ViewSets
try:
    from .views_ut import (
        TrustRelationshipViewSet,
        TrustGroupViewSet,
        TrustMetricsViewSet,
        TrustLevelViewSet
    )
    TRUST_VIEWS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Trust views not available: {e}")
    TRUST_VIEWS_AVAILABLE = False

# Trust management router
router = DefaultRouter()

if TRUST_VIEWS_AVAILABLE:
    router.register(r'relationships', TrustRelationshipViewSet, basename='trust-relationship')
    router.register(r'groups', TrustGroupViewSet, basename='trust-group')
    router.register(r'metrics', TrustMetricsViewSet, basename='trust-metrics')
    router.register(r'levels', TrustLevelViewSet, basename='trust-level')

urlpatterns = [
    path('', include(router.urls)),
]
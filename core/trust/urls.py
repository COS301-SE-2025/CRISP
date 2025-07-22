from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TrustRelationshipViewSet,
    TrustGroupViewSet,
    TrustMetricsViewSet
)

# Trust management system URLs
router = DefaultRouter()
router.register(r'relationships', TrustRelationshipViewSet, basename='trust-relationship')
router.register(r'groups', TrustGroupViewSet, basename='trust-group')
router.register(r'metrics', TrustMetricsViewSet, basename='trust-metrics')

urlpatterns = [
    path('', include(router.urls)),
]

# API documentation patterns
api_patterns = [
    path('trust/', include(urlpatterns)),
]
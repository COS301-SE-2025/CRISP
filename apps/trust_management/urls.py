"""
URL configuration for Trust Management app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from .views import TrustRelationshipViewSet, TrustGroupViewSet

router = DefaultRouter()
# router.register(r'relationships', TrustRelationshipViewSet)
# router.register(r'groups', TrustGroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Add specific trust endpoints here
]

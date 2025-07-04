"""
URL configuration for Core integration services
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from .views import IntegrationViewSet

router = DefaultRouter()
# router.register(r'integration', IntegrationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Add integration endpoints here
]

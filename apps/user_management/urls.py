"""
URL configuration for User Management app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from .views import UserViewSet, OrganizationViewSet

router = DefaultRouter()
# router.register(r'users', UserViewSet)
# router.register(r'organizations', OrganizationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Add specific auth endpoints here
]

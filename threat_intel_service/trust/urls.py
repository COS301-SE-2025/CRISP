from django.urls import path, include
from rest_framework.routers import DefaultRouter
from trust import views

# Create a router for ViewSet-based APIs
router = DefaultRouter()
router.register(r'relationships', views.TrustRelationshipViewSet)
router.register(r'groups', views.TrustGroupViewSet)
router.register(r'memberships', views.TrustGroupMembershipViewSet)

urlpatterns = [
    # Include the router's URLs
    path('', include(router.urls)),
]
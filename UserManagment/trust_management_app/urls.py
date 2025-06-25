"""
Trust Management URL Configuration

URL routing for trust management REST API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api.views.trust_views import TrustRelationshipViewSet, TrustLogViewSet
from .api.views.group_views import TrustGroupViewSet, TrustGroupMembershipViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'relationships', TrustRelationshipViewSet, basename='trustrelationship')
router.register(r'groups', TrustGroupViewSet, basename='trustgroup')
router.register(r'memberships', TrustGroupMembershipViewSet, basename='trustgroupmembership')
router.register(r'logs', TrustLogViewSet, basename='trustlog')

app_name = 'trust_management'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Custom endpoints (if needed for non-DRF views)
    # path('custom-endpoint/', views.custom_view, name='custom-endpoint'),
]

# URL patterns for different API operations:
#
# Trust Relationships:
# - GET /api/relationships/ - List relationships
# - POST /api/relationships/create_relationship/ - Create relationship
# - POST /api/relationships/approve_relationship/ - Approve relationship
# - POST /api/relationships/revoke_relationship/ - Revoke relationship
# - POST /api/relationships/check_trust/ - Check trust level
# - POST /api/relationships/test_intelligence_access/ - Test access
# - POST /api/relationships/update_trust_level/ - Update trust level
# - GET /api/relationships/get_sharing_organizations/ - Get sharing orgs
#
# Trust Groups:
# - GET /api/groups/ - List groups
# - POST /api/groups/create_group/ - Create group
# - POST /api/groups/join_group/ - Join group
# - POST /api/groups/leave_group/ - Leave group
# - GET /api/groups/{id}/members/ - Get group members
# - POST /api/groups/{id}/promote_member/ - Promote member
# - GET /api/groups/{id}/statistics/ - Get group statistics
# - GET /api/groups/public_groups/ - Get public groups
# - GET /api/groups/my_groups/ - Get user's groups
#
# Group Memberships:
# - GET /api/memberships/ - List memberships
# - GET /api/memberships/{id}/ - Get specific membership
# - PUT /api/memberships/{id}/ - Update membership
# - DELETE /api/memberships/{id}/ - Remove membership
#
# Trust Logs:
# - GET /api/logs/ - List trust activity logs
# - GET /api/logs/{id}/ - Get specific log entry
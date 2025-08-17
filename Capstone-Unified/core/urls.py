"""
Core URL Configuration - Unified CRISP System URLs
Includes all API endpoints for the integrated system
"""

from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from core.models.models import ThreatFeed, Indicator, TTPData, CustomUser, Organization
from core.api import auth_api, user_api, trust_api, organization_api

@api_view(['GET'])
def status_view(request):
    """System status endpoint"""
    return Response({
        'status': 'active',
        'app': 'CRISP Unified Platform',
        'version': '1.0.0',
        'threat_feeds': ThreatFeed.objects.count(),
        'indicators': Indicator.objects.count(),
        'ttps': TTPData.objects.count(),
        'users': CustomUser.objects.count(),
        'organizations': Organization.objects.count()
    })

# Authentication URLs
auth_urlpatterns = [
    path('login/', auth_api.CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('refresh/', TokenRefreshView.as_view(), name='auth_refresh'),
    path('register/', auth_api.register, name='auth_register'),
    path('logout/', auth_api.logout, name='auth_logout'),
    path('profile/', auth_api.profile, name='auth_profile'),
    path('profile/update/', auth_api.update_profile, name='auth_update_profile'),
    path('change-password/', auth_api.change_password, name='auth_change_password'),
    path('forgot-password/', auth_api.forgot_password, name='auth_forgot_password'),
    path('reset-password/', auth_api.reset_password, name='auth_reset_password'),
    path('verify-token/', auth_api.verify_token, name='auth_verify_token'),
]

# User Management URLs
user_urlpatterns = [
    path('', user_api.list_users, name='user_list'),
    path('create/', user_api.create_user, name='user_create'),
    path('<uuid:user_id>/', user_api.get_user, name='user_detail'),
    path('<uuid:user_id>/update/', user_api.update_user, name='user_update'),
    path('<uuid:user_id>/delete-permanently/', user_api.delete_user_permanently, name='user_delete_permanent'),
    path('<uuid:user_id>/deactivate/', user_api.deactivate_user, name='user_deactivate'),
    path('<uuid:user_id>/reactivate/', user_api.reactivate_user, name='user_reactivate'),
    path('invite/', user_api.invite_user, name='user_invite'),
    path('invitations/', user_api.list_invitations, name='invitation_list'),
    path('invitations/<uuid:invitation_id>/cancel/', user_api.cancel_invitation, name='invitation_cancel'),
]

# Trust Management URLs
trust_urlpatterns = [
    path('bilateral/', trust_api.list_bilateral_trusts, name='trust_bilateral_list'),
    path('bilateral/request/', trust_api.request_bilateral_trust, name='trust_bilateral_request'),
    path('bilateral/<uuid:trust_id>/respond/', trust_api.respond_bilateral_trust, name='trust_bilateral_respond'),
    path('bilateral/<uuid:trust_id>/update/', trust_api.update_bilateral_trust, name='trust_bilateral_update'),
    path('bilateral/<uuid:trust_id>/revoke/', trust_api.revoke_bilateral_trust, name='trust_bilateral_revoke'),
    path('level/<uuid:organization_id>/', trust_api.get_trust_level, name='trust_level'),
    path('levels/', trust_api.list_trust_levels, name='trust_levels_list'),
    path('community/', trust_api.list_community_trusts, name='trust_community_list'),
    path('dashboard/', trust_api.get_trust_dashboard, name='trust_dashboard'),
]

# Organization Management URLs
organization_urlpatterns = [
    path('', organization_api.list_organizations, name='organization_list'),
    path('types/', organization_api.get_organization_types, name='organization_types'),
    path('create/', organization_api.create_organization, name='organization_create'),
    path('<uuid:organization_id>/', organization_api.get_organization, name='organization_detail'),
    path('<uuid:organization_id>/update/', organization_api.update_organization, name='organization_update'),
    path('<uuid:organization_id>/delete-permanently/', organization_api.delete_organization_permanently, name='organization_delete_permanent'),
    path('<uuid:organization_id>/deactivate/', organization_api.deactivate_organization, name='organization_deactivate'),
    path('<uuid:organization_id>/reactivate/', organization_api.reactivate_organization, name='organization_reactivate'),
    path('<uuid:organization_id>/members/', organization_api.list_organization_members, name='organization_members'),
    path('<uuid:organization_id>/statistics/', organization_api.get_organization_statistics, name='organization_statistics'),
    path('<uuid:organization_id>/trust-relationships/', organization_api.get_organization_trust_relationships, name='organization_trust_relationships'),
]

# Main URL patterns
urlpatterns = [
    path('', status_view, name='core-status'),
    path('auth/', include(auth_urlpatterns)),
    path('users/', include(user_urlpatterns)),
    path('trust/', include(trust_urlpatterns)),
    path('organizations/', include(organization_urlpatterns)),
]
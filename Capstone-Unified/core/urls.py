"""
Core URL Configuration - Unified CRISP System URLs
Includes all API endpoints for the integrated system
"""

from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import routers # Import routers
from core.models.models import ThreatFeed, Indicator, TTPData, Organization
from core.user_management.models import CustomUser
from core.api import auth_api, user_api, trust_api, organization_api
from core.api.threat_feed_views import (
    ThreatFeedViewSet, # Import ThreatFeedViewSet
    indicators_list, indicators_export, indicators_bulk_import, indicator_update, indicator_delete, indicator_share, # Import indicator views
    indicator_generate_share_url, indicator_shared_access, sharing_permissions, # New sharing endpoints
    threat_activity_chart_data, system_health, recent_activities, # Import other views
    ttps_list, ttp_detail, mitre_matrix, ttp_trends, ttp_export,
    ttp_mitre_mapping, ttp_bulk_mapping, ttp_mapping_validation,
    ttp_auto_map_existing, ttp_technique_frequencies, ttp_tactic_frequencies,
    ttp_technique_trends, ttp_feed_comparison, ttp_seasonal_patterns,
    ttp_clear_aggregation_cache, ttp_filter_options, ttp_advanced_search,
    ttp_search_suggestions, ttp_matrix_cell_details, ttp_technique_details,
    ttp_export_csv, ttp_export_stix, virustotal_sync  # New plain Django export views and VirusTotal sync
)
from core.api.ttp_views import TTPExportView, MITREMatrixView
from core.api import reports_api

# Set up REST API router
router = routers.DefaultRouter()
router.register(r'threat-feeds', ThreatFeedViewSet, basename='threat-feed')


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
    path('connected/', organization_api.get_connected_organizations, name='organization_connected'),
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

# TTP URLs
ttp_urlpatterns = [
    path('', ttps_list, name='ttps-list'),
    path('mitre-matrix/', mitre_matrix, name='mitre-matrix'),
    path('trends/', ttp_trends, name='ttp-trends'),
    path('export/', ttp_export, name='ttp-export'),
    path('export-csv/', ttp_export_csv, name='ttp-export-csv'),  # New CSV export
    path('export-stix/', ttp_export_stix, name='ttp-export-stix'),  # New STIX export
    path('mitre-mapping/', ttp_mitre_mapping, name='ttp-mitre-mapping'),
    path('bulk-mapping/', ttp_bulk_mapping, name='ttp-bulk-mapping'),
    path('mapping-validation/', ttp_mapping_validation, name='ttp-mapping-validation'),
    path('auto-map-existing/', ttp_auto_map_existing, name='ttp-auto-map-existing'),
    path('technique-frequencies/', ttp_technique_frequencies, name='ttp-technique-frequencies'),
    path('tactic-frequencies/', ttp_tactic_frequencies, name='ttp-tactic-frequencies'),
    path('technique-trends/', ttp_technique_trends, name='ttp-technique-trends'),
    path('feed-comparison/', ttp_feed_comparison, name='ttp-feed-comparison'),
    path('seasonal-patterns/', ttp_seasonal_patterns, name='ttp-seasonal-patterns'),
    path('clear-aggregation-cache/', ttp_clear_aggregation_cache, name='ttp-clear-aggregation-cache'),
    path('filter-options/', ttp_filter_options, name='ttp-filter-options'),
    path('advanced-search/', ttp_advanced_search, name='ttp-advanced-search'),
    path('search-suggestions/', ttp_search_suggestions, name='ttp-search-suggestions'),
    path('matrix-cell-details/', ttp_matrix_cell_details, name='ttp-matrix-cell-details'),
    path('technique-details/<str:technique_id>/', ttp_technique_details, name='ttp-technique-details'),
    path('<int:ttp_id>/', ttp_detail, name='ttp-detail'),
]

# Threat Feed URLs (moved from crisp_unified/urls.py)
threat_feed_urlpatterns = [
    path('', include(router.urls)), # Include router URLs here
    path('indicators/', indicators_list, name='indicators-list'),
    path('indicators/export/', indicators_export, name='indicators-export'),
    path('indicators/bulk-import/', indicators_bulk_import, name='indicators-bulk-import'),
    path('indicators/<int:indicator_id>/update/', indicator_update, name='indicator-update'),
    path('indicators/<int:indicator_id>/delete/', indicator_delete, name='indicator-delete'),
    path('indicators/<int:indicator_id>/share/', indicator_share, name='indicator-share'),
    path('indicators/<int:indicator_id>/generate-share-url/', indicator_generate_share_url, name='indicator-generate-share-url'),
    path('indicators/shared/<str:share_token>/', indicator_shared_access, name='indicator-shared-access'),
    path('sharing-permissions/', sharing_permissions, name='sharing-permissions'),
    path('threat-activity-chart/', threat_activity_chart_data, name='threat-activity-chart'),
    path('system-health/', system_health, name='system-health'),
    path('recent-activities/', recent_activities, name='recent-activities'),
    path('virustotal/sync/', virustotal_sync, name='virustotal-sync'),  # VirusTotal sync endpoint
]

# Reports URLs
reports_urlpatterns = [
    path('education-sector-analysis/', reports_api.education_sector_analysis, name='reports_education_sector'),
    path('financial-sector-analysis/', reports_api.financial_sector_analysis, name='reports_financial_sector'),
    path('government-sector-analysis/', reports_api.government_sector_analysis, name='reports_government_sector'),
    path('status/', reports_api.report_status, name='reports_status'),
]

# Main URL patterns
urlpatterns = [
    path('', status_view, name='core-status'),
    path('auth/', include(auth_urlpatterns)),
    path('users/', include(user_urlpatterns)),
    path('trust/', include(trust_urlpatterns)),
    path('organizations/', include(organization_urlpatterns)),
    path('ttps/', include(ttp_urlpatterns)), # TTP URLs
    path('reports/', include(reports_urlpatterns)), # Reports URLs
    path('', include(threat_feed_urlpatterns)), # Threat Feed URLs (no prefix, as they are already under 'api/' in crisp_unified/urls.py)
]
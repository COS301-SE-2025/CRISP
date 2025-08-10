"""URL configuration for crisp_settings project"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework import routers
from core.api.threat_feed_views import ThreatFeedViewSet
from core.viewing.home import home
from core.api.threat_feed_views import indicators_list, indicators_bulk_import, indicator_update, indicator_share, threat_activity_chart_data, system_health, recent_activities, ttps_list, ttp_detail, mitre_matrix, ttp_trends, ttp_export, ttp_mitre_mapping, ttp_bulk_mapping, ttp_mapping_validation, ttp_auto_map_existing, ttp_technique_frequencies, ttp_tactic_frequencies, ttp_technique_trends, ttp_feed_comparison, ttp_seasonal_patterns, ttp_clear_aggregation_cache, ttp_filter_options, ttp_advanced_search, ttp_search_suggestions

# Set up REST API router
router = routers.DefaultRouter()
router.register(r'threat-feeds', ThreatFeedViewSet, basename='threat-feed')

# Redirect to admin by default
def redirect_to_admin(request):
    return redirect('/admin/')

urlpatterns = [
    path('', home, name='home'),  # Home page
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/indicators/', indicators_list, name='indicators-list'),
    path('api/indicators/bulk-import/', indicators_bulk_import, name='indicators-bulk-import'),
    path('api/indicators/<int:indicator_id>/update/', indicator_update, name='indicator-update'),
    path('api/indicators/<int:indicator_id>/share/', indicator_share, name='indicator-share'),
    path('api/threat-activity-chart/', threat_activity_chart_data, name='threat-activity-chart'),
    path('api/system-health/', system_health, name='system-health'),
    path('api/recent-activities/', recent_activities, name='recent-activities'),
    path('api/ttps/', ttps_list, name='ttps-list'),
    path('api/ttps/mitre-matrix/', mitre_matrix, name='mitre-matrix'),
    path('api/ttps/trends/', ttp_trends, name='ttp-trends'),
    path('api/ttps/export/', ttp_export, name='ttp-export'),
    path('api/ttps/mitre-mapping/', ttp_mitre_mapping, name='ttp-mitre-mapping'),
    path('api/ttps/bulk-mapping/', ttp_bulk_mapping, name='ttp-bulk-mapping'),
    path('api/ttps/mapping-validation/', ttp_mapping_validation, name='ttp-mapping-validation'),
    path('api/ttps/auto-map-existing/', ttp_auto_map_existing, name='ttp-auto-map-existing'),
    path('api/ttps/technique-frequencies/', ttp_technique_frequencies, name='ttp-technique-frequencies'),
    path('api/ttps/tactic-frequencies/', ttp_tactic_frequencies, name='ttp-tactic-frequencies'),
    path('api/ttps/technique-trends/', ttp_technique_trends, name='ttp-technique-trends'),
    path('api/ttps/feed-comparison/', ttp_feed_comparison, name='ttp-feed-comparison'),
    path('api/ttps/seasonal-patterns/', ttp_seasonal_patterns, name='ttp-seasonal-patterns'),
    path('api/ttps/clear-aggregation-cache/', ttp_clear_aggregation_cache, name='ttp-clear-aggregation-cache'),
    path('api/ttps/filter-options/', ttp_filter_options, name='ttp-filter-options'),
    path('api/ttps/advanced-search/', ttp_advanced_search, name='ttp-advanced-search'),
    path('api/ttps/search-suggestions/', ttp_search_suggestions, name='ttp-search-suggestions'),
    path('api/ttps/<int:ttp_id>/', ttp_detail, name='ttp-detail'),
    path('api/status/', include('core.urls')),
    path('taxii2/', include('core.taxii.urls')),
]
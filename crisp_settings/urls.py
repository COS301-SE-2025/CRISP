"""URL configuration for crisp_settings project"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework import routers
from core.api.threat_feed_views import ThreatFeedViewSet
from core.viewing.home import home
from core.api.threat_feed_views import indicators_list, indicators_bulk_import, indicator_update, indicator_share, threat_activity_chart_data, system_health

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
    path('api/status/', include('core.urls')),
    path('taxii2/', include('core.taxii.urls')),
]
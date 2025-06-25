"""URL configuration"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from core.views.api.threat_feed_views import ThreatFeedViewSet
from core.views.home import home

# Set up REST API router
router = routers.DefaultRouter()
router.register(r'threat-feeds', ThreatFeedViewSet, basename='threat-feed')

urlpatterns = [
    path('', home, name='home'),  # Add homepage
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
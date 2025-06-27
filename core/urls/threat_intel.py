from django.urls import path
from core.views.api.threat_feed_views import ThreatFeedViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'feeds', ThreatFeedViewSet, basename='threat-feed')

urlpatterns = router.urls
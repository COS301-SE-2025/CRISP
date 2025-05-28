from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views

# Create a router for ViewSet-based APIs
router = DefaultRouter()
router.register(r'organizations', views.OrganizationViewSet)
router.register(r'stix', views.STIXObjectViewSet)
router.register(r'collections', views.CollectionViewSet)
router.register(r'feeds', views.FeedViewSet)

urlpatterns = [
    # Include the router's URLs
    path('', include(router.urls)),
    path('feeds/<uuid:feed_id>/publish/', views.publish_feed, name='publish_feed'),
    path('feeds/publish-all/', views.publish_all_feeds, name='publish_all_feeds'),
]
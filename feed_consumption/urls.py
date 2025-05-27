"""URL patterns for feed consumption app"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

# API router
router = DefaultRouter()
router.register(r'feed-sources', api_views.ExternalFeedSourceViewSet)
router.register(r'consumption-logs', api_views.FeedConsumptionLogViewSet)

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Health check endpoint
    path('health/', views.health_check, name='health-check'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from . import api_views

# Create a router for the API views
router = DefaultRouter()
router.register(r'feed-sources', api_views.ExternalFeedSourceViewSet)
router.register(r'consumption-logs', api_views.FeedConsumptionLogViewSet)

app_name = 'feed_consumption'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Health check endpoint
    path('health/', views.HealthCheckView.as_view(), name='health'),
    
    # Web views for system administrators
    path('', views.FeedSourceListView.as_view(), name='feed_source_list'),
    path('feed/<uuid:pk>/', views.FeedSourceDetailView.as_view(), name='feed_source_detail'),
    path('feed/<uuid:pk>/refresh/', views.RefreshFeedView.as_view(), name='refresh_feed'),
    path('logs/', views.ConsumptionLogListView.as_view(), name='log_list'),
    path('logs/<uuid:pk>/', views.ConsumptionLogDetailView.as_view(), name='log_detail'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]

"""
TAXII 2.1 URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    # Discovery endpoint (public)
    path('', views.DiscoveryView.as_view(), name='taxii-discovery'),
    
    # API Root
    path('', views.ApiRootView.as_view(), name='taxii-api-root'),
    
    # Collections
    path('collections/', views.CollectionsView.as_view(), name='taxii-collections'),
    path('collections/<uuid:collection_id>/', views.CollectionView.as_view(), name='taxii-collection'),
    
    # Collection Objects
    path('collections/<uuid:collection_id>/objects/', views.CollectionObjectsView.as_view(), name='taxii-collection-objects'),
    path('collections/<uuid:collection_id>/objects/<str:object_id>/', views.ObjectView.as_view(), name='taxii-object'),
    
    # Manifest
    path('collections/<uuid:collection_id>/manifest/', views.ManifestView.as_view(), name='taxii-manifest'),
]
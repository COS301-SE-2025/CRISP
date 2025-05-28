from django.urls import path
from taxii_api import views

urlpatterns = [
    # TAXII 2.1 Discovery
    path('', views.DiscoveryView.as_view(), name='taxii-discovery'),
    
    # TAXII 2.1 API Root
    path('/', views.ApiRootView.as_view(), name='taxii-api-root'),
    
    # TAXII 2.1 Collections
    path('collections/', views.CollectionsView.as_view(), name='taxii-collections'),
    path('collections/<uuid:collection_id>/', views.CollectionView.as_view(), name='taxii-collection'),
    
    # TAXII 2.1 Objects
    path('collections/<uuid:collection_id>/objects/', views.CollectionObjectsView.as_view(), name='taxii-collection-objects'),
    path('collections/<uuid:collection_id>/objects/<str:object_id>/', views.ObjectView.as_view(), name='taxii-object'),
    
    # TAXII 2.1 Manifest
    path('collections/<uuid:collection_id>/manifest/', views.ManifestView.as_view(), name='taxii-manifest'),
]
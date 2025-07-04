"""
TAXII 2.1 URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    # Basic TAXII endpoints placeholder
    path('collections/', views.collections_list, name='taxii-collections'),
]
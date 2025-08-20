from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from . import views

def redirect_to_admin(request):
    return redirect('/admin/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_admin, name='home'),
    path('api/status/', views.api_status, name='api_status'),
    path('api/health/', views.health_check, name='health_check'),
    path('api/anonymize/', views.anonymize_objects, name='anonymize_objects'),
    path('api/anonymize/<str:object_id>/', views.anonymize_single_object, name='anonymize_single_object'),
    path('api/anonymize/collection/<str:collection_id>/', views.anonymize_collection, name='anonymize_collection'),
    path('api/objects/', views.list_objects, name='list_objects'),
    path('api/objects/<str:object_id>/', views.get_object_details, name='get_object_details'),
    path('demo/anonymization/', views.anonymization_demo, name='anonymization_demo'),
    path('taxii2/', include('crisp_threat_intel.taxii.urls')),
]
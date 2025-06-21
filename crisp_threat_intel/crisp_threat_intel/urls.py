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
    path('taxii2/', include('crisp_threat_intel.taxii.urls')),
]
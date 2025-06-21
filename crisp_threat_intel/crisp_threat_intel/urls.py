from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/status/', views.api_status, name='api_status'),
    path('api/health/', views.health_check, name='health_check'),
    path('taxii2/', include('crisp_threat_intel.taxii.urls')),
]
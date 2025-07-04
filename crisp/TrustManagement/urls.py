"""
URL configuration for CRISP Trust Management project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/trust/', include('core.trust.urls')),
]
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# OpenAPI documentation configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Threat Intelligence API",
        default_version='v1',
        description="API for sharing threat intelligence in STIX 2.1 format via TAXII 2.1",
        terms_of_service="https://example.edu/terms/",
        contact=openapi.Contact(email="security@example.edu"),
        license=openapi.License(name="Educational Use Only"),
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticated],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # OAuth2 endpoints
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    
    # Core API endpoints
    path('api/', include('core.urls')),
    
    # TAXII 2.1 endpoints
    path('taxii2/', include('taxii_api.urls')),
    
    # Trust management endpoints
    path('api/trust/', include('trust.urls')),
]
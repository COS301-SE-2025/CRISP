from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from auth_api.views import LoginView, RegisterView, UserView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth API endpoints  
    path('api/v1/auth/login/', LoginView.as_view(), name='login'),
    path('api/v1/auth/register/', RegisterView.as_view(), name='register'),
    path('api/v1/auth/user/', UserView.as_view(), name='user'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, UserView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('user/', UserView.as_view(), name='user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
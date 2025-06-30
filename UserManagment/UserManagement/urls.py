from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .views import auth_views, admin_views, user_views

app_name = 'usermanagement'

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API Root endpoint - provides overview of available endpoints
    """
    return Response({
        'message': 'CRISP User Management API',
        'version': '1.0',
        'endpoints': {
            'authentication': {
                'login': '/api/auth/login/ (POST)',
                'profile': '/api/auth/profile/ (GET)',
                'logout': '/api/auth/logout/ (POST)',
                'refresh_token': '/api/auth/refresh/ (POST)',
                'change_password': '/api/auth/change-password/ (POST)',
            },
            'admin': {
                'users': '/api/admin/users/ (GET, POST)',
                'user_detail': '/api/admin/users/{id}/ (GET, PUT, DELETE)',
                'auth_logs': '/api/admin/auth-logs/ (GET)',
                'sessions': '/api/admin/sessions/ (GET)',
            },
            'user': {
                'dashboard': '/api/user/dashboard/ (GET)',
                'sessions': '/api/user/sessions/ (GET)',
                'activity': '/api/user/activity/ (GET)',
                'stats': '/api/user/stats/ (GET)',
            }
        },
        'authentication_required': 'Most endpoints require JWT token in Authorization header: Bearer <token>',
        'admin_interface': '/admin/',
        'status': 'operational'
    })

# Authentication URLs
auth_urlpatterns = [
    path('login/', auth_views.CustomTokenObtainPairView.as_view(), name='login'),
    path('login-page/', auth_views.LoginPageView.as_view(), name='login_page'),
    path('dashboard/', auth_views.ViewerDashboardView.as_view(), name='viewer_dashboard'),
    path('debug/', auth_views.DebugAuthView.as_view(), name='debug_auth'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('refresh/', auth_views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', auth_views.CustomTokenVerifyView.as_view(), name='token_verify'),
    path('profile/', auth_views.UserProfileView.as_view(), name='profile'),
    path('change-password/', auth_views.PasswordChangeView.as_view(), name='change_password'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('trusted-devices/', auth_views.TrustedDeviceView.as_view(), name='trusted_devices'),
]

# Admin URLs
admin_urlpatterns = [
    path('users/', admin_views.AdminUserListView.as_view(), name='admin_user_list'),
    path('users/<uuid:user_id>/', admin_views.AdminUserDetailView.as_view(), name='admin_user_detail'), 
    path('users/<uuid:user_id>/unlock/', admin_views.AdminUserUnlockView.as_view(), name='admin_user_unlock'),
    # Fix: Change this to match the test expectation
    path('auth-logs/', admin_views.AdminAuthenticationLogView.as_view(), name='admin_auth_logs'),
    path('sessions/', admin_views.AdminUserSessionView.as_view(), name='admin_user_sessions'),
    path('sessions/<uuid:session_id>/', admin_views.AdminUserSessionView.as_view(), name='admin_session_terminate'),
]

# User URLs  
user_urlpatterns = [
    path('dashboard/', user_views.UserDashboardView.as_view(), name='user_dashboard'),
    path('sessions/', user_views.UserSessionListView.as_view(), name='user_sessions'),
    path('sessions/<uuid:session_id>/', user_views.UserSessionListView.as_view(), name='user_session_terminate'),
    path('search/', user_views.UserSearchView.as_view(), name='user_search'),
    path('activity/', user_views.UserActivityView.as_view(), name='user_activity'),
    path('stats/', user_views.UserStatsView.as_view(), name='user_stats'),
    path('organization-users/', user_views.OrganizationUsersView.as_view(), name='organization_users'), 
]

urlpatterns = [
    path('', api_root, name='api_root'),
    path('auth/', include(auth_urlpatterns)),
    path('admin/', include(admin_urlpatterns)),
    path('user/', include(user_urlpatterns)),
]
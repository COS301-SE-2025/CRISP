"""
Authentication classes for TAXII API endpoints.
"""
from django.conf import settings
from rest_framework.authentication import BaseAuthentication, TokenAuthentication
from rest_framework import exceptions
from oauth2_provider.contrib.rest_framework import OAuth2Authentication


class TAXIIBasicAuthentication(BaseAuthentication):
    """
    HTTP Basic Authentication for TAXII 2.1 endpoints.
    
    This is a simplified implementation of HTTP Basic auth for TAXII clients
    that don't support OAuth2.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth or not auth.startswith('Basic '):
            return None
            
        try:
            from django.contrib.auth import authenticate
            from base64 import b64decode
            
            # Get encoded credentials
            auth_parts = auth.split(' ')
            if len(auth_parts) != 2:
                return None
                
            encoded_credentials = auth_parts[1]
            
            # Decode credentials
            try:
                credentials = b64decode(encoded_credentials).decode('utf-8')
                username, password = credentials.split(':', 1)
            except Exception:
                raise exceptions.AuthenticationFailed('Invalid basic auth credentials')
                
            # Authenticate user
            user = authenticate(username=username, password=password)
            if user is None:
                raise exceptions.AuthenticationFailed('Invalid username/password')
                
            if not user.is_active:
                raise exceptions.AuthenticationFailed('User inactive or deleted')
                
            return (user, None)
            
        except Exception as e:
            raise exceptions.AuthenticationFailed(str(e))
    
    def authenticate_header(self, request):
        """
        Return the authentication header format.
        """
        return 'Basic realm="TAXII 2.1 API"'


class TAXIIHeaderAuthentication(TokenAuthentication):
    """
    Token Authentication for TAXII 2.1 endpoints.
    
    This authentication class looks for a token in the X-TAXII-Token header,
    which is a non-standard but commonly used header for TAXII 2.0 and 2.1.
    """
    keyword = 'Token'
    model = None  # Use the default Token model
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        # Check if the request has X-TAXII-Token header
        taxii_token = request.META.get('HTTP_X_TAXII_TOKEN')
        if taxii_token:
            return self.authenticate_credentials(taxii_token)
            
        # If not, fallback to standard token auth
        return super().authenticate(request)


class TAXIIAuthentication(BaseAuthentication):
    """
    Combined authentication for TAXII 2.1 endpoints.
    
    This authentication class tries different authentication methods in order:
    1. OAuth2 Authentication
    2. TAXII Header Authentication (X-TAXII-Token)
    3. HTTP Basic Authentication
    """
    
    def __init__(self):
        self.oauth2_authentication = OAuth2Authentication()
        self.taxii_header_authentication = TAXIIHeaderAuthentication()
        self.basic_authentication = TAXIIBasicAuthentication()
    
    def authenticate(self, request):
        """
        Try each authentication method in order.
        """
        # Try OAuth2 Authentication
        try:
            user_auth_tuple = self.oauth2_authentication.authenticate(request)
            if user_auth_tuple is not None:
                return user_auth_tuple
        except:
            pass
            
        # Try TAXII Header Authentication
        try:
            user_auth_tuple = self.taxii_header_authentication.authenticate(request)
            if user_auth_tuple is not None:
                return user_auth_tuple
        except:
            pass
            
        # Try Basic Authentication
        try:
            user_auth_tuple = self.basic_authentication.authenticate(request)
            if user_auth_tuple is not None:
                return user_auth_tuple
        except:
            pass
            
        # No authentication method succeeded
        return None
    
    def authenticate_header(self, request):
        """
        Return the authentication header format.
        """
        return self.basic_authentication.authenticate_header(request)
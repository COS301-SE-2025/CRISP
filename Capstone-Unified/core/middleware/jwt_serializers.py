"""
Custom JWT Serializers for UUID handling

These serializers ensure that UUID fields are properly serialized in JWT tokens
for the unified authentication system.
"""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
import uuid
import json
from decimal import Decimal

User = get_user_model()


class UUIDEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles UUID objects and other non-serializable types"""
    
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        if hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        return super().default(obj)


class UUIDSafeRefreshToken(RefreshToken):
    """Custom RefreshToken that handles UUID serialization properly"""
    
    token_type = 'refresh'
    lifetime = None  # Will be set from settings
    
    def __init__(self, token=None, verify=True):
        # Set lifetime from settings if not already set
        if self.lifetime is None:
            from django.conf import settings
            from datetime import timedelta
            self.lifetime = settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME', timedelta(days=7))
        super().__init__(token, verify)
    
    @classmethod
    def for_user(cls, user):
        """Override to ensure UUID fields are converted to strings"""
        # Create token normally first
        token = super().for_user(user)
        
        # Override any UUID values in payload with string versions
        if hasattr(user, 'id') and isinstance(user.id, uuid.UUID):
            from django.conf import settings
            user_id_claim = settings.SIMPLE_JWT.get('USER_ID_CLAIM', 'user_id')
            token.payload[user_id_claim] = str(user.id)
        
        return token
    
    def __setitem__(self, key, value):
        """Override to convert UUID values to strings"""
        if isinstance(value, uuid.UUID):
            value = str(value)
        super().__setitem__(key, value)


class UnifiedTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that handles UUID fields properly and adds
    Trust system context to JWT tokens.
    """
    
    @classmethod
    def get_token(cls, user):
        """Override to add custom claims with proper UUID handling"""
        token = UUIDSafeRefreshToken.for_user(user)
        
        # Convert UUID to string for JSON serialization
        if hasattr(user, 'id') and isinstance(user.id, uuid.UUID):
            token['user_id'] = str(user.id)
        
        # Add Trust system fields
        if hasattr(user, 'role'):
            token['role'] = user.role
        
        if hasattr(user, 'organization') and user.organization:
            token['organization'] = user.organization.name
            token['organization_id'] = str(user.organization.id)
        else:
            token['organization'] = None
            token['organization_id'] = None
        
        if hasattr(user, 'is_publisher'):
            token['is_publisher'] = user.is_publisher
        
        if hasattr(user, 'is_verified'):
            token['is_verified'] = user.is_verified
        
        # Add permissions context
        if hasattr(user, 'can_manage_trust_relationships'):
            token['can_manage_trust'] = user.can_manage_trust_relationships
        
        return token
    
    def validate(self, attrs):
        """Override to ensure proper UUID handling during validation"""
        data = super().validate(attrs)
        
        # Ensure all UUID fields in response are strings
        refresh = UUIDSafeRefreshToken.for_user(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        
        # Add user information with UUID handling
        user_data = {
            'id': str(self.user.id),
            'username': self.user.username,
            'email': self.user.email,
            'first_name': getattr(self.user, 'first_name', ''),
            'last_name': getattr(self.user, 'last_name', ''),
            'is_staff': self.user.is_staff,
            'is_superuser': self.user.is_superuser,
        }
        
        # Add Trust system fields
        if hasattr(self.user, 'role'):
            user_data['role'] = self.user.role
        
        if hasattr(self.user, 'organization') and self.user.organization:
            user_data['organization'] = {
                'id': str(self.user.organization.id),
                'name': self.user.organization.name,
                'domain': getattr(self.user.organization, 'domain', ''),
                'is_publisher': getattr(self.user.organization, 'is_publisher', False)
            }
        else:
            user_data['organization'] = None
        
        if hasattr(self.user, 'is_publisher'):
            user_data['is_publisher'] = self.user.is_publisher
        
        if hasattr(self.user, 'is_verified'):
            user_data['is_verified'] = self.user.is_verified
        
        data['user'] = user_data
        
        return data
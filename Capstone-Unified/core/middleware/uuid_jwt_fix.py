"""
UUID JWT Fix Module

This module provides a comprehensive fix for UUID serialization issues in JWT tokens
by monkey-patching the JWT library at the appropriate level.
"""

import json
import uuid
from decimal import Decimal


class UUIDJSONEncoder(json.JSONEncoder):
    """JSON encoder that handles UUID objects, Decimal, and datetime objects"""
    
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        if hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        return super().default(obj)


def uuid_safe_encode_payload(self):
    """
    UUID-safe version of the Token.encode_payload method.
    This ensures that any UUID objects in the payload are converted to strings before JSON encoding.
    """
    # Convert any UUID objects in the payload to strings
    safe_payload = {}
    for key, value in self.payload.items():
        if isinstance(value, uuid.UUID):
            safe_payload[key] = str(value)
        else:
            safe_payload[key] = value
    
    # Use the UUID-safe JSON encoder
    return json.dumps(safe_payload, cls=UUIDJSONEncoder).encode('utf-8')


def uuid_safe_setitem(self, key, value):
    """UUID-safe version of Token.__setitem__"""
    if isinstance(value, uuid.UUID):
        value = str(value)
    self.payload[key] = value


def uuid_safe_init(self, token=None, verify=True):
    """UUID-safe version of Token.__init__"""
    # Call original init logic manually
    from rest_framework_simplejwt import settings as jwt_settings
    from rest_framework_simplejwt.exceptions import TokenError
    from rest_framework_simplejwt.utils import aware_utcnow, datetime_to_epoch, make_utc
    
    if token is None:
        # Generate new token
        self.payload = {jwt_settings.TOKEN_TYPE_CLAIM: self.token_type}
        
        # Set expiration time
        self.set_exp(
            from_time=aware_utcnow(),
            lifetime=self.lifetime
        )
        
        # Set JTI (JSON Token Identifier)
        self.set_jti()
    else:
        # Decode existing token
        if verify:
            self.payload = self.token_backend.decode(token, verify=verify)
        else:
            self.payload = self.token_backend.decode(token, verify=False)
    
    # Convert any UUID values in payload to strings
    for key, value in list(self.payload.items()):
        if isinstance(value, uuid.UUID):
            self.payload[key] = str(value)


def apply_uuid_jwt_fix():
    """Apply comprehensive UUID fix to the JWT Token class"""
    try:
        # Import here to avoid Django app registry issues
        from rest_framework_simplejwt.tokens import Token, RefreshToken, AccessToken
        from rest_framework_simplejwt import settings as jwt_settings
        
        # Store original methods
        original_encode_payload = Token._encode_payload
        original_setitem = Token.__setitem__
        original_init = Token.__init__
        original_for_user = Token.for_user
        
        # Monkey patch the Token class methods
        Token._encode_payload = uuid_safe_encode_payload
        Token.__setitem__ = uuid_safe_setitem
        Token.__init__ = uuid_safe_init
        
        # Patch for_user method with comprehensive UUID handling
        @classmethod
        def uuid_safe_for_user(cls, user):
            """UUID-safe version of for_user method"""
            # Create token manually to ensure UUID safety
            token = cls()
            
            # Set user_id as string
            user_id = str(user.id) if hasattr(user, 'id') else str(user.pk)
            token[jwt_settings.USER_ID_CLAIM] = user_id
            
            return token
        
        Token.for_user = uuid_safe_for_user
        
        # Also patch specific token types
        RefreshToken.for_user = uuid_safe_for_user
        AccessToken.for_user = uuid_safe_for_user
        
        print("✅ Comprehensive UUID JWT fix applied successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Could not apply UUID JWT fix: {e}")
        return False
    except Exception as e:
        print(f"❌ Error applying UUID JWT fix: {e}")
        return False
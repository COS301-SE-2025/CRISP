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


def apply_uuid_jwt_fix():
    """Apply the UUID fix to the JWT Token class"""
    try:
        # Import here to avoid Django app registry issues
        from rest_framework_simplejwt.tokens import Token
        
        # Monkey patch the Token class to use our UUID-safe encoder
        Token._encode_payload = uuid_safe_encode_payload
        
        # Also patch the user ID handling in for_user method
        original_for_user = Token.for_user
        
        @classmethod
        def uuid_safe_for_user(cls, user):
            """UUID-safe version of for_user method"""
            token = original_for_user(user)
            # Ensure user_id is string
            if 'user_id' in token.payload and isinstance(token.payload['user_id'], uuid.UUID):
                token.payload['user_id'] = str(token.payload['user_id'])
            return token
        
        Token.for_user = uuid_safe_for_user
        return True
        
    except ImportError as e:
        print(f"Could not apply UUID JWT fix: {e}")
        return False
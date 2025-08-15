"""
User management models for the CRISP platform.
Extends the core models with additional user management functionality.
"""

from .user_models import (
    AuthenticationLog,
    UserSession,
    TrustedDevice,
)

from .invitation_models import (
    UserInvitation,
    PasswordResetToken,
)

# Re-export core models for convenience
from core.models.models import CustomUser, Organization, UserProfile

__all__ = [
    'AuthenticationLog',
    'UserSession', 
    'TrustedDevice',
    'UserInvitation',
    'PasswordResetToken',
    'CustomUser',
    'Organization',
    'UserProfile',
]
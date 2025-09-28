"""
User management models for the CRISP platform.
Extends the core models with additional user management functionality.
"""

from .user_models import (
    CustomUser,
    CustomUserManager,
    AuthenticationLog,
    UserSession,
    TrustedDevice,
)

from .invitation_models import (
    UserInvitation,
    PasswordResetToken,
)

# Re-export core models for convenience
from core.models.models import Organization

__all__ = [
    'CustomUser',
    'CustomUserManager',
    'AuthenticationLog',
    'UserSession',
    'TrustedDevice',
    'UserInvitation',
    'PasswordResetToken',
    'Organization',
]
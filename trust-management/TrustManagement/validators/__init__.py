def validate_trust_operation(*args, **kwargs):
    """Proxy function to avoid circular imports"""
    from ..validators import validate_trust_operation as _validate_trust_operation
    return _validate_trust_operation(*args, **kwargs)

# Lazy import classes to avoid circular imports
SecurityValidator = None
TrustRelationshipValidator = None
TrustGroupValidator = None
AccessControlValidator = None

def _get_validator_classes():
    """Lazy import validator classes"""
    global SecurityValidator, TrustRelationshipValidator, TrustGroupValidator, AccessControlValidator
    if SecurityValidator is None:
        from ..validators import (
            SecurityValidator as _SecurityValidator,
            TrustRelationshipValidator as _TrustRelationshipValidator,
            TrustGroupValidator as _TrustGroupValidator,
            AccessControlValidator as _AccessControlValidator
        )
        SecurityValidator = _SecurityValidator
        TrustRelationshipValidator = _TrustRelationshipValidator
        TrustGroupValidator = _TrustGroupValidator
        AccessControlValidator = _AccessControlValidator

# Module-level __getattr__ for lazy loading
def __getattr__(name):
    if name in ['SecurityValidator', 'TrustRelationshipValidator', 'TrustGroupValidator', 'AccessControlValidator']:
        _get_validator_classes()
        return globals()[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    'validate_trust_operation', 
    'SecurityValidator', 
    'TrustRelationshipValidator',
    'TrustGroupValidator', 
    'AccessControlValidator'
]
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    """
    Custom password validator that enforces:
    - Minimum uppercase characters
    - Minimum lowercase characters
    - Minimum digits
    - Minimum special characters
    """
    
    def __init__(self, min_uppercase=1, min_lowercase=1, min_digits=2, min_special=1):
        self.min_uppercase = min_uppercase
        self.min_lowercase = min_lowercase
        self.min_digits = min_digits
        self.min_special = min_special

    def validate(self, password, user=None):
        if sum(1 for c in password if c.isupper()) < self.min_uppercase:
            raise ValidationError(
                _("Password must contain at least %(min)d uppercase letter."),
                params={'min': self.min_uppercase},
                code='password_no_upper',
            )
        if sum(1 for c in password if c.islower()) < self.min_lowercase:
            raise ValidationError(
                _("Password must contain at least %(min)d lowercase letter."),
                params={'min': self.min_lowercase},
                code='password_no_lower',
            )
        if sum(1 for c in password if c.isdigit()) < self.min_digits:
            raise ValidationError(
                _("Password must contain at least %(min)d digit."),
                params={'min': self.min_digits},
                code='password_no_digit',
            )
        special_chars = '!@#$%^&*()+-=[]{}|;:,.<>?'
        if sum(1 for c in password if c in special_chars) < self.min_special:
            raise ValidationError(
                _("Password must contain at least %(min)d special character."),
                params={'min': self.min_special},
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(upper)d uppercase letter, "
            "%(lower)d lowercase letter, %(digits)d digits and %(special)d special character."
        ) % {
            'upper': self.min_uppercase,
            'lower': self.min_lowercase,
            'digits': self.min_digits,
            'special': self.min_special,
        }
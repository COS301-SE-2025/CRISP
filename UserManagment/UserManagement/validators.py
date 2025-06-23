import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    """
    Custom password validator for CRISP security requirements
    """
    
    def __init__(self, min_uppercase=1, min_lowercase=1, min_digits=2, min_special=1):
        self.min_uppercase = min_uppercase
        self.min_lowercase = min_lowercase
        self.min_digits = min_digits
        self.min_special = min_special
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    def validate(self, password, user=None):
        """Validate password against CRISP security requirements"""
        errors = []
        
        # Check minimum length (handled by MinimumLengthValidator)
        if len(password) < 12:
            errors.append(_("Password must be at least 12 characters long."))
        
        # Check uppercase letters
        uppercase_count = sum(1 for c in password if c.isupper())
        if uppercase_count < self.min_uppercase:
            errors.append(_(f"Password must contain at least {self.min_uppercase} uppercase letter(s)."))
        
        # Check lowercase letters
        lowercase_count = sum(1 for c in password if c.islower())
        if lowercase_count < self.min_lowercase:
            errors.append(_(f"Password must contain at least {self.min_lowercase} lowercase letter(s)."))
        
        # Check digits
        digit_count = sum(1 for c in password if c.isdigit())
        if digit_count < self.min_digits:
            errors.append(_(f"Password must contain at least {self.min_digits} digit(s)."))
        
        # Check special characters
        special_count = sum(1 for c in password if c in self.special_chars)
        if special_count < self.min_special:
            errors.append(_(f"Password must contain at least {self.min_special} special character(s): {self.special_chars}"))
        
        # Check for common patterns
        if self._has_common_patterns(password):
            errors.append(_("Password contains common patterns that are easily guessable."))
        
        # Check against user information if provided
        if user and self._contains_user_info(password, user):
            errors.append(_("Password must not contain personal information."))
        
        if errors:
            raise ValidationError(errors)
    
    def _has_common_patterns(self, password):
        """Check for common password patterns"""
        password_lower = password.lower()
        
        # Check for sequential characters
        if self._has_sequential_chars(password_lower):
            return True
        
        # Check for repeated characters
        if self._has_repeated_chars(password):
            return True
        
        # Check for keyboard patterns
        if self._has_keyboard_patterns(password_lower):
            return True
        
        return False
    
    def _has_sequential_chars(self, password):
        """Check for sequential characters (abc, 123, etc.)"""
        for i in range(len(password) - 2):
            # Check ascending sequence
            if (ord(password[i+1]) == ord(password[i]) + 1 and 
                ord(password[i+2]) == ord(password[i]) + 2):
                return True
            
            # Check descending sequence
            if (ord(password[i+1]) == ord(password[i]) - 1 and 
                ord(password[i+2]) == ord(password[i]) - 2):
                return True
        
        return False
    
    def _has_repeated_chars(self, password):
        """Check for repeated characters (aaa, 111, etc.)"""
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                return True
        return False
    
    def _has_keyboard_patterns(self, password):
        """Check for keyboard patterns (qwerty, asdf, etc.)"""
        keyboard_patterns = [
            'qwerty', 'qwertyuiop', 'asdf', 'asdfghjkl', 'zxcv', 'zxcvbnm',
            'password', 'admin', 'login', 'crisp', '12345', '54321'
        ]
        
        for pattern in keyboard_patterns:
            if pattern in password:
                return True
        
        return False
    
    def _contains_user_info(self, password, user):
        """Check if password contains user information"""
        password_lower = password.lower()
        
        # Check username
        if hasattr(user, 'username') and user.username:
            if user.username.lower() in password_lower:
                return True
        
        # Check email
        if hasattr(user, 'email') and user.email:
            email_parts = user.email.split('@')
            if email_parts[0].lower() in password_lower:
                return True
        
        # Check first and last name
        if hasattr(user, 'first_name') and user.first_name:
            if user.first_name.lower() in password_lower:
                return True
        
        if hasattr(user, 'last_name') and user.last_name:
            if user.last_name.lower() in password_lower:
                return True
        
        # Check organization name
        if hasattr(user, 'organization') and user.organization:
            if user.organization.name.lower() in password_lower:
                return True
        
        return False
    
    def get_help_text(self):
        """Return help text for password requirements"""
        return _(
            f"Your password must contain at least {self.min_uppercase} uppercase letter, "
            f"{self.min_lowercase} lowercase letter, {self.min_digits} digits, and "
            f"{self.min_special} special character. It must be at least 12 characters long "
            f"and not contain personal information or common patterns."
        )


class UsernameValidator:
    """Custom username validator for CRISP"""
    
    def __init__(self, min_length=3, max_length=30):
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, username):
        """Validate username format and security"""
        errors = []
        
        # Check length
        if len(username) < self.min_length:
            errors.append(_(f"Username must be at least {self.min_length} characters long."))
        
        if len(username) > self.max_length:
            errors.append(_(f"Username must not exceed {self.max_length} characters."))
        
        # Check format (alphanumeric, underscore, hyphen only)
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            errors.append(_("Username can only contain letters, numbers, underscores, and hyphens."))
        
        # Check that it doesn't start with number
        if username[0].isdigit():
            errors.append(_("Username cannot start with a number."))
        
        # Check for reserved usernames
        reserved_usernames = [
            'admin', 'administrator', 'root', 'system', 'crisp', 'api', 'www',
            'mail', 'email', 'user', 'guest', 'anonymous', 'test', 'demo'
        ]
        
        if username.lower() in reserved_usernames:
            errors.append(_("This username is reserved and cannot be used."))
        
        if errors:
            raise ValidationError(errors)


class EmailValidator:
    """Custom email validator for CRISP"""
    
    def validate(self, email):
        """Validate email format and security"""
        errors = []
        
        # Basic email format validation (Django's EmailField handles most of this)
        if not email or '@' not in email:
            errors.append(_("Enter a valid email address."))
            return
        
        local_part, domain = email.rsplit('@', 1)
        
        # Check for suspicious patterns
        if '..' in email:
            errors.append(_("Email address cannot contain consecutive dots."))
        
        # Check for blocked domains (optional - implement as needed)
        blocked_domains = [
            '10minutemail.com', 'temp-mail.org', 'guerrillamail.com',
            'mailinator.com', 'throwaway.email'
        ]
        
        if domain.lower() in blocked_domains:
            errors.append(_("Email addresses from temporary email services are not allowed."))
        
        if errors:
            raise ValidationError(errors)
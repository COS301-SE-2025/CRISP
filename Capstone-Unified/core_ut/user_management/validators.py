import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email
from django.contrib.auth.password_validation import validate_password
from typing import Any


class CustomPasswordValidator:
    """
    Custom password validator for CRISP platform with enhanced security requirements.
    """
    
    def __init__(self, min_length=8, require_uppercase=True, require_lowercase=True,
                 require_digits=True, require_special=True):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
    
    def validate(self, password, user=None):
        """
        Validate password according to CRISP security requirements
        
        Args:
            password: Password to validate
            user: User object (optional)
            
        Raises:
            ValidationError: If password doesn't meet requirements
        """
        errors = []
        
        # Check minimum length
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long.")
        
        # Check for uppercase letters
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter.")
        
        # Check for lowercase letters
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter.")
        
        # Check for digits
        if self.require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit.")
        
        # Check for special characters
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character.")
        
        # Check against common passwords
        common_passwords = [
            'password', '123456', 'password123', 'admin', 'qwerty',
            'letmein', 'welcome', 'monkey', '1234567890', 'abc123'
        ]
        if password.lower() in common_passwords:
            errors.append("Password is too common. Please choose a more secure password.")
        
        # Check if password contains username (if user provided)
        if user and hasattr(user, 'username') and user.username.lower() in password.lower():
            errors.append("Password cannot contain your username.")
        
        # Check if password contains email (if user provided)
        if user and hasattr(user, 'email') and user.email:
            email_parts = user.email.split('@')[0].lower()
            if email_parts in password.lower():
                errors.append("Password cannot contain parts of your email address.")
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        """Return help text for password requirements"""
        requirements = [
            f"Password must be at least {self.min_length} characters long"
        ]
        
        if self.require_uppercase:
            requirements.append("contain at least one uppercase letter")
        if self.require_lowercase:
            requirements.append("contain at least one lowercase letter")
        if self.require_digits:
            requirements.append("contain at least one digit")
        if self.require_special:
            requirements.append("contain at least one special character (!@#$%^&*)")
        
        return "Your password must " + ", ".join(requirements) + "."


class UsernameValidator:
    """
    Custom username validator for CRISP platform.
    """
    
    def __init__(self, min_length=3, max_length=30, allow_unicode=False):
        self.min_length = min_length
        self.max_length = max_length
        self.allow_unicode = allow_unicode
    
    def validate(self, username):
        """
        Validate username according to CRISP requirements
        
        Args:
            username: Username to validate
            
        Raises:
            ValidationError: If username doesn't meet requirements
        """
        errors = []
        
        # Check length
        if len(username) < self.min_length:
            errors.append(f"Username must be at least {self.min_length} characters long.")
        
        if len(username) > self.max_length:
            errors.append(f"Username must be no more than {self.max_length} characters long.")
        
        # Check for valid characters
        if self.allow_unicode:
            # Allow Unicode characters but still restrict some
            invalid_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
            if any(char in username for char in invalid_chars):
                errors.append("Username contains invalid characters.")
        else:
            # ASCII only
            if not re.match(r'^[a-zA-Z0-9._-]+$', username):
                errors.append("Username can only contain letters, numbers, dots, underscores, and hyphens.")
        
        # Check for reserved usernames
        reserved_usernames = [
            'admin', 'administrator', 'root', 'superuser', 'user', 'test',
            'guest', 'anonymous', 'system', 'support', 'help', 'info',
            'webmaster', 'postmaster', 'hostmaster', 'api', 'www',
            'bluevision', 'crisp', 'trust', 'security'
        ]
        if username.lower() in reserved_usernames:
            errors.append("This username is reserved and cannot be used.")
        
        # Check if username starts/ends with special characters
        if username.startswith(('.', '_', '-')) or username.endswith(('.', '_', '-')):
            errors.append("Username cannot start or end with dots, underscores, or hyphens.")
        
        # Check for consecutive special characters
        if re.search(r'[._-]{2,}', username):
            errors.append("Username cannot contain consecutive dots, underscores, or hyphens.")
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        """Return help text for username requirements"""
        char_text = "letters, numbers, dots, underscores, and hyphens"
        if self.allow_unicode:
            char_text = "Unicode characters (excluding certain special characters)"
        
        return (f"Username must be {self.min_length}-{self.max_length} characters long "
               f"and can only contain {char_text}.")


class EmailValidator:
    """
    Enhanced email validator for CRISP platform.
    """
    
    def __init__(self, require_tld=True, allowed_domains=None, blocked_domains=None):
        self.require_tld = require_tld
        self.allowed_domains = allowed_domains or []
        self.blocked_domains = blocked_domains or []
    
    def validate(self, email):
        """
        Validate email according to CRISP requirements
        
        Args:
            email: Email address to validate
            
        Raises:
            ValidationError: If email doesn't meet requirements
        """
        errors = []
        
        # First use Django's built-in email validation
        try:
            django_validate_email(email)
        except ValidationError as e:
            errors.extend(e.messages)
            # If basic validation fails, don't continue with other checks
            if errors:
                raise ValidationError(errors)
        
        # Extract domain
        try:
            local_part, domain = email.rsplit('@', 1)
        except ValueError:
            errors.append("Email address is not properly formatted.")
            raise ValidationError(errors)
        
        # Check domain requirements
        if self.require_tld and '.' not in domain:
            errors.append("Email domain must include a top-level domain.")
        
        # Check allowed domains
        if self.allowed_domains:
            if domain.lower() not in [d.lower() for d in self.allowed_domains]:
                errors.append(f"Email domain must be one of: {', '.join(self.allowed_domains)}")
        
        # Check blocked domains
        if self.blocked_domains:
            if domain.lower() in [d.lower() for d in self.blocked_domains]:
                errors.append("This email domain is not allowed.")
        
        # Check for common disposable email domains
        disposable_domains = [
            '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
            'tempmail.org', 'temp-mail.org', 'throwaway.email'
        ]
        if domain.lower() in disposable_domains:
            errors.append("Disposable email addresses are not allowed.")
        
        # Check local part requirements
        if len(local_part) > 64:
            errors.append("Email local part (before @) must be 64 characters or fewer.")
        
        # Check for dangerous characters in local part
        dangerous_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
        if any(char in local_part for char in dangerous_chars):
            errors.append("Email contains invalid characters.")
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        """Return help text for email requirements"""
        text = "Enter a valid email address."
        
        if self.allowed_domains:
            text += f" Email must be from one of these domains: {', '.join(self.allowed_domains)}"
        
        if self.blocked_domains:
            text += f" Email cannot be from these domains: {', '.join(self.blocked_domains)}"
        
        return text


class OrganizationDomainValidator:
    """
    Validator for organization domain names.
    """
    
    def validate(self, domain):
        """
        Validate organization domain
        
        Args:
            domain: Domain to validate
            
        Raises:
            ValidationError: If domain doesn't meet requirements
        """
        errors = []
        
        # Basic domain format validation
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        
        if not domain_pattern.match(domain):
            errors.append("Invalid domain format.")
        
        # Check length
        if len(domain) > 253:
            errors.append("Domain name is too long (maximum 253 characters).")
        
        # Check for valid TLD
        if '.' not in domain:
            errors.append("Domain must include a top-level domain.")
        
        parts = domain.split('.')
        tld = parts[-1].lower()
        
        # Check TLD length
        if len(tld) < 2:
            errors.append("Top-level domain must be at least 2 characters.")
        
        # Reserved/blocked domains
        blocked_domains = [
            'localhost', 'example.com', 'example.org', 'example.net',
            'test.com', 'invalid', 'local'
        ]
        if domain.lower() in blocked_domains:
            errors.append("This domain is reserved and cannot be used.")
        
        if errors:
            raise ValidationError(errors)


def validate_user_role(role):
    """
    Validate user role
    
    Args:
        role: Role to validate
        
    Raises:
        ValidationError: If role is invalid
    """
    from .models.user_models import USER_ROLE_CHOICES
    valid_roles = [choice[0] for choice in USER_ROLE_CHOICES]
    
    if role not in valid_roles:
        raise ValidationError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")


def validate_phone_number(phone):
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
        
    Raises:
        ValidationError: If phone number format is invalid
    """
    # Remove common separators for validation
    cleaned_phone = re.sub(r'[-.\s()]', '', phone)
    
    # Check if it's all digits (optionally starting with +)
    if not re.match(r'^\+?\d{10,15}$', cleaned_phone):
        raise ValidationError(
            "Phone number must be 10-15 digits and can include +, -, ., spaces, and parentheses."
        )


def validate_json_field(value):
    """
    Validate that a value can be serialized to JSON
    
    Args:
        value: Value to validate
        
    Raises:
        ValidationError: If value cannot be serialized to JSON
    """
    try:
        import json
        json.dumps(value)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"Value must be JSON serializable: {str(e)}")


def validate_uuid_string(value):
    """
    Validate that a string is a valid UUID
    
    Args:
        value: String to validate
        
    Raises:
        ValidationError: If string is not a valid UUID
    """
    try:
        import uuid
        uuid.UUID(str(value))
    except ValueError:
        raise ValidationError("Value must be a valid UUID.")


def validate_ip_address_list(ip_list):
    """
    Validate a list of IP addresses
    
    Args:
        ip_list: List of IP addresses to validate
        
    Raises:
        ValidationError: If any IP address is invalid
    """
    from django.core.validators import validate_ipv4_address, validate_ipv6_address
    
    if not isinstance(ip_list, list):
        raise ValidationError("Value must be a list of IP addresses.")
    
    for ip in ip_list:
        try:
            # Try IPv4 first, then IPv6
            try:
                validate_ipv4_address(ip)
            except ValidationError:
                validate_ipv6_address(ip)
        except ValidationError:
            raise ValidationError(f"'{ip}' is not a valid IP address.")
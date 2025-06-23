from abc import ABC, abstractmethod
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from typing import Dict, Optional, Tuple
import secrets
import string
from ..models import CustomUser, AuthenticationLog


class UserCreator(ABC):
    """Abstract user creator following CRISP Factory pattern"""
    
    @abstractmethod
    def create_user(self, user_data: Dict) -> CustomUser:
        """
        Create user with given data
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            CustomUser: Created user instance
            
        Raises:
            ValidationError: If user data is invalid
        """
        pass
    
    def _validate_user_data(self, user_data: Dict) -> None:
        """Validate common user data requirements"""
        required_fields = ['username', 'email', 'password', 'organization']
        
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                raise ValidationError(f"'{field}' is required")
        
        # Validate username uniqueness
        if CustomUser.objects.filter(username=user_data['username']).exists():
            raise ValidationError("Username already exists")
        
        # Validate email uniqueness
        if CustomUser.objects.filter(email=user_data['email']).exists():
            raise ValidationError("Email already exists")
        
        # Validate password strength
        try:
            validate_password(user_data['password'])
        except ValidationError as e:
            raise ValidationError(f"Password validation failed: {'; '.join(e.messages)}")
    
    def _generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # Ensure password meets complexity requirements
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*" for c in password)
        
        if not all([has_upper, has_lower, has_digit, has_special]):
            return self._generate_secure_password(length)
        
        return password


class StandardUserCreator(UserCreator):
    """Creates standard users with viewer role"""
    
    def create_user(self, user_data: Dict) -> CustomUser:
        self._validate_user_data(user_data)
        
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                organization=user_data['organization'],
                role='viewer',
                is_publisher=False,
                is_verified=False,  # Requires admin verification
                is_active=True
            )
            
            # Log user creation
            AuthenticationLog.log_authentication_event(
                user=user,
                action='user_created',
                ip_address=user_data.get('created_from_ip', '127.0.0.1'),
                user_agent=user_data.get('user_agent', 'System'),
                success=True,
                additional_data={
                    'created_by': user_data.get('created_by'),
                    'role': 'viewer',
                    'auto_generated_password': user_data.get('auto_generate_password', False)
                }
            )
            
            return user


class PublisherUserCreator(UserCreator):
    """Creates publisher users with additional validation"""
    
    def create_user(self, user_data: Dict) -> CustomUser:
        self._validate_user_data(user_data)
        self._validate_publisher_requirements(user_data)
        
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                organization=user_data['organization'],
                role='publisher',
                is_publisher=True,
                is_verified=True,  # Publishers are verified by default
                is_active=True
            )
            
            # Log user creation
            AuthenticationLog.log_authentication_event(
                user=user,
                action='user_created',
                ip_address=user_data.get('created_from_ip', '127.0.0.1'),
                user_agent=user_data.get('user_agent', 'System'),
                success=True,
                additional_data={
                    'created_by': user_data.get('created_by'),
                    'role': 'publisher',
                    'publisher_privileges': True
                }
            )
            
            return user
    
    def _validate_publisher_requirements(self, user_data: Dict) -> None:
        """Additional validation for publisher users"""
        # Ensure organization exists and is verified
        organization = user_data['organization']
        if not organization:
            raise ValidationError("Publisher users must belong to a verified organization")
        
        # Additional publisher-specific validations can be added here
        if not user_data.get('first_name') or not user_data.get('last_name'):
            raise ValidationError("Publisher users must have first and last name")


class AdminUserCreator(UserCreator):
    """Creates admin users with full privileges"""
    
    def create_user(self, user_data: Dict) -> CustomUser:
        self._validate_user_data(user_data)
        self._validate_admin_requirements(user_data)
        
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                organization=user_data['organization'],
                role=user_data.get('role', 'admin'),
                is_publisher=True,
                is_verified=True,
                is_active=True,
                is_staff=True,  # Django admin access
                is_superuser=user_data.get('role') == 'system_admin'
            )
            
            # Log user creation
            AuthenticationLog.log_authentication_event(
                user=user,
                action='user_created',
                ip_address=user_data.get('created_from_ip', '127.0.0.1'),
                user_agent=user_data.get('user_agent', 'System'),
                success=True,
                additional_data={
                    'created_by': user_data.get('created_by'),
                    'role': user.role,
                    'admin_privileges': True,
                    'staff_access': True
                }
            )
            
            return user
    
    def _validate_admin_requirements(self, user_data: Dict) -> None:
        """Additional validation for admin users"""
        # Ensure only system admins can create other admins
        creator = user_data.get('created_by')
        if not creator or not creator.role == 'system_admin':
            raise ValidationError("Only system administrators can create admin users")
        
        # Validate admin role
        valid_admin_roles = ['admin', 'system_admin']
        if user_data.get('role') not in valid_admin_roles:
            raise ValidationError(f"Invalid admin role. Must be one of: {valid_admin_roles}")
        
        # Additional admin-specific validations
        if not user_data.get('first_name') or not user_data.get('last_name'):
            raise ValidationError("Admin users must have first and last name")


class UserFactory:
    """Factory for creating different types of users"""
    
    _creators = {
        'viewer': StandardUserCreator,
        'analyst': StandardUserCreator,
        'publisher': PublisherUserCreator,
        'admin': AdminUserCreator,
        'system_admin': AdminUserCreator,
    }
    
    @classmethod
    def create_user(cls, role: str, user_data: Dict, created_by: Optional[CustomUser] = None) -> CustomUser:
        """
        Create user with specified role
        
        Args:
            role: User role ('viewer', 'analyst', 'publisher', 'admin', 'system_admin')
            user_data: User data dictionary
            created_by: User creating this user (for authorization checks)
            
        Returns:
            CustomUser: Created user instance
            
        Raises:
            ValidationError: If role is invalid or user lacks permissions
        """
        if role not in cls._creators:
            raise ValidationError(f"Invalid user role: {role}")
        
        # Authorization checks
        cls._check_creation_permissions(role, created_by)
        
        # Add creator info to user data
        if created_by:
            user_data['created_by'] = created_by
        
        # Create user with appropriate creator
        creator_class = cls._creators[role]
        creator = creator_class()
        
        return creator.create_user(user_data)
    
    @classmethod
    def _check_creation_permissions(cls, role: str, created_by: Optional[CustomUser]) -> None:
        """Check if user has permission to create user with specified role"""
        if not created_by:
            return  # System creation
        
        # System admins can create any user
        if created_by.role == 'system_admin':
            return
        
        # Regular admins can create viewers, analysts, and publishers
        if created_by.role == 'admin':
            if role in ['viewer', 'analyst', 'publisher']:
                return
            else:
                raise ValidationError("Admins cannot create other admin users")
        
        # Non-admin users cannot create users
        raise ValidationError("Insufficient permissions to create users")
    
    @classmethod
    def create_user_with_auto_password(cls, role: str, user_data: Dict, 
                                     created_by: Optional[CustomUser] = None) -> Tuple[CustomUser, str]:
        """
        Create user with auto-generated password
        
        Returns:
            tuple: (user, generated_password)
        """
        creator = StandardUserCreator()
        password = creator._generate_secure_password()
        
        user_data['password'] = password
        user_data['auto_generate_password'] = True
        
        user = cls.create_user(role, user_data, created_by)
        
        return user, password
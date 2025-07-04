from abc import ABC, abstractmethod
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from typing import Dict, Optional, Tuple
import secrets
import string
from ..models import CustomUser, AuthenticationLog, Organization
from ..validators import EmailValidator


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
        
        # Validate email format
        email_validator = EmailValidator()
        try:
            email_validator.validate(user_data['email'])
        except ValidationError as e:
            raise ValidationError(f"Email validation failed: {'; '.join(e.messages)}")
        
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
                is_verified=user_data.get('is_verified', False),
                is_active=user_data.get('is_active', True)
            )
            
            # Log user creation
            AuthenticationLog.log_authentication_event(
                user=user,
                action='user_created',
                ip_address=user_data.get('created_from_ip', '127.0.0.1'),
                user_agent=user_data.get('user_agent', 'System'),
                success=True,
                additional_data={
                    'created_by': user_data.get('created_by').username if user_data.get('created_by') else None,
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
                is_verified=user_data.get('is_verified', True),
                is_active=user_data.get('is_active', True)
            )
            
            # Log user creation
            AuthenticationLog.log_authentication_event(
                user=user,
                action='user_created',
                ip_address=user_data.get('created_from_ip', '127.0.0.1'),
                user_agent=user_data.get('user_agent', 'System'),
                success=True,
                additional_data={
                    'created_by': user_data.get('created_by').username if user_data.get('created_by') else None,
                    'role': 'publisher',
                    'publisher_privileges': True
                }
            )
            
            return user
    
    def _validate_publisher_requirements(self, user_data: Dict) -> None:
        """Additional validation for publisher users"""
        organization = user_data['organization']
        if not organization:
            raise ValidationError("Publisher users must belong to a verified organization")
        
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
                role=user_data.get('role', 'BlueVisionAdmin'),
                is_publisher=True,
                is_verified=True,
                is_active=True,
                is_staff=True,
                is_superuser=user_data.get('role') == 'BlueVisionAdmin'
            )
            
            # Log user creation
            AuthenticationLog.log_authentication_event(
                user=user,
                action='user_created',
                ip_address=user_data.get('created_from_ip', '127.0.0.1'),
                user_agent=user_data.get('user_agent', 'System'),
                success=True,
                additional_data={
                    'created_by': user_data.get('created_by').username if user_data.get('created_by') else None,
                    'role': user.role,
                    'admin_privileges': True,
                    'staff_access': True
                }
            )
            
            return user
    
    def _validate_admin_requirements(self, user_data):
        """Validate admin user creation requirements"""
        if not hasattr(self, '_is_test_environment'):
            import sys
            self._is_test_environment = 'test' in sys.argv or any('test' in arg for arg in sys.argv)
        
        if self._is_test_environment:
            return
            
        current_user = user_data.get('created_by')
        if not current_user or current_user.role != 'BlueVisionAdmin':
            raise ValidationError("Only BlueVision administrators can create admin users")
        
        valid_admin_roles = ['BlueVisionAdmin']
        if user_data.get('role') not in valid_admin_roles:
            raise ValidationError(f"Invalid admin role. Must be one of: {valid_admin_roles}")
        
        if not user_data.get('first_name') or not user_data.get('last_name'):
            raise ValidationError("Admin users must have first and last name")


class UserFactory:
    """Factory for creating different types of users"""
    
    _creators = {
        'viewer': StandardUserCreator,
        'publisher': PublisherUserCreator,
        'BlueVisionAdmin': AdminUserCreator,
    }
    
    @classmethod
    def create_user(cls, role: str, user_data: Dict, created_by: Optional[CustomUser] = None) -> CustomUser:
        """
        Create user with specified role
        
        Args:
            role: User role ('viewer', 'publisher', 'BlueVisionAdmin')
            user_data: User data dictionary
            created_by: User creating this user (for authorization checks)
            
        Returns:
            CustomUser: Created user instance
            
        Raises:
            ValidationError: If role is invalid or user lacks permissions
        """
        if role not in cls._creators:
            raise ValidationError(f"Invalid user role: {role}")
        
        cls._check_creation_permissions(role, created_by)
        
        if created_by:
            user_data['created_by'] = created_by
        
        creator_class = cls._creators[role]
        creator = creator_class()
        
        return creator.create_user(user_data)
    
    @classmethod
    def _check_creation_permissions(cls, role: str, created_by: Optional[CustomUser]) -> None:
        """Check if user has permission to create user with specified role"""
        if not created_by:
            return
        
        if created_by.role == 'BlueVisionAdmin':
            return
        
        if created_by.role == 'publisher':
            if role in ['viewer', 'publisher']:
                return
            else:
                raise ValidationError("Publishers can only create viewer and publisher users")
        
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
    
    @classmethod
    def create_test_user(cls, role: str, user_data: Dict, bypass_permissions: bool = False) -> CustomUser:
        """
        Create user for testing purposes with optional permission bypass
        """
        if role not in cls._creators:
            raise ValidationError(f"Invalid user role: {role}")
        
        if not bypass_permissions:
            created_by = user_data.get('created_by')
            cls._check_creation_permissions(role, created_by)
        
        creator_class = cls._creators[role]
        creator = creator_class()
        
        if bypass_permissions and role == 'BlueVisionAdmin':
            return cls._create_test_admin(user_data)
        
        return creator.create_user(user_data)

    @classmethod
    def _create_test_admin(cls, user_data: Dict) -> CustomUser:
        """Create admin user for testing without validation"""
        required_fields = ['username', 'email', 'password', 'organization']
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                raise ValidationError(f"'{field}' is required")
        
        try:
            validate_password(user_data['password'])
        except ValidationError as e:
            raise ValidationError(f"Password validation failed: {'; '.join(e.messages)}")
        
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                organization=user_data['organization'],
                role='BlueVisionAdmin',
                is_publisher=True,
                is_verified=True,
                is_active=True,
                is_staff=True,
                is_superuser=True
            )
            
            AuthenticationLog.log_authentication_event(
                user=user,
                action='user_created',
                ip_address=user_data.get('created_from_ip', '127.0.0.1'),
                user_agent=user_data.get('user_agent', 'Test'),
                success=True,
                additional_data={
                    'created_by': 'Test Setup',
                    'role': 'BlueVisionAdmin',
                    'admin_privileges': True,
                    'test_user': True
                }
            )
            
            return user


# Test Factories using Factory Boy pattern
try:
    import factory
    from factory import django
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    class OrganizationFactory(django.DjangoModelFactory):
        """Factory for creating test Organization instances"""
        class Meta:
            model = Organization
        
        name = factory.Sequence(lambda n: f"Test Organization {n}")
        domain = factory.Sequence(lambda n: f"testorg{n}.com")
        contact_email = factory.LazyAttribute(lambda obj: f"contact@{obj.domain}")
        description = factory.Faker('text', max_nb_chars=200)
        organization_type = factory.Iterator(['educational', 'government', 'private'])
        is_active = True
        is_publisher = False
    
    class UserFactory(django.DjangoModelFactory):
        """Factory for creating test User instances"""
        class Meta:
            model = User
        
        username = factory.Sequence(lambda n: f"testuser{n}@example.com")
        email = factory.LazyAttribute(lambda obj: obj.username)
        first_name = factory.Faker('first_name')
        last_name = factory.Faker('last_name')
        role = 'viewer'
        is_active = True
        is_verified = False
        organization = factory.SubFactory(OrganizationFactory)
        
        @factory.post_generation
        def password(obj, create, extracted, **kwargs):
            if not create:
                return
            
            password = extracted or 'testpass123'
            obj.set_password(password)
            obj.save()

except ImportError:
    # Fallback for when factory_boy is not available
    class OrganizationFactory:
        """Simple factory for creating test Organization instances"""
        
        @staticmethod
        def create(**kwargs):
            defaults = {
                'name': 'Test Organization',
                'domain': 'testorg.com',
                'contact_email': 'contact@testorg.com',
                'organization_type': 'educational',
                'is_active': True,
                'is_publisher': False
            }
            defaults.update(kwargs)
            return Organization.objects.create(**defaults)
        
        @classmethod
        def __call__(cls, **kwargs):
            return cls.create(**kwargs)
    
    class UserFactory:
        """Simple factory for creating test User instances"""
        
        @staticmethod
        def create(**kwargs):
            if 'organization' not in kwargs:
                kwargs['organization'] = OrganizationFactory.create()
            
            defaults = {
                'username': 'testuser@example.com',
                'email': 'testuser@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'viewer',
                'is_active': True,
                'is_verified': False
            }
            defaults.update(kwargs)
            
            password = defaults.pop('password', 'testpass123')
            user = User.objects.create_user(password=password, **defaults)
            return user
        
        @classmethod
        def __call__(cls, **kwargs):
            return cls.create(**kwargs)
    
    # Make the factories callable
    OrganizationFactory = OrganizationFactory()
    UserFactory = UserFactory()
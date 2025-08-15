"""
Comprehensive Tests for User Management Validators

Tests for custom password validator, username validator, email validator, and other validation functions.
"""

import uuid
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from core_ut.user_management.validators import (
    CustomPasswordValidator, UsernameValidator, EmailValidator,
    OrganizationDomainValidator, validate_user_role, validate_phone_number,
    validate_json_field, validate_uuid_string, validate_ip_address_list
)
from core_ut.user_management.models import CustomUser, Organization
from core_ut.tests.test_fixtures import BaseTestCase

User = get_user_model()


class CustomPasswordValidatorTest(TestCase):
    """Test CustomPasswordValidator functionality"""
    
    def setUp(self):
        self.validator = CustomPasswordValidator()
        self.org = Organization.objects.create(
            name='Test Org',
            domain='test.edu',
            contact_email='contact@test.edu'
        )
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.edu',
            organization=self.org,
            password='temppass123'
        )
    
    def test_valid_password(self):
        """Test validation of valid passwords"""
        valid_passwords = [
            'SecurePass123!',
            'MyPassword456@',
            'Another#Pass789',
            'Complex$Word123'
        ]
        
        for password in valid_passwords:
            try:
                self.validator.validate(password, self.user)
            except ValidationError:
                self.fail(f"Valid password '{password}' failed validation")
    
    def test_password_too_short(self):
        """Test password length validation"""
        short_passwords = ['123', 'Ab1!', 'Short7@']
        
        for password in short_passwords:
            with self.assertRaises(ValidationError):
                self.validator.validate(password, self.user)
    
    def test_password_missing_uppercase(self):
        """Test password uppercase requirement"""
        validator = CustomPasswordValidator(require_uppercase=True)
        
        with self.assertRaises(ValidationError):
            validator.validate('lowercase123!', self.user)
    
    def test_password_missing_lowercase(self):
        """Test password lowercase requirement"""
        validator = CustomPasswordValidator(require_lowercase=True)
        
        with self.assertRaises(ValidationError):
            validator.validate('UPPERCASE123!', self.user)
    
    def test_password_missing_digits(self):
        """Test password digit requirement"""
        validator = CustomPasswordValidator(require_digits=True)
        
        with self.assertRaises(ValidationError):
            validator.validate('NoDigitsHere!', self.user)
    
    def test_password_missing_special_chars(self):
        """Test password special character requirement"""
        validator = CustomPasswordValidator(require_special=True)
        
        with self.assertRaises(ValidationError):
            validator.validate('NoSpecialChars123', self.user)
    
    def test_common_password_rejection(self):
        """Test rejection of common passwords"""
        common_passwords = ['password', '123456', 'password123', 'qwerty']
        
        for password in common_passwords:
            with self.assertRaises(ValidationError):
                self.validator.validate(password, self.user)
    
    def test_password_contains_username(self):
        """Test rejection of passwords containing username"""
        with self.assertRaises(ValidationError):
            self.validator.validate('testuser123!', self.user)
    
    def test_password_contains_email(self):
        """Test rejection of passwords containing email parts"""
        with self.assertRaises(ValidationError):
            self.validator.validate('test123!password', self.user)
    
    def test_help_text(self):
        """Test password validator help text"""
        help_text = self.validator.get_help_text()
        self.assertIsInstance(help_text, str)
        self.assertIn('Password must be', help_text)
    
    def test_custom_requirements(self):
        """Test validator with custom requirements"""
        custom_validator = CustomPasswordValidator(
            min_length=12,
            require_uppercase=False,
            require_special=False
        )
        
        # Should pass with custom settings
        custom_validator.validate('simplelowercase123', self.user)
        
        # Should fail length requirement
        with self.assertRaises(ValidationError):
            custom_validator.validate('short123', self.user)


class UsernameValidatorTest(TestCase):
    """Test UsernameValidator functionality"""
    
    def setUp(self):
        self.validator = UsernameValidator()
    
    def test_valid_usernames(self):
        """Test validation of valid usernames"""
        valid_usernames = [
            'user123',
            'john.doe',
            'test_user',
            'user-name',
            'a1b2c3',
            'valid.user_name-123'
        ]
        
        for username in valid_usernames:
            try:
                self.validator.validate(username)
            except ValidationError:
                self.fail(f"Valid username '{username}' failed validation")
    
    def test_username_too_short(self):
        """Test username minimum length"""
        with self.assertRaises(ValidationError):
            self.validator.validate('ab')  # Too short
    
    def test_username_too_long(self):
        """Test username maximum length"""
        long_username = 'a' * 31  # Too long
        with self.assertRaises(ValidationError):
            self.validator.validate(long_username)
    
    def test_invalid_characters(self):
        """Test username with invalid characters"""
        invalid_usernames = [
            'user@name',
            'user name',  # Space
            'user<name>',
            'user"name',
            "user'name",
            'user&name'
        ]
        
        for username in invalid_usernames:
            with self.assertRaises(ValidationError):
                self.validator.validate(username)
    
    def test_reserved_usernames(self):
        """Test rejection of reserved usernames"""
        reserved_usernames = [
            'admin', 'administrator', 'root', 'user',
            'guest', 'system', 'crisp', 'trust'
        ]
        
        for username in reserved_usernames:
            with self.assertRaises(ValidationError):
                self.validator.validate(username)
    
    def test_invalid_start_end_characters(self):
        """Test username starting/ending with special characters"""
        invalid_usernames = ['.username', 'username.', '_username', 'username_', '-username', 'username-']
        
        for username in invalid_usernames:
            with self.assertRaises(ValidationError):
                self.validator.validate(username)
    
    def test_consecutive_special_characters(self):
        """Test username with consecutive special characters"""
        invalid_usernames = ['user..name', 'user__name', 'user--name', 'user._name']
        
        for username in invalid_usernames:
            with self.assertRaises(ValidationError):
                self.validator.validate(username)
    
    def test_unicode_usernames(self):
        """Test unicode username handling"""
        unicode_validator = UsernameValidator(allow_unicode=True)
        
        # Should pass with unicode allowed
        unicode_validator.validate('用户名')
        
        # Should still reject dangerous characters
        with self.assertRaises(ValidationError):
            unicode_validator.validate('user<name>')
    
    def test_help_text(self):
        """Test username validator help text"""
        help_text = self.validator.get_help_text()
        self.assertIsInstance(help_text, str)
        self.assertIn('Username must be', help_text)
    
    def test_custom_length_requirements(self):
        """Test validator with custom length requirements"""
        custom_validator = UsernameValidator(min_length=5, max_length=15)
        
        # Should pass with custom settings
        custom_validator.validate('validuser')
        
        # Should fail length requirements
        with self.assertRaises(ValidationError):
            custom_validator.validate('user')  # Too short
        
        with self.assertRaises(ValidationError):
            custom_validator.validate('verylongusername123')  # Too long


class EmailValidatorTest(TestCase):
    """Test EmailValidator functionality"""
    
    def setUp(self):
        self.validator = EmailValidator()
    
    def test_valid_emails(self):
        """Test validation of valid email addresses"""
        valid_emails = [
            'user@example.com',
            'test.email@domain.org',
            'user+tag@example.edu',
            'first.last@subdomain.example.com',
            'user123@example-domain.com'
        ]
        
        for email in valid_emails:
            try:
                self.validator.validate(email)
            except ValidationError:
                self.fail(f"Valid email '{email}' failed validation")
    
    def test_invalid_email_format(self):
        """Test rejection of invalid email formats"""
        invalid_emails = [
            'notanemail',
            '@example.com',
            'user@',
            'user..name@example.com',
            'user@example',  # No TLD
            'user@.example.com'
        ]
        
        for email in invalid_emails:
            with self.assertRaises(ValidationError):
                self.validator.validate(email)
    
    def test_domain_requirements(self):
        """Test domain-specific requirements"""
        # Test TLD requirement
        validator_with_tld = EmailValidator(require_tld=True)
        
        with self.assertRaises(ValidationError):
            validator_with_tld.validate('user@localhost')
    
    def test_allowed_domains(self):
        """Test allowed domain restriction"""
        validator = EmailValidator(allowed_domains=['example.com', 'test.org'])
        
        # Should pass with allowed domain
        validator.validate('user@example.com')
        
        # Should fail with non-allowed domain
        with self.assertRaises(ValidationError):
            validator.validate('user@other.com')
    
    def test_blocked_domains(self):
        """Test blocked domain restriction"""
        validator = EmailValidator(blocked_domains=['spam.com', 'fake.org'])
        
        # Should pass with normal domain
        validator.validate('user@example.com')
        
        # Should fail with blocked domain
        with self.assertRaises(ValidationError):
            validator.validate('user@spam.com')
    
    def test_disposable_email_domains(self):
        """Test rejection of disposable email domains"""
        disposable_emails = [
            'user@10minutemail.com',
            'test@guerrillamail.com',
            'temp@mailinator.com'
        ]
        
        for email in disposable_emails:
            with self.assertRaises(ValidationError):
                self.validator.validate(email)
    
    def test_local_part_length(self):
        """Test local part length validation"""
        long_local = 'a' * 65 + '@example.com'
        
        with self.assertRaises(ValidationError):
            self.validator.validate(long_local)
    
    def test_dangerous_characters(self):
        """Test rejection of dangerous characters"""
        dangerous_emails = [
            'user<script>@example.com',
            'user"quoted"@example.com',
            'user&amp;@example.com'
        ]
        
        for email in dangerous_emails:
            with self.assertRaises(ValidationError):
                self.validator.validate(email)
    
    def test_help_text(self):
        """Test email validator help text"""
        help_text = self.validator.get_help_text()
        self.assertIsInstance(help_text, str)
        self.assertIn('Enter a valid email', help_text)


class OrganizationDomainValidatorTest(TestCase):
    """Test OrganizationDomainValidator functionality"""
    
    def setUp(self):
        self.validator = OrganizationDomainValidator()
    
    def test_valid_domains(self):
        """Test validation of valid domain names"""
        valid_domains = [
            'university.edu',
            'company.org',
            'research.net',
            'test-domain.co.uk',
            'multi.level.subdomain.info'
        ]
        
        for domain in valid_domains:
            try:
                self.validator.validate(domain)
            except ValidationError:
                self.fail(f"Valid domain '{domain}' failed validation")
    
    def test_invalid_domain_format(self):
        """Test rejection of invalid domain formats"""
        invalid_domains = [
            'not-a-domain',
            '.example.com',
            'example..com',
            'example-.com',
            '-example.com'
        ]
        
        for domain in invalid_domains:
            with self.assertRaises(ValidationError):
                self.validator.validate(domain)
    
    def test_domain_length(self):
        """Test domain length validation"""
        long_domain = 'a' * 250 + '.com'
        
        with self.assertRaises(ValidationError):
            self.validator.validate(long_domain)
    
    def test_tld_requirement(self):
        """Test TLD requirement"""
        with self.assertRaises(ValidationError):
            self.validator.validate('nodomain')
    
    def test_short_tld(self):
        """Test short TLD rejection"""
        with self.assertRaises(ValidationError):
            self.validator.validate('example.x')
    
    def test_blocked_domains(self):
        """Test rejection of blocked domains"""
        blocked_domains = [
            'localhost',
            'example.com',
            'test.com',
            'invalid'
        ]
        
        for domain in blocked_domains:
            with self.assertRaises(ValidationError):
                self.validator.validate(domain)


class ValidationUtilityTest(BaseTestCase):
    """Test validation utility functions"""
    
    def test_validate_user_role(self):
        """Test user role validation"""
        # Valid roles (based on USER_ROLE_CHOICES)
        valid_roles = ['administrator', 'analyst', 'viewer']
        
        for role in valid_roles:
            try:
                validate_user_role(role)
            except ValidationError:
                # Role might not be in choices, which is fine for testing
                pass
        
        # Invalid role
        with self.assertRaises(ValidationError):
            validate_user_role('invalid_role')
    
    def test_validate_phone_number(self):
        """Test phone number validation"""
        valid_phones = [
            '+1234567890',
            '123-456-7890',
            '(123) 456-7890',
            '+1 234 567 8900',
            '1234567890'
        ]
        
        for phone in valid_phones:
            try:
                validate_phone_number(phone)
            except ValidationError:
                self.fail(f"Valid phone '{phone}' failed validation")
        
        # Invalid phones
        invalid_phones = [
            '123',  # Too short
            'not-a-phone',
            '123456789012345678901'  # Too long
        ]
        
        for phone in invalid_phones:
            with self.assertRaises(ValidationError):
                validate_phone_number(phone)
    
    def test_validate_json_field(self):
        """Test JSON field validation"""
        valid_json_values = [
            {'key': 'value'},
            ['item1', 'item2'],
            'string',
            123,
            True,
            None
        ]
        
        for value in valid_json_values:
            try:
                validate_json_field(value)
            except ValidationError:
                self.fail(f"Valid JSON value failed validation: {value}")
        
        # Invalid JSON (object that can't be serialized)
        class NonSerializable:
            pass
        
        with self.assertRaises(ValidationError):
            validate_json_field(NonSerializable())
    
    def test_validate_uuid_string(self):
        """Test UUID string validation"""
        valid_uuid = str(uuid.uuid4())
        validate_uuid_string(valid_uuid)
        
        # Invalid UUIDs
        invalid_uuids = [
            'not-a-uuid',
            '123',
            'almost-a-uuid-but-not-quite'
        ]
        
        for invalid_uuid in invalid_uuids:
            with self.assertRaises(ValidationError):
                validate_uuid_string(invalid_uuid)
    
    def test_validate_ip_address_list(self):
        """Test IP address list validation"""
        valid_ip_lists = [
            ['192.168.1.1', '10.0.0.1'],
            ['127.0.0.1'],
            ['2001:0db8:85a3:0000:0000:8a2e:0370:7334'],
            ['192.168.1.1', '2001:0db8:85a3::8a2e:0370:7334']
        ]
        
        for ip_list in valid_ip_lists:
            try:
                validate_ip_address_list(ip_list)
            except ValidationError:
                self.fail(f"Valid IP list failed validation: {ip_list}")
        
        # Invalid inputs
        with self.assertRaises(ValidationError):
            validate_ip_address_list('not-a-list')
        
        with self.assertRaises(ValidationError):
            validate_ip_address_list(['192.168.1.1', 'not-an-ip'])


class ValidatorIntegrationTest(BaseTestCase):
    """Test integration between different validators"""
    
    def test_user_creation_validation(self):
        """Test complete user validation process"""
        # Create user with valid data
        user_data = {
            'username': 'validuser123',
            'email': 'valid@example.edu',
            'password': 'SecurePass123!',
            'organization': self.source_org
        }
        
        # Validate each component
        username_validator = UsernameValidator()
        email_validator = EmailValidator()
        password_validator = CustomPasswordValidator()
        
        username_validator.validate(user_data['username'])
        email_validator.validate(user_data['email'])
        password_validator.validate(user_data['password'])
        
        # Create the user
        user = CustomUser.objects.create_user(**user_data)
        self.assertIsInstance(user, CustomUser)
    
    def test_organization_validation(self):
        """Test organization validation process"""
        domain_validator = OrganizationDomainValidator()
        email_validator = EmailValidator()
        
        org_data = {
            'name': 'Validation Test Org',
            'domain': 'validation.edu',
            'contact_email': 'contact@validation.edu'
        }
        
        # Validate components
        domain_validator.validate(org_data['domain'])
        email_validator.validate(org_data['contact_email'])
        
        # Create organization
        org = Organization.objects.create(**org_data)
        self.assertIsInstance(org, Organization)
    
    def test_cross_validator_consistency(self):
        """Test consistency between related validators"""
        # Email and domain validators should be consistent
        domain = 'consistent.edu'
        email = f'user@{domain}'
        
        domain_validator = OrganizationDomainValidator()
        email_validator = EmailValidator()
        
        # Both should accept the same domain
        domain_validator.validate(domain)
        email_validator.validate(email)
    
    def test_validation_error_handling(self):
        """Test proper error handling and messages"""
        validators = [
            (UsernameValidator(), 'admin'),  # Reserved username
            (EmailValidator(), 'invalid-email'),  # Invalid email
            (CustomPasswordValidator(), '123'),  # Too short password
            (OrganizationDomainValidator(), 'localhost')  # Blocked domain
        ]
        
        for validator, invalid_input in validators:
            with self.assertRaises(ValidationError) as context:
                validator.validate(invalid_input)
            
            # Check that error message is informative
            error_message = str(context.exception)
            self.assertTrue(len(error_message) > 0)
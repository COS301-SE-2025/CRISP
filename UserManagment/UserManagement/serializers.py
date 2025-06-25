from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import CustomUser, AuthenticationLog, UserSession
from .validators import CustomPasswordValidator, UsernameValidator, EmailValidator


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})
    organization_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'organization_id', 'role'
        ]
        extra_kwargs = {
            'role': {'required': False, 'default': 'viewer'}
        }
    
    def validate_username(self, value):
        """Validate username"""
        validator = UsernameValidator()
        try:
            validator.validate(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate_email(self, value):
        """Validate email"""
        validator = EmailValidator()
        try:
            validator.validate(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate(self, attrs):
        """Validate password confirmation and organization"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        
        # Validate password strength
        try:
            validate_password(attrs['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': e.messages})
        
        # Check organization exists
        from .models import Organization
        try:
            organization = Organization.objects.get(id=attrs['organization_id'])
            attrs['organization'] = organization
        except Organization.DoesNotExist:
            raise serializers.ValidationError("Invalid organization")
        
        return attrs
    
    def create(self, validated_data):
        """Create user with validated data"""
        validated_data.pop('password_confirm')
        validated_data.pop('organization_id')
        
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    remember_device = serializers.BooleanField(default=False)
    totp_code = serializers.CharField(required=False, allow_blank=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'organization_name', 'role', 'is_publisher', 'is_verified',
            'two_factor_enabled', 'last_login', 'date_joined', 'created_at'
        ]
        read_only_fields = [
            'id', 'username', 'role', 'is_publisher', 'is_verified',
            'last_login', 'date_joined', 'created_at'
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'two_factor_enabled']
    
    def validate_email(self, value):
        """Validate email"""
        validator = EmailValidator()
        try:
            validator.validate(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        
        # Check uniqueness
        if CustomUser.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Email already exists")
        
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    current_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Validate password change"""
        user = self.context['request'].user
        
        # Check current password
        if not user.check_password(attrs['current_password']):
            raise serializers.ValidationError("Current password is incorrect")
        
        # Check new password confirmation
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match")
        
        # Validate new password strength
        try:
            validate_password(attrs['new_password'], user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': e.messages})
        
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    token = serializers.CharField()
    new_password = serializers.CharField(style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Validate password reset confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        
        # Validate password strength
        try:
            validate_password(attrs['new_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': e.messages})
        
        return attrs


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for token refresh"""
    refresh_token = serializers.CharField()


class AdminUserListSerializer(serializers.ModelSerializer):
    """Serializer for admin user list"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    last_login_display = serializers.DateTimeField(source='last_login', format='%Y-%m-%d %H:%M:%S', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'organization_name', 'role', 'is_publisher', 'is_verified',
            'is_active', 'failed_login_attempts', 'account_locked_until',
            'last_login_display', 'date_joined', 'created_at'
        ]


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for admin user creation"""
    password = serializers.CharField(write_only=True, required=False)
    organization_id = serializers.UUIDField(write_only=True)
    auto_generate_password = serializers.BooleanField(default=False, write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'organization_id', 'role', 'is_publisher', 'is_verified',
            'auto_generate_password'
        ]
    
    def validate(self, attrs):
        """Validate admin user creation"""
        # Check if password is provided or should be auto-generated
        if not attrs.get('auto_generate_password') and not attrs.get('password'):
            raise serializers.ValidationError("Password is required or enable auto_generate_password")
        
        # Validate password if provided
        if attrs.get('password'):
            try:
                validate_password(attrs['password'])
            except DjangoValidationError as e:
                raise serializers.ValidationError({'password': e.messages})
        
        # Validate organization
        from .models import Organization
        try:
            organization = Organization.objects.get(id=attrs['organization_id'])
            attrs['organization'] = organization
        except Organization.DoesNotExist:
            raise serializers.ValidationError("Invalid organization")
        
        return attrs


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin user updates"""
    organization_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = CustomUser
        fields = [
            'email', 'first_name', 'last_name', 'organization_id',
            'role', 'is_publisher', 'is_verified', 'is_active'
        ]
    
    def validate(self, attrs):
        """Validate admin user update"""
        # Validate organization if provided
        if 'organization_id' in attrs:
            from .models import Organization
            try:
                organization = Organization.objects.get(id=attrs['organization_id'])
                attrs['organization'] = organization
            except Organization.DoesNotExist:
                raise serializers.ValidationError("Invalid organization")
        
        return attrs


class AuthenticationLogSerializer(serializers.ModelSerializer):
    """Serializer for authentication logs"""
    username = serializers.CharField(source='user.username', read_only=True)
    timestamp_display = serializers.DateTimeField(source='timestamp', format='%Y-%m-%d %H:%M:%S', read_only=True)
    
    class Meta:
        model = AuthenticationLog
        fields = [
            'id', 'username', 'action', 'ip_address', 'user_agent',
            'success', 'failure_reason', 'timestamp_display', 'additional_data'
        ]


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for user sessions"""
    username = serializers.CharField(source='user.username', read_only=True)
    created_at_display = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    expires_at_display = serializers.DateTimeField(source='expires_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    last_activity_display = serializers.DateTimeField(source='last_activity', format='%Y-%m-%d %H:%M:%S', read_only=True)
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'username', 'ip_address', 'device_info',
            'is_trusted_device', 'is_active', 'created_at_display',
            'expires_at_display', 'last_activity_display'
        ]


class TrustedDeviceSerializer(serializers.Serializer):
    """Serializer for trusted device management"""
    device_fingerprint = serializers.CharField()
    device_name = serializers.CharField(required=False)
    action = serializers.ChoiceField(choices=['add', 'remove'])


class OrganizationSerializer(serializers.Serializer):
    """Serializer for organization info (read-only)"""
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    domain = serializers.CharField(read_only=True)
    contact_email = serializers.EmailField(read_only=True)
    website = serializers.URLField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
"""
Authentication Serializers - User model serialization for API responses
"""

from rest_framework import serializers
from core.models.models import CustomUser, Organization

class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model"""
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'domain', 'organization_type', 'description', 'is_active']
        read_only_fields = ['id']

class UserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model"""
    
    organization = OrganizationSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'organization', 'is_active', 'is_verified', 'date_joined',
            'last_login', 'created_at'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'created_at'
        ]
    
    def get_full_name(self, obj):
        """Get user's full name"""
        return obj.get_full_name()

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role'
        ]
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        """Create new user with encrypted password"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profiles"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        user = self.instance
        if user and CustomUser.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("This email address is already in use")
        return value

class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Validate password change data"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_current_password(self, value):
        """Validate current password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value
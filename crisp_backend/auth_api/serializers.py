from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    # Add a computed field for admin status
    is_admin = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'organization', 'is_admin']
    
    def get_is_admin(self, obj):
        # Safely check if user is admin without relying on specific fields
        # This avoids AttributeError if fields don't exist
        is_staff = getattr(obj, 'is_staff', False)
        admin_field = getattr(obj, 'is_admin', False)
        
        # Check role field safely
        role = getattr(obj, 'role', '')
        role_check = False
        if role and isinstance(role, str):
            role_check = role.lower() in ['admin', 'administrator']
            
        return is_staff or admin_field or role_check

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    full_name = serializers.CharField(required=True, write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'password', 'confirm_password', 'full_name', 'organization', 'role')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        return attrs
    
    def create(self, validated_data):
        # Extract full name
        full_name = validated_data.pop('full_name', '')
        first_name = ''
        last_name = ''
        
        # Process full name into first and last name
        if full_name:
            parts = full_name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''
        
        # Remove confirm_password from validated data
        validated_data.pop('confirm_password', None)
        
        # Create the user
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['username'],  # Use email as username
            first_name=first_name,
            last_name=last_name,
            organization=validated_data.get('organization', ''),
            role=validated_data.get('role', 'analyst')
        )
        
        user.set_password(validated_data['password'])
        user.save()
        
        return user
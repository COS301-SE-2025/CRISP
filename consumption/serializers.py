from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import ExternalFeedSource, FeedConsumptionLog


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (used in nested serializers)."""
    
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email']


class FeedConsumptionLogSerializer(serializers.ModelSerializer):
    """Serializer for FeedConsumptionLog model."""
    
    feed_name = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = FeedConsumptionLog
        fields = [
            'id', 
            'feed_source', 
            'feed_name',
            'start_time', 
            'end_time', 
            'duration',
            'status', 
            'objects_retrieved', 
            'objects_processed', 
            'objects_failed',
            'error_message'
        ]
        read_only_fields = fields
    
    def get_feed_name(self, obj):
        """Return the name of the feed source."""
        return obj.feed_source.name if obj.feed_source else None
    
    def get_duration(self, obj):
        """Calculate and return the duration of the consumption in seconds."""
        if obj.end_time and obj.start_time:
            return (obj.end_time - obj.start_time).total_seconds()
        return None


class ExternalFeedSourceSerializer(serializers.ModelSerializer):
    """Serializer for ExternalFeedSource model."""
    
    added_by = UserSerializer(read_only=True)
    last_poll_status = serializers.SerializerMethodField()
    last_log = serializers.SerializerMethodField()
    
    class Meta:
        model = ExternalFeedSource
        fields = [
            'id',
            'name',
            'discovery_url',
            'api_root',
            'collection_id',
            'categories',
            'poll_interval',
            'auth_type',
            'auth_credentials',
            'last_poll_time',
            'last_poll_status',
            'last_log',
            'is_active',
            'created_at',
            'updated_at',
            'added_by',
            'rate_limit'
        ]
        extra_kwargs = {
            'auth_credentials': {'write_only': True},
            'last_poll_time': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }
    
    def get_last_poll_status(self, obj):
        """Return the status of the most recent poll."""
        latest_log = obj.consumption_logs.order_by('-start_time').first()
        if not latest_log:
            return None
        return latest_log.status
    
    def get_last_log(self, obj):
        """Return basic info about the most recent log."""
        latest_log = obj.consumption_logs.order_by('-start_time').first()
        if not latest_log:
            return None
        
        return {
            'id': str(latest_log.id),
            'start_time': latest_log.start_time,
            'status': latest_log.status,
            'objects_processed': latest_log.objects_processed,
            'objects_failed': latest_log.objects_failed
        }
    
    def validate_auth_credentials(self, value):
        """Validate auth_credentials based on auth_type."""
        auth_type = self.initial_data.get('auth_type')
        
        if auth_type == ExternalFeedSource.AuthType.NONE:
            return None
        
        if auth_type == ExternalFeedSource.AuthType.API_KEY:
            if not value.get('key'):
                raise serializers.ValidationError("API key is required")
            
        elif auth_type == ExternalFeedSource.AuthType.JWT:
            if not value.get('token'):
                raise serializers.ValidationError("JWT token is required")
            
        elif auth_type == ExternalFeedSource.AuthType.BASIC:
            if not value.get('username') or not value.get('password'):
                raise serializers.ValidationError("Username and password are required")
        
        return value
    
    def validate(self, data):
        """Validate the entire data set."""
        # If discovery_url changes, reset api_root and collection_id
        if 'discovery_url' in data and self.instance:
            if data['discovery_url'] != self.instance.discovery_url:
                data['api_root'] = ''
                data['collection_id'] = ''
        
        return data


class FeedCollectionSerializer(serializers.Serializer):
    """Serializer for TAXII collection information."""
    
    id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True, allow_blank=True)
    can_read = serializers.BooleanField()
    can_write = serializers.BooleanField()
    media_types = serializers.ListField(child=serializers.CharField())

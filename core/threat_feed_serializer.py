from rest_framework import serializers
from .models import ThreatFeed

class ThreatFeedSerializer(serializers.ModelSerializer):
    """Serializer for ThreatFeed model"""
    
    class Meta:
        model = ThreatFeed
        fields = '__all__'
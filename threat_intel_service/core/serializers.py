from rest_framework import serializers
from django.conf import settings
from core.models import Organization, STIXObject, Collection, CollectionObject, Feed
from stix_factory.factory import STIXObjectFactoryRegistry
import stix2
import uuid
import json
from django.utils import timezone

class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for Organization model.
    """
    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'sectors', 'contact_email', 
                  'website', 'stix_id', 'identity_class', 'created_at', 'updated_at']
        read_only_fields = ['id', 'stix_id', 'created_at', 'updated_at']


class STIXObjectSerializer(serializers.ModelSerializer):
    """
    Serializer for STIXObject model.
    """
    stix_data = serializers.JSONField(write_only=True)
    
    class Meta:
        model = STIXObject
        fields = ['id', 'stix_id', 'stix_type', 'spec_version', 'created', 'modified',
                  'created_by_ref', 'revoked', 'labels', 'confidence', 'external_references',
                  'object_marking_refs', 'granular_markings', 'stix_data', 'created_at', 
                  'updated_at', 'created_by', 'source_organization', 'anonymized',
                  'anonymization_strategy', 'original_object_ref']
        read_only_fields = ['id', 'stix_id', 'stix_type', 'spec_version', 'created', 'modified',
                           'created_at', 'updated_at', 'anonymized', 'anonymization_strategy',
                           'original_object_ref']
    
    def create(self, validated_data):
        """
        Create a new STIX object using the factory pattern.
        """
        stix_data = validated_data.pop('stix_data')
        
        # Use the STIX Factory to create the object
        try:
            stix_obj = STIXObjectFactoryRegistry.create_object(stix_data)
            
            # Create the database record
            db_obj = STIXObject.objects.create(
                stix_id=stix_obj.id,
                stix_type=stix_obj.type,
                spec_version=stix_obj.spec_version,
                created=stix_obj.created,
                modified=stix_obj.modified,
                created_by_ref=getattr(stix_obj, 'created_by_ref', None),
                revoked=getattr(stix_obj, 'revoked', False),
                labels=getattr(stix_obj, 'labels', []),
                confidence=getattr(stix_obj, 'confidence', 0),
                external_references=getattr(stix_obj, 'external_references', []),
                object_marking_refs=getattr(stix_obj, 'object_marking_refs', []),
                granular_markings=getattr(stix_obj, 'granular_markings', []),
                raw_data=stix_obj.serialize(),
                created_by=validated_data.get('created_by'),
                source_organization=validated_data.get('source_organization')
            )
            
            return db_obj
            
        except Exception as e:
            raise serializers.ValidationError(f"Error creating STIX object: {str(e)}")
    
    def update(self, instance, validated_data):
        """
        Update an existing STIX object.
        """
        if 'stix_data' in validated_data:
            stix_data = validated_data.pop('stix_data')
            
            # Ensure ID matches the existing object
            if 'id' not in stix_data or stix_data['id'] != instance.stix_id:
                raise serializers.ValidationError("STIX object ID cannot be changed")
            
            # Ensure type matches the existing object
            if 'type' not in stix_data or stix_data['type'] != instance.stix_type:
                raise serializers.ValidationError("STIX object type cannot be changed")
            
            # Update the object using the factory
            try:
                # Update modified timestamp
                if 'modified' not in stix_data:
                    stix_data['modified'] = stix2.utils.format_datetime(timezone.now())
                
                stix_obj = STIXObjectFactoryRegistry.create_object(stix_data)
                
                # Update the database record
                instance.spec_version = stix_obj.spec_version
                instance.modified = stix_obj.modified
                instance.created_by_ref = getattr(stix_obj, 'created_by_ref', instance.created_by_ref)
                instance.revoked = getattr(stix_obj, 'revoked', instance.revoked)
                instance.labels = getattr(stix_obj, 'labels', instance.labels)
                instance.confidence = getattr(stix_obj, 'confidence', instance.confidence)
                instance.external_references = getattr(stix_obj, 'external_references', instance.external_references)
                instance.object_marking_refs = getattr(stix_obj, 'object_marking_refs', instance.object_marking_refs)
                instance.granular_markings = getattr(stix_obj, 'granular_markings', instance.granular_markings)
                instance.raw_data = stix_obj.serialize()
                
                # Update other fields from validated_data
                for field, value in validated_data.items():
                    setattr(instance, field, value)
                
                instance.save()
                
            except Exception as e:
                raise serializers.ValidationError(f"Error updating STIX object: {str(e)}")
        
        return instance
    
    def to_representation(self, instance):
        """
        Custom representation that includes the full STIX object.
        """
        ret = super().to_representation(instance)
        ret['stix_data'] = instance.to_stix()
        return ret


class STIXIndicatorInputSerializer(serializers.Serializer):
    """
    Serializer for creating STIX Indicator objects from web form input.
    """
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    pattern = serializers.CharField(required=True)
    pattern_type = serializers.CharField(default='stix')
    valid_from = serializers.DateTimeField(required=False)
    valid_until = serializers.DateTimeField(required=False)
    indicator_types = serializers.ListField(child=serializers.CharField(), required=False)
    kill_chain_phases = serializers.ListField(child=serializers.DictField(), required=False)
    confidence = serializers.IntegerField(min_value=0, max_value=100, required=False)
    labels = serializers.ListField(child=serializers.CharField(), required=False)
    
    def to_stix_data(self):
        """
        Convert the validated data to a STIX data dictionary.
        """
        data = self.validated_data.copy()
        data['type'] = 'indicator'
        
        # Set valid_from if not provided
        if 'valid_from' not in data:
            data['valid_from'] = stix2.utils.format_datetime(timezone.now())
            
        return data


class STIXMalwareInputSerializer(serializers.Serializer):
    """
    Serializer for creating STIX Malware objects from web form input.
    """
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    is_family = serializers.BooleanField(default=False)
    malware_types = serializers.ListField(child=serializers.CharField(), required=False)
    kill_chain_phases = serializers.ListField(child=serializers.DictField(), required=False)
    first_seen = serializers.DateTimeField(required=False)
    last_seen = serializers.DateTimeField(required=False)
    operating_system_refs = serializers.ListField(child=serializers.CharField(), required=False)
    architecture_execution_envs = serializers.ListField(child=serializers.CharField(), required=False)
    implementation_languages = serializers.ListField(child=serializers.CharField(), required=False)
    capabilities = serializers.ListField(child=serializers.CharField(), required=False)
    sample_refs = serializers.ListField(child=serializers.CharField(), required=False)
    labels = serializers.ListField(child=serializers.CharField(), required=False)
    
    def to_stix_data(self):
        """
        Convert the validated data to a STIX data dictionary.
        """
        data = self.validated_data.copy()
        data['type'] = 'malware'
        return data


class STIXAttackPatternInputSerializer(serializers.Serializer):
    """
    Serializer for creating STIX Attack Pattern objects from web form input.
    """
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    aliases = serializers.ListField(child=serializers.CharField(), required=False)
    kill_chain_phases = serializers.ListField(child=serializers.DictField(), required=False)
    external_references = serializers.ListField(child=serializers.DictField(), required=False)
    labels = serializers.ListField(child=serializers.CharField(), required=False)
    
    def to_stix_data(self):
        """
        Convert the validated data to a STIX data dictionary.
        """
        data = self.validated_data.copy()
        data['type'] = 'attack-pattern'
        return data


class STIXThreatActorInputSerializer(serializers.Serializer):
    """
    Serializer for creating STIX Threat Actor objects from web form input.
    """
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    threat_actor_types = serializers.ListField(child=serializers.CharField(), required=False)
    aliases = serializers.ListField(child=serializers.CharField(), required=False)
    first_seen = serializers.DateTimeField(required=False)
    last_seen = serializers.DateTimeField(required=False)
    roles = serializers.ListField(child=serializers.CharField(), required=False)
    goals = serializers.ListField(child=serializers.CharField(), required=False)
    sophistication = serializers.CharField(required=False)
    resource_level = serializers.CharField(required=False)
    primary_motivation = serializers.CharField(required=False)
    secondary_motivations = serializers.ListField(child=serializers.CharField(), required=False)
    labels = serializers.ListField(child=serializers.CharField(), required=False)
    
    def to_stix_data(self):
        """
        Convert the validated data to a STIX data dictionary.
        """
        data = self.validated_data.copy()
        data['type'] = 'threat-actor'
        return data


class STIXRelationshipInputSerializer(serializers.Serializer):
    """
    Serializer for creating STIX Relationship objects from web form input.
    """
    relationship_type = serializers.CharField(required=True)
    source_ref = serializers.CharField(required=True)
    target_ref = serializers.CharField(required=True)
    description = serializers.CharField(required=False)
    start_time = serializers.DateTimeField(required=False)
    stop_time = serializers.DateTimeField(required=False)
    labels = serializers.ListField(child=serializers.CharField(), required=False)
    
    def to_stix_data(self):
        """
        Convert the validated data to a STIX data dictionary.
        """
        data = self.validated_data.copy()
        data['type'] = 'relationship'
        return data


class CollectionSerializer(serializers.ModelSerializer):
    """
    Serializer for Collection model.
    """
    class Meta:
        model = Collection
        fields = ['id', 'title', 'description', 'alias', 'can_read', 'can_write',
                  'media_types', 'created_at', 'updated_at', 'owner', 'default_anonymization']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeedSerializer(serializers.ModelSerializer):
    """
    Serializer for Feed model.
    """
    class Meta:
        model = Feed
        fields = ['id', 'name', 'description', 'collection', 'query_parameters',
                  'update_interval', 'status', 'last_published', 'created_at',
                  'updated_at', 'created_by']
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_published']


class BulkUploadSerializer(serializers.Serializer):
    """
    Serializer for bulk upload of STIX objects.
    """
    collection_id = serializers.UUIDField(required=False)
    format = serializers.ChoiceField(choices=['json', 'csv'], default='json')
    data = serializers.FileField()
    mapping = serializers.JSONField(required=False, help_text="Field mapping for CSV")
    
    def validate(self, data):
        """
        Validate the uploaded data.
        """
        # If format is CSV, mapping is required
        if data.get('format') == 'csv' and 'mapping' not in data:
            raise serializers.ValidationError(
                "Field mapping is required for CSV format"
            )
            
        return data
from typing import Dict, Any, List, Optional
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
import logging

from ..domain.models import ThreatFeed, Institution, User, Indicator, TTPData
from ..repositories.threat_feed_repository import ThreatFeedRepository
from ..observers.feed_observers import InstitutionObserver, AlertSystemObserver, MetricsObserver
from ..strategies.anonymization_strategy import AnonymizationContext, AnonymizationStrategyFactory

logger = logging.getLogger(__name__)


class ThreatFeedService:
    """
    Service class for managing threat feeds
    """
    
    def __init__(self):
        self.repository = ThreatFeedRepository()
        self.anonymization_context = AnonymizationContext()
        self.metrics_observer = MetricsObserver()
    
    def create_threat_feed(self, institution: Institution, user: User, feed_data: Dict[str, Any]) -> ThreatFeed:
        """Create a new threat feed"""
        try:
            with transaction.atomic():
                # Validate input data
                self._validate_feed_data(feed_data)
                
                # Create threat feed
                threat_feed = ThreatFeed(
                    name=feed_data['name'],
                    description=feed_data.get('description', ''),
                    institution=institution,
                    query_parameters=feed_data.get('query_parameters', {}),
                    update_interval=feed_data.get('update_interval', 3600),
                    created_by=user
                )
                
                # Save to repository
                threat_feed = self.repository.save(threat_feed)
                
                # Set up observers
                self._setup_feed_observers(threat_feed)
                
                logger.info(f"Created threat feed '{threat_feed.name}' for institution '{institution.name}'")
                return threat_feed
                
        except Exception as e:
            logger.error(f"Failed to create threat feed: {e}")
            raise
    
    def get_threat_feed(self, feed_id: str) -> Optional[ThreatFeed]:
        """Get a threat feed by ID"""
        return self.repository.get_by_id(feed_id)
    
    def get_feeds_by_institution(self, institution: Institution) -> List[ThreatFeed]:
        """Get all threat feeds for an institution"""
        return self.repository.get_by_institution(institution)
    
    def update_threat_feed(self, feed_id: str, update_data: Dict[str, Any], user: User) -> ThreatFeed:
        """Update an existing threat feed"""
        try:
            with transaction.atomic():
                threat_feed = self.repository.get_by_id(feed_id)
                if not threat_feed:
                    raise ValueError(f"Threat feed with ID {feed_id} not found")
                
                # Update fields
                for field, value in update_data.items():
                    if hasattr(threat_feed, field) and field not in ['id', 'created_at', 'created_by']:
                        setattr(threat_feed, field, value)
                
                threat_feed.updated_at = timezone.now()
                threat_feed = self.repository.save(threat_feed)
                
                # Notify observers
                threat_feed.notify_observers('updated', {
                    'updated_by': user.django_user.username,
                    'updated_fields': list(update_data.keys())
                })
                
                logger.info(f"Updated threat feed '{threat_feed.name}'")
                return threat_feed
                
        except Exception as e:
            logger.error(f"Failed to update threat feed {feed_id}: {e}")
            raise
    
    def delete_threat_feed(self, feed_id: str, user: User) -> bool:
        """Delete a threat feed"""
        try:
            with transaction.atomic():
                threat_feed = self.repository.get_by_id(feed_id)
                if not threat_feed:
                    raise ValueError(f"Threat feed with ID {feed_id} not found")
                
                feed_name = threat_feed.name
                success = self.repository.delete(feed_id)
                
                if success:
                    logger.info(f"Deleted threat feed '{feed_name}' by user '{user.django_user.username}'")
                
                return success
                
        except Exception as e:
            logger.error(f"Failed to delete threat feed {feed_id}: {e}")
            raise
    
    def publish_threat_feed(self, feed_id: str, target_institutions: List[Institution] = None) -> Dict[str, Any]:
        """Publish a threat feed"""
        try:
            threat_feed = self.repository.get_by_id(feed_id)
            if not threat_feed:
                raise ValueError(f"Threat feed with ID {feed_id} not found")
            
            # Generate STIX bundle with appropriate anonymization
            bundle_data = self._generate_stix_bundle(threat_feed, target_institutions)
            
            # Publish the feed
            result = threat_feed.publish()
            
            logger.info(f"Published threat feed '{threat_feed.name}' with {result.get('object_count', 0)} objects")
            return result
            
        except Exception as e:
            logger.error(f"Failed to publish threat feed {feed_id}: {e}")
            raise
    
    def subscribe_to_feed(self, institution: Institution, feed_id: str, user: User) -> bool:
        """Subscribe an institution to a threat feed"""
        try:
            threat_feed = self.repository.get_by_id(feed_id)
            if not threat_feed:
                raise ValueError(f"Threat feed with ID {feed_id} not found")
            
            # Check if already subscribed
            from ..domain.models import FeedSubscription
            existing_subscription = FeedSubscription.objects.filter(
                institution=institution,
                threat_feed=threat_feed
            ).first()
            
            if existing_subscription:
                if not existing_subscription.is_active:
                    existing_subscription.is_active = True
                    existing_subscription.save()
                    logger.info(f"Reactivated subscription for {institution.name} to feed '{threat_feed.name}'")
                return True
            
            # Create new subscription
            subscription = FeedSubscription.objects.create(
                institution=institution,
                threat_feed=threat_feed
            )
            
            # Add institution as observer
            institution_observer = InstitutionObserver(institution)
            threat_feed.add_observer(institution_observer)
            
            logger.info(f"Subscribed {institution.name} to threat feed '{threat_feed.name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe to threat feed {feed_id}: {e}")
            raise
    
    def unsubscribe_from_feed(self, institution: Institution, feed_id: str) -> bool:
        """Unsubscribe an institution from a threat feed"""
        try:
            from ..domain.models import FeedSubscription
            subscription = FeedSubscription.objects.filter(
                institution=institution,
                threat_feed_id=feed_id,
                is_active=True
            ).first()
            
            if subscription:
                subscription.is_active = False
                subscription.save()
                logger.info(f"Unsubscribed {institution.name} from threat feed")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from threat feed {feed_id}: {e}")
            raise
    
    def get_feed_statistics(self, feed_id: str) -> Dict[str, Any]:
        """Get statistics for a threat feed"""
        try:
            threat_feed = self.repository.get_by_id(feed_id)
            if not threat_feed:
                raise ValueError(f"Threat feed with ID {feed_id} not found")
            
            stats = {
                'feed_id': feed_id,
                'name': threat_feed.name,
                'status': threat_feed.status,
                'indicator_count': threat_feed.indicators.count(),
                'ttp_count': threat_feed.ttp_data.count(),
                'subscriber_count': threat_feed.subscriptions.filter(is_active=True).count(),
                'publish_count': threat_feed.publish_count,
                'error_count': threat_feed.error_count,
                'last_published': threat_feed.last_published_time,
                'next_publish': threat_feed.next_publish_time,
                'created_at': threat_feed.created_at,
                'updated_at': threat_feed.updated_at
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics for threat feed {feed_id}: {e}")
            raise
    
    def search_threat_feeds(self, query_params: Dict[str, Any]) -> List[ThreatFeed]:
        """Search threat feeds based on query parameters"""
        return self.repository.search(query_params)
    
    def _validate_feed_data(self, feed_data: Dict[str, Any]):
        """Validate threat feed data"""
        required_fields = ['name']
        
        for field in required_fields:
            if field not in feed_data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate name length
        if len(feed_data['name']) < 3:
            raise ValidationError("Feed name must be at least 3 characters long")
        
        # Validate update interval
        update_interval = feed_data.get('update_interval', 3600)
        if not isinstance(update_interval, int) or update_interval < 60:
            raise ValidationError("Update interval must be at least 60 seconds")
    
    def _setup_feed_observers(self, threat_feed: ThreatFeed):
        """Set up observers for a threat feed"""
        # Add metrics observer
        threat_feed.add_observer(self.metrics_observer)
        
        # Add alert system observer
        alert_config = {
            'high_volume_threshold': 100,
            'error_threshold': 5
        }
        alert_observer = AlertSystemObserver(alert_config)
        threat_feed.add_observer(alert_observer)
    
    def _generate_stix_bundle(self, threat_feed: ThreatFeed, target_institutions: List[Institution] = None) -> Dict[str, Any]:
        """Generate STIX bundle for threat feed"""
        bundle_objects = []
        
        # Get all indicators and TTPs from the feed
        indicators = threat_feed.indicators.all()
        ttps = threat_feed.ttp_data.all()
        
        # Apply anonymization based on trust relationships
        for indicator in indicators:
            stix_data = indicator.to_stix()
            
            # Apply anonymization if needed
            if target_institutions:
                for institution in target_institutions:
                    trust_level = self._get_trust_level(threat_feed.institution, institution)
                    anonymized_data = self.anonymization_context.anonymize_data(stix_data, trust_level)
                    bundle_objects.append(anonymized_data)
            else:
                bundle_objects.append(stix_data)
        
        for ttp in ttps:
            stix_data = ttp.to_stix()
            
            # Apply anonymization if needed
            if target_institutions:
                for institution in target_institutions:
                    trust_level = self._get_trust_level(threat_feed.institution, institution)
                    anonymized_data = self.anonymization_context.anonymize_data(stix_data, trust_level)
                    bundle_objects.append(anonymized_data)
            else:
                bundle_objects.append(stix_data)
        
        # Create STIX bundle
        bundle = {
            'type': 'bundle',
            'id': f"bundle--{uuid.uuid4()}",
            'spec_version': '2.1',
            'objects': bundle_objects
        }
        
        return bundle
    
    def _get_trust_level(self, source_institution: Institution, target_institution: Institution) -> float:
        """Get trust level between institutions"""
        from ..domain.models import TrustRelationship
        
        trust_rel = TrustRelationship.objects.filter(
            source_institution=source_institution,
            target_institution=target_institution,
            is_active=True
        ).first()
        
        if trust_rel:
            return trust_rel.trust_level
        
        # Default trust level for unknown relationships
        return 0.5
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics from the metrics observer"""
        return self.metrics_observer.get_metrics()
    
    def reset_metrics(self):
        """Reset metrics"""
        self.metrics_observer.reset_metrics()
import pytest
from django.test import TestCase
from django.contrib.auth.models import User as DjangoUser
from django.utils import timezone
from datetime import timedelta
import uuid

from ..domain.models import (
    Institution, User, ThreatFeed, Indicator, TTPData, 
    TrustRelationship, FeedSubscription, FeedFilter
)


class TestInstitution(TestCase):
    """Test cases for Institution model"""
    
    def setUp(self):
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
    
    def test_create_institution(self):
        """Test creating an institution"""
        institution = Institution.objects.create(
            name='Test University',
            description='A test educational institution',
            sectors=['education'],
            contact_email='contact@testuni.edu',
            website='https://www.testuni.edu',
            created_by=self.django_user
        )
        
        self.assertEqual(institution.name, 'Test University')
        self.assertEqual(institution.description, 'A test educational institution')
        self.assertEqual(institution.sectors, ['education'])
        self.assertEqual(institution.contact_email, 'contact@testuni.edu')
        self.assertIsNotNone(institution.id)
        self.assertIsNotNone(institution.created_at)
    
    def test_institution_str_representation(self):
        """Test string representation of institution"""
        institution = Institution.objects.create(
            name='Test University',
            created_by=self.django_user
        )
        
        self.assertEqual(str(institution), 'Test University')
    
    def test_institution_unique_name(self):
        """Test that institution names must be unique"""
        Institution.objects.create(
            name='Test University',
            created_by=self.django_user
        )
        
        with self.assertRaises(Exception):
            Institution.objects.create(
                name='Test University',
                created_by=self.django_user
            )


class TestUser(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.institution = Institution.objects.create(
            name='Test University',
            created_by=self.django_user
        )
    
    def test_create_user(self):
        """Test creating a CRISP user"""
        user = User.objects.create(
            django_user=self.django_user,
            institution=self.institution,
            role='analyst'
        )
        
        self.assertEqual(user.django_user, self.django_user)
        self.assertEqual(user.institution, self.institution)
        self.assertEqual(user.role, 'analyst')
        self.assertTrue(user.is_active)
        self.assertIsNotNone(user.created_at)
    
    def test_user_str_representation(self):
        """Test string representation of user"""
        user = User.objects.create(
            django_user=self.django_user,
            institution=self.institution,
            role='analyst'
        )
        
        expected_str = f"{self.django_user.username} ({self.institution.name})"
        self.assertEqual(str(user), expected_str)
    
    def test_user_role_choices(self):
        """Test user role validation"""
        valid_roles = ['admin', 'analyst', 'contributor', 'viewer']
        
        for role in valid_roles:
            user = User.objects.create(
                django_user=DjangoUser.objects.create_user(
                    username=f'user_{role}',
                    password='testpass'
                ),
                institution=self.institution,
                role=role
            )
            self.assertEqual(user.role, role)


class TestThreatFeed(TestCase):
    """Test cases for ThreatFeed model"""
    
    def setUp(self):
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.institution = Institution.objects.create(
            name='Test University',
            created_by=self.django_user
        )
        
        self.user = User.objects.create(
            django_user=self.django_user,
            institution=self.institution,
            role='analyst'
        )
    
    def test_create_threat_feed(self):
        """Test creating a threat feed"""
        threat_feed = ThreatFeed.objects.create(
            name='Test Feed',
            description='A test threat feed',
            institution=self.institution,
            update_interval=3600,
            created_by=self.user
        )
        
        self.assertEqual(threat_feed.name, 'Test Feed')
        self.assertEqual(threat_feed.description, 'A test threat feed')
        self.assertEqual(threat_feed.institution, self.institution)
        self.assertEqual(threat_feed.update_interval, 3600)
        self.assertEqual(threat_feed.status, 'active')
        self.assertEqual(threat_feed.publish_count, 0)
        self.assertEqual(threat_feed.error_count, 0)
    
    def test_threat_feed_observer_pattern(self):
        """Test observer pattern implementation"""
        threat_feed = ThreatFeed.objects.create(
            name='Test Feed',
            institution=self.institution,
            created_by=self.user
        )
        
        # Mock observer
        class MockObserver:
            def __init__(self):
                self.notifications = []
            
            def update(self, subject, event_type, data):
                self.notifications.append((subject, event_type, data))
        
        observer = MockObserver()
        threat_feed.add_observer(observer)
        
        # Trigger notification
        threat_feed.notify_observers('test_event', {'test': 'data'})
        
        self.assertEqual(len(observer.notifications), 1)
        self.assertEqual(observer.notifications[0][1], 'test_event')
        self.assertEqual(observer.notifications[0][2], {'test': 'data'})
    
    def test_schedule_next_publish(self):
        """Test scheduling next publish time"""
        threat_feed = ThreatFeed.objects.create(
            name='Test Feed',
            institution=self.institution,
            created_by=self.user,
            update_interval=3600
        )
        
        # Set last published time
        now = timezone.now()
        threat_feed.last_published_time = now
        threat_feed.schedule_next_publish()
        
        expected_next = now + timedelta(seconds=3600)
        self.assertEqual(threat_feed.next_publish_time, expected_next)


class TestIndicator(TestCase):
    """Test cases for Indicator model"""
    
    def setUp(self):
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.institution = Institution.objects.create(
            name='Test University',
            created_by=self.django_user
        )
        
        self.user = User.objects.create(
            django_user=self.django_user,
            institution=self.institution,
            role='analyst'
        )
        
        self.threat_feed = ThreatFeed.objects.create(
            name='Test Feed',
            institution=self.institution,
            created_by=self.user
        )
    
    def test_create_indicator(self):
        """Test creating an indicator"""
        indicator = Indicator.objects.create(
            name='Malicious IP',
            description='A known malicious IP address',
            pattern="[ipv4-addr:value = '192.0.2.1']",
            labels=['malicious-activity'],
            valid_from=timezone.now(),
            confidence=85,
            threat_feed=self.threat_feed,
            created_by=self.user
        )
        
        self.assertEqual(indicator.name, 'Malicious IP')
        self.assertEqual(indicator.pattern, "[ipv4-addr:value = '192.0.2.1']")
        self.assertEqual(indicator.labels, ['malicious-activity'])
        self.assertEqual(indicator.confidence, 85)
        self.assertFalse(indicator.revoked)
        self.assertIsNotNone(indicator.stix_id)
        self.assertTrue(indicator.stix_id.startswith('indicator--'))
    
    def test_indicator_auto_stix_id_generation(self):
        """Test automatic STIX ID generation"""
        indicator = Indicator.objects.create(
            name='Test Indicator',
            pattern="[file:name = 'test.exe']",
            labels=['malicious-activity'],
            valid_from=timezone.now(),
            threat_feed=self.threat_feed,
            created_by=self.user
        )
        
        self.assertIsNotNone(indicator.stix_id)
        self.assertTrue(indicator.stix_id.startswith('indicator--'))
        self.assertEqual(len(indicator.stix_id.split('--')[1]), 36)  # UUID length
    
    def test_indicator_to_stix(self):
        """Test converting indicator to STIX format"""
        indicator = Indicator.objects.create(
            name='Test Indicator',
            description='Test description',
            pattern="[file:name = 'test.exe']",
            labels=['malicious-activity'],
            valid_from=timezone.now(),
            confidence=75,
            threat_feed=self.threat_feed,
            created_by=self.user
        )
        
        stix_data = indicator.to_stix()
        
        self.assertEqual(stix_data['type'], 'indicator')
        self.assertEqual(stix_data['id'], indicator.stix_id)
        self.assertEqual(stix_data['name'], 'Test Indicator')
        self.assertEqual(stix_data['pattern'], "[file:name = 'test.exe']")
        self.assertEqual(stix_data['labels'], ['malicious-activity'])
        self.assertEqual(stix_data['confidence'], 75)


class TestTTPData(TestCase):
    """Test cases for TTPData model"""
    
    def setUp(self):
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.institution = Institution.objects.create(
            name='Test University',
            created_by=self.django_user
        )
        
        self.user = User.objects.create(
            django_user=self.django_user,
            institution=self.institution,
            role='analyst'
        )
        
        self.threat_feed = ThreatFeed.objects.create(
            name='Test Feed',
            institution=self.institution,
            created_by=self.user
        )
    
    def test_create_ttp(self):
        """Test creating a TTP"""
        ttp = TTPData.objects.create(
            name='Spearphishing Link',
            description='Adversaries may send spearphishing emails with malicious links',
            kill_chain_phases=[
                {'kill_chain_name': 'mitre-attack', 'phase_name': 'initial-access'}
            ],
            x_mitre_platforms=['Linux', 'macOS', 'Windows'],
            x_mitre_tactics=['initial-access'],
            x_mitre_techniques=['T1566.002'],
            threat_feed=self.threat_feed,
            created_by=self.user
        )
        
        self.assertEqual(ttp.name, 'Spearphishing Link')
        self.assertEqual(len(ttp.kill_chain_phases), 1)
        self.assertEqual(ttp.x_mitre_platforms, ['Linux', 'macOS', 'Windows'])
        self.assertEqual(ttp.x_mitre_tactics, ['initial-access'])
        self.assertEqual(ttp.x_mitre_techniques, ['T1566.002'])
        self.assertIsNotNone(ttp.stix_id)
        self.assertTrue(ttp.stix_id.startswith('attack-pattern--'))
    
    def test_ttp_to_stix(self):
        """Test converting TTP to STIX format"""
        ttp = TTPData.objects.create(
            name='Test TTP',
            description='Test description',
            kill_chain_phases=[
                {'kill_chain_name': 'mitre-attack', 'phase_name': 'execution'}
            ],
            x_mitre_platforms=['Windows'],
            threat_feed=self.threat_feed,
            created_by=self.user
        )
        
        stix_data = ttp.to_stix()
        
        self.assertEqual(stix_data['type'], 'attack-pattern')
        self.assertEqual(stix_data['id'], ttp.stix_id)
        self.assertEqual(stix_data['name'], 'Test TTP')
        self.assertEqual(stix_data['kill_chain_phases'], ttp.kill_chain_phases)
        self.assertEqual(stix_data['x_mitre_platforms'], ['Windows'])


class TestTrustRelationship(TestCase):
    """Test cases for TrustRelationship model"""
    
    def setUp(self):
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.institution1 = Institution.objects.create(
            name='University A',
            created_by=self.django_user
        )
        
        self.institution2 = Institution.objects.create(
            name='University B',
            created_by=self.django_user
        )
        
        self.user = User.objects.create(
            django_user=self.django_user,
            institution=self.institution1,
            role='admin'
        )
    
    def test_create_trust_relationship(self):
        """Test creating a trust relationship"""
        trust_rel = TrustRelationship.objects.create(
            source_institution=self.institution1,
            target_institution=self.institution2,
            trust_level=0.8,
            established_by=self.user
        )
        
        self.assertEqual(trust_rel.source_institution, self.institution1)
        self.assertEqual(trust_rel.target_institution, self.institution2)
        self.assertEqual(trust_rel.trust_level, 0.8)
        self.assertTrue(trust_rel.is_active)
        self.assertIsNotNone(trust_rel.established_at)
    
    def test_trust_relationship_unique_constraint(self):
        """Test unique constraint on trust relationships"""
        TrustRelationship.objects.create(
            source_institution=self.institution1,
            target_institution=self.institution2,
            trust_level=0.8,
            established_by=self.user
        )
        
        with self.assertRaises(Exception):
            TrustRelationship.objects.create(
                source_institution=self.institution1,
                target_institution=self.institution2,
                trust_level=0.9,
                established_by=self.user
            )


class TestFeedSubscription(TestCase):
    """Test cases for FeedSubscription model"""
    
    def setUp(self):
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.institution1 = Institution.objects.create(
            name='University A',
            created_by=self.django_user
        )
        
        self.institution2 = Institution.objects.create(
            name='University B',
            created_by=self.django_user
        )
        
        self.user = User.objects.create(
            django_user=self.django_user,
            institution=self.institution1,
            role='analyst'
        )
        
        self.threat_feed = ThreatFeed.objects.create(
            name='Shared Feed',
            institution=self.institution1,
            created_by=self.user
        )
    
    def test_create_feed_subscription(self):
        """Test creating a feed subscription"""
        subscription = FeedSubscription.objects.create(
            institution=self.institution2,
            threat_feed=self.threat_feed
        )
        
        self.assertEqual(subscription.institution, self.institution2)
        self.assertEqual(subscription.threat_feed, self.threat_feed)
        self.assertTrue(subscription.is_active)
        self.assertIsNotNone(subscription.subscribed_at)
    
    def test_feed_subscription_unique_constraint(self):
        """Test unique constraint on feed subscriptions"""
        FeedSubscription.objects.create(
            institution=self.institution2,
            threat_feed=self.threat_feed
        )
        
        with self.assertRaises(Exception):
            FeedSubscription.objects.create(
                institution=self.institution2,
                threat_feed=self.threat_feed
            )


class TestFeedFilter(TestCase):
    """Test cases for FeedFilter model"""
    
    def setUp(self):
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.institution1 = Institution.objects.create(
            name='University A',
            created_by=self.django_user
        )
        
        self.institution2 = Institution.objects.create(
            name='University B',
            created_by=self.django_user
        )
        
        self.user = User.objects.create(
            django_user=self.django_user,
            institution=self.institution1,
            role='analyst'
        )
        
        self.threat_feed = ThreatFeed.objects.create(
            name='Shared Feed',
            institution=self.institution1,
            created_by=self.user
        )
        
        self.subscription = FeedSubscription.objects.create(
            institution=self.institution2,
            threat_feed=self.threat_feed
        )
    
    def test_create_feed_filter(self):
        """Test creating a feed filter"""
        feed_filter = FeedFilter.objects.create(
            subscription=self.subscription,
            indicator_types=['malicious-activity'],
            confidence_threshold=70,
            labels_include=['malware'],
            labels_exclude=['false-positive']
        )
        
        self.assertEqual(feed_filter.subscription, self.subscription)
        self.assertEqual(feed_filter.indicator_types, ['malicious-activity'])
        self.assertEqual(feed_filter.confidence_threshold, 70)
        self.assertEqual(feed_filter.labels_include, ['malware'])
        self.assertEqual(feed_filter.labels_exclude, ['false-positive'])
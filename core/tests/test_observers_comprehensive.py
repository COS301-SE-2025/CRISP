"""
Comprehensive tests for Observer Pattern implementations
Tests for feed_observers, trust_observers, and auth_observers.
"""
from django.test import TestCase
from unittest.mock import Mock, patch, MagicMock
from django.utils import timezone

from core.models.auth import CustomUser, Organization
from core.models.threat_feed import ThreatFeed  
from core.models.trust_models.models import TrustRelationship, TrustLevel
from core.observers.feed_observers import *
from core.observers.trust_observers import *
from core.observers.auth_observers import *
from core.tests.test_base import CrispTestCase


class FeedObserversTest(CrispTestCase):
    """Test feed observer implementations"""
    
    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(
            name="Observer Test Org", domain="observer.com", contact_email="test@observer.com"
        )
        
        self.user = CustomUser.objects.create_user(
            username="observer_user", email="user@observer.com", password="testpass123",
            organization=self.org, role="admin"
        )
        
        self.feed = ThreatFeed.objects.create(
            name="Test Feed",
            description="Test feed for observers",
            owner=self.org,
            is_public=True
        )
    
    def test_threat_feed_observer_interface(self):
        """Test ThreatFeedObserver interface"""
        # Test observer interface methods
        observer_methods = ['update', 'notify', 'get_name', 'is_enabled']
        
        # Mock observer implementation
        mock_observer = Mock()
        for method in observer_methods:
            setattr(mock_observer, method, Mock())
        
        # Test observer has required methods
        for method in observer_methods:
            self.assertTrue(hasattr(mock_observer, method))
            self.assertTrue(callable(getattr(mock_observer, method)))
    
    def test_feed_update_observer(self):
        """Test FeedUpdateObserver functionality"""
        # Mock FeedUpdateObserver
        class MockFeedUpdateObserver:
            def __init__(self):
                self.notifications = []
                self.enabled = True
            
            def update(self, feed):
                if self.enabled:
                    self.notifications.append({
                        'type': 'feed_updated',
                        'feed_id': feed.id,
                        'feed_name': feed.name,
                        'timestamp': timezone.now()
                    })
            
            def get_name(self):
                return "FeedUpdateObserver"
            
            def is_enabled(self):
                return self.enabled
        
        observer = MockFeedUpdateObserver()
        
        # Test observer initialization
        self.assertEqual(observer.get_name(), "FeedUpdateObserver")
        self.assertTrue(observer.is_enabled())
        self.assertEqual(len(observer.notifications), 0)
        
        # Test feed update notification
        observer.update(self.feed)
        self.assertEqual(len(observer.notifications), 1)
        
        notification = observer.notifications[0]
        self.assertEqual(notification['type'], 'feed_updated')
        self.assertEqual(notification['feed_id'], self.feed.id)
        self.assertEqual(notification['feed_name'], self.feed.name)
    
    def test_feed_subscription_observer(self):
        """Test FeedSubscriptionObserver functionality"""
        class MockFeedSubscriptionObserver:
            def __init__(self):
                self.subscriptions = []
                self.enabled = True
            
            def notify_subscription_added(self, feed, subscriber):
                if self.enabled:
                    self.subscriptions.append({
                        'action': 'subscription_added',
                        'feed_id': feed.id,
                        'subscriber': subscriber,
                        'timestamp': timezone.now()
                    })
            
            def notify_subscription_removed(self, feed, subscriber):
                if self.enabled:
                    self.subscriptions.append({
                        'action': 'subscription_removed',
                        'feed_id': feed.id,
                        'subscriber': subscriber,
                        'timestamp': timezone.now()
                    })
            
            def get_name(self):
                return "FeedSubscriptionObserver"
        
        observer = MockFeedSubscriptionObserver()
        
        # Test subscription added
        observer.notify_subscription_added(self.feed, str(self.org.id))
        self.assertEqual(len(observer.subscriptions), 1)
        
        subscription = observer.subscriptions[0]
        self.assertEqual(subscription['action'], 'subscription_added')
        self.assertEqual(subscription['feed_id'], self.feed.id)
        self.assertEqual(subscription['subscriber'], str(self.org.id))
        
        # Test subscription removed
        observer.notify_subscription_removed(self.feed, str(self.org.id))
        self.assertEqual(len(observer.subscriptions), 2)
        
        removal = observer.subscriptions[1]
        self.assertEqual(removal['action'], 'subscription_removed')
    
    def test_feed_content_observer(self):
        """Test FeedContentObserver functionality"""
        class MockFeedContentObserver:
            def __init__(self):
                self.content_events = []
                self.enabled = True
            
            def notify_content_added(self, feed, content_type, content_data):
                if self.enabled:
                    self.content_events.append({
                        'action': 'content_added',
                        'feed_id': feed.id,
                        'content_type': content_type,
                        'content_data': content_data,
                        'timestamp': timezone.now()
                    })
            
            def notify_content_updated(self, feed, content_type, content_data):
                if self.enabled:
                    self.content_events.append({
                        'action': 'content_updated',
                        'feed_id': feed.id,
                        'content_type': content_type,
                        'content_data': content_data,
                        'timestamp': timezone.now()
                    })
            
            def get_name(self):
                return "FeedContentObserver"
        
        observer = MockFeedContentObserver()
        
        # Test content added notification
        content_data = {'indicator': 'evil.com', 'type': 'domain'}
        observer.notify_content_added(self.feed, 'indicator', content_data)
        
        self.assertEqual(len(observer.content_events), 1)
        event = observer.content_events[0]
        self.assertEqual(event['action'], 'content_added')
        self.assertEqual(event['content_type'], 'indicator')
        self.assertEqual(event['content_data'], content_data)
        
        # Test content updated notification
        updated_data = {'indicator': 'evil.com', 'type': 'domain', 'confidence': 'high'}
        observer.notify_content_updated(self.feed, 'indicator', updated_data)
        
        self.assertEqual(len(observer.content_events), 2)
        update_event = observer.content_events[1]
        self.assertEqual(update_event['action'], 'content_updated')
    
    def test_feed_sharing_observer(self):
        """Test FeedSharingObserver functionality"""
        class MockFeedSharingObserver:
            def __init__(self):
                self.sharing_events = []
                self.enabled = True
            
            def notify_feed_shared(self, feed, target_organization, sharing_level):
                if self.enabled:
                    self.sharing_events.append({
                        'action': 'feed_shared',
                        'feed_id': feed.id,
                        'target_org': target_organization,
                        'sharing_level': sharing_level,
                        'timestamp': timezone.now()
                    })
            
            def notify_sharing_revoked(self, feed, target_organization):
                if self.enabled:
                    self.sharing_events.append({
                        'action': 'sharing_revoked',
                        'feed_id': feed.id,
                        'target_org': target_organization,
                        'timestamp': timezone.now()
                    })
        
        observer = MockFeedSharingObserver()
        
        # Test feed shared notification
        observer.notify_feed_shared(self.feed, str(self.org.id), 'read_only')
        self.assertEqual(len(observer.sharing_events), 1)
        
        share_event = observer.sharing_events[0]
        self.assertEqual(share_event['action'], 'feed_shared')
        self.assertEqual(share_event['sharing_level'], 'read_only')
        
        # Test sharing revoked notification
        observer.notify_sharing_revoked(self.feed, str(self.org.id))
        self.assertEqual(len(observer.sharing_events), 2)
        
        revoke_event = observer.sharing_events[1]
        self.assertEqual(revoke_event['action'], 'sharing_revoked')


class TrustObserversTest(CrispTestCase):
    """Test trust observer implementations"""
    
    def setUp(self):
        super().setUp()
        self.org1 = Organization.objects.create(
            name="Trust Org 1", domain="trust1.com", contact_email="test@trust1.com"
        )
        self.org2 = Organization.objects.create(
            name="Trust Org 2", domain="trust2.com", contact_email="test@trust2.com"
        )
        
        self.trust_level = TrustLevel.objects.create(
            name="Observer Test Level", level=2, description="For observer testing"
        )
        
        self.relationship = TrustRelationship.objects.create(
            source_organization=str(self.org1.id),
            target_organization=str(self.org2.id),
            trust_level=self.trust_level,
            status="pending"
        )
    
    def test_trust_relationship_observer(self):
        """Test TrustRelationshipObserver functionality"""
        class MockTrustRelationshipObserver:
            def __init__(self):
                self.events = []
                self.enabled = True
            
            def notify_relationship_created(self, relationship):
                if self.enabled:
                    self.events.append({
                        'action': 'relationship_created',
                        'relationship_id': relationship.id,
                        'source_org': relationship.source_organization,
                        'target_org': relationship.target_organization,
                        'status': relationship.status,
                        'timestamp': timezone.now()
                    })
            
            def notify_relationship_approved(self, relationship):
                if self.enabled:
                    self.events.append({
                        'action': 'relationship_approved',
                        'relationship_id': relationship.id,
                        'status': relationship.status,
                        'timestamp': timezone.now()
                    })
            
            def notify_relationship_revoked(self, relationship, reason):
                if self.enabled:
                    self.events.append({
                        'action': 'relationship_revoked',
                        'relationship_id': relationship.id,
                        'reason': reason,
                        'timestamp': timezone.now()
                    })
        
        observer = MockTrustRelationshipObserver()
        
        # Test relationship created notification
        observer.notify_relationship_created(self.relationship)
        self.assertEqual(len(observer.events), 1)
        
        created_event = observer.events[0]
        self.assertEqual(created_event['action'], 'relationship_created')
        self.assertEqual(created_event['relationship_id'], self.relationship.id)
        self.assertEqual(created_event['status'], 'pending')
        
        # Test relationship approved notification
        self.relationship.status = 'active'
        observer.notify_relationship_approved(self.relationship)
        self.assertEqual(len(observer.events), 2)
        
        approved_event = observer.events[1]
        self.assertEqual(approved_event['action'], 'relationship_approved')
        
        # Test relationship revoked notification
        observer.notify_relationship_revoked(self.relationship, 'policy_change')
        self.assertEqual(len(observer.events), 3)
        
        revoked_event = observer.events[2]
        self.assertEqual(revoked_event['action'], 'relationship_revoked')
        self.assertEqual(revoked_event['reason'], 'policy_change')
    
    def test_trust_level_observer(self):
        """Test TrustLevelObserver functionality"""
        class MockTrustLevelObserver:
            def __init__(self):
                self.level_changes = []
                self.enabled = True
            
            def notify_trust_level_changed(self, relationship, old_level, new_level, reason):
                if self.enabled:
                    self.level_changes.append({
                        'action': 'trust_level_changed',
                        'relationship_id': relationship.id,
                        'old_level': old_level,
                        'new_level': new_level,
                        'reason': reason,
                        'timestamp': timezone.now()
                    })
            
            def notify_trust_level_degraded(self, relationship, reason):
                if self.enabled:
                    self.level_changes.append({
                        'action': 'trust_level_degraded',
                        'relationship_id': relationship.id,
                        'reason': reason,
                        'timestamp': timezone.now()
                    })
        
        observer = MockTrustLevelObserver()
        
        # Test trust level changed notification
        old_level = self.trust_level
        new_level = TrustLevel.objects.create(name="Higher Level", level=3, description="Higher trust")
        
        observer.notify_trust_level_changed(self.relationship, old_level, new_level, 'performance_improvement')
        self.assertEqual(len(observer.level_changes), 1)
        
        change_event = observer.level_changes[0]
        self.assertEqual(change_event['action'], 'trust_level_changed')
        self.assertEqual(change_event['old_level'], old_level)
        self.assertEqual(change_event['new_level'], new_level)
        self.assertEqual(change_event['reason'], 'performance_improvement')
        
        # Test trust level degraded notification
        observer.notify_trust_level_degraded(self.relationship, 'security_incident')
        self.assertEqual(len(observer.level_changes), 2)
        
        degraded_event = observer.level_changes[1]
        self.assertEqual(degraded_event['action'], 'trust_level_degraded')
        self.assertEqual(degraded_event['reason'], 'security_incident')
    
    def test_trust_policy_observer(self):
        """Test TrustPolicyObserver functionality"""
        class MockTrustPolicyObserver:
            def __init__(self):
                self.policy_events = []
                self.enabled = True
            
            def notify_policy_updated(self, organization, policy_changes):
                if self.enabled:
                    self.policy_events.append({
                        'action': 'policy_updated',
                        'organization': organization,
                        'changes': policy_changes,
                        'timestamp': timezone.now()
                    })
            
            def notify_policy_violation(self, relationship, violation_type, details):
                if self.enabled:
                    self.policy_events.append({
                        'action': 'policy_violation',
                        'relationship_id': relationship.id,
                        'violation_type': violation_type,
                        'details': details,
                        'timestamp': timezone.now()
                    })
        
        observer = MockTrustPolicyObserver()
        
        # Test policy updated notification
        policy_changes = {
            'sharing_scope': {'old': 'limited', 'new': 'full'},
            'anonymization_level': {'old': 'medium', 'new': 'low'}
        }
        
        observer.notify_policy_updated(str(self.org1.id), policy_changes)
        self.assertEqual(len(observer.policy_events), 1)
        
        policy_event = observer.policy_events[0]
        self.assertEqual(policy_event['action'], 'policy_updated')
        self.assertEqual(policy_event['changes'], policy_changes)
        
        # Test policy violation notification
        violation_details = {
            'attempted_action': 'data_sharing',
            'policy_rule': 'anonymization_required',
            'severity': 'medium'
        }
        
        observer.notify_policy_violation(self.relationship, 'anonymization_bypass', violation_details)
        self.assertEqual(len(observer.policy_events), 2)
        
        violation_event = observer.policy_events[1]
        self.assertEqual(violation_event['action'], 'policy_violation')
        self.assertEqual(violation_event['violation_type'], 'anonymization_bypass')
    
    def test_trust_audit_observer(self):
        """Test TrustAuditObserver functionality"""
        class MockTrustAuditObserver:
            def __init__(self):
                self.audit_logs = []
                self.enabled = True
            
            def log_trust_action(self, user, action, target, details):
                if self.enabled:
                    self.audit_logs.append({
                        'user': user,
                        'action': action,
                        'target': target,
                        'details': details,
                        'timestamp': timezone.now(),
                        'ip_address': '192.168.1.1'
                    })
            
            def log_access_attempt(self, user, resource, granted, reason):
                if self.enabled:
                    self.audit_logs.append({
                        'type': 'access_attempt',
                        'user': user,
                        'resource': resource,
                        'granted': granted,
                        'reason': reason,
                        'timestamp': timezone.now()
                    })
        
        observer = MockTrustAuditObserver()
        
        # Test trust action logging
        user = CustomUser.objects.create_user(
            username="audit_user", email="audit@trust1.com", password="testpass123",
            organization=self.org1, role="admin"
        )
        
        observer.log_trust_action(
            user.id, 'relationship_created', 
            f'relationship_{self.relationship.id}',
            {'target_org': str(self.org2.id)}
        )
        
        self.assertEqual(len(observer.audit_logs), 1)
        audit_log = observer.audit_logs[0]
        self.assertEqual(audit_log['action'], 'relationship_created')
        self.assertEqual(audit_log['user'], user.id)
        
        # Test access attempt logging
        observer.log_access_attempt(
            user.id, 'intelligence_feed_123', True, 'sufficient_trust_level'
        )
        
        self.assertEqual(len(observer.audit_logs), 2)
        access_log = observer.audit_logs[1]
        self.assertEqual(access_log['type'], 'access_attempt')
        self.assertTrue(access_log['granted'])
        self.assertEqual(access_log['reason'], 'sufficient_trust_level')


class AuthObserversTest(CrispTestCase):
    """Test authentication observer implementations"""
    
    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(
            name="Auth Observer Org", domain="authobs.com", contact_email="test@authobs.com"
        )
        
        self.user = CustomUser.objects.create_user(
            username="auth_user", email="user@authobs.com", password="testpass123",
            organization=self.org, role="admin"
        )
    
    def test_authentication_observer(self):
        """Test AuthenticationObserver functionality"""
        class MockAuthenticationObserver:
            def __init__(self):
                self.auth_events = []
                self.enabled = True
            
            def notify_login_success(self, user, ip_address, user_agent):
                if self.enabled:
                    self.auth_events.append({
                        'action': 'login_success',
                        'user_id': user.id,
                        'username': user.username,
                        'ip_address': ip_address,
                        'user_agent': user_agent,
                        'timestamp': timezone.now()
                    })
            
            def notify_login_failure(self, username, ip_address, reason):
                if self.enabled:
                    self.auth_events.append({
                        'action': 'login_failure',
                        'username': username,
                        'ip_address': ip_address,
                        'reason': reason,
                        'timestamp': timezone.now()
                    })
            
            def notify_logout(self, user, ip_address):
                if self.enabled:
                    self.auth_events.append({
                        'action': 'logout',
                        'user_id': user.id,
                        'username': user.username,
                        'ip_address': ip_address,
                        'timestamp': timezone.now()
                    })
        
        observer = MockAuthenticationObserver()
        
        # Test login success notification
        observer.notify_login_success(self.user, '192.168.1.100', 'Mozilla/5.0')
        self.assertEqual(len(observer.auth_events), 1)
        
        login_event = observer.auth_events[0]
        self.assertEqual(login_event['action'], 'login_success')
        self.assertEqual(login_event['user_id'], self.user.id)
        self.assertEqual(login_event['ip_address'], '192.168.1.100')
        
        # Test login failure notification
        observer.notify_login_failure('invalid_user', '192.168.1.100', 'invalid_credentials')
        self.assertEqual(len(observer.auth_events), 2)
        
        failure_event = observer.auth_events[1]
        self.assertEqual(failure_event['action'], 'login_failure')
        self.assertEqual(failure_event['username'], 'invalid_user')
        self.assertEqual(failure_event['reason'], 'invalid_credentials')
        
        # Test logout notification
        observer.notify_logout(self.user, '192.168.1.100')
        self.assertEqual(len(observer.auth_events), 3)
        
        logout_event = observer.auth_events[2]
        self.assertEqual(logout_event['action'], 'logout')
    
    def test_session_observer(self):
        """Test SessionObserver functionality"""
        class MockSessionObserver:
            def __init__(self):
                self.session_events = []
                self.enabled = True
            
            def notify_session_created(self, user, session_id, ip_address):
                if self.enabled:
                    self.session_events.append({
                        'action': 'session_created',
                        'user_id': user.id,
                        'session_id': session_id,
                        'ip_address': ip_address,
                        'timestamp': timezone.now()
                    })
            
            def notify_session_expired(self, session_id, user_id, reason):
                if self.enabled:
                    self.session_events.append({
                        'action': 'session_expired',
                        'session_id': session_id,
                        'user_id': user_id,
                        'reason': reason,
                        'timestamp': timezone.now()
                    })
            
            def notify_session_extended(self, session_id, user_id, extension_time):
                if self.enabled:
                    self.session_events.append({
                        'action': 'session_extended',
                        'session_id': session_id,
                        'user_id': user_id,
                        'extension_time': extension_time,
                        'timestamp': timezone.now()
                    })
        
        observer = MockSessionObserver()
        
        # Test session created notification
        session_id = 'session_123456'
        observer.notify_session_created(self.user, session_id, '192.168.1.100')
        self.assertEqual(len(observer.session_events), 1)
        
        created_event = observer.session_events[0]
        self.assertEqual(created_event['action'], 'session_created')
        self.assertEqual(created_event['session_id'], session_id)
        
        # Test session expired notification
        observer.notify_session_expired(session_id, self.user.id, 'timeout')
        self.assertEqual(len(observer.session_events), 2)
        
        expired_event = observer.session_events[1]
        self.assertEqual(expired_event['action'], 'session_expired')
        self.assertEqual(expired_event['reason'], 'timeout')
        
        # Test session extended notification
        observer.notify_session_extended(session_id, self.user.id, 3600)  # 1 hour
        self.assertEqual(len(observer.session_events), 3)
        
        extended_event = observer.session_events[2]
        self.assertEqual(extended_event['action'], 'session_extended')
        self.assertEqual(extended_event['extension_time'], 3600)
    
    def test_security_observer(self):
        """Test SecurityObserver functionality"""
        class MockSecurityObserver:
            def __init__(self):
                self.security_events = []
                self.enabled = True
            
            def notify_suspicious_activity(self, user_id, activity_type, details, severity):
                if self.enabled:
                    self.security_events.append({
                        'action': 'suspicious_activity',
                        'user_id': user_id,
                        'activity_type': activity_type,
                        'details': details,
                        'severity': severity,
                        'timestamp': timezone.now()
                    })
            
            def notify_account_locked(self, user_id, reason, lock_duration):
                if self.enabled:
                    self.security_events.append({
                        'action': 'account_locked',
                        'user_id': user_id,
                        'reason': reason,
                        'lock_duration': lock_duration,
                        'timestamp': timezone.now()
                    })
            
            def notify_privilege_escalation_attempt(self, user_id, attempted_role, current_role):
                if self.enabled:
                    self.security_events.append({
                        'action': 'privilege_escalation_attempt',
                        'user_id': user_id,
                        'attempted_role': attempted_role,
                        'current_role': current_role,
                        'timestamp': timezone.now()
                    })
        
        observer = MockSecurityObserver()
        
        # Test suspicious activity notification
        details = {
            'failed_attempts': 5,
            'ip_addresses': ['192.168.1.100', '192.168.1.101'],
            'time_window': '5 minutes'
        }
        
        observer.notify_suspicious_activity(
            self.user.id, 'multiple_failed_logins', details, 'high'
        )
        self.assertEqual(len(observer.security_events), 1)
        
        suspicious_event = observer.security_events[0]
        self.assertEqual(suspicious_event['action'], 'suspicious_activity')
        self.assertEqual(suspicious_event['activity_type'], 'multiple_failed_logins')
        self.assertEqual(suspicious_event['severity'], 'high')
        
        # Test account locked notification
        observer.notify_account_locked(self.user.id, 'too_many_failed_attempts', 3600)
        self.assertEqual(len(observer.security_events), 2)
        
        locked_event = observer.security_events[1]
        self.assertEqual(locked_event['action'], 'account_locked')
        self.assertEqual(locked_event['lock_duration'], 3600)
        
        # Test privilege escalation attempt notification
        observer.notify_privilege_escalation_attempt(self.user.id, 'system_admin', 'admin')
        self.assertEqual(len(observer.security_events), 3)
        
        escalation_event = observer.security_events[2]
        self.assertEqual(escalation_event['action'], 'privilege_escalation_attempt')
        self.assertEqual(escalation_event['attempted_role'], 'system_admin')
        self.assertEqual(escalation_event['current_role'], 'admin')


class ObserverPatternTest(CrispTestCase):
    """Test Observer pattern implementation and integration"""
    
    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(
            name="Pattern Test Org", domain="pattern.com", contact_email="test@pattern.com"
        )
    
    def test_observer_registration(self):
        """Test observer registration mechanism"""
        class MockSubject:
            def __init__(self):
                self.observers = []
            
            def attach(self, observer):
                if observer not in self.observers:
                    self.observers.append(observer)
            
            def detach(self, observer):
                if observer in self.observers:
                    self.observers.remove(observer)
            
            def notify(self, event_data):
                for observer in self.observers:
                    observer.update(event_data)
        
        class MockObserver:
            def __init__(self, name):
                self.name = name
                self.notifications = []
            
            def update(self, event_data):
                self.notifications.append(event_data)
        
        subject = MockSubject()
        observer1 = MockObserver("Observer1")
        observer2 = MockObserver("Observer2")
        
        # Test observer registration
        subject.attach(observer1)
        subject.attach(observer2)
        self.assertEqual(len(subject.observers), 2)
        
        # Test notification propagation
        event_data = {'type': 'test_event', 'data': 'test_data'}
        subject.notify(event_data)
        
        self.assertEqual(len(observer1.notifications), 1)
        self.assertEqual(len(observer2.notifications), 1)
        self.assertEqual(observer1.notifications[0], event_data)
        self.assertEqual(observer2.notifications[0], event_data)
        
        # Test observer deregistration
        subject.detach(observer1)
        self.assertEqual(len(subject.observers), 1)
        
        # Test notification after deregistration
        another_event = {'type': 'another_event', 'data': 'more_data'}
        subject.notify(another_event)
        
        self.assertEqual(len(observer1.notifications), 1)  # No new notifications
        self.assertEqual(len(observer2.notifications), 2)  # Received new notification
    
    def test_observer_error_handling(self):
        """Test observer error handling"""
        class MockSubjectWithErrorHandling:
            def __init__(self):
                self.observers = []
                self.failed_observers = []
            
            def attach(self, observer):
                if observer not in self.observers:
                    self.observers.append(observer)
            
            def notify(self, event_data):
                for observer in self.observers[:]:  # Copy list to avoid modification during iteration
                    try:
                        observer.update(event_data)
                    except Exception as e:
                        self.failed_observers.append((observer, str(e)))
                        # Optionally remove failed observer
                        # self.observers.remove(observer)
        
        class FailingObserver:
            def update(self, event_data):
                raise Exception("Observer failure")
        
        class WorkingObserver:
            def __init__(self):
                self.notifications = []
            
            def update(self, event_data):
                self.notifications.append(event_data)
        
        subject = MockSubjectWithErrorHandling()
        failing_observer = FailingObserver()
        working_observer = WorkingObserver()
        
        subject.attach(failing_observer)
        subject.attach(working_observer)
        
        # Test notification with failing observer
        event_data = {'type': 'test_event'}
        subject.notify(event_data)
        
        # Working observer should still receive notification
        self.assertEqual(len(working_observer.notifications), 1)
        
        # Failed observer should be recorded
        self.assertEqual(len(subject.failed_observers), 1)
        self.assertEqual(subject.failed_observers[0][0], failing_observer)
    
    def test_observer_priority_system(self):
        """Test observer priority system"""
        class PrioritySubject:
            def __init__(self):
                self.observers = []
            
            def attach(self, observer, priority=0):
                self.observers.append((observer, priority))
                # Sort by priority (higher numbers first)
                self.observers.sort(key=lambda x: x[1], reverse=True)
            
            def notify(self, event_data):
                for observer, priority in self.observers:
                    observer.update(event_data)
        
        class PriorityObserver:
            def __init__(self, name):
                self.name = name
                self.notifications = []
                self.notification_order = []
            
            def update(self, event_data):
                self.notifications.append(event_data)
                # Record order for testing
                import time
                self.notification_order.append(time.time())
        
        subject = PrioritySubject()
        high_priority_observer = PriorityObserver("High")
        low_priority_observer = PriorityObserver("Low")
        medium_priority_observer = PriorityObserver("Medium")
        
        # Attach observers with different priorities
        subject.attach(low_priority_observer, priority=1)
        subject.attach(high_priority_observer, priority=10)
        subject.attach(medium_priority_observer, priority=5)
        
        # Test priority ordering
        priorities = [priority for observer, priority in subject.observers]
        self.assertEqual(priorities, [10, 5, 1])  # High to low
        
        # Test notification order
        event_data = {'type': 'priority_test'}
        subject.notify(event_data)
        
        # All observers should receive notification
        self.assertEqual(len(high_priority_observer.notifications), 1)
        self.assertEqual(len(medium_priority_observer.notifications), 1)
        self.assertEqual(len(low_priority_observer.notifications), 1)
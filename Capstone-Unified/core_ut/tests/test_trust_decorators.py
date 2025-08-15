"""
Tests for Trust Management Decorator Patterns

Comprehensive tests for decorator patterns including security enhancement,
compliance validation, audit logging, and decorator chains.
"""

import uuid
from unittest.mock import patch, Mock
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from core_ut.trust.models import TrustLevel, TrustRelationship
from core_ut.tests.test_fixtures import BaseTestCase
from core_ut.trust.patterns.decorator.trust_decorators import (
    BasicTrustEvaluation, SecurityEnhancementDecorator, ComplianceDecorator,
    AuditDecorator, TrustDecoratorChain
)


class TrustEvaluationTest(BaseTestCase):
    """Test basic trust evaluation functionality"""
    
    def setUp(self):
        super().setUp()
        self.trust_level = TrustLevel.objects.create(
            name='Decorator Test Level',
            level='trusted',
            numerical_value=75,
            description='Level for decorator testing',
            created_by=str(self.admin_user.id)
        )

    def test_basic_evaluation_without_relationship(self):
        """Test basic trust evaluation with no relationship"""
        evaluator = BasicTrustEvaluation()
        result = evaluator.evaluate({})
        
        self.assertFalse(result['allowed'])
        self.assertEqual(result['access_level'], 'none')
        self.assertIn('No trust relationship', result['reason'])

    def test_basic_evaluation_with_effective_relationship(self):
        """Test basic trust evaluation with effective relationship"""
        relationship = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            status='active',
            approved_by_source=True,
            approved_by_target=True,
            created_by=self.admin_user,
            last_modified_by=self.admin_user
        )
        
        evaluator = BasicTrustEvaluation(relationship)
        result = evaluator.evaluate({})
        
        self.assertTrue(result['allowed'])
        self.assertIn('Access granted', result['reason'])

    def test_access_level_determination(self):
        """Test access level determination logic"""
        relationship = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            access_level='read',
            created_by=self.admin_user,
            last_modified_by=self.admin_user
        )
        
        evaluator = BasicTrustEvaluation(relationship)
        access_level = evaluator.get_access_level()
        self.assertIsNotNone(access_level)


class SecurityEnhancementDecoratorTest(BaseTestCase):
    """Test security enhancement decorator"""
    
    def setUp(self):
        super().setUp()
        self.trust_level = TrustLevel.objects.create(
            name='Security Test Level',
            level='trusted',
            numerical_value=80,
            description='Level for security testing',
            created_by=str(self.admin_user.id)
        )
        
        self.relationship = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            status='active',
            approved_by_source=True,
            approved_by_target=True,
            created_by=self.admin_user,
            last_modified_by=self.admin_user
        )

    def test_security_enhancement_during_hours(self):
        """Test security enhancement during normal hours"""
        basic_eval = BasicTrustEvaluation(self.relationship)
        decorator = SecurityEnhancementDecorator(basic_eval, security_level='high')
        
        context = {
            'user': str(self.admin_user.id),
            'request_time': timezone.now().replace(hour=10)  # Normal hours
        }
        
        result = decorator.evaluate(context)
        self.assertTrue(result['allowed'])
        self.assertTrue(result['security_enhanced'])
        self.assertEqual(result['security_level'], 'high')

    def test_security_enhancement_off_hours(self):
        """Test security enhancement during off hours"""
        basic_eval = BasicTrustEvaluation(self.relationship)
        decorator = SecurityEnhancementDecorator(basic_eval, security_level='standard')
        
        context = {
            'user': str(self.admin_user.id),
            'request_time': timezone.now().replace(hour=2)  # Off hours
        }
        
        result = decorator.evaluate(context)
        self.assertTrue(result['allowed'])
        self.assertTrue(result['security_enhanced'])
        self.assertIn('security_warning', result)


class ComplianceDecoratorTest(BaseTestCase):
    """Test compliance validation decorator"""
    
    def setUp(self):
        super().setUp()
        self.trust_level = TrustLevel.objects.create(
            name='Compliance Test Level',
            level='trusted',
            numerical_value=85,
            description='Level for compliance testing',
            created_by=str(self.admin_user.id)
        )
        
        self.relationship = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            status='active',
            approved_by_source=True,
            approved_by_target=True,
            created_by=self.admin_user,
            last_modified_by=self.admin_user
        )

    def test_compliance_validation_normal_retention(self):
        """Test compliance validation with normal retention"""
        basic_eval = BasicTrustEvaluation(self.relationship)
        decorator = ComplianceDecorator(basic_eval, compliance_framework='GDPR')
        
        context = {
            'user': str(self.admin_user.id),
            'data_retention_days': 365,
            'resource_type': 'indicator'
        }
        
        result = decorator.evaluate(context)
        self.assertTrue(result['allowed'])
        self.assertTrue(result['compliance_validated'])
        self.assertEqual(result['compliance_framework'], 'GDPR')

    def test_compliance_validation_long_retention(self):
        """Test compliance validation with long retention period"""
        basic_eval = BasicTrustEvaluation(self.relationship)
        decorator = ComplianceDecorator(basic_eval, compliance_framework='TEST')
        
        context = {
            'user': str(self.admin_user.id),
            'data_retention_days': 3000,  # Very long retention
            'resource_type': 'indicator'
        }
        
        result = decorator.evaluate(context)
        self.assertTrue(result['allowed'])
        self.assertTrue(result['compliance_validated'])
        self.assertIn('compliance_warning', result)


class AuditDecoratorTest(BaseTestCase):
    """Test audit logging decorator"""
    
    def setUp(self):
        super().setUp()
        self.trust_level = TrustLevel.objects.create(
            name='Audit Test Level',
            level='trusted',
            numerical_value=90,
            description='Level for audit testing',
            created_by=str(self.admin_user.id)
        )
        
        self.relationship = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            status='active',
            approved_by_source=True,
            approved_by_target=True,
            created_by=self.admin_user,
            last_modified_by=self.admin_user
        )

    @patch('core.trust.patterns.decorator.trust_decorators.logger')
    def test_audit_logging_with_sensitive_data(self, mock_logger):
        """Test audit logging with sensitive data sanitization"""
        basic_eval = BasicTrustEvaluation(self.relationship)
        decorator = AuditDecorator(basic_eval, audit_level='detailed')
        
        sensitive_context = {
            'user': str(self.admin_user.id),
            'password': 'secret123',
            'api_key': 'key_abc123',
            'normal_field': 'safe_data'
        }
        
        result = decorator.evaluate(sensitive_context)
        self.assertTrue(result['allowed'])
        self.assertTrue(result['audit_logged'])
        self.assertIn('audit_reference', result)
        
        # Verify logging was called
        mock_logger.info.assert_called()

    def test_context_sanitization(self):
        """Test sensitive context data sanitization"""
        basic_eval = BasicTrustEvaluation(self.relationship)
        decorator = AuditDecorator(basic_eval, audit_level='standard')
        
        sensitive_context = {
            'user': str(self.admin_user.id),
            'password': 'secret',
            'api_key': 'key123',
            'token': 'token456',
            'normal_field': 'safe'
        }
        
        sanitized = decorator._sanitize_context(sensitive_context)
        
        self.assertEqual(sanitized['password'], '[REDACTED]')
        self.assertEqual(sanitized['api_key'], '[REDACTED]')
        self.assertEqual(sanitized['token'], '[REDACTED]')
        self.assertEqual(sanitized['normal_field'], 'safe')


class TrustDecoratorChainTest(BaseTestCase):
    """Test decorator chain building and execution"""
    
    def setUp(self):
        super().setUp()
        self.trust_level = TrustLevel.objects.create(
            name='Chain Test Level',
            level='trusted',
            numerical_value=95,
            description='Level for chain testing',
            created_by=str(self.admin_user.id)
        )
        
        self.relationship = TrustRelationship.objects.create(
            source_organization=self.source_org,
            target_organization=self.target_org,
            trust_level=self.trust_level,
            status='active',
            approved_by_source=True,
            approved_by_target=True,
            created_by=self.admin_user,
            last_modified_by=self.admin_user
        )

    def test_decorator_chain_building(self):
        """Test building decorator chain with multiple enhancements"""
        chain = TrustDecoratorChain(self.relationship)
        decorated = (chain
                    .add_security_enhancement('high')
                    .add_compliance_validation('GDPR')
                    .add_audit_logging('detailed')
                    .build())
        
        context = {
            'user': str(self.admin_user.id),
            'request_time': timezone.now(),
            'resource_type': 'indicator',
            'data_retention_days': 365
        }
        
        result = decorated.evaluate(context)
        self.assertTrue(result['allowed'])
        self.assertTrue(result['security_enhanced'])
        self.assertTrue(result['compliance_validated'])
        self.assertTrue(result['audit_logged'])

    def test_decorator_chain_convenience_evaluate(self):
        """Test convenience evaluate method on chain"""
        chain = TrustDecoratorChain(self.relationship)
        chain.add_security_enhancement().add_compliance_validation()
        
        context = {
            'user': str(self.admin_user.id),
            'resource_type': 'indicator'
        }
        
        result = chain.evaluate(context)
        self.assertIsNotNone(result)
        self.assertIn('allowed', result)

    def test_empty_decorator_chain(self):
        """Test decorator chain with no relationship"""
        chain = TrustDecoratorChain()
        result = chain.evaluate({})
        
        self.assertFalse(result['allowed'])
        self.assertEqual(result['access_level'], 'none')
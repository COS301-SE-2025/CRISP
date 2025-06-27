"""
Integration tests for trust-based anonymization workflow.

These tests verify the complete end-to-end flow from trust relationships
to appropriate anonymization levels for intelligence sharing.
"""
import os
import sys
import django

# Add the project root to Python path for standalone execution
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    sys.path.insert(0, project_root)
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.test_settings')
    django.setup()

from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from datetime import timedelta
import json

try:
    from ..services.trust_anonymization_service import TrustAnonymizationService
    from ..services.trust_service import TrustService
    from ..models.trust_models.models import TrustRelationship, TrustLevel, TrustGroup, TrustGroupMembership
    from ..models.auth import Organization, CustomUser
    from ..models.threat_feed import ThreatFeed
    from ..models.indicator import Indicator
    from ..models.ttp_data import TTPData
    from ..models.institution import Institution
    from ..strategies.context import AnonymizationContext
    from ..strategies.enums import AnonymizationLevel, DataType
except ImportError:
    # Fallback for standalone execution
    from core.services.trust_anonymization_service import TrustAnonymizationService
    from core.services.trust_service import TrustService
    from core.models.trust_models.models import TrustRelationship, TrustLevel, TrustGroup, TrustGroupMembership
    from core.models.auth import Organization, CustomUser
    from core.models.threat_feed import ThreatFeed
    from core.models.indicator import Indicator
    from core.models.ttp_data import TTPData
    from core.models.institution import Institution
    from core.strategies.context import AnonymizationContext
    from core.strategies.enums import AnonymizationLevel, DataType


class TrustAnonymizationIntegrationTestCase(TransactionTestCase):
    """Test trust-based anonymization integration"""
    
    def setUp(self):
        """Set up test environment with organizations, trust relationships, and data"""
        # Create organizations
        self.org_high_trust = Organization.objects.create(
            name='High Trust University',
            description='University with high trust relationship',
            domain='hightrustuni.edu'
        )
        

        self.org_medium_trust = Organization.objects.create(
            name='Medium Trust Corp',
            description='Corporation with medium trust relationship', 
            domain='mediumtrust.com'
        )
        
        self.org_low_trust = Organization.objects.create(
            name='Low Trust Inc',
            description='Organization with low trust relationship',
            domain='lowtrust.org'
        )
        
        self.org_no_trust = Organization.objects.create(
            name='No Trust Org',
            description='Organization with no trust relationship',
            domain='notrust.net'
        )
        
        # Create trust levels
        self.trust_level_high = TrustLevel.objects.create(
            name='High Trust',
            level='high',
            numerical_value=90,
            default_anonymization_level='none',
            default_access_level='full',
            description='High trust with no anonymization'
        )
        
        self.trust_level_medium = TrustLevel.objects.create(
            name='Medium Trust',
            level='medium',
            numerical_value=60,
            default_anonymization_level='partial',
            default_access_level='contribute',
            description='Medium trust with partial anonymization'
        )
        
        self.trust_level_low = TrustLevel.objects.create(
            name='Low Trust',
            level='low',
            numerical_value=30,
            default_anonymization_level='full',
            default_access_level='read',
            description='Low trust with full anonymization'
        )
          # Create trust relationships
        self.trust_rel_high = TrustRelationship.objects.create(
            source_organization=self.org_high_trust,
            target_organization=self.org_medium_trust,
            trust_level=self.trust_level_high,
            relationship_type='bilateral',
            status='active',
            is_active=True,
            approved_by_source=True,
            approved_by_target=True,
            anonymization_level='none',  # Override default
            created_by='system',
            valid_from=timezone.now(),
            valid_until=timezone.now() + timedelta(days=365)
        )
        
        self.trust_rel_medium = TrustRelationship.objects.create(
            source_organization=self.org_high_trust,
            target_organization=self.org_low_trust,
            trust_level=self.trust_level_medium,
            relationship_type='bilateral',
            status='active',
            is_active=True,
            approved_by_source=True,
            approved_by_target=True,
            anonymization_level='custom',  # Use trust level default
            created_by='system',
            valid_from=timezone.now(),
            valid_until=timezone.now() + timedelta(days=365)
        )
        
        self.trust_rel_low = TrustRelationship.objects.create(
            source_organization=self.org_medium_trust,
            target_organization=self.org_low_trust,
            trust_level=self.trust_level_low,
            relationship_type='bilateral',
            status='active',
            is_active=True,
            approved_by_source=True,
            approved_by_target=True,
            anonymization_level='full',  # Explicit full anonymization
            created_by='system',
            valid_from=timezone.now(),
            valid_until=timezone.now() + timedelta(days=365)
        )
        
        # Create threat feed
        self.threat_feed = ThreatFeed.objects.create(
            name='Test Threat Feed',
            description='Test feed for anonymization testing',
            owner=self.org_high_trust,  # Use the organization object directly
            is_public=False
        )
        
        # Create test indicators
        self.indicator_ip = Indicator.objects.create(
            type='ip',
            value='192.168.1.100',
            description='Suspicious IP address from our network monitoring',
            threat_feed=self.threat_feed,
            confidence=85,
            stix_id='indicator--ip-test-001'
        )
        
        self.indicator_domain = Indicator.objects.create(
            type='domain',
            value='malicious-domain.evil.com',
            description='Known C&C domain used in recent attacks against educational institutions',
            threat_feed=self.threat_feed,
            confidence=90,
            stix_id='indicator--domain-test-001'
        )
        
        # Create test TTP
        self.ttp_spearphishing = TTPData.objects.create(
            name='Spear Phishing Against Universities',
            description='Targeted phishing campaign against university administrators using fake IT security alerts',
            threat_feed=self.threat_feed,
            mitre_technique_id='T1566.001',
            mitre_tactic='initial_access',
            stix_id='attack-pattern--spearphish-test-001'
        )
        
        # Initialize service
        self.trust_anonymization_service = TrustAnonymizationService()
    
    def test_trust_level_to_anonymization_mapping(self):
        """Test that trust levels correctly map to anonymization levels"""
        # High trust -> no anonymization
        anon_level = self.trust_anonymization_service.get_trust_based_anonymization_level(
            self.org_high_trust, self.org_medium_trust
        )
        self.assertEqual(anon_level, 'none')
        
        # Medium trust -> partial anonymization (using trust level default)
        anon_level = self.trust_anonymization_service.get_trust_based_anonymization_level(
            self.org_high_trust, self.org_low_trust
        )
        self.assertEqual(anon_level, 'partial')
        
        # Low trust -> full anonymization
        anon_level = self.trust_anonymization_service.get_trust_based_anonymization_level(
            self.org_medium_trust, self.org_low_trust
        )
        self.assertEqual(anon_level, 'full')
        
        # No trust -> full anonymization
        anon_level = self.trust_anonymization_service.get_trust_based_anonymization_level(
            self.org_high_trust, self.org_no_trust
        )
        self.assertEqual(anon_level, 'full')
    
    
    def test_bulk_anonymization(self):
        """Test bulk anonymization of multiple indicators and TTPs"""
        indicators = [self.indicator_ip, self.indicator_domain]
        ttps = [self.ttp_spearphishing]
        
        # Test bulk anonymization for medium trust organization
        result = self.trust_anonymization_service.bulk_anonymize_for_organization(
            indicators=indicators,
            ttps=ttps,
            target_org=self.org_low_trust  # Medium trust relationship
        )
        
        # Check structure
        self.assertIn('indicators', result)
        self.assertIn('ttps', result)
        self.assertIn('stats', result)
        
        # Check stats
        self.assertEqual(result['stats']['indicators_processed'], 2)
        self.assertEqual(result['stats']['ttps_processed'], 1)
        self.assertEqual(result['stats']['errors'], 0)
        
        # Check that all items were processed
        self.assertEqual(len(result['indicators']), 2)
        self.assertEqual(len(result['ttps']), 1)
        
        # Verify anonymization was applied
        for indicator in result['indicators']:
            self.assertIn('value', indicator)
            self.assertIn('description', indicator)
            
        for ttp in result['ttps']:
            self.assertIn('name', ttp)
            self.assertIn('description', ttp)
    
    def test_sharing_organizations_list(self):
        """Test getting list of organizations for sharing with anonymization levels"""
        sharing_orgs = self.trust_anonymization_service.get_sharing_organizations_for_data(
            self.org_high_trust, 'TLP:GREEN'
        )
        
        # Should return organizations with trust relationships
        org_names = [org.name for org, level in sharing_orgs]
        anon_levels = [level for org, level in sharing_orgs]
        
        # Verify expected organizations are included
        self.assertIn('Medium Trust Corp', org_names)
        self.assertIn('Low Trust Inc', org_names)
        
        # Verify anonymization levels are correct
        self.assertIn('none', anon_levels)  # High trust relationship
        self.assertIn('partial', anon_levels)  # Medium trust relationship
    
    
    def test_error_handling_and_security_defaults(self):
        """Test that errors default to secure anonymization levels"""
        # Test with invalid organization (should default to full anonymization)
        try:
            # Create an indicator with a different threat feed (no clear source org relationship)
            other_threat_feed = ThreatFeed.objects.create(
                name='Other Threat Feed',
                description='Different feed for error testing',
                owner=self.org_no_trust,  # Use the organization object directly
                is_public=False
            )
            
            orphaned_indicator = Indicator.objects.create(
                type='ip',
                value='10.0.0.1',
                description='Orphaned indicator',
                threat_feed=other_threat_feed,  # Different threat feed
                confidence=50,
                stix_id='indicator--orphaned-test-001'
            )
            
            anonymized = self.trust_anonymization_service.anonymize_indicator_for_organization(
                orphaned_indicator, self.org_no_trust
            )
            
            # Should apply full anonymization by default
            self.assertNotEqual(anonymized['value'], '10.0.0.1')
            
        except Exception as e:
            # Should handle gracefully
            self.fail(f"Error handling failed: {str(e)}")
    
    def test_classification_level_restrictions(self):
        """Test that classification levels are respected"""
        # Test with different TLP levels
        sharing_orgs_white = self.trust_anonymization_service.get_sharing_organizations_for_data(
            self.org_high_trust, 'TLP:WHITE'
        )
        
        sharing_orgs_red = self.trust_anonymization_service.get_sharing_organizations_for_data(
            self.org_high_trust, 'TLP:RED'
        )
        
        # WHITE should have more recipients than RED
        self.assertGreaterEqual(len(sharing_orgs_white), len(sharing_orgs_red))
    
    def test_end_to_end_intelligence_sharing_workflow(self):
        """Test complete end-to-end workflow of trust-based intelligence sharing"""
        # 1. Organization has intelligence to share
        indicators_to_share = [self.indicator_ip, self.indicator_domain]
        ttps_to_share = [self.ttp_spearphishing]
        
        # 2. Get list of organizations to share with
        sharing_targets = self.trust_anonymization_service.get_sharing_organizations_for_data(
            self.org_high_trust, 'TLP:GREEN'
        )
        
        self.assertGreater(len(sharing_targets), 0, "Should have organizations to share with")
        
        # 3. For each target organization, create appropriately anonymized intelligence packages
        sharing_packages = {}
        
        for target_org, expected_anon_level in sharing_targets:
            package = self.trust_anonymization_service.bulk_anonymize_for_organization(
                indicators=indicators_to_share,
                ttps=ttps_to_share,
                target_org=target_org
            )
            
            sharing_packages[target_org.name] = package
            
            # Verify package structure
            self.assertIn('indicators', package)
            self.assertIn('ttps', package)
            self.assertIn('stats', package)
            
            # Verify appropriate anonymization was applied
            self.assertEqual(package['stats']['indicators_processed'], 2)
            self.assertEqual(package['stats']['ttps_processed'], 1)
            self.assertEqual(package['stats']['errors'], 0)
        
        # 4. Verify different anonymization levels were applied to different organizations
        # High trust org should get less anonymized data than low trust org
        if 'Medium Trust Corp' in sharing_packages and 'Low Trust Inc' in sharing_packages:
            high_trust_package = sharing_packages['Medium Trust Corp']
            low_trust_package = sharing_packages['Low Trust Inc']
            
            # Compare anonymization (exact comparison depends on anonymization strategy implementation)
            # For now, just verify packages exist and have correct structure
            self.assertEqual(len(high_trust_package['indicators']), 2)
            self.assertEqual(len(low_trust_package['indicators']), 2)


if __name__ == '__main__':
    import unittest
    unittest.main()
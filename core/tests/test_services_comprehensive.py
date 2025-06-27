"""
Comprehensive tests for all service components
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from core.models.auth import CustomUser, Organization
from core.tests.test_base import CrispTestCase


class ServiceMockTest(CrispTestCase):
    """Test service functionality with mocked dependencies"""
    
    def setUp(self):
        super().setUp()
        self.org = Organization.objects.create(
            name="Mock Service Org", domain="mockservice.com", contact_email="test@mockservice.com"
        )
    
    def test_auth_service_mock(self):
        """Test authentication service mock functionality"""
        # Test basic service instantiation and method calls
        from core.services.auth_service import AuthenticationService
        auth_service = AuthenticationService()
        
        # Test that service has expected methods
        self.assertTrue(hasattr(auth_service, 'authenticate_user'))
        self.assertTrue(hasattr(auth_service, 'verify_token'))
        self.assertTrue(hasattr(auth_service, 'logout_user'))
    
    def test_trust_service_mock(self):
        """Test trust service mock functionality"""
        from core.services.trust_service import TrustService
        
        # Test static method availability
        self.assertTrue(hasattr(TrustService, 'check_trust_level'))
        self.assertTrue(hasattr(TrustService, 'can_access_intelligence'))
    
    def test_indicator_service_validation(self):
        """Test indicator service validation"""
        from core.services.indicator_service import IndicatorService
        indicator_service = IndicatorService()
        
        # Test domain validation
        self.assertTrue(indicator_service.validate_indicator('domain', 'example.com'))
        self.assertFalse(indicator_service.validate_indicator('domain', 'invalid..domain'))
        
        # Test IP validation  
        self.assertTrue(indicator_service.validate_indicator('ip', '192.168.1.1'))
        self.assertFalse(indicator_service.validate_indicator('ip', '999.999.999.999'))
    
    def test_ttp_service_validation(self):
        """Test TTP service validation"""
        from core.services.ttp_service import TTPService
        ttp_service = TTPService()
        
        # Test MITRE ID validation
        self.assertTrue(ttp_service.validate_mitre_id('T1059'))
        self.assertTrue(ttp_service.validate_mitre_id('T1059.001'))
        self.assertFalse(ttp_service.validate_mitre_id('X1059'))
    
    def test_anonymization_service_basic(self):
        """Test anonymization service basic functionality"""
        from core.services.trust_anonymization_service import TrustAnonymizationService
        anon_service = TrustAnonymizationService()
        
        stix_data = {
            "type": "indicator",
            "pattern": "[file:hashes.MD5 = 'test']",
            "created_by_ref": "identity--test"
        }
        
        # Test none level
        result = anon_service.anonymize_stix_object(stix_data, "none", str(self.org.id))
        self.assertEqual(result, stix_data)
    
    @patch('requests.get')
    def test_otx_service_network(self, mock_get):
        """Test OTX service network operations"""
        from core.services.otx_service import OTXService
        otx_service = OTXService()
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': []}
        mock_get.return_value = mock_response
        
        result = otx_service.fetch_otx_data('test_endpoint')
        self.assertTrue(result['success'])
    
    def test_service_error_handling(self):
        """Test service error handling"""
        from core.services.auth_service import AuthenticationService
        auth_service = AuthenticationService()
        
        # Test with non-existent user
        result = auth_service.authenticate_user(
            username="nonexistent",
            password="wrong", 
            ip_address="192.168.1.100",
            user_agent="Test"
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
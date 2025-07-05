import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
import django
from django.test import TestCase
from django.db import transaction
from run_integration_tests_final import run_all_tests, print_header, print_step

# Import the function to test

class TestRunIntegrationTestsFinal:
    """Test suite for the CRISP integration test runner"""
    
    def setup_method(self):
        """Set up test environment for each test method"""
        self.project_root = Path(__file__).parent
        
    @patch('run_integration_tests_final.django.setup')
    @patch('run_integration_tests_final.call_command')
    @patch('run_integration_tests_final.settings')
    def test_system_checks_success(self, mock_settings, mock_call_command, mock_django_setup):
        """Test successful system checks execution"""
        mock_settings.DATABASES = {'default': {'NAME': 'test_db'}}
        mock_call_command.return_value = None
        
        # Mock all the imports and models
        with patch('run_integration_tests_final.TrustLevel') as mock_trust_level, \
             patch('run_integration_tests_final.CRISPIntegrationService') as mock_service, \
             patch('run_integration_tests_final.Organization') as mock_org, \
             patch('run_integration_tests_final.get_user_model') as mock_user_model, \
             patch('run_integration_tests_final.TrustRelationship') as mock_trust_rel, \
             patch('run_integration_tests_final.TrustLog') as mock_trust_log:
            
            # Setup mock data
            mock_trust_level.objects.filter.return_value.count.return_value = 5
            mock_trust_level.objects.get_or_create.return_value = (Mock(), True)
            mock_trust_level.objects.count.return_value = 5
            mock_trust_level.objects.all.return_value = [
                Mock(name='Trusted Partners', is_active=True, numerical_value=100)
            ]
            
            mock_org.objects.count.return_value = 2
            mock_user_model.return_value.objects.count.return_value = 2
            mock_trust_rel.objects.count.return_value = 1
            mock_trust_log.objects.count.return_value = 1
            
            # Setup service mock
            mock_org_instance = Mock()
            mock_org_instance.name = 'Test Integration University'
            mock_service.create_organization_with_trust_setup.return_value = mock_org_instance
            
            mock_user_instance = Mock()
            mock_user_instance.email = 'admin@testorg.edu'
            mock_user_model.return_value.objects.get.return_value = mock_user_instance
            
            mock_relationship = Mock()
            mock_relationship.id = 'test-relationship-id'
            mock_relationship.trust_level.name = 'Trusted Partners'
            mock_service.create_trust_relationship.return_value = mock_relationship
            
            result = run_all_tests()
            
            # Verify system checks were called
            mock_call_command.assert_any_call('check', verbosity=1)
            mock_call_command.assert_any_call('migrate', verbosity=1)
            
            # Should return success (0)
            assert result == 0
    
    @patch('run_integration_tests_final.django.setup')
    @patch('run_integration_tests_final.call_command')
    @patch('run_integration_tests_final.settings')
    def test_system_checks_failure(self, mock_settings, mock_call_command, mock_django_setup):
        """Test system checks failure handling"""
        mock_settings.DATABASES = {'default': {'NAME': 'test_db'}}
        mock_call_command.side_effect = Exception("System check failed")
        
        with patch('run_integration_tests_final.TrustLevel') as mock_trust_level, \
             patch('run_integration_tests_final.CRISPIntegrationService'), \
             patch('run_integration_tests_final.Organization'), \
             patch('run_integration_tests_final.get_user_model'), \
             patch('run_integration_tests_final.TrustRelationship'), \
             patch('run_integration_tests_final.TrustLog'):
            
            # Setup minimal mocks to avoid other errors
            mock_trust_level.objects.filter.return_value.count.return_value = 0
            mock_trust_level.objects.count.return_value = 0
            
            result = run_all_tests()
            
            # Should return failure (1) due to system check failure
            assert result == 1
    
    @patch('run_integration_tests_final.django.setup')
    @patch('run_integration_tests_final.call_command')
    @patch('run_integration_tests_final.settings')
    def test_trust_level_creation(self, mock_settings, mock_call_command, mock_django_setup):
        """Test trust level creation during test data setup"""
        mock_settings.DATABASES = {'default': {'NAME': 'test_db'}}
        mock_call_command.return_value = None
        
        with patch('run_integration_tests_final.TrustLevel') as mock_trust_level, \
             patch('run_integration_tests_final.transaction') as mock_transaction, \
             patch('run_integration_tests_final.CRISPIntegrationService'), \
             patch('run_integration_tests_final.Organization'), \
             patch('run_integration_tests_final.get_user_model'), \
             patch('run_integration_tests_final.TrustRelationship'), \
             patch('run_integration_tests_final.TrustLog'):
            
            # Setup transaction mock
            mock_transaction.atomic.return_value.__enter__ = Mock()
            mock_transaction.atomic.return_value.__exit__ = Mock()
            
            # Setup trust level creation
            mock_trust_level_instance = Mock()
            mock_trust_level_instance.name = 'Trusted Partners'
            mock_trust_level_instance.is_active = True
            mock_trust_level_instance.numerical_value = 100
            
            mock_trust_level.objects.get_or_create.return_value = (mock_trust_level_instance, True)
            mock_trust_level.objects.filter.return_value.count.return_value = 5
            mock_trust_level.objects.count.return_value = 5
            mock_trust_level.objects.all.return_value = [mock_trust_level_instance]
            mock_trust_level.objects.get.return_value = mock_trust_level_instance
            
            # Setup other mocks
            mock_org_count = Mock()
            mock_org_count.objects.count.return_value = 0
            
            result = run_all_tests()
            
            # Verify trust levels were created
            assert mock_trust_level.objects.get_or_create.call_count == 5
            
            # Verify the specific trust levels
            expected_calls = [
                call('Untrusted', defaults={'level': 'untrusted', 'numerical_value': 0, 'description': 'No trust established', 'created_by': 'test_system', 'is_active': True}),
                call('Limited Trust', defaults={'level': 'limited_trust', 'numerical_value': 25, 'description': 'Limited trust for basic operations', 'created_by': 'test_system', 'is_active': True}),
                call('Moderate Trust', defaults={'level': 'moderate_trust', 'numerical_value': 50, 'description': 'Moderate trust for standard operations', 'created_by': 'test_system', 'is_active': True}),
                call('High Trust', defaults={'level': 'high_trust', 'numerical_value': 75, 'description': 'High trust for sensitive operations', 'created_by': 'test_system', 'is_active': True}),
                call('Trusted Partners', defaults={'level': 'trusted_partners', 'numerical_value': 100, 'description': 'Full trust for all operations', 'created_by': 'test_system', 'is_active': True})
            ]
            
            mock_trust_level.objects.get_or_create.assert_has_calls(expected_calls)
    
    @patch('run_integration_tests_final.django.setup')
    @patch('run_integration_tests_final.call_command')
    @patch('run_integration_tests_final.settings')
    def test_organization_creation_integration(self, mock_settings, mock_call_command, mock_django_setup):
        """Test organization creation with trust setup"""
        mock_settings.DATABASES = {'default': {'NAME': 'test_db'}}
        mock_call_command.return_value = None
        
        with patch('run_integration_tests_final.TrustLevel') as mock_trust_level, \
             patch('run_integration_tests_final.CRISPIntegrationService') as mock_service, \
             patch('run_integration_tests_final.Organization') as mock_org, \
             patch('run_integration_tests_final.get_user_model') as mock_user_model, \
             patch('run_integration_tests_final.TrustRelationship') as mock_trust_rel, \
             patch('run_integration_tests_final.TrustLog') as mock_trust_log:
            
            # Setup trust level mocks
            mock_trust_level_instance = Mock()
            mock_trust_level_instance.name = 'Trusted Partners'
            mock_trust_level_instance.is_active = True
            mock_trust_level_instance.numerical_value = 100
            
            mock_trust_level.objects.get_or_create.return_value = (mock_trust_level_instance, True)
            mock_trust_level.objects.filter.return_value.count.return_value = 5
            mock_trust_level.objects.count.return_value = 5
            mock_trust_level.objects.all.return_value = [mock_trust_level_instance]
            mock_trust_level.objects.get.return_value = mock_trust_level_instance
            
            # Setup organization creation
            mock_org_instance = Mock()
            mock_org_instance.name = 'Test Integration University'
            mock_service.create_organization_with_trust_setup.return_value = mock_org_instance
            
            # Setup user creation
            mock_user_instance = Mock()
            mock_user_instance.email = 'admin@testorg.edu'
            mock_user_model.return_value.objects.get.return_value = mock_user_instance
            
            # Setup trust relationship creation
            mock_relationship = Mock()
            mock_relationship.id = 'test-relationship-id'
            mock_relationship.trust_level.name = 'Trusted Partners'
            mock_service.create_trust_relationship.return_value = mock_relationship
            
            # Setup final report mocks
            mock_org.objects.count.return_value = 2
            mock_user_model.return_value.objects.count.return_value = 2
            mock_trust_rel.objects.count.return_value = 1
            mock_trust_log.objects.count.return_value = 1
            
            result = run_all_tests()
            
            # Verify organization creation was called
            assert mock_service.create_organization_with_trust_setup.call_count == 2
            
            # Verify the organization creation parameters
            calls = mock_service.create_organization_with_trust_setup.call_args_list
            
            # First organization
            first_call = calls[0]
            assert first_call[1]['name'] == 'Test Integration University'
            assert first_call[1]['domain'] == 'testintegration.edu'
            assert first_call[1]['admin_user_data']['email'] == 'admin@testorg.edu'
            
            # Second organization
            second_call = calls[1]
            assert second_call[1]['name'] == 'Test Partner University'
            assert second_call[1]['domain'] == 'testpartner.edu'
            assert second_call[1]['admin_user_data']['email'] == 'admin@testorg2.edu'
            
            # Verify trust relationship creation
            mock_service.create_trust_relationship.assert_called_once()
            
            assert result == 0
    
    @patch('run_integration_tests_final.django.setup')
    @patch('run_integration_tests_final.call_command')
    @patch('run_integration_tests_final.settings')
    def test_trust_relationship_creation_failure(self, mock_settings, mock_call_command, mock_django_setup):
        """Test handling of trust relationship creation failure"""
        mock_settings.DATABASES = {'default': {'NAME': 'test_db'}}
        mock_call_command.return_value = None
        
        with patch('run_integration_tests_final.TrustLevel') as mock_trust_level, \
             patch('run_integration_tests_final.CRISPIntegrationService') as mock_service, \
             patch('run_integration_tests_final.Organization') as mock_org, \
             patch('run_integration_tests_final.get_user_model') as mock_user_model, \
             patch('run_integration_tests_final.TrustRelationship') as mock_trust_rel, \
             patch('run_integration_tests_final.TrustLog') as mock_trust_log:
            
            # Setup trust level mocks
            mock_trust_level_instance = Mock()
            mock_trust_level_instance.name = 'Trusted Partners'
            mock_trust_level_instance.is_active = True
            mock_trust_level_instance.numerical_value = 100
            
            mock_trust_level.objects.get_or_create.return_value = (mock_trust_level_instance, True)
            mock_trust_level.objects.filter.return_value.count.return_value = 5
            mock_trust_level.objects.count.return_value = 5
            mock_trust_level.objects.all.return_value = [mock_trust_level_instance]
            mock_trust_level.objects.get.return_value = mock_trust_level_instance
            
            # Setup organization creation to succeed
            mock_org_instance = Mock()
            mock_org_instance.name = 'Test Integration University'
            mock_service.create_organization_with_trust_setup.return_value = mock_org_instance
            
            # Setup user creation to succeed
            mock_user_instance = Mock()
            mock_user_instance.email = 'admin@testorg.edu'
            mock_user_model.return_value.objects.get.return_value = mock_user_instance
            
            # Setup trust relationship creation to fail
            mock_service.create_trust_relationship.side_effect = Exception("Trust relationship creation failed")
            
            # Setup final report mocks
            mock_org.objects.count.return_value = 2
            mock_user_model.return_value.objects.count.return_value = 2
            mock_trust_rel.objects.count.return_value = 0
            mock_trust_log.objects.count.return_value = 0
            
            result = run_all_tests()
            
            # Should still return success if organization creation succeeded
            # but trust relationship creation failed
            assert result == 1  # Will be 1 due to manual integration test failure
    
    @patch('run_integration_tests_final.django.setup')
    @patch('run_integration_tests_final.call_command')
    @patch('run_integration_tests_final.settings')
    def test_no_trust_levels_available(self, mock_settings, mock_call_command, mock_django_setup):
        """Test handling when no trust levels are available"""
        mock_settings.DATABASES = {'default': {'NAME': 'test_db'}}
        mock_call_command.return_value = None
        
        with patch('run_integration_tests_final.TrustLevel') as mock_trust_level, \
             patch('run_integration_tests_final.CRISPIntegrationService') as mock_service, \
             patch('run_integration_tests_final.Organization') as mock_org, \
             patch('run_integration_tests_final.get_user_model') as mock_user_model, \
             patch('run_integration_tests_final.TrustRelationship') as mock_trust_rel, \
             patch('run_integration_tests_final.TrustLog') as mock_trust_log:
            
            # Setup trust level creation but no active trust levels
            mock_trust_level.objects.get_or_create.return_value = (Mock(), True)
            mock_trust_level.objects.filter.return_value.count.return_value = 0
            mock_trust_level.objects.count.return_value = 5
            mock_trust_level.objects.all.return_value = []
            
            # Mock DoesNotExist exception
            mock_trust_level.DoesNotExist = Exception
            mock_trust_level.objects.get.side_effect = mock_trust_level.DoesNotExist()
            
            # Setup organization creation to succeed
            mock_org_instance = Mock()
            mock_org_instance.name = 'Test Integration University'
            mock_service.create_organization_with_trust_setup.return_value = mock_org_instance
            
            # Setup user creation to succeed
            mock_user_instance = Mock()
            mock_user_instance.email = 'admin@testorg.edu'
            mock_user_model.return_value.objects.get.return_value = mock_user_instance
            
            # Setup final report mocks
            mock_org.objects.count.return_value = 2
            mock_user_model.return_value.objects.count.return_value = 2
            mock_trust_rel.objects.count.return_value = 0
            mock_trust_log.objects.count.return_value = 0
            
            result = run_all_tests()
            
            # Should still complete successfully but skip trust relationship creation
            assert result == 0
    
    @patch('run_integration_tests_final.django.setup')
    @patch('run_integration_tests_final.call_command')
    @patch('run_integration_tests_final.settings')
    def test_database_migration_failure(self, mock_settings, mock_call_command, mock_django_setup):
        """Test handling of database migration failure"""
        mock_settings.DATABASES = {'default': {'NAME': 'test_db'}}
        
        # First call (check) succeeds, second call (migrate) fails
        mock_call_command.side_effect = [None, Exception("Migration failed")]
        
        with patch('run_integration_tests_final.TrustLevel') as mock_trust_level, \
             patch('run_integration_tests_final.CRISPIntegrationService'), \
             patch('run_integration_tests_final.Organization'), \
             patch('run_integration_tests_final.get_user_model'), \
             patch('run_integration_tests_final.TrustRelationship'), \
             patch('run_integration_tests_final.TrustLog'):
            
            # Setup minimal mocks
            mock_trust_level.objects.filter.return_value.count.return_value = 0
            mock_trust_level.objects.count.return_value = 0
            
            result = run_all_tests()
            
            # Should return failure due to migration failure
            assert result == 1
    
    @patch('run_integration_tests_final.django.setup')
    @patch('run_integration_tests_final.call_command')
    @patch('run_integration_tests_final.settings')
    def test_final_report_generation(self, mock_settings, mock_call_command, mock_django_setup):
        """Test final report generation with statistics"""
        mock_settings.DATABASES = {'default': {'NAME': 'test_db'}}
        mock_call_command.return_value = None
        
        with patch('run_integration_tests_final.TrustLevel') as mock_trust_level, \
             patch('run_integration_tests_final.CRISPIntegrationService') as mock_service, \
             patch('run_integration_tests_final.Organization') as mock_org, \
             patch('run_integration_tests_final.get_user_model') as mock_user_model, \
             patch('run_integration_tests_final.TrustRelationship') as mock_trust_rel, \
             patch('run_integration_tests_final.TrustLog') as mock_trust_log:
            
            # Setup trust level mocks
            mock_trust_level_instance = Mock()
            mock_trust_level_instance.name = 'Trusted Partners'
            mock_trust_level_instance.is_active = True
            mock_trust_level_instance.numerical_value = 100
            
            mock_trust_level.objects.get_or_create.return_value = (mock_trust_level_instance, True)
            mock_trust_level.objects.filter.return_value.count.return_value = 5
            mock_trust_level.objects.count.return_value = 5
            mock_trust_level.objects.all.return_value = [mock_trust_level_instance]
            mock_trust_level.objects.get.return_value = mock_trust_level_instance
            
            # Setup organization and user creation
            mock_org_instance = Mock()
            mock_org_instance.name = 'Test Integration University'
            mock_service.create_organization_with_trust_setup.return_value = mock_org_instance
            
            mock_user_instance = Mock()
            mock_user_instance.email = 'admin@testorg.edu'
            mock_user_model.return_value.objects.get.return_value = mock_user_instance
            
            mock_relationship = Mock()
            mock_relationship.id = 'test-relationship-id'
            mock_relationship.trust_level.name = 'Trusted Partners'
            mock_service.create_trust_relationship.return_value = mock_relationship
            
            # Setup final report with specific counts
            mock_org.objects.count.return_value = 5
            mock_user_model.return_value.objects.count.return_value = 10
            mock_trust_level.objects.count.return_value = 5
            mock_trust_rel.objects.count.return_value = 3
            mock_trust_log.objects.count.return_value = 15
            
            result = run_all_tests()
            
            # Verify final report data was accessed
            mock_org.objects.count.assert_called_once()
            mock_user_model.return_value.objects.count.assert_called_once()
            mock_trust_level.objects.count.assert_called()
            mock_trust_rel.objects.count.assert_called_once()
            mock_trust_log.objects.count.assert_called_once()
            
            assert result == 0
    
    def test_print_header_formatting(self):
        """Test header formatting function"""
        with patch('builtins.print') as mock_print:
            print_header("Test Header")
            
            # Verify print was called with correct formatting
            calls = mock_print.call_args_list
            assert len(calls) == 3
            assert "=" * 70 in calls[0][0][0]
            assert "CRISP Integration Tests: Test Header" in calls[1][0][0]
            assert "=" * 70 in calls[2][0][0]
    
    def test_print_step_formatting(self):
        """Test step formatting function"""
        with patch('builtins.print') as mock_print:
            print_step(1, "Test Step Description")
            
            # Verify print was called with correct formatting
            calls = mock_print.call_args_list
            assert len(calls) == 2
            assert "Step 1: Test Step Description" in calls[0][0][0]
            assert "-" * 50 in calls[1][0][0]
    
    @patch('run_integration_tests_final.django.setup')
    @patch('run_integration_tests_final.call_command')
    @patch('run_integration_tests_final.settings')
    def test_integration_test_command_failure(self, mock_settings, mock_call_command, mock_django_setup):
        """Test handling of integration test command failure"""
        mock_settings.DATABASES = {'default': {'NAME': 'test_db'}}
        
        # Setup call_command to fail on integration tests
        def call_command_side_effect(command, *args, **kwargs):
            if command == 'test' and args[0] == 'apps.core.tests_integration':
                raise Exception("Integration tests failed")
            return None
        
        mock_call_command.side_effect = call_command_side_effect
        
        with patch('run_integration_tests_final.TrustLevel') as mock_trust_level, \
             patch('run_integration_tests_final.CRISPIntegrationService'), \
             patch('run_integration_tests_final.Organization'), \
             patch('run_integration_tests_final.get_user_model'), \
             patch('run_integration_tests_final.TrustRelationship'), \
             patch('run_integration_tests_final.TrustLog'):
            
            # Setup minimal mocks
            mock_trust_level.objects.get_or_create.return_value = (Mock(), True)
            mock_trust_level.objects.filter.return_value.count.return_value = 5
            mock_trust_level.objects.count.return_value = 5
            
            result = run_all_tests()
            
            # Should return failure due to integration test failure
            assert result == 1
    
    @patch('run_integration_tests_final.django.setup')
    @patch('run_integration_tests_final.call_command')
    @patch('run_integration_tests_final.settings')
    def test_complete_integration_success_scenario(self, mock_settings, mock_call_command, mock_django_setup):
        """Test complete successful integration scenario"""
        mock_settings.DATABASES = {'default': {'NAME': 'test_db'}}
        mock_call_command.return_value = None
        
        with patch('run_integration_tests_final.TrustLevel') as mock_trust_level, \
             patch('run_integration_tests_final.CRISPIntegrationService') as mock_service, \
             patch('run_integration_tests_final.Organization') as mock_org, \
             patch('run_integration_tests_final.get_user_model') as mock_user_model, \
             patch('run_integration_tests_final.TrustRelationship') as mock_trust_rel, \
             patch('run_integration_tests_final.TrustLog') as mock_trust_log, \
             patch('run_integration_tests_final.transaction') as mock_transaction:
            
            # Setup transaction mock
            mock_transaction.atomic.return_value.__enter__ = Mock()
            mock_transaction.atomic.return_value.__exit__ = Mock()
            
            # Setup complete successful scenario
            mock_trust_level_instance = Mock()
            mock_trust_level_instance.name = 'Trusted Partners'
            mock_trust_level_instance.is_active = True
            mock_trust_level_instance.numerical_value = 100
            
            mock_trust_level.objects.get_or_create.return_value = (mock_trust_level_instance, True)
            mock_trust_level.objects.filter.return_value.count.return_value = 5
            mock_trust_level.objects.count.return_value = 5
            mock_trust_level.objects.all.return_value = [mock_trust_level_instance]
            mock_trust_level.objects.get.return_value = mock_trust_level_instance
            
            # Setup organization creation
            mock_org_instance_1 = Mock()
            mock_org_instance_1.name = 'Test Integration University'
            mock_org_instance_2 = Mock()
            mock_org_instance_2.name = 'Test Partner University'
            
            mock_service.create_organization_with_trust_setup.side_effect = [
                mock_org_instance_1, mock_org_instance_2
            ]
            
            # Setup user creation
            mock_user_instance_1 = Mock()
            mock_user_instance_1.email = 'admin@testorg.edu'
            mock_user_instance_2 = Mock()
            mock_user_instance_2.email = 'admin@testorg2.edu'
            
            mock_user_model.return_value.objects.get.side_effect = [
                mock_user_instance_1, mock_user_instance_2
            ]
            
            # Setup trust relationship creation
            mock_relationship = Mock()
            mock_relationship.id = 'test-relationship-id'
            mock_relationship.trust_level.name = 'Trusted Partners'
            mock_service.create_trust_relationship.return_value = mock_relationship
            
            # Setup final report
            mock_org.objects.count.return_value = 2
            mock_user_model.return_value.objects.count.return_value = 2
            mock_trust_rel.objects.count.return_value = 1
            mock_trust_log.objects.count.return_value = 1
            
            result = run_all_tests()
            
            # Verify all steps completed successfully
            assert result == 0
            
            # Verify all major operations were called
            mock_call_command.assert_any_call('check', verbosity=1)
            mock_call_command.assert_any_call('migrate', verbosity=1)
            mock_call_command.assert_any_call('test', 'apps.core.tests_integration', verbosity=1)
            
            assert mock_service.create_organization_with_trust_setup.call_count == 2
            assert mock_service.create_trust_relationship.call_count == 1
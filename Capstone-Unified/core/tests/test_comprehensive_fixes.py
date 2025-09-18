"""
Comprehensive tests for all the fixes implemented for the issues:
1. TTP data management - database persistence and real-time updates
2. Data export functionality - STIX and CSV formats
3. IOC sharing capabilities
4. Comprehensive threat feed data sources with TTP extraction
"""
import json
import uuid
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from core.models.models import (
    ThreatFeed, Indicator, TTPData, Organization, SystemActivity
)
from core.user_management.models import CustomUser
from core.services.ttp_service import TTPService
from core.services.ioc_sharing_service import IOCSharingService
from core.services.anonymization_service import AnonymizationService
from core.services.ttp_extraction_service import TTPExtractionService
from core.repositories.ttp_repository import TTPRepository


class TTPDataManagementTestCase(TestCase):
    """Test TTP data management - database persistence and real-time updates"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.organization = Organization.objects.create(
            name='Test Organization',
            description='Test organization for testing'
        )
        self.user.organization = self.organization
        self.user.save()

        self.threat_feed = ThreatFeed.objects.create(
            name='Test Feed',
            description='Test threat feed',
            taxii_server_url='http://test.com/feed',
            is_active=True,
            owner=self.organization
        )

    def test_ttp_creation_and_persistence(self):
        """Test that TTP creation persists correctly in the database"""
        ttp_data = {
            'name': 'Test TTP',
            'description': 'Test TTP description',
            'mitre_technique_id': 'T1001',
            'mitre_tactic': 'initial_access',
            'threat_feed': self.threat_feed
        }

        # Create TTP
        ttp = TTPData.objects.create(**ttp_data)
        self.assertIsNotNone(ttp.id)
        self.assertEqual(ttp.name, 'Test TTP')

        # Test immediate retrieval
        retrieved_ttp = TTPData.objects.get(id=ttp.id)
        self.assertEqual(retrieved_ttp.name, 'Test TTP')
        self.assertEqual(retrieved_ttp.mitre_technique_id, 'T1001')

    def test_ttp_update_persistence(self):
        """Test that TTP updates persist correctly"""
        ttp = TTPData.objects.create(
            name='Original TTP',
            description='Original description',
            mitre_technique_id='T1001',
            mitre_tactic='initial_access',
            threat_feed=self.threat_feed
        )

        # Update TTP
        ttp.name = 'Updated TTP'
        ttp.description = 'Updated description'
        ttp.save()

        # Verify update persisted
        updated_ttp = TTPData.objects.get(id=ttp.id)
        self.assertEqual(updated_ttp.name, 'Updated TTP')
        self.assertEqual(updated_ttp.description, 'Updated description')

    def test_ttp_repository_operations(self):
        """Test TTP repository CRUD operations"""
        repository = TTPRepository()

        # Test creation
        ttp_data = {
            'name': 'Repository Test TTP',
            'description': 'Created via repository',
            'mitre_technique_id': 'T1002',
            'mitre_tactic': 'execution',
            'threat_feed': self.threat_feed
        }
        ttp = repository.create(ttp_data)
        self.assertIsNotNone(ttp.id)

        # Test retrieval
        retrieved_ttp = repository.get_by_id(ttp.id)
        self.assertEqual(retrieved_ttp.name, 'Repository Test TTP')

        # Test update
        updated_ttp = repository.update(ttp.id, {'name': 'Updated Repository TTP'})
        self.assertEqual(updated_ttp.name, 'Updated Repository TTP')

        # Test deletion
        success = repository.delete(ttp.id)
        self.assertTrue(success)
        self.assertIsNone(repository.get_by_id(ttp.id))

    def test_ttp_service_operations(self):
        """Test TTP service operations with user context"""
        service = TTPService()

        ttp_data = {
            'name': 'Service Test TTP',
            'description': 'Created via service',
            'mitre_technique_id': 'T1003',
            'mitre_tactic': 'credential_access'
        }

        # Test creation with user context
        ttp = service.create_ttp(ttp_data, user=self.user)
        self.assertIsNotNone(ttp.id)
        self.assertEqual(ttp.name, 'Service Test TTP')

        # Test retrieval with trust context
        retrieved_ttp = service.get_ttp_with_trust_context(ttp.id, self.user)
        self.assertIsNotNone(retrieved_ttp)
        self.assertEqual(retrieved_ttp.name, 'Service Test TTP')


class DataExportTestCase(APITestCase):
    """Test data export functionality - STIX and CSV formats"""

    def setUp(self):
        self.organization = Organization.objects.create(
            name='Test Organization',
            description='Test organization'
        )
        self.threat_feed = ThreatFeed.objects.create(
            name='Export Test Feed',
            description='Feed for export testing',
            taxii_server_url='http://test.com/feed',
            is_active=True,
            owner=self.organization
        )

        # Create test TTPs
        self.ttps = []
        for i in range(3):
            ttp = TTPData.objects.create(
                name=f'Export Test TTP {i+1}',
                description=f'Test TTP {i+1} for export testing',
                mitre_technique_id=f'T100{i+1}',
                mitre_tactic='execution',
                threat_feed=self.threat_feed
            )
            self.ttps.append(ttp)

    def test_json_export(self):
        """Test JSON export functionality"""
        from core.api.ttp_views import TTPExportView

        view = TTPExportView()
        queryset = TTPData.objects.filter(threat_feed=self.threat_feed)

        response = view._export_json(queryset, None, True)
        self.assertEqual(response.status_code, 200)

        data = response.data
        self.assertIn('ttps', data)
        self.assertIn('count', data)
        self.assertEqual(data['count'], 3)
        self.assertEqual(len(data['ttps']), 3)

    def test_csv_export(self):
        """Test CSV export functionality"""
        from core.api.ttp_views import TTPExportView

        view = TTPExportView()
        queryset = TTPData.objects.filter(threat_feed=self.threat_feed)

        response = view._export_csv(queryset, None)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])

        # Check CSV content
        content = response.content.decode('utf-8')
        lines = content.strip().split('\n')
        self.assertGreater(len(lines), 3)  # Header + 3 TTPs

    def test_stix_export(self):
        """Test STIX export functionality"""
        from core.api.ttp_views import TTPExportView

        view = TTPExportView()
        queryset = TTPData.objects.filter(threat_feed=self.threat_feed)

        response = view._export_stix(queryset)
        self.assertEqual(response.status_code, 200)

        data = response.data
        self.assertIn('type', data)
        self.assertIn('objects', data)
        self.assertEqual(data['type'], 'bundle')
        self.assertEqual(len(data['objects']), 3)

        # Validate STIX object structure
        stix_obj = data['objects'][0]
        self.assertEqual(stix_obj['type'], 'attack-pattern')
        self.assertIn('id', stix_obj)
        self.assertIn('name', stix_obj)
        self.assertIn('created', stix_obj)


class IOCSharingTestCase(TestCase):
    """Test IOC sharing capabilities"""

    def setUp(self):
        self.org1 = Organization.objects.create(
            name='Organization 1',
            description='First test organization'
        )
        self.org2 = Organization.objects.create(
            name='Organization 2',
            description='Second test organization'
        )

        self.user1 = CustomUser.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user1.organization = self.org1
        self.user1.save()

        self.threat_feed = ThreatFeed.objects.create(
            name='Sharing Test Feed',
            description='Feed for sharing tests',
            taxii_server_url='http://test.com/feed',
            is_active=True,
            owner=self.org1
        )

        self.indicator = Indicator.objects.create(
            type='md5',
            value='d41d8cd98f00b204e9800998ecf8427e',
            threat_feed=self.threat_feed
        )

    def test_anonymization_service(self):
        """Test anonymization service functionality"""
        service = AnonymizationService()

        # Test minimal anonymization
        anonymized = service.anonymize_indicator(self.indicator, 'minimal')
        self.assertTrue(anonymized['is_anonymized'])
        self.assertEqual(anonymized['anonymization_level'], 'minimal')
        self.assertEqual(anonymized['type'], self.indicator.type)

        # Test partial anonymization
        anonymized = service.anonymize_indicator(self.indicator, 'partial')
        self.assertTrue(anonymized['is_anonymized'])
        self.assertEqual(anonymized['anonymization_level'], 'partial')
        # For hash types, should be truncated
        self.assertTrue(anonymized['value'].endswith('...'))

        # Test full anonymization
        anonymized = service.anonymize_indicator(self.indicator, 'full')
        self.assertTrue(anonymized['is_anonymized'])
        self.assertEqual(anonymized['anonymization_level'], 'full')
        self.assertEqual(anonymized['value'], '[MD5_HASH]')

    def test_share_url_generation(self):
        """Test share URL generation"""
        service = IOCSharingService()

        # Create mock user for testing
        mock_user = type('MockUser', (), {
            'id': self.user1.id,
            'username': self.user1.username,
            'organization': self.org1,
            'is_authenticated': True
        })()

        # Mock the access control check
        service.access_control.can_share_indicator = lambda user, indicator: True

        result = service.generate_share_url(
            indicator_id=self.indicator.id,
            sharing_user=mock_user,
            expiry_hours=24
        )

        self.assertTrue(result['success'])
        self.assertIn('share_url', result)
        self.assertIn('share_token', result)
        self.assertIn('expires_at', result)

    def test_sharing_permissions(self):
        """Test sharing permissions functionality"""
        service = IOCSharingService()

        permissions = service.get_sharing_permissions(self.user1)

        self.assertIn('can_share', permissions)
        self.assertIn('user_organization', permissions)
        self.assertIn('share_methods', permissions)
        self.assertIn('anonymization_levels', permissions)


class TTPExtractionTestCase(TestCase):
    """Test comprehensive threat feed data sources with TTP extraction"""

    def setUp(self):
        # Create a test organization for the threat feed
        self.organization = Organization.objects.create(
            name='Test Organization',
            description='Test organization for extraction testing'
        )

        self.threat_feed = ThreatFeed.objects.create(
            name='Extraction Test Feed',
            description='Feed containing TTPs for extraction testing',
            taxii_server_url='http://test.com/feed',
            is_active=True,
            owner=self.organization
        )

        # Create indicators with TTP-related content
        self.indicators = [
            Indicator.objects.create(
                type='md5',
                value='abc123def456',
                threat_feed=self.threat_feed,
                description='Malware using T1055 process injection and powershell execution'
            ),
            Indicator.objects.create(
                type='ip',
                value='192.168.1.100',
                threat_feed=self.threat_feed,
                description='C2 server using spearphishing for initial access'
            ),
            Indicator.objects.create(
                type='domain',
                value='malicious.example.com',
                threat_feed=self.threat_feed,
                description='Domain used for lateral movement and credential dumping'
            )
        ]

    def test_ttp_extraction_from_text(self):
        """Test TTP extraction from text content"""
        service = TTPExtractionService()

        # Test technique ID extraction
        text = "The malware uses T1055 for process injection and T1059.001 for PowerShell execution"
        ttps = service._extract_ttps_from_text(text)

        self.assertGreater(len(ttps), 0)
        technique_ids = [ttp['mitre_technique_id'] for ttp in ttps]
        self.assertIn('T1055', technique_ids)
        self.assertIn('T1059.001', technique_ids)

    def test_ttp_extraction_from_technique_names(self):
        """Test TTP extraction from technique names"""
        service = TTPExtractionService()

        text = "The attack involved spearphishing and credential dumping with lsass access"
        ttps = service._extract_ttps_from_text(text)

        self.assertGreater(len(ttps), 0)
        technique_ids = [ttp['mitre_technique_id'] for ttp in ttps]
        self.assertIn('T1566.001', technique_ids)  # spearphishing
        self.assertIn('T1003', technique_ids)      # credential dumping
        self.assertIn('T1003.001', technique_ids)  # lsass

    def test_ttp_inference_from_indicator_types(self):
        """Test TTP inference from indicator types"""
        service = TTPExtractionService()

        # Test file hash inference
        hash_indicator = self.indicators[0]  # md5 hash
        ttps = service._infer_ttps_from_indicator_type(hash_indicator)
        self.assertGreater(len(ttps), 0)
        self.assertEqual(ttps[0]['mitre_technique_id'], 'T1204.002')

        # Test IP address inference
        ip_indicator = self.indicators[1]  # IP address
        ttps = service._infer_ttps_from_indicator_type(ip_indicator)
        self.assertGreater(len(ttps), 0)
        self.assertEqual(ttps[0]['mitre_technique_id'], 'T1071')

    def test_feed_ttp_extraction(self):
        """Test complete TTP extraction from a threat feed"""
        service = TTPExtractionService()

        result = service.extract_ttps_from_feed(self.threat_feed)

        self.assertTrue(result['success'])
        self.assertEqual(result['feed_id'], self.threat_feed.id)
        self.assertEqual(result['indicators_analyzed'], len(self.indicators))
        self.assertGreater(len(result['ttps_extracted']), 0)

        # Verify TTPs were created in database
        created_ttps = TTPData.objects.filter(threat_feed=self.threat_feed)
        self.assertGreater(created_ttps.count(), 0)

    def test_extraction_recommendations(self):
        """Test TTP extraction recommendations"""
        service = TTPExtractionService()

        recommendations = service.get_extraction_recommendations()

        self.assertIn('feeds_without_ttps', recommendations)
        self.assertIn('feeds_with_low_ttp_coverage', recommendations)
        self.assertIn('recommendations', recommendations)

        # Our test feed should appear in feeds without TTPs initially
        feed_names = [feed['name'] for feed in recommendations['feeds_without_ttps']]
        self.assertIn(self.threat_feed.name, feed_names)


class IntegrationTestCase(APITestCase):
    """Integration tests for the complete system"""

    def setUp(self):
        self.organization = Organization.objects.create(
            name='Integration Test Org',
            description='Organization for integration testing'
        )

        self.user = CustomUser.objects.create_user(
            username='integrationuser',
            email='integration@example.com',
            password='testpass123'
        )
        self.user.organization = self.organization
        self.user.save()

        self.threat_feed = ThreatFeed.objects.create(
            name='Integration Test Feed',
            description='Feed for integration testing',
            taxii_server_url='http://test.com/feed',
            is_active=True,
            owner=self.organization
        )

        self.client.force_authenticate(user=self.user)

    def test_ttp_crud_workflow(self):
        """Test complete TTP CRUD workflow through API"""
        # Create TTP
        ttp_data = {
            'name': 'Integration Test TTP',
            'description': 'TTP created for integration testing',
            'mitre_technique_id': 'T9999',
            'mitre_tactic': 'execution',
            'threat_feed_id': self.threat_feed.id
        }

        # POST to create TTP (using ttps_list endpoint)
        response = self.client.post('/api/ttps/', ttp_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ttp_id = response.data['id']

        # GET TTP details
        response = self.client.get(f'/api/ttps/{ttp_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Integration Test TTP')

        # UPDATE TTP
        update_data = {
            'name': 'Updated Integration Test TTP',
            'description': 'Updated description'
        }
        response = self.client.patch(f'/api/ttps/{ttp_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Updated Integration Test TTP')

        # DELETE TTP
        response = self.client.delete(f'/api/ttps/{ttp_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_export_workflow(self):
        """Test export functionality through API"""
        # Create test TTP
        ttp = TTPData.objects.create(
            name='Export Integration TTP',
            description='TTP for export integration testing',
            mitre_technique_id='T8888',
            mitre_tactic='execution',
            threat_feed=self.threat_feed
        )

        # Test JSON export
        response = self.client.get('/api/ttps/export/?format=json&limit=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ttps', response.data)

        # Test CSV export
        response = self.client.get('/api/ttps/export/?format=csv&limit=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')

        # Test STIX export
        response = self.client.get('/api/ttps/export/?format=stix&limit=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'bundle')

    def test_system_health_check(self):
        """Test that all systems are functioning correctly"""
        # Test system health endpoint
        response = self.client.get('/api/threat-feeds/system-health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        health_data = response.data
        self.assertIn('status', health_data)
        self.assertIn('database', health_data)

        # Verify database is healthy
        self.assertEqual(health_data['database']['status'], 'healthy')


class PerformanceTestCase(TestCase):
    """Performance tests for the implemented fixes"""

    def setUp(self):
        self.organization = Organization.objects.create(
            name='Performance Test Organization',
            description='Organization for performance testing'
        )

        self.threat_feed = ThreatFeed.objects.create(
            name='Performance Test Feed',
            description='Feed for performance testing',
            taxii_server_url='http://test.com/feed',
            is_active=True,
            owner=self.organization
        )

    def test_bulk_ttp_creation_performance(self):
        """Test performance of bulk TTP creation"""
        import time

        start_time = time.time()

        # Create 100 TTPs
        ttps = []
        for i in range(100):
            ttp_data = {
                'name': f'Performance Test TTP {i}',
                'description': f'Performance test TTP number {i}',
                'mitre_technique_id': f'T{8000 + i}',
                'mitre_tactic': 'execution',
                'threat_feed': self.threat_feed
            }
            ttps.append(TTPData(**ttp_data))

        TTPData.objects.bulk_create(ttps)
        end_time = time.time()

        duration = end_time - start_time
        self.assertLess(duration, 10.0)  # Should complete within 10 seconds

        # Verify all TTPs were created
        created_count = TTPData.objects.filter(threat_feed=self.threat_feed).count()
        self.assertEqual(created_count, 100)

    def test_export_performance(self):
        """Test performance of data export functions"""
        import time
        from core.api.ttp_views import TTPExportView

        # Create 50 test TTPs
        ttps = []
        for i in range(50):
            ttps.append(TTPData(
                name=f'Export Performance TTP {i}',
                description=f'Export performance test TTP {i}',
                mitre_technique_id=f'T{7000 + i}',
                mitre_tactic='execution',
                threat_feed=self.threat_feed
            ))
        TTPData.objects.bulk_create(ttps)

        view = TTPExportView()
        queryset = TTPData.objects.filter(threat_feed=self.threat_feed)

        # Test JSON export performance
        start_time = time.time()
        response = view._export_json(queryset, None, True)
        json_duration = time.time() - start_time
        self.assertLess(json_duration, 5.0)  # Should complete within 5 seconds

        # Test CSV export performance
        start_time = time.time()
        response = view._export_csv(queryset, None)
        csv_duration = time.time() - start_time
        self.assertLess(csv_duration, 5.0)  # Should complete within 5 seconds

        # Test STIX export performance
        start_time = time.time()
        response = view._export_stix(queryset)
        stix_duration = time.time() - start_time
        self.assertLess(stix_duration, 5.0)  # Should complete within 5 seconds
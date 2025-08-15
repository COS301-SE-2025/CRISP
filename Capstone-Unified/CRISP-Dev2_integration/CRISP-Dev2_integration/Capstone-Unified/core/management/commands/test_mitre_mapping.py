"""
Management command to test TTP-MITRE mapping service
"""

from django.core.management.base import BaseCommand
from core.services.mitre_mapping_service import TTPMappingService, MITREFrameworkData
import json


class Command(BaseCommand):
    help = 'Test TTP-MITRE mapping service with sample data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--sample-ttps',
            action='store_true',
            help='Test with predefined sample TTPs'
        )
        parser.add_argument(
            '--framework-data',
            action='store_true',
            help='Test MITRE framework data loading'
        )
        parser.add_argument(
            '--bulk-test',
            action='store_true',
            help='Test bulk mapping functionality'
        )
        parser.add_argument(
            '--validation-test',
            action='store_true',
            help='Test mapping validation'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing TTP-MITRE Mapping Service'))
        self.stdout.write('=' * 50)
        
        if options['framework_data']:
            self.test_framework_data()
        
        if options['sample_ttps']:
            self.test_sample_ttps()
        
        if options['bulk_test']:
            self.test_bulk_mapping()
        
        if options['validation_test']:
            self.test_validation()
        
        if not any(options.values()):
            # Run all tests if no specific option is provided
            self.test_framework_data()
            self.test_sample_ttps()
            self.test_bulk_mapping()
            self.test_validation()
    
    def test_framework_data(self):
        """Test MITRE framework data loading"""
        self.stdout.write('\n1. Testing MITRE Framework Data Loading')
        self.stdout.write('-' * 40)
        
        try:
            mitre_data = MITREFrameworkData()
            
            self.stdout.write(f'Loaded {len(mitre_data.techniques)} techniques')
            self.stdout.write(f'Loaded {len(mitre_data.tactics)} tactics')
            
            # Test a few specific lookups
            test_technique = mitre_data.get_technique('T1566')
            if test_technique:
                self.stdout.write(f'✓ Found T1566: {test_technique.get("name", "Unknown")}')
            else:
                self.stdout.write('✗ T1566 not found (using fallback data)')
            
            test_tactic = mitre_data.get_tactic('initial-access')
            if test_tactic:
                self.stdout.write(f'✓ Found initial-access: {test_tactic.get("name", "Unknown")}')
            else:
                self.stdout.write('✗ initial-access tactic not found')
            
            # Test search functionality
            search_results = mitre_data.search_techniques('phishing', limit=3)
            self.stdout.write(f'Search for "phishing" returned {len(search_results)} results')
            for result in search_results[:2]:
                self.stdout.write(f'  - {result["technique_id"]}: {result["name"]} (score: {result["score"]:.1f})')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error testing framework data: {e}'))
    
    def test_sample_ttps(self):
        """Test mapping with sample TTPs"""
        self.stdout.write('\n2. Testing Sample TTP Mappings')
        self.stdout.write('-' * 40)
        
        sample_ttps = [
            {
                'name': 'Spear Phishing Email Attack',
                'description': 'Adversaries send targeted phishing emails to specific individuals with malicious attachments or links to gain initial access to systems.'
            },
            {
                'name': 'PowerShell Command Execution',
                'description': 'Malicious actors use PowerShell to execute commands, download additional payloads, and maintain persistence on compromised systems.'
            },
            {
                'name': 'Credential Dumping with Mimikatz',
                'description': 'Attackers use tools like Mimikatz to extract plaintext passwords, hashes, and Kerberos tickets from memory.'
            },
            {
                'name': 'Lateral Movement via RDP',
                'description': 'Adversaries move laterally through the network using Remote Desktop Protocol connections with compromised credentials.'
            },
            {
                'name': 'Data Exfiltration over DNS',
                'description': 'Sensitive data is exfiltrated from the network by encoding it in DNS queries to attacker-controlled domains.'
            }
        ]
        
        mapping_service = TTPMappingService()
        
        for i, ttp in enumerate(sample_ttps, 1):
            try:
                self.stdout.write(f'\nTest {i}: {ttp["name"]}')
                result = mapping_service.map_ttp_to_mitre(ttp['name'], ttp['description'])
                
                if result.get('success') and result.get('best_match'):
                    match = result['best_match']
                    self.stdout.write(f'  ✓ Mapped to: {match.get("technique_id")} - {match.get("technique_name")}')
                    self.stdout.write(f'    Tactic: {match.get("tactic_id")} - {match.get("tactic_name")}')
                    self.stdout.write(f'    Confidence: {result.get("confidence", 0):.1f}%')
                    self.stdout.write(f'    Quality: {match.get("match_quality", "unknown")}')
                else:
                    self.stdout.write(f'  ✗ No mapping found: {result.get("error", "Unknown error")}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error mapping TTP {i}: {e}'))
    
    def test_bulk_mapping(self):
        """Test bulk mapping functionality"""
        self.stdout.write('\n3. Testing Bulk Mapping')
        self.stdout.write('-' * 40)
        
        bulk_ttps = [
            {'id': 1, 'name': 'Malware Installation', 'description': 'Installing malicious software on target systems'},
            {'id': 2, 'name': 'Registry Persistence', 'description': 'Modifying Windows registry for persistence'},
            {'id': 3, 'name': 'Network Reconnaissance', 'description': 'Scanning networks to discover assets and services'},
            {'id': 4, 'name': 'Process Injection', 'description': 'Injecting code into legitimate processes to evade detection'}
        ]
        
        try:
            mapping_service = TTPMappingService()
            result = mapping_service.bulk_map_ttps(bulk_ttps)
            
            self.stdout.write(f'Bulk mapping results:')
            self.stdout.write(f'  Total TTPs: {result.get("total_ttps", 0)}')
            self.stdout.write(f'  Successfully mapped: {result.get("mapped_count", 0)}')
            self.stdout.write(f'  High confidence: {result.get("high_confidence_count", 0)}')
            self.stdout.write(f'  Errors: {len(result.get("errors", []))}')
            
            for mapping in result.get('mappings', [])[:3]:  # Show first 3
                ttp_name = mapping.get('ttp_name', 'Unknown')
                mapping_result = mapping.get('mapping', {})
                best_match = mapping_result.get('best_match')
                
                if best_match:
                    self.stdout.write(f'  - {ttp_name}: {best_match.get("technique_id")} ({mapping_result.get("confidence", 0):.1f}%)')
                else:
                    self.stdout.write(f'  - {ttp_name}: No mapping found')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in bulk mapping test: {e}'))
    
    def test_validation(self):
        """Test mapping validation"""
        self.stdout.write('\n4. Testing Mapping Validation')
        self.stdout.write('-' * 40)
        
        test_cases = [
            {'technique_id': 'T1566', 'tactic_id': 'initial-access', 'should_be_valid': True},
            {'technique_id': 'T1059', 'tactic_id': 'execution', 'should_be_valid': True},
            {'technique_id': 'T1566', 'tactic_id': 'impact', 'should_be_valid': False},  # Invalid combination
            {'technique_id': 'T9999', 'tactic_id': 'initial-access', 'should_be_valid': False},  # Non-existent technique
            {'technique_id': 'T1566', 'tactic_id': 'fake-tactic', 'should_be_valid': False}  # Non-existent tactic
        ]
        
        mapping_service = TTPMappingService()
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                result = mapping_service.validate_mapping(
                    test_case['technique_id'], 
                    test_case['tactic_id']
                )
                
                is_valid = result.get('valid', False)
                expected = test_case['should_be_valid']
                
                status = '✓' if is_valid == expected else '✗'
                self.stdout.write(
                    f'  {status} Test {i}: {test_case["technique_id"]} + {test_case["tactic_id"]} '
                    f'-> {"Valid" if is_valid else "Invalid"}'
                )
                
                if not is_valid and result.get('error'):
                    self.stdout.write(f'    Error: {result["error"]}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error in validation test {i}: {e}'))
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('TTP-MITRE Mapping Service Testing Complete'))
"""
VirusTotal API Service for threat intelligence and TTP extraction
"""
import logging
import requests
import time
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from core.models.models import ThreatFeed, Indicator, TTPData, SystemActivity

logger = logging.getLogger(__name__)


class VirusTotalService:
    """Service for integrating with VirusTotal API"""

    def __init__(self):
        self.api_key = getattr(settings, 'VIRUSTOTAL_API_KEY', None)
        self.base_url = 'https://www.virustotal.com/api/v3'
        self.headers = {
            'x-apikey': self.api_key,
            'Content-Type': 'application/json'
        }

        # Rate limiting: Free tier = 4 requests per minute
        self.rate_limit_delay = 15  # seconds between requests

    def test_api_connection(self) -> Dict[str, Any]:
        """Test VirusTotal API connection"""
        if not self.api_key:
            return {'success': False, 'error': 'No VirusTotal API key configured'}

        try:
            response = requests.get(
                f'{self.base_url}/users/{self.api_key}',
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'VirusTotal API connection successful',
                    'quota': response.headers.get('X-API-Quota-Hourly', 'Unknown')
                }
            else:
                return {
                    'success': False,
                    'error': f'API test failed: {response.status_code}',
                    'details': response.text
                }
        except Exception as e:
            return {'success': False, 'error': f'Connection failed: {str(e)}'}

    def get_file_behavior(self, file_hash: str) -> Dict[str, Any]:
        """Get file behavior analysis with TTP mappings"""
        try:
            # Get file report
            response = requests.get(
                f'{self.base_url}/files/{file_hash}',
                headers=self.headers,
                timeout=30
            )

            if response.status_code != 200:
                return {'success': False, 'error': f'File not found: {response.status_code}'}

            data = response.json()

            # Extract TTP-relevant data
            ttps = []
            behavior_data = data.get('data', {}).get('attributes', {})

            # Extract from sandbox reports
            sandbox_verdicts = behavior_data.get('sandbox_verdicts', {})
            for sandbox, verdict_data in sandbox_verdicts.items():
                if isinstance(verdict_data, dict):
                    malware_names = verdict_data.get('malware_names', [])
                    ttps.extend(self._extract_ttps_from_malware_names(malware_names))

            # Extract from signature-based detections
            last_analysis = behavior_data.get('last_analysis_results', {})
            for engine, result in last_analysis.items():
                if result.get('category') == 'malicious':
                    result_name = result.get('result', '')
                    ttps.extend(self._extract_ttps_from_detection(result_name))

            time.sleep(self.rate_limit_delay)  # Rate limiting

            return {
                'success': True,
                'file_hash': file_hash,
                'ttps': list(set(ttps)),  # Remove duplicates
                'scan_date': behavior_data.get('last_analysis_date'),
                'reputation': behavior_data.get('reputation', 0)
            }

        except Exception as e:
            logger.error(f"VirusTotal file analysis error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_url_analysis(self, url: str) -> Dict[str, Any]:
        """Get URL analysis with TTP mappings"""
        try:
            # Submit URL for analysis
            submit_response = requests.post(
                f'{self.base_url}/urls',
                headers=self.headers,
                json={'url': url},
                timeout=30
            )

            if submit_response.status_code != 200:
                return {'success': False, 'error': f'URL submission failed: {submit_response.status_code}'}

            analysis_id = submit_response.json()['data']['id']

            time.sleep(self.rate_limit_delay)  # Rate limiting

            # Get analysis results
            analysis_response = requests.get(
                f'{self.base_url}/analyses/{analysis_id}',
                headers=self.headers,
                timeout=30
            )

            if analysis_response.status_code != 200:
                return {'success': False, 'error': 'Analysis retrieval failed'}

            data = analysis_response.json()
            attributes = data.get('data', {}).get('attributes', {})

            # Extract TTPs from URL analysis
            ttps = []

            # Check for malicious categories
            stats = attributes.get('stats', {})
            if stats.get('malicious', 0) > 0:
                ttps.append('T1189')  # Drive-by Compromise
                ttps.append('T1566.002')  # Spearphishing Link

            # Check for suspicious patterns
            results = attributes.get('results', {})
            for engine, result in results.items():
                if result.get('category') == 'malicious':
                    result_name = result.get('result', '')
                    ttps.extend(self._extract_ttps_from_detection(result_name))

            time.sleep(self.rate_limit_delay)  # Rate limiting

            return {
                'success': True,
                'url': url,
                'ttps': list(set(ttps)),
                'scan_date': attributes.get('date'),
                'stats': stats
            }

        except Exception as e:
            logger.error(f"VirusTotal URL analysis error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _extract_ttps_from_malware_names(self, malware_names: List[str]) -> List[str]:
        """Extract MITRE TTPs from malware family names"""
        ttps = []

        malware_ttp_mapping = {
            'trojan': ['T1055', 'T1083', 'T1082'],  # Process Injection, File Discovery, System Info Discovery
            'backdoor': ['T1071', 'T1105', 'T1090'],  # Application Layer Protocol, Ingress Tool Transfer, Proxy
            'ransomware': ['T1486', 'T1082', 'T1083'],  # Data Encrypted for Impact, System Discovery
            'keylogger': ['T1056.001', 'T1113'],  # Keylogging, Screen Capture
            'stealer': ['T1555', 'T1552', 'T1005'],  # Credentials from Password Stores, Unsecured Credentials
            'miner': ['T1496'],  # Resource Hijacking
            'rootkit': ['T1014', 'T1562.001'],  # Rootkit, Disable or Modify Tools
            'worm': ['T1021', 'T1210'],  # Remote Services, Exploitation of Remote Services
            'downloader': ['T1105', 'T1071'],  # Ingress Tool Transfer, Application Layer Protocol
            'dropper': ['T1105', 'T1204.002'],  # Ingress Tool Transfer, User Execution: Malicious File
        }

        for name in malware_names:
            name_lower = name.lower()
            for malware_type, techniques in malware_ttp_mapping.items():
                if malware_type in name_lower:
                    ttps.extend(techniques)

        return ttps

    def _extract_ttps_from_detection(self, detection_name: str) -> List[str]:
        """Extract TTPs from antivirus detection names"""
        ttps = []
        detection_lower = detection_name.lower()

        # Malware family-based TTP mappings
        if any(word in detection_lower for word in ['ransom', 'wannacry', 'wannacryptor', 'crypt', 'encrypt']):
            ttps.extend(['T1486', 'T1082', 'T1083', 'T1057'])  # Data Encrypted for Impact, System Discovery, Process Discovery

        if any(word in detection_lower for word in ['trojan', 'trj']):
            ttps.extend(['T1055', 'T1083', 'T1082', 'T1071'])  # Process Injection, File Discovery, System Info, Application Layer Protocol

        if any(word in detection_lower for word in ['backdoor', 'rat']):
            ttps.extend(['T1071', 'T1105', 'T1090'])  # Application Layer Protocol, Ingress Tool Transfer, Proxy

        if any(word in detection_lower for word in ['keylog', 'keylogger']):
            ttps.extend(['T1056.001', 'T1113'])  # Keylogging, Screen Capture

        if any(word in detection_lower for word in ['stealer', 'steal', 'info']):
            ttps.extend(['T1555', 'T1552', 'T1005'])  # Credentials from Password Stores, Unsecured Credentials, Local Data

        if any(word in detection_lower for word in ['miner', 'mining', 'coin']):
            ttps.extend(['T1496'])  # Resource Hijacking

        if any(word in detection_lower for word in ['rootkit']):
            ttps.extend(['T1014', 'T1562.001'])  # Rootkit, Disable or Modify Tools

        if any(word in detection_lower for word in ['worm']):
            ttps.extend(['T1021', 'T1210', 'T1018'])  # Remote Services, Exploitation of Remote Services, Remote System Discovery

        if any(word in detection_lower for word in ['downloader', 'loader']):
            ttps.extend(['T1105', 'T1071'])  # Ingress Tool Transfer, Application Layer Protocol

        if any(word in detection_lower for word in ['dropper']):
            ttps.extend(['T1105', 'T1204.002'])  # Ingress Tool Transfer, User Execution: Malicious File

        if any(word in detection_lower for word in ['emotet', 'banking']):
            ttps.extend(['T1056.001', 'T1555', 'T1071', 'T1055'])  # Keylogging, Credential Stores, Network Protocol, Process Injection

        if any(word in detection_lower for word in ['mirai', 'botnet', 'bot']):
            ttps.extend(['T1210', 'T1059', 'T1018'])  # Exploitation of Remote Services, Command and Scripting Interpreter

        if any(word in detection_lower for word in ['conficker', 'kido']):
            ttps.extend(['T1021', 'T1210', 'T1112'])  # Remote Services, Exploitation, Registry Modification

        if any(word in detection_lower for word in ['stuxnet']):
            ttps.extend(['T1210', 'T1105', 'T1055', 'T1014'])  # Exploitation, Ingress Tool Transfer, Process Injection, Rootkit

        # Technique-based detection patterns
        if any(word in detection_lower for word in ['powershell', 'ps1']):
            ttps.append('T1059.001')  # PowerShell

        if any(word in detection_lower for word in ['cmd', 'batch', 'bat']):
            ttps.append('T1059.003')  # Windows Command Shell

        if any(word in detection_lower for word in ['registry', 'regedit']):
            ttps.append('T1112')  # Modify Registry

        if any(word in detection_lower for word in ['persistence', 'startup']):
            ttps.append('T1547')  # Boot or Logon Autostart Execution

        if any(word in detection_lower for word in ['injection', 'inject']):
            ttps.append('T1055')  # Process Injection

        if any(word in detection_lower for word in ['credential', 'password']):
            ttps.append('T1003')  # OS Credential Dumping

        if any(word in detection_lower for word in ['spyware', 'spy']):
            ttps.extend(['T1113', 'T1056', 'T1005'])  # Screen Capture, Input Capture, Local Data

        if any(word in detection_lower for word in ['adware']):
            ttps.extend(['T1071', 'T1105'])  # Application Layer Protocol, Ingress Tool Transfer

        return list(set(ttps))  # Remove duplicates

    def sync_virustotal_feed(self, threat_feed: ThreatFeed, limit: int = 100) -> Dict[str, Any]:
        """Sync TTP data from VirusTotal feed"""
        results = {
            'feed_name': threat_feed.name,
            'sync_timestamp': timezone.now().isoformat(),
            'success': False,
            'ttps_created': 0,
            'indicators_processed': 0,
            'errors': []
        }

        try:
            # Test API connection first
            api_test = self.test_api_connection()
            if not api_test['success']:
                results['errors'].append(f"API connection failed: {api_test['error']}")
                return results

            with transaction.atomic():
                # Get existing indicators from this feed that don't have TTPs
                indicators = Indicator.objects.filter(
                    threat_feed=threat_feed,
                    type__in=['md5', 'sha1', 'sha256', 'url']
                )[:limit]

                results['indicators_processed'] = len(indicators)

                for indicator in indicators:
                    try:
                        if indicator.type in ['md5', 'sha1', 'sha256']:
                            # Analyze file hash
                            analysis = self.get_file_behavior(indicator.value)
                        elif indicator.type == 'url':
                            # Analyze URL
                            analysis = self.get_url_analysis(indicator.value)
                        else:
                            continue

                        if analysis['success'] and analysis.get('ttps'):
                            # Create TTP records
                            for ttp_id in analysis['ttps']:
                                ttp_name = self._get_technique_name(ttp_id)
                                ttp_tactic = self._get_technique_tactic(ttp_id)

                                # Check if TTP already exists
                                existing_ttp = TTPData.objects.filter(
                                    mitre_technique_id=ttp_id,
                                    threat_feed=threat_feed
                                ).first()

                                if not existing_ttp:
                                    TTPData.objects.create(
                                        name=ttp_name,
                                        description=f'VirusTotal analysis detected: {ttp_name}',
                                        mitre_technique_id=ttp_id,
                                        mitre_tactic=ttp_tactic,
                                        threat_feed=threat_feed,
                                        stix_id=f'attack-pattern--vt-{ttp_id.lower()}-{indicator.id}',
                                        created_at=timezone.now(),
                                        updated_at=timezone.now()
                                    )
                                    results['ttps_created'] += 1

                        # Rate limiting between requests
                        time.sleep(self.rate_limit_delay)

                    except Exception as e:
                        results['errors'].append(f"Error processing {indicator.value}: {str(e)}")
                        continue

                # Update feed sync information
                threat_feed.last_sync = timezone.now()
                threat_feed.sync_count = threat_feed.sync_count + 1
                threat_feed.last_error = None
                threat_feed.save()

                results['success'] = True

                # Log the sync activity
                SystemActivity.objects.create(
                    activity_type='virustotal_sync',
                    category='threat_feed',
                    title=f'VirusTotal sync completed for {threat_feed.name}',
                    description=f'Processed {results["indicators_processed"]} indicators, created {results["ttps_created"]} TTPs',
                    threat_feed=threat_feed,
                    metadata=results
                )

        except Exception as e:
            results['errors'].append(f"Sync failed: {str(e)}")
            logger.error(f"VirusTotal sync error: {str(e)}")

            # Update feed error
            threat_feed.last_error = str(e)
            threat_feed.save()

        return results

    def _get_technique_name(self, technique_id: str) -> str:
        """Get human-readable name for MITRE technique"""
        technique_names = {
            'T1055': 'Process Injection',
            'T1059.001': 'PowerShell',
            'T1059.003': 'Windows Command Shell',
            'T1071': 'Application Layer Protocol',
            'T1082': 'System Information Discovery',
            'T1083': 'File and Directory Discovery',
            'T1105': 'Ingress Tool Transfer',
            'T1112': 'Modify Registry',
            'T1189': 'Drive-by Compromise',
            'T1204.002': 'User Execution: Malicious File',
            'T1486': 'Data Encrypted for Impact',
            'T1547': 'Boot or Logon Autostart Execution',
            'T1555': 'Credentials from Password Stores',
            'T1562.001': 'Disable or Modify Tools',
            'T1566.002': 'Spearphishing Link',
        }
        return technique_names.get(technique_id, f'MITRE Technique {technique_id}')

    def _get_technique_tactic(self, technique_id: str) -> str:
        """Get MITRE tactic for technique"""
        technique_tactics = {
            'T1055': 'defense_evasion',
            'T1059': 'execution',
            'T1071': 'command_and_control',
            'T1082': 'discovery',
            'T1083': 'discovery',
            'T1105': 'command_and_control',
            'T1112': 'defense_evasion',
            'T1189': 'initial_access',
            'T1204': 'execution',
            'T1486': 'impact',
            'T1547': 'persistence',
            'T1555': 'credential_access',
            'T1562': 'defense_evasion',
            'T1566': 'initial_access',
        }

        # Get base technique (before the dot)
        base_technique = technique_id.split('.')[0]
        return technique_tactics.get(base_technique, 'unknown')
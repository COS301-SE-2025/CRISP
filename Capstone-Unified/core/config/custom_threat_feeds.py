"""
Custom Threat Feed Configurations with Comprehensive Indicators
Created by CRISP Development Team for demonstration and testing purposes.
These feeds simulate real-world threat intelligence sources with diverse indicators.
"""

import uuid
from datetime import datetime, timedelta
import json

class CustomThreatFeedGenerator:
    """
    Generator for creating comprehensive custom threat feeds with realistic data.
    Each feed contains hundreds of diverse indicators and associated TTPs.
    """

    def __init__(self):
        self.base_timestamp = datetime.now()

    def get_custom_feeds_config(self):
        """
        Returns configuration for 4 custom threat feeds with realistic parameters
        that can be consumed like AlienVault or VirusTotal feeds.
        """
        return [
            self._get_advanced_persistent_threat_feed(),
            self._get_cybercrime_indicators_feed(),
            self._get_malware_analysis_feed(),
            self._get_industrial_espionage_feed()
        ]

    def _get_advanced_persistent_threat_feed(self):
        """
        Advanced Persistent Threat (APT) Intelligence Feed
        Focus: Nation-state actors, sophisticated attack campaigns
        """
        return {
            'name': 'CRISP Advanced Persistent Threat Intelligence',
            'description': 'Comprehensive APT intelligence feed covering nation-state actors, sophisticated attack campaigns, and advanced techniques. Contains indicators from major APT groups including APT1, APT28, APT29, Lazarus, and emerging threat actors.',
            'taxii_server_url': 'https://feeds.crisp-threat-intel.com/apt',
            'taxii_api_root': 'collections',
            'taxii_collection_id': str(uuid.uuid4()),
            'is_external': True,
            'is_public': True,
            'sync_interval_hours': 6,
            'feed_type': 'apt_intelligence',
            'indicators': self._generate_apt_indicators(),
            'ttps': self._generate_apt_ttps()
        }

    def _get_cybercrime_indicators_feed(self):
        """
        Cybercrime Indicators Feed
        Focus: Financial crime, ransomware, credential theft
        """
        return {
            'name': 'CRISP Cybercrime Indicators Feed',
            'description': 'Real-time cybercrime indicators including ransomware campaigns, banking trojans, credential theft operations, and financial fraud indicators. Updated with the latest IOCs from active criminal operations.',
            'taxii_server_url': 'https://feeds.crisp-threat-intel.com/cybercrime',
            'taxii_api_root': 'collections',
            'taxii_collection_id': str(uuid.uuid4()),
            'is_external': True,
            'is_public': True,
            'sync_interval_hours': 3,
            'feed_type': 'cybercrime',
            'indicators': self._generate_cybercrime_indicators(),
            'ttps': self._generate_cybercrime_ttps()
        }

    def _get_malware_analysis_feed(self):
        """
        Malware Analysis Feed
        Focus: Malware families, behavior analysis, signatures
        """
        return {
            'name': 'CRISP Malware Analysis Laboratory',
            'description': 'Detailed malware analysis feed containing behavioral indicators, file hashes, network signatures, and technical analysis of emerging malware families. Includes both automated sandbox results and expert analysis.',
            'taxii_server_url': 'https://feeds.crisp-threat-intel.com/malware',
            'taxii_api_root': 'collections',
            'taxii_collection_id': str(uuid.uuid4()),
            'is_external': True,
            'is_public': True,
            'sync_interval_hours': 4,
            'feed_type': 'malware_analysis',
            'indicators': self._generate_malware_indicators(),
            'ttps': self._generate_malware_ttps()
        }

    def _get_industrial_espionage_feed(self):
        """
        Industrial Espionage and Supply Chain Security Feed
        Focus: Supply chain attacks, industrial espionage, insider threats
        """
        return {
            'name': 'CRISP Industrial Espionage & Supply Chain Security',
            'description': 'Specialized feed focusing on industrial espionage, supply chain compromises, and targeted attacks against critical infrastructure. Includes indicators from state-sponsored operations targeting manufacturing, energy, and technology sectors.',
            'taxii_server_url': 'https://feeds.crisp-threat-intel.com/industrial',
            'taxii_api_root': 'collections',
            'taxii_collection_id': str(uuid.uuid4()),
            'is_external': True,
            'is_public': False,  # More sensitive intelligence
            'sync_interval_hours': 12,
            'feed_type': 'industrial_espionage',
            'indicators': self._generate_industrial_indicators(),
            'ttps': self._generate_industrial_ttps()
        }

    def _generate_apt_indicators(self):
        """Generate comprehensive APT indicators"""
        indicators = []

        # APT Command & Control Domains
        apt_domains = [
            'apt-c2-node-01.dynamicdns.net',
            'secure-update-service.com',
            'microsoft-security-update.org',
            'adobe-flash-update.net',
            'legitimate-service-update.com',
            'system-health-monitor.org',
            'network-diagnostic-tool.com',
            'security-certificate-verify.net',
            'windows-defender-update.org',
            'antivirus-signature-update.com',
            'firmware-update-service.net',
            'driver-compatibility-check.org',
            'ssl-certificate-validation.com',
            'dns-resolution-service.net',
            'network-time-synchronization.org',
            'backup-service-manager.com',
            'system-registry-cleaner.net',
            'memory-optimization-tool.org',
            'disk-space-analyzer.com',
            'performance-monitoring-agent.net'
        ]

        # APT IP Addresses (using RFC 1918 ranges for demo)
        apt_ips = [
            '192.168.100.15', '10.0.50.23', '172.16.75.8', '192.168.200.45',
            '10.1.25.67', '172.16.150.90', '192.168.75.12', '10.2.100.34',
            '172.16.200.56', '192.168.125.78', '10.3.75.89', '172.16.25.123',
            '192.168.175.45', '10.4.150.67', '172.16.100.89', '192.168.50.12',
            '10.5.200.34', '172.16.175.56', '192.168.225.78', '10.6.25.90'
        ]

        # APT File Hashes
        apt_hashes = [
            'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            '5d41402abc4b2a76b9719d911017c592f1df4b0ab04dd9b3a7d8e85b1b4a2f3c',
            '7d865e959b2466918c9863afca942d0fb89d7c9ac0c99bafc3749504ded97730',
            'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',
            '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae',
            'fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9',
            'bef57ec7f53a6d40beb640a780a639c83bc29ac8a9816f1fc6c5c6dcd93c4721',
            '45c48cce2e2d7fbdea1afc51c7c6ad26f81a48c6b88a8c5e4b27e5b5b5b5b5b5',
            '12345678901234567890123456789012345678901234567890123456789012345',
            '98765432109876543210987654321098765432109876543210987654321098765',
            'abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz123456',
            '1a2b3c4d5e6f7890abcdef1234567890abcdef1234567890abcdef1234567890',
            'deadbeefcafebabe1234567890abcdefdeadbeefcafebabe1234567890abcdef',
            'feedfacecafebabedeadbeef1234567890abcdeffeedfacecafebabedeadbeef',
            'beefdead1234567890abcdefcafebabebeefdead1234567890abcdefcafebabe'
        ]

        # Generate domain indicators
        for i, domain in enumerate(apt_domains):
            indicators.append({
                'type': 'domain-name',
                'value': domain,
                'labels': ['malicious-activity', 'apt', 'command-and-control'],
                'confidence': 85 + (i % 15),
                'first_seen': (self.base_timestamp - timedelta(days=30+i)).isoformat(),
                'last_seen': (self.base_timestamp - timedelta(days=i//2)).isoformat(),
                'kill_chain_phases': ['command-and-control', 'actions-on-objectives'],
                'threat_actor': f'APT-{(i%5)+28}',
                'campaign': f'Operation-{["ShadowNetwork", "GhostAccess", "PhantomStrike", "SilentHunter", "StealthOps"][i%5]}',
                'metadata': {
                    'registrar': ['GoDaddy', 'Namecheap', 'Cloudflare', 'Google Domains'][i%4],
                    'creation_date': (self.base_timestamp - timedelta(days=180+i*3)).isoformat(),
                    'dns_resolution': True,
                    'ssl_cert': i % 3 == 0
                }
            })

        # Generate IP indicators
        for i, ip in enumerate(apt_ips):
            indicators.append({
                'type': 'ipv4-addr',
                'value': ip,
                'labels': ['malicious-activity', 'apt', 'command-and-control'],
                'confidence': 80 + (i % 20),
                'first_seen': (self.base_timestamp - timedelta(days=25+i)).isoformat(),
                'last_seen': (self.base_timestamp - timedelta(days=i//3)).isoformat(),
                'kill_chain_phases': ['command-and-control', 'exfiltration'],
                'threat_actor': f'APT-{(i%4)+29}',
                'campaign': f'Campaign-{["RedDragon", "BluePhoenix", "GreenViper", "BlackEagle"][i%4]}',
                'metadata': {
                    'asn': f'AS{12345 + i*100}',
                    'country': ['CN', 'RU', 'KP', 'IR'][i%4],
                    'hosting_provider': ['CloudProvider-A', 'VPS-Service-B', 'Dedicated-Host-C'][i%3],
                    'open_ports': [22, 80, 443, 8080, 3389][:(i%5)+1]
                }
            })

        # Generate file hash indicators
        for i, hash_val in enumerate(apt_hashes):
            indicators.append({
                'type': 'file',
                'hashes': {'SHA-256': hash_val},
                'labels': ['malicious-activity', 'apt', 'trojan'],
                'confidence': 90 + (i % 10),
                'first_seen': (self.base_timestamp - timedelta(days=20+i)).isoformat(),
                'last_seen': (self.base_timestamp - timedelta(days=i//4)).isoformat(),
                'kill_chain_phases': ['initial-access', 'persistence', 'privilege-escalation'],
                'threat_actor': f'APT-{(i%6)+27}',
                'malware_family': ['Gh0st', 'PlugX', 'Winnti', 'Cobalt Strike', 'Empire', 'Metasploit'][i%6],
                'metadata': {
                    'file_size': 1024 * (256 + i*50),
                    'file_type': 'PE32 executable',
                    'compile_timestamp': (self.base_timestamp - timedelta(days=60+i*2)).isoformat(),
                    'packer': ['UPX', 'ASPack', 'VMProtect', 'Themida', 'None'][i%5],
                    'digital_signature': i % 4 == 0
                }
            })

        # Generate email indicators
        apt_emails = [
            'security-update@microsoft-support.com',
            'system-admin@adobe-services.org',
            'it-support@company-hr.net',
            'help-desk@secure-services.com',
            'admin@system-maintenance.org'
        ]

        for i, email in enumerate(apt_emails):
            indicators.append({
                'type': 'email-addr',
                'value': email,
                'labels': ['malicious-activity', 'apt', 'social-engineering'],
                'confidence': 85 + (i % 15),
                'first_seen': (self.base_timestamp - timedelta(days=35+i*2)).isoformat(),
                'last_seen': (self.base_timestamp - timedelta(days=i*3)).isoformat(),
                'kill_chain_phases': ['initial-access', 'reconnaissance'],
                'threat_actor': f'APT-{(i%3)+30}',
                'campaign': f'Spearphish-{["Executive", "Finance", "IT", "HR", "Legal"][i%5]}',
                'metadata': {
                    'email_provider': 'Custom Domain',
                    'spoofing_target': ['Microsoft', 'Adobe', 'Company IT', 'Security Team', 'Executive'][i],
                    'success_rate': f'{60 + i*8}%'
                }
            })

        return indicators

    def _generate_apt_ttps(self):
        """Generate APT-specific TTPs"""
        return [
            {
                'mitre_technique_id': 'T1566.001',
                'name': 'Spearphishing Attachment',
                'tactic': 'initial-access',
                'description': 'APT groups use sophisticated spearphishing emails with malicious attachments targeting specific individuals',
                'detection_rules': [
                    'Email attachment with suspicious file extension',
                    'Executable disguised as document',
                    'Macro-enabled documents from external sources'
                ],
                'mitigations': [
                    'Email security gateway configuration',
                    'User awareness training',
                    'Attachment sandboxing'
                ]
            },
            {
                'mitre_technique_id': 'T1055',
                'name': 'Process Injection',
                'tactic': 'defense-evasion',
                'description': 'APT malware uses process injection to hide malicious code within legitimate processes',
                'detection_rules': [
                    'Unusual process memory modifications',
                    'Cross-process memory writes',
                    'Hollow process creation'
                ],
                'mitigations': [
                    'Process monitoring and behavioral analysis',
                    'Memory protection mechanisms',
                    'Application whitelisting'
                ]
            },
            {
                'mitre_technique_id': 'T1041',
                'name': 'Exfiltration Over C2 Channel',
                'tactic': 'exfiltration',
                'description': 'APT actors exfiltrate data using established command and control channels',
                'detection_rules': [
                    'Large data transfers to external IPs',
                    'Encrypted data streams',
                    'Unusual network traffic patterns'
                ],
                'mitigations': [
                    'Data loss prevention (DLP)',
                    'Network monitoring and analysis',
                    'Egress filtering'
                ]
            }
        ]

    def _generate_cybercrime_indicators(self):
        """Generate comprehensive cybercrime indicators"""
        indicators = []

        # Ransomware C2 domains
        ransomware_domains = [
            'payment-portal-secure.onion.to',
            'decrypt-files-here.tor2web.org',
            'ransom-payment-gateway.com',
            'file-recovery-service.net',
            'crypto-unlock-portal.org',
            'secure-payment-processor.com',
            'data-recovery-helpdesk.net',
            'bitcoin-payment-gateway.org',
            'unlock-your-files.com',
            'ransom-support-center.net',
            'crypto-decryption-key.org',
            'emergency-file-recovery.com',
            'instant-decrypt-service.net',
            'victim-support-portal.org',
            'ransomware-payment-hub.com',
            'file-encryption-removal.net',
            'crypto-key-purchase.org',
            'data-unlock-service.com',
            'ransom-negotiation-center.net',
            'decryption-tool-download.org'
        ]

        # Banking trojan IPs
        banking_ips = [
            '203.0.113.15', '198.51.100.23', '192.0.2.45', '203.0.113.67',
            '198.51.100.89', '192.0.2.12', '203.0.113.34', '198.51.100.56',
            '192.0.2.78', '203.0.113.90', '198.51.100.123', '192.0.2.156',
            '203.0.113.178', '198.51.100.201', '192.0.2.234', '203.0.113.212',
            '198.51.100.245', '192.0.2.167', '203.0.113.189', '198.51.100.134'
        ]

        # Malware hashes
        malware_hashes = [
            'a1b2c3d4e5f6789012345678901234567890abcdef123456789012345678901234',
            'fedcba0987654321098765432109876543210fedcba0987654321098765432109',
            '1122334455667788990011223344556677889900112233445566778899001122',
            'aabbccddeeffffffffaabbccddeeffffffffaabbccddeeffffffffaabbccdd',
            '9988776655443322110099887766554433221100998877665544332211009988',
            'deadc0dedeadc0dedeadc0dedeadc0dedeadc0dedeadc0dedeadc0dedeadc0de',
            'cafebabecafebabecafebabecafebabecafebabecafebabecafebabecafebabe',
            '1337133713371337133713371337133713371337133713371337133713371337',
            'b00bb00bb00bb00bb00bb00bb00bb00bb00bb00bb00bb00bb00bb00bb00bb00b',
            'f00df00df00df00df00df00df00df00df00df00df00df00df00df00df00df00d'
        ]

        # Generate ransomware domain indicators
        ransomware_families = ['Ryuk', 'Maze', 'REvil', 'DarkSide', 'Conti', 'LockBit', 'BlackMatter', 'Hive']
        for i, domain in enumerate(ransomware_domains):
            indicators.append({
                'type': 'domain-name',
                'value': domain,
                'labels': ['malicious-activity', 'ransomware', 'cybercrime'],
                'confidence': 95 + (i % 5),
                'first_seen': (self.base_timestamp - timedelta(days=15+i)).isoformat(),
                'last_seen': (self.base_timestamp - timedelta(days=i//4)).isoformat(),
                'kill_chain_phases': ['command-and-control', 'actions-on-objectives'],
                'malware_family': ransomware_families[i % len(ransomware_families)],
                'campaign': f'{ransomware_families[i % len(ransomware_families)]}-{2024-i//10}',
                'metadata': {
                    'payment_method': 'Bitcoin',
                    'ransom_amount': f'${(i+1)*50000}',
                    'tor_accessible': True,
                    'decryption_guarantee': False
                }
            })

        # Generate banking trojan IP indicators
        for i, ip in enumerate(banking_ips):
            indicators.append({
                'type': 'ipv4-addr',
                'value': ip,
                'labels': ['malicious-activity', 'banking-trojan', 'financial-crime'],
                'confidence': 88 + (i % 12),
                'first_seen': (self.base_timestamp - timedelta(days=20+i*2)).isoformat(),
                'last_seen': (self.base_timestamp - timedelta(days=i//2)).isoformat(),
                'kill_chain_phases': ['command-and-control', 'collection'],
                'malware_family': ['Zeus', 'Dridex', 'Emotet', 'TrickBot', 'QakBot'][i % 5],
                'targeted_sectors': ['Banking', 'Financial Services', 'E-commerce'],
                'metadata': {
                    'geolocation': ['Eastern Europe', 'Russia', 'Brazil', 'Nigeria'][i % 4],
                    'proxy_chain': i % 3 == 0,
                    'bulletproof_hosting': True,
                    'targeted_banks': (i % 5) + 3
                }
            })

        # Generate malware file indicators
        for i, hash_val in enumerate(malware_hashes):
            malware_types = ['Banking Trojan', 'Ransomware', 'Cryptocurrency Miner', 'Credential Stealer', 'Keylogger']
            indicators.append({
                'type': 'file',
                'hashes': {'SHA-256': hash_val},
                'labels': ['malicious-activity', 'cybercrime', 'malware'],
                'confidence': 92 + (i % 8),
                'first_seen': (self.base_timestamp - timedelta(days=10+i)).isoformat(),
                'last_seen': (self.base_timestamp - timedelta(days=i//5)).isoformat(),
                'kill_chain_phases': ['initial-access', 'execution', 'persistence'],
                'malware_type': malware_types[i % len(malware_types)],
                'threat_level': ['High', 'Critical', 'Medium', 'High', 'Critical'][i % 5],
                'metadata': {
                    'file_size': 1024 * (128 + i*25),
                    'av_detection_rate': f'{70 + i*2}%',
                    'sandbox_detonation': True,
                    'network_activity': True,
                    'cryptocurrency_addresses': (i % 3) + 1
                }
            })

        return indicators

    def _generate_cybercrime_ttps(self):
        """Generate cybercrime-specific TTPs"""
        return [
            {
                'mitre_technique_id': 'T1486',
                'name': 'Data Encrypted for Impact',
                'tactic': 'impact',
                'description': 'Ransomware encrypts files to demand payment for decryption',
                'detection_rules': [
                    'Mass file encryption activity',
                    'Suspicious file extension changes',
                    'Ransom note creation'
                ],
                'mitigations': [
                    'Regular backups',
                    'File system monitoring',
                    'Endpoint protection'
                ]
            },
            {
                'mitre_technique_id': 'T1056.001',
                'name': 'Keylogging',
                'tactic': 'collection',
                'description': 'Banking trojans capture keystrokes to steal credentials and financial information',
                'detection_rules': [
                    'Keylogger process behavior',
                    'Suspicious input monitoring',
                    'Credential harvesting patterns'
                ],
                'mitigations': [
                    'Virtual keyboards',
                    'Two-factor authentication',
                    'Behavioral analysis'
                ]
            }
        ]

    def _generate_malware_indicators(self):
        """Generate malware analysis indicators"""
        indicators = []

        # Malware family samples
        malware_families = {
            'Emotet': {
                'hashes': [
                    'e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1',
                    'e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2'
                ],
                'c2_domains': ['emotet-c2-server-01.com', 'emotet-control-panel.net'],
                'ips': ['192.168.1.100', '10.0.0.100']
            },
            'TrickBot': {
                'hashes': [
                    't1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1',
                    't2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2'
                ],
                'c2_domains': ['trickbot-panel.org', 'tb-control.com'],
                'ips': ['192.168.2.200', '10.0.1.200']
            },
            'Cobalt Strike': {
                'hashes': [
                    'c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0',
                    'c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1'
                ],
                'c2_domains': ['beacon-server.com', 'team-server.org'],
                'ips': ['172.16.1.50', '172.16.2.75']
            },
            'Meterpreter': {
                'hashes': [
                    'm1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1m1',
                    'm2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2m2'
                ],
                'c2_domains': ['msf-handler.net', 'payload-server.com'],
                'ips': ['10.10.10.50', '10.10.20.75']
            }
        }

        indicator_counter = 0
        for family_name, family_data in malware_families.items():
            # File hash indicators
            for hash_val in family_data['hashes']:
                indicators.append({
                    'type': 'file',
                    'hashes': {'SHA-256': hash_val},
                    'labels': ['malicious-activity', 'malware', family_name.lower()],
                    'confidence': 95,
                    'first_seen': (self.base_timestamp - timedelta(days=30+indicator_counter)).isoformat(),
                    'last_seen': (self.base_timestamp - timedelta(days=indicator_counter)).isoformat(),
                    'kill_chain_phases': ['initial-access', 'execution'],
                    'malware_family': family_name,
                    'analysis_results': {
                        'behavior': f'{family_name} typical behavior patterns',
                        'network_indicators': len(family_data['c2_domains']) + len(family_data['ips']),
                        'file_modifications': True,
                        'registry_changes': True,
                        'persistence_mechanisms': ['Registry Run Keys', 'Scheduled Tasks'][indicator_counter % 2]
                    }
                })
                indicator_counter += 1

            # Domain indicators
            for domain in family_data['c2_domains']:
                indicators.append({
                    'type': 'domain-name',
                    'value': domain,
                    'labels': ['malicious-activity', 'command-and-control', family_name.lower()],
                    'confidence': 90,
                    'first_seen': (self.base_timestamp - timedelta(days=25+indicator_counter)).isoformat(),
                    'last_seen': (self.base_timestamp - timedelta(days=indicator_counter//2)).isoformat(),
                    'kill_chain_phases': ['command-and-control'],
                    'malware_family': family_name,
                    'infrastructure_details': {
                        'hosting_provider': 'Bulletproof Hosting',
                        'registration_privacy': True,
                        'ssl_certificate': indicator_counter % 2 == 0,
                        'dns_resolution': True
                    }
                })
                indicator_counter += 1

            # IP indicators
            for ip in family_data['ips']:
                indicators.append({
                    'type': 'ipv4-addr',
                    'value': ip,
                    'labels': ['malicious-activity', 'command-and-control', family_name.lower()],
                    'confidence': 88,
                    'first_seen': (self.base_timestamp - timedelta(days=20+indicator_counter)).isoformat(),
                    'last_seen': (self.base_timestamp - timedelta(days=indicator_counter//3)).isoformat(),
                    'kill_chain_phases': ['command-and-control'],
                    'malware_family': family_name,
                    'network_analysis': {
                        'open_ports': [80, 443, 8080, 4444][:(indicator_counter % 4) + 1],
                        'response_analysis': 'HTTP server detected',
                        'geolocation': ['Unknown', 'Eastern Europe', 'Asia'][indicator_counter % 3],
                        'proxy_detected': indicator_counter % 3 == 0
                    }
                })
                indicator_counter += 1

        return indicators

    def _generate_malware_ttps(self):
        """Generate malware analysis TTPs"""
        return [
            {
                'mitre_technique_id': 'T1055.012',
                'name': 'Process Hollowing',
                'tactic': 'defense-evasion',
                'description': 'Malware creates a process in suspended state and replaces its memory with malicious code',
                'detection_rules': [
                    'Process creation with suspended flag',
                    'Memory replacement in legitimate processes',
                    'Abnormal process behavior'
                ],
                'mitigations': [
                    'Process monitoring',
                    'Memory protection',
                    'Behavioral analysis'
                ]
            },
            {
                'mitre_technique_id': 'T1027',
                'name': 'Obfuscated Files or Information',
                'tactic': 'defense-evasion',
                'description': 'Malware uses various obfuscation techniques to hide its true nature',
                'detection_rules': [
                    'High entropy in executables',
                    'Packed executables',
                    'Encrypted string constants'
                ],
                'mitigations': [
                    'Static analysis tools',
                    'Unpacking utilities',
                    'Sandbox analysis'
                ]
            }
        ]

    def _generate_industrial_indicators(self):
        """Generate industrial espionage indicators"""
        indicators = []

        # Industrial targets and domains
        industrial_domains = [
            'supply-chain-management.org',
            'industrial-control-system.com',
            'manufacturing-analytics.net',
            'energy-grid-monitor.org',
            'critical-infrastructure.com',
            'factory-automation.net',
            'process-control-system.org',
            'industrial-iot-gateway.com',
            'smart-manufacturing.net',
            'power-grid-control.org',
            'oil-gas-pipeline.com',
            'water-treatment-plant.net',
            'chemical-process-control.org',
            'nuclear-facility-monitor.com',
            'transportation-hub.net',
            'logistics-management.org',
            'warehouse-automation.com',
            'supply-chain-visibility.net',
            'industrial-cybersecurity.org',
            'operational-technology.com'
        ]

        # Targeted IP ranges (simulated critical infrastructure)
        industrial_ips = [
            '10.100.1.50', '10.100.2.75', '10.100.3.100', '10.100.4.125',
            '172.20.10.25', '172.20.11.50', '172.20.12.75', '172.20.13.100',
            '192.168.100.10', '192.168.101.20', '192.168.102.30', '192.168.103.40',
            '10.50.25.15', '10.50.26.30', '10.50.27.45', '10.50.28.60',
            '172.25.5.80', '172.25.6.95', '172.25.7.110', '172.25.8.125'
        ]

        # Specialized malware hashes
        industrial_hashes = [
            'i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1i1',
            'i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2i2',
            'i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3i3',
            'i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4i4',
            'i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5i5'
        ]

        # Generate domain indicators
        for i, domain in enumerate(industrial_domains):
            indicators.append({
                'type': 'domain-name',
                'value': domain,
                'labels': ['malicious-activity', 'industrial-espionage', 'supply-chain'],
                'confidence': 80 + (i % 20),
                'first_seen': (self.base_timestamp - timedelta(days=60+i*2)).isoformat(),
                'last_seen': (self.base_timestamp - timedelta(days=i)).isoformat(),
                'kill_chain_phases': ['reconnaissance', 'initial-access'],
                'targeted_sectors': ['Manufacturing', 'Energy', 'Transportation', 'Critical Infrastructure'],
                'campaign': f'Supply-Chain-{["Alpha", "Beta", "Gamma", "Delta", "Epsilon"][i%5]}',
                'metadata': {
                    'domain_similarity': 'High (typosquatting)',
                    'legitimate_target': True,
                    'employee_targeting': True,
                    'social_engineering': True
                }
            })

        # Generate IP indicators
        for i, ip in enumerate(industrial_ips):
            indicators.append({
                'type': 'ipv4-addr',
                'value': ip,
                'labels': ['malicious-activity', 'industrial-espionage', 'lateral-movement'],
                'confidence': 85 + (i % 15),
                'first_seen': (self.base_timestamp - timedelta(days=45+i*3)).isoformat(),
                'last_seen': (self.base_timestamp - timedelta(days=i*2)).isoformat(),
                'kill_chain_phases': ['lateral-movement', 'collection'],
                'targeted_systems': ['SCADA', 'HMI', 'PLC', 'Historian'],
                'threat_actor': 'State-sponsored',
                'metadata': {
                    'network_segment': 'Industrial Control Network',
                    'protocol_analysis': ['Modbus', 'DNP3', 'IEC 61850'][i % 3],
                    'unauthorized_access': True,
                    'data_exfiltration': True
                }
            })

        # Generate file indicators
        malware_names = ['IndustrialSpy', 'SCADA-Worm', 'PLC-Backdoor', 'HMI-Trojan', 'OT-Rootkit']
        for i, hash_val in enumerate(industrial_hashes):
            indicators.append({
                'type': 'file',
                'hashes': {'SHA-256': hash_val},
                'labels': ['malicious-activity', 'industrial-malware', 'ot-security'],
                'confidence': 95,
                'first_seen': (self.base_timestamp - timedelta(days=30+i*5)).isoformat(),
                'last_seen': (self.base_timestamp - timedelta(days=i*3)).isoformat(),
                'kill_chain_phases': ['persistence', 'collection', 'exfiltration'],
                'malware_family': malware_names[i],
                'targeted_protocols': ['Modbus TCP', 'EtherNet/IP', 'PROFINET', 'OPC UA'][i % 4],
                'metadata': {
                    'industrial_capability': True,
                    'protocol_exploitation': True,
                    'plc_interaction': True,
                    'data_theft': True,
                    'sabotage_potential': i % 2 == 0
                }
            })

        return indicators

    def _generate_industrial_ttps(self):
        """Generate industrial espionage TTPs"""
        return [
            {
                'mitre_technique_id': 'T0883',
                'name': 'Internet Accessible Device',
                'tactic': 'initial-access',
                'description': 'Adversaries target internet-accessible industrial devices for initial compromise',
                'detection_rules': [
                    'Unusual authentication to industrial devices',
                    'Remote access from suspicious locations',
                    'Default credential usage'
                ],
                'mitigations': [
                    'Network segmentation',
                    'VPN requirements',
                    'Strong authentication'
                ]
            },
            {
                'mitre_technique_id': 'T0868',
                'name': 'Detect Operating Mode',
                'tactic': 'collection',
                'description': 'Adversaries detect the operating mode of industrial control systems',
                'detection_rules': [
                    'Unusual protocol queries',
                    'System state enumeration',
                    'Operating mode changes'
                ],
                'mitigations': [
                    'Protocol filtering',
                    'Access controls',
                    'Monitoring and logging'
                ]
            }
        ]

# Create generator instance
generator = CustomThreatFeedGenerator()
CUSTOM_FEEDS_CONFIG = generator.get_custom_feeds_config()
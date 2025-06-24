"""
Mock STIX data for testing CRISP threat feed consumption.
"""

# STIX 1.x mock data (XML-based)
STIX1_INDICATOR_XML = """
<stix:STIX_Package 
    xmlns:stix="http://stix.mitre.org/stix-1"
    xmlns:stixCommon="http://stix.mitre.org/common-1"
    xmlns:indicator="http://stix.mitre.org/Indicator-2"
    xmlns:cybox="http://cybox.mitre.org/cybox-2"
    xmlns:AddressObj="http://cybox.mitre.org/objects#AddressObject-2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    version="1.2">
    <stix:Indicators>
        <stix:Indicator id="example:indicator-1">
            <indicator:Title>Test Indicator</indicator:Title>
            <indicator:Description>This is a test indicator</indicator:Description>
            <indicator:Observable>
                <cybox:Object>
                    <cybox:Properties xsi:type="AddressObj:AddressObjectType">
                        <AddressObj:Address_Value>192.168.1.1</AddressObj:Address_Value>
                    </cybox:Properties>
                </cybox:Object>
            </indicator:Observable>
        </stix:Indicator>
    </stix:Indicators>
</stix:STIX_Package>
"""

STIX1_TTP_XML = """
<stix:STIX_Package
    xmlns:stix="http://stix.mitre.org/stix-1"
    xmlns:stixCommon="http://stix.mitre.org/common-1"
    xmlns:ttp="http://stix.mitre.org/TTP-1"
    version="1.2">
    <stix:TTPs>
        <stix:TTP id="example:ttp-1">
            <ttp:Title>Common Ransomware Delivery Method</ttp:Title>
            <ttp:Description>This is a test TTP that uses spear phishing emails to deliver ransomware.</ttp:Description>
        </stix:TTP>
    </stix:TTPs>
</stix:STIX_Package>
"""

INVALID_XML = """
<invalid>
    This is not valid XML - missing closing tag
"""

# Simplified TAXII 1.x content block
TAXII1_CONTENT_BLOCK = {
    'content': STIX1_INDICATOR_XML.encode('utf-8'),
    'timestamp': '2024-06-20T15:16:56Z',
    'binding': 'urn:stix.mitre.org:xml:1.2'
}

# STIX 2.0 mock data (JSON-based)
STIX20_BUNDLE = {
    "type": "bundle",
    "id": "bundle--5d0092c5-9f89-460c-93f6-35a0587ac55d",
    "spec_version": "2.0",
    "objects": [
        {
            "type": "indicator",
            "id": "indicator--29aba82c-5393-42a8-9edb-6a2cb1df0a2c",
            "created": "2024-06-20T15:16:56.987Z",
            "modified": "2024-06-20T15:16:56.987Z",
            "name": "Malicious Domain",
            "description": "Domain associated with recent phishing campaign",
            "pattern": "[domain-name:value = 'evil-domain.com']",
            "valid_from": "2024-06-20T15:16:56.987Z",
            "labels": ["malicious-activity", "phishing"],
            "pattern_type": "stix",
            "spec_version": "2.0",
            "confidence": 85
        },
        {
            "type": "attack-pattern",
            "id": "attack-pattern--7e33a43e-e34b-40ec-89da-36c9bb2caff5",
            "created": "2024-06-20T15:16:56.987Z",
            "modified": "2024-06-20T15:16:56.987Z",
            "name": "Spear Phishing with Malicious Attachment",
            "description": "A spear phishing attack with a malicious attachment containing macro code",
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": "T1566.001",
                    "url": "https://attack.mitre.org/techniques/T1566/001"
                }
            ],
            "kill_chain_phases": [
                {
                    "kill_chain_name": "mitre-attack",
                    "phase_name": "initial_access"
                }
            ],
            "spec_version": "2.0"
        }
    ]
}

# STIX 2.1 mock data (JSON-based)
STIX21_BUNDLE = {
    "type": "bundle",
    "id": "bundle--83392364-5e18-4dfc-a3c1-7cd4adc7b542",
    "objects": [
        {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--8d12f4d7-e50d-4535-aab9-f017a534cc75",
            "created": "2024-06-20T15:16:56.987Z",
            "modified": "2024-06-20T15:16:56.987Z",
            "name": "Malicious File Hash",
            "description": "SHA-256 hash of a malicious executable file",
            "indicator_types": ["malicious-activity"],
            "pattern": "[file:hashes.'SHA-256' = '4bac27393bdd9777ce02453256c5577cd02275510b2227f473d03f533924f877']",
            "pattern_type": "stix",
            "pattern_version": "2.1",
            "valid_from": "2024-06-20T15:16:56.987Z",
            "confidence": 90
        },
        {
            "type": "attack-pattern",
            "spec_version": "2.1",
            "id": "attack-pattern--d18f4181-1782-4202-9141-d47d3cc9f95a",
            "created": "2024-06-20T15:16:56.987Z",
            "modified": "2024-06-20T15:16:56.987Z",
            "name": "Drive-by Compromise",
            "description": "Adversaries may gain access to a system through a user visiting a compromised website",
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": "T1189",
                    "url": "https://attack.mitre.org/techniques/T1189"
                }
            ],
            "kill_chain_phases": [
                {
                    "kill_chain_name": "mitre-attack",
                    "phase_name": "initial_access"
                }
            ]
        }
    ]
}

# Sample TAXII 2.0/2.1 collection information
TAXII2_COLLECTIONS = [
    {
        "id": "91a7b528-80eb-42ed-a74d-c6fbd5a26116",
        "title": "High Value Indicators",
        "description": "Curated set of high confidence indicators",
        "can_read": True,
        "can_write": False,
        "media_types": ["application/vnd.oasis.stix+json; version=2.0", "application/vnd.oasis.stix+json; version=2.1"]
    },
    {
        "id": "64993447-4d7e-4f70-b94d-d7f33742ee63",
        "title": "Emerging Threats",
        "description": "Recent and emerging threat indicators",
        "can_read": True,
        "can_write": True,
        "media_types": ["application/vnd.oasis.stix+json; version=2.1"]
    }
]
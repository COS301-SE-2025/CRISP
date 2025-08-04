"""
Mock STIX data for testing CRISP threat feed consumption.
"""

class MockContentBlock:
    """Mock TAXII content block that mimics the structure returned by cabby client"""
    def __init__(self, content, content_binding="application/xml", timestamp_label=None):
        self.content = content
        self.content_binding = content_binding
        self.timestamp_label = timestamp_label or "2023-01-01T00:00:00.000Z"

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

# TAXII 1.x Content Block
TAXII1_CONTENT_BLOCK = MockContentBlock(
    content=STIX1_INDICATOR_XML,
    content_binding="application/xml",
    timestamp_label="2023-01-01T00:00:00.000Z"
)

# STIX 2.0 Indicator
STIX20_INDICATOR = {
    "type": "indicator",
    "id": "indicator--01234567-89ab-cdef-0123-456789abcdef",
    "created": "2023-01-01T00:00:00.000Z",
    "modified": "2023-01-01T00:00:00.000Z",
    "labels": ["malicious-activity"],
    "pattern": "[ipv4-addr:value = '192.168.1.1']"
}

# STIX 2.0 Attack Pattern
STIX20_ATTACK_PATTERN = {
    "type": "attack-pattern",
    "id": "attack-pattern--01234567-89ab-cdef-0123-456789abcdef",
    "created": "2023-01-01T00:00:00.000Z",
    "modified": "2023-01-01T00:00:00.000Z",
    "name": "Spear Phishing",
    "description": "Targeted phishing attack"
}

# STIX 2.0 mock data (JSON-based)
STIX20_BUNDLE = {
    "type": "bundle",
    "id": "bundle--01234567-89ab-cdef-0123-456789abcdef",
    "objects": [
        STIX20_INDICATOR,
        STIX20_ATTACK_PATTERN
    ]
}

# STIX 2.1 Indicator
STIX21_INDICATOR = {
    "type": "indicator",
    "spec_version": "2.1",
    "id": "indicator--01234567-89ab-cdef-0123-456789abcdef",
    "created": "2023-01-01T00:00:00.000Z",
    "modified": "2023-01-01T00:00:00.000Z",
    "pattern": "[domain-name:value = 'malicious-domain.com']",
    "pattern_type": "stix",
    "valid_from": "2023-01-01T00:00:00.000Z",
    "labels": ["malicious-activity"]
}

STIX21_ATTACK_PATTERN = {
    "type": "attack-pattern",
    "spec_version": "2.1",
    "id": "attack-pattern--01234567-89ab-cdef-0123-456789abcdef",
    "created": "2023-01-01T00:00:00.000Z",
    "modified": "2023-01-01T00:00:00.000Z",
    "name": "PowerShell",
    "description": "PowerShell execution technique"
}

# STIX 2.1 Bundle
STIX21_BUNDLE = {
    "type": "bundle",
    "id": "bundle--01234567-89ab-cdef-0123-456789abcdef",
    "objects": [
        STIX21_INDICATOR,
        STIX21_ATTACK_PATTERN
    ]
}

# TAXII 2.x Collections
TAXII2_COLLECTIONS = [
    {
        "id": "collection-01234567-89ab-cdef-0123-456789abcdef",
        "title": "High Value Indicators",
        "description": "High confidence threat indicators",
        "can_read": True,
        "can_write": False,
        "media_types": ["application/stix+json;version=2.1"]
    },
    {
        "id": "collection-fedcba98-7654-3210-fedc-ba9876543210",
        "title": "Emerging Threats",
        "description": "Recently discovered threats",
        "can_read": True,
        "can_write": False,
        "media_types": ["application/stix+json;version=2.1"]
    }
]
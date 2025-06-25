"""
Configuration for TAXII sources.
"""

TAXII_SOURCES = {
    'alienvault_otx': {
        'name': 'AlienVault OTX',
        'discovery_url': 'https://otx.alienvault.com/taxii/discovery',
        'poll_url': 'https://otx.alienvault.com/taxii/poll',
        'collections_url': 'https://otx.alienvault.com/taxii/collections',
        'collections': {
            # Will be dynamically populated based on available collections
        },
        'poll_interval': 86400,
    }
}
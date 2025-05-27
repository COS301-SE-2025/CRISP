import requests
import json # Added for sending JSON data
import uuid # Import the uuid module

CLIENT_ID = 'xgChDOAuKAIEwIj6llbMZCQtF9w9avYJ4ctl5gno'
CLIENT_SECRET = 'MyNewRawSecretForOAuth123!' # Ensure this is the RAW secret

BASE_URL = 'http://localhost:8000'

def get_oauth_token():
    """Get OAuth token using client credentials"""
    token_url = f'{BASE_URL}/o/token/'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'read write'
    }
    response = requests.post(token_url, headers=headers, data=data)
    
    print(f"\nToken request details:")
    print(f"URL: {token_url}")
    print(f"Headers: {headers}")
    print(f"Data (client_secret is RAW): {{'grant_type': '{data['grant_type']}', 'client_id': '{data['client_id']}', 'client_secret': 'RAW_SECRET_SENT_NOT_LOGGED', 'scope': '{data['scope']}'}}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def create_stix_indicator(token):
    print("\n--- Testing STIX Indicator Creation ---")
    url = f"{BASE_URL}/api/stix/create-from-form/indicator/"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    payload = {
        "name": "Test Suspicious IP via API",
        "description": "Indicator for a suspicious IP address created via API test.",
        "pattern": "[ipv4-addr:value = '192.0.2.123']", # Example IP
        "pattern_type": "stix",
        "indicator_types": ["malicious-activity"],
        "valid_from": "2024-01-01T00:00:00Z" # Use a valid ISO 8601 timestamp
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"URL: {url}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}...")
    if response.status_code == 201: # Typically 201 Created
        return response.json().get('id') # Assuming the response contains the new object's ID
    return None

def get_taxii_collections(token):
    print("\n--- Testing GET TAXII Collections ---")
    url = f"{BASE_URL}/taxii2/collections/"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    print(f"URL: {url}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}...")
    if response.status_code == 200:
        collections = response.json().get('collections')
        if collections:
            return collections[0].get('id') # Return the ID of the first collection for further testing
    return None

def publish_to_taxii_collection(token, collection_id, stix_object_payload):
    if not collection_id:
        print("Skipping TAXII publish: No collection ID provided.")
        return
    print(f"\n--- Testing Publish to TAXII Collection (ID: {collection_id}) ---")
    url = f"{BASE_URL}/taxii2/collections/{collection_id}/objects/"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/stix+json;version=2.1'}
    # The payload for TAXII is typically a STIX bundle
    bundle = {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}", # Use uuid.uuid4()
        "objects": [stix_object_payload] # Assuming stix_object_payload is a valid STIX object dict
    }
    response = requests.post(url, headers=headers, json=bundle)
    print(f"URL: {url}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}...")

def anonymize_stix_object(token, stix_object_id):
    if not stix_object_id:
        print("Skipping Anonymization: No STIX object ID provided.")
        return
    print(f"\n--- Testing STIX Object Anonymization (ID: {stix_object_id}) ---")
    url = f"{BASE_URL}/api/stix/{stix_object_id}/anonymize/"
    headers = {'Authorization': f'Bearer {token}'}
    # You might need to specify an anonymization level if the API supports it
    # data = {"level": "partial"}
    # response = requests.post(url, headers=headers, json=data)
    response = requests.post(url, headers=headers) # Assuming default anonymization or GET
    print(f"URL: {url}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}...")


def test_all_endpoints(token):
    print("\n--- Testing General Endpoints ---")
    endpoints = [
        f'{BASE_URL}/api/organizations/',
        # f'{BASE_URL}/api/collections/', # This is different from TAXII collections
        f'{BASE_URL}/taxii2/',
    ]
    headers = {'Authorization': f'Bearer {token}'}
    for endpoint in endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        response = requests.get(endpoint, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200] if response.text else 'No content'}...")

    # STIX Object Creation
    # This is a more complete STIX object example for publishing
    indicator_payload_for_publishing = {
        "type": "indicator",
        "spec_version": "2.1",
        "id": f"indicator--{uuid.uuid4()}", # Use uuid.uuid4()
        "name": "Test Indicator for TAXII",
        "description": "Indicator for TAXII publishing test.",
        "pattern": "[ipv4-addr:value = '192.0.2.254']",
        "pattern_type": "stix",
        "indicator_types": ["malicious-activity"],
        "valid_from": "2024-01-01T00:00:00Z",
        "created": "2024-01-01T00:00:00Z", # Required for STIX
        "modified": "2024-01-01T00:00:00Z" # Required for STIX
    }
    # The create_stix_indicator function uses /api/stix/create-from-form/ which might return a different structure
    # For direct publishing, you often construct the STIX object yourself.
    # Let's assume create_stix_indicator is for the web form style API.
    created_stix_id = create_stix_indicator(token)


    # TAXII Workflow
    taxii_collection_id = get_taxii_collections(token)
    if taxii_collection_id and indicator_payload_for_publishing: # Use the self-constructed one for TAXII
        publish_to_taxii_collection(token, taxii_collection_id, indicator_payload_for_publishing)

    # Anonymization
    if created_stix_id: # Use the ID from the /api/stix/create-from-form/ endpoint
        anonymize_stix_object(token, created_stix_id)


if __name__ == '__main__':
    print("Attempting to get OAuth token...")
    token = get_oauth_token()
    
    if token:
        print(f"\nSuccessfully obtained token: {token[:20]}...")
        test_all_endpoints(token) # Renamed from test_endpoints to test_all_endpoints
    else:
        print("\nFailed to obtain token.")
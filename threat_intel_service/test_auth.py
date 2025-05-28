import requests
import json
import uuid
import time
import logging

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Test Configuration ---
# These should match your setup_oauth.py and Django settings
# For a real CI/CD, these would come from environment variables or a config file
CLIENT_ID = 'xgChDOAuKAIEwIj6llbMZCQtF9w9avYJ4ctl5gno'
CLIENT_SECRET = 'MyNewRawSecretForOAuth123!' # RAW secret
INVALID_CLIENT_SECRET = 'InvalidSecret!'
BASE_URL = 'http://localhost:8000' # Ensure your Django dev server is running here

TOKEN_URL = f'{BASE_URL}/o/token/'
TAXII_DISCOVERY_URL = f'{BASE_URL}/taxii2/'
TAXII_API_ROOT_URL = f'{BASE_URL}/taxii2/' # As per views.py, discovery and api root are same path
TAXII_COLLECTIONS_URL = f'{BASE_URL}/taxii2/collections/'
STIX_CREATE_INDICATOR_URL = f"{BASE_URL}/api/stix/create-from-form/indicator/"
ORGANIZATIONS_API_URL = f'{BASE_URL}/api/organizations/'

# --- Test Statistics ---
class AuthTestStats:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.timings = {}
        self.errors = []

    def record_pass(self, test_name):
        self.passed += 1
        logger.info(f"PASS: {test_name}")

    def record_fail(self, test_name, error_message, response_text=None):
        self.failed += 1
        full_error = f"FAIL: {test_name} - {error_message}"
        if response_text:
            full_error += f" | Response: {response_text[:200]}..."
        self.errors.append(full_error)
        logger.error(full_error)


    def record_timing(self, test_name, duration):
        self.timings[test_name] = duration
        logger.info(f"TIME: {test_name} - {duration:.4f}s")

    def print_summary(self):
        total_tests = self.passed + self.failed
        logger.info("\n" + "="*30 + " AUTH TEST SUMMARY " + "="*30)
        logger.info(f"Total Auth Tests: {total_tests}")
        logger.info(f"Passed: {self.passed}")
        logger.info(f"Failed: {self.failed}")
        if self.failed > 0:
            logger.error("\n--- Detailed Auth Failures ---")
            for error in self.errors:
                logger.error(error)
        logger.info("\n--- Auth Test Timings (seconds) ---")
        for name, duration in sorted(self.timings.items(), key=lambda item: item[1], reverse=True):
            logger.info(f"{name}: {duration:.4f}")
        logger.info("="*77 + "\n")

stats = AuthTestStats()

# --- Helper Functions ---
def timed_test(func):
    def wrapper(*args, **kwargs):
        test_name = func.__name__
        start_time = time.time()
        try:
            func(*args, **kwargs)
            # stats.record_pass(test_name) # Failures are recorded explicitly in tests
        except AssertionError as e:
            # stats.record_fail(test_name, str(e)) # Already handled in test
            pass # Assertion errors are handled within test cases for more specific logging
        except Exception as e:
            stats.record_fail(test_name, f"Unexpected error: {type(e).__name__} - {str(e)}")
        finally:
            duration = time.time() - start_time
            stats.record_timing(test_name, duration)
    return wrapper

def get_oauth_token(client_id, client_secret, scope='read write'):
    """Get OAuth token using client credentials."""
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope
    }
    logger.info(f"\nRequesting token from: {TOKEN_URL}")
    logger.info(f"Data (client_secret is RAW): {{'grant_type': '{data['grant_type']}', 'client_id': '{data['client_id']}', 'client_secret': 'RAW_SECRET_SENT_NOT_LOGGED', 'scope': '{data['scope']}'}}")

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    logger.info(f"Token request status: {response.status_code}")
    logger.info(f"Token response: {response.text[:500]}...")

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        expires_in = token_data.get('expires_in')
        logger.info(f"Token obtained successfully. Expires in: {expires_in}s")
        return access_token
    return None

# --- Test Cases ---

@timed_test
def test_get_oauth_token_valid_credentials():
    logger.info("\n--- Testing OAuth Token Retrieval (Valid Credentials) ---")
    token = get_oauth_token(CLIENT_ID, CLIENT_SECRET)
    if token:
        stats.record_pass("test_get_oauth_token_valid_credentials")
        assert token is not None, "Failed to obtain token with valid credentials."
    else:
        stats.record_fail("test_get_oauth_token_valid_credentials", "Token was None with valid credentials.")
    return token


@timed_test
def test_get_oauth_token_invalid_client_id():
    logger.info("\n--- Testing OAuth Token Retrieval (Invalid Client ID) ---")
    token = get_oauth_token("invalid_client_id", CLIENT_SECRET)
    if token is None:
        stats.record_pass("test_get_oauth_token_invalid_client_id")
    else:
        stats.record_fail("test_get_oauth_token_invalid_client_id", "Token obtained with invalid client ID.")
    assert token is None, "Token obtained with invalid client ID."

@timed_test
def test_get_oauth_token_invalid_client_secret():
    logger.info("\n--- Testing OAuth Token Retrieval (Invalid Client Secret) ---")
    token = get_oauth_token(CLIENT_ID, INVALID_CLIENT_SECRET)
    if token is None:
        stats.record_pass("test_get_oauth_token_invalid_client_secret")
    else:
        stats.record_fail("test_get_oauth_token_invalid_client_secret", "Token obtained with invalid client secret.")
    assert token is None, "Token obtained with invalid client secret."


@timed_test
def test_access_taxii_discovery_without_token():
    logger.info("\n--- Testing Access to TAXII Discovery (No Token) ---")
    response = requests.get(TAXII_DISCOVERY_URL)
    logger.info(f"Status: {response.status_code}, Response: {response.text[:200]}...")
    # TAXII discovery might be public or require auth depending on server config.
    # Assuming it requires auth for this test.
    # Django REST Framework typically returns 401 or 403 if auth is required and not provided/invalid.
    # OAuth2Provider typically returns 401 if token is missing/invalid for protected endpoints.
    if response.status_code in [401, 403]:
        stats.record_pass("test_access_taxii_discovery_without_token")
    else:
        stats.record_fail("test_access_taxii_discovery_without_token", f"Expected 401/403, got {response.status_code}", response.text)
    assert response.status_code in [401, 403], f"Expected 401/403 for unauthenticated access to TAXII Discovery, got {response.status_code}"

@timed_test
def test_access_taxii_collections_with_valid_token(token):
    if not token:
        stats.record_fail("test_access_taxii_collections_with_valid_token", "Skipped due to no valid token.")
        logger.warning("Skipping test_access_taxii_collections_with_valid_token: No valid token.")
        return

    logger.info("\n--- Testing Access to TAXII Collections (Valid Token) ---")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(TAXII_COLLECTIONS_URL, headers=headers)
    logger.info(f"Status: {response.status_code}, Response: {response.text[:200]}...")
    if response.status_code == 200:
        stats.record_pass("test_access_taxii_collections_with_valid_token")
    else:
        stats.record_fail("test_access_taxii_collections_with_valid_token", f"Expected 200, got {response.status_code}", response.text)
    assert response.status_code == 200, "Failed to access TAXII Collections with a valid token."
    try:
        collections_data = response.json()
        assert "collections" in collections_data, "TAXII Collections response missing 'collections' key."
    except json.JSONDecodeError:
        stats.record_fail("test_access_taxii_collections_with_valid_token", "Response was not valid JSON", response.text)
        assert False, "TAXII Collections response was not valid JSON."


@timed_test
def test_create_stix_indicator_without_token():
    logger.info("\n--- Testing STIX Indicator Creation (No Token) ---")
    payload = {
        "name": "Unauthorized Test IP", "description": "Attempt to create via API without token.",
        "pattern": "[ipv4-addr:value = '192.0.2.100']", "pattern_type": "stix",
        "indicator_types": ["malicious-activity"], "valid_from": "2024-01-01T00:00:00Z"
    }
    response = requests.post(STIX_CREATE_INDICATOR_URL, json=payload)
    logger.info(f"Status: {response.status_code}, Response: {response.text[:200]}...")
    if response.status_code in [401, 403]:
         stats.record_pass("test_create_stix_indicator_without_token")
    else:
        stats.record_fail("test_create_stix_indicator_without_token", f"Expected 401/403, got {response.status_code}", response.text)
    assert response.status_code in [401, 403], f"Expected 401/403 for unauthenticated STIX creation, got {response.status_code}"

@timed_test
def test_create_stix_indicator_with_valid_token(token):
    if not token:
        stats.record_fail("test_create_stix_indicator_with_valid_token", "Skipped due to no valid token.")
        logger.warning("Skipping test_create_stix_indicator_with_valid_token: No valid token.")
        return

    logger.info("\n--- Testing STIX Indicator Creation (Valid Token) ---")
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    payload = {
        "name": "Authorized Test IP via API",
        "description": "Indicator for a suspicious IP address created via authorized API test.",
        "pattern": f"[ipv4-addr:value = '192.0.2.{uuid.uuid4().fields[-1]%255}']", # Unique IP
        "pattern_type": "stix",
        "indicator_types": ["malicious-activity"],
        "valid_from": "2024-01-01T00:00:00Z"
    }
    response = requests.post(STIX_CREATE_INDICATOR_URL, headers=headers, json=payload)
    logger.info(f"Status: {response.status_code}, Response: {response.text[:500]}...")
    if response.status_code == 201: # Typically 201 Created
        stats.record_pass("test_create_stix_indicator_with_valid_token")
        try:
            response_data = response.json()
            assert "id" in response_data, "Create STIX response missing 'id' key."
            assert "stix_id" in response_data, "Create STIX response missing 'stix_id' key."
        except json.JSONDecodeError:
            stats.record_fail("test_create_stix_indicator_with_valid_token", "Response was not valid JSON", response.text)
            assert False, "Create STIX response was not valid JSON."
    else:
        stats.record_fail("test_create_stix_indicator_with_valid_token", f"Expected 201, got {response.status_code}", response.text)

    assert response.status_code == 201, "Failed to create STIX Indicator with a valid token."


@timed_test
def test_access_general_api_endpoints_with_valid_token(token):
    if not token:
        stats.record_fail("test_access_general_api_endpoints_with_valid_token", "Skipped due to no valid token.")
        logger.warning("Skipping test_access_general_api_endpoints_with_valid_token: No valid token.")
        return

    logger.info("\n--- Testing Access to General API Endpoints (Valid Token) ---")
    endpoints_to_test = [
        ORGANIZATIONS_API_URL,
        TAXII_DISCOVERY_URL, # Should be accessible with token too
        # Add more general authenticated endpoints here if they exist
    ]
    headers = {'Authorization': f'Bearer {token}'}
    all_passed = True
    for endpoint in endpoints_to_test:
        logger.info(f"Testing endpoint: {endpoint}")
        response = requests.get(endpoint, headers=headers)
        logger.info(f"Status: {response.status_code}, Response: {response.text[:200]}...")
        if response.status_code != 200:
            all_passed = False
            stats.record_fail(f"test_access_general_api_endpoint_{endpoint.split('/')[-2] or 'root'}", f"Failed for {endpoint}. Expected 200, got {response.status_code}", response.text)
        assert response.status_code == 200, f"Failed to access {endpoint} with a valid token. Status: {response.status_code}"
    if all_passed:
        stats.record_pass("test_access_general_api_endpoints_with_valid_token")


def main():
    logger.info("======== Starting OAuth and API Authentication Tests ========")

    # Run tests that don't require a token first
    test_get_oauth_token_invalid_client_id()
    test_get_oauth_token_invalid_client_secret()
    test_access_taxii_discovery_without_token()
    test_create_stix_indicator_without_token()

    # Get a valid token for subsequent tests
    valid_token = test_get_oauth_token_valid_credentials() # This test also records its own pass/fail

    if valid_token:
        logger.info(f"\nSuccessfully obtained token: {valid_token[:20]}...")
        # Run tests that require a valid token
        test_access_taxii_collections_with_valid_token(valid_token)
        test_create_stix_indicator_with_valid_token(valid_token)
        test_access_general_api_endpoints_with_valid_token(valid_token)
        # Add more authenticated endpoint tests here
    else:
        logger.error("\nFailed to obtain a valid token. Dependent tests will be skipped or will fail.")
        # Explicitly fail tests that couldn't run
        stats.record_fail("test_access_taxii_collections_with_valid_token", "Skipped: No valid token available.")
        stats.record_fail("test_create_stix_indicator_with_valid_token", "Skipped: No valid token available.")
        stats.record_fail("test_access_general_api_endpoints_with_valid_token", "Skipped: No valid token available.")


    logger.info("======== OAuth and API Authentication Tests Completed ========")
    stats.print_summary()

    if stats.failed > 0:
        exit(1) # Exit with error code if any auth tests failed

if __name__ == '__main__':
    # It's good practice to ensure the OAuth2 application is set up before running.
    # You might run `python3 setup_oauth.py` manually or call it here if idempotent.
    logger.info("Please ensure the OAuth2 application is correctly set up using 'python3 setup_oauth.py' and the Django development server is running.")
    logger.info(f"Targeting BASE_URL: {BASE_URL}\n")
    time.sleep(2) # Give a moment for the user to see the message
    main()
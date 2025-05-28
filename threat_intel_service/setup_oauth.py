import os
import django
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'threat_intel.settings')
BASE_DIR = Path(__file__).resolve().parent

# Initialize Django
django.setup()

from django.contrib.auth.models import User
from oauth2_provider.models import Application

# --- Use the same Client ID but a NEW RAW secret ---
NEW_RAW_CLIENT_SECRET = 'MyNewRawSecretForOAuth123!'
CLIENT_ID_TO_USE = 'xgChDOAuKAIEwIj6llbMZCQtF9w9avYJ4ctl5gno'

def setup_oauth():
    try:
        # Get admin user - ensure 'jadyn' is your superuser
        admin_user = User.objects.get(username='jadyn')
        
        # Delete existing application if it exists to ensure a clean state
        Application.objects.filter(client_id=CLIENT_ID_TO_USE).delete()
        print(f"Deleted existing application with Client ID: {CLIENT_ID_TO_USE}, if any.")
        
        # Create new application with the RAW secret
        # django-oauth-toolkit will hash this raw secret automatically
        app = Application.objects.create(
            name='Threat Intel Client',
            client_id=CLIENT_ID_TO_USE,
            client_secret=NEW_RAW_CLIENT_SECRET, # Provide the RAW secret here
            user=admin_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
            skip_authorization=True # Relevant for auth code grant, but good to set
        )
        
        print("\nOAuth2 application (re)created successfully:")
        print(f"Name: {app.name}")
        print(f"Client ID: {app.client_id}")
        # IMPORTANT: app.client_secret here will show the HASHED version stored in DB
        # We provided the RAW secret above for creation.
        print(f"Client Secret (Hashed in DB): {app.client_secret}")
        print(f"Make sure test_auth.py uses the RAW secret: '{NEW_RAW_CLIENT_SECRET}'")
        
    except User.DoesNotExist:
        print(f"Error: Superuser 'jadyn' not found. Please create it first using 'python3 manage.py createsuperuser'.")
    except Exception as e:
        print(f"An error occurred during OAuth2 setup: {str(e)}")

if __name__ == '__main__':
    setup_oauth()
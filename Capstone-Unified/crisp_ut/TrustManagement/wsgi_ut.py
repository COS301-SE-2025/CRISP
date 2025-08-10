"""
WSGI config for CRISP Trust Management project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.TrustManagement.settings')

application = get_wsgi_application()
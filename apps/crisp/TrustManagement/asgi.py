"""
ASGI config for CRISP Trust Management project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.TrustManagement.settings')

application = get_asgi_application()
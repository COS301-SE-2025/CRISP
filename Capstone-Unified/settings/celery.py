from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')

# Create the app
app = Celery('crisp_unified')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from specific packages
app.autodiscover_tasks(['core.tasks'])

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
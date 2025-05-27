import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_project.settings')

app = Celery('crisp_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Add periodic tasks
app.conf.beat_schedule = {
    'schedule-feed-consumption': {
        'task': 'feed_consumption.tasks.schedule_feed_consumption',
        'schedule': 300.0,  # Run every 5 minutes
    },
    'retry-failed-feeds': {
        'task': 'feed_consumption.tasks.retry_failed_feeds',
        'schedule': 3600.0,  # Run every hour
    },
}

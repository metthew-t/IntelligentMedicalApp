"""
Celery configuration for Intelligent Medical and Hospital Management System.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('intelligent_medical')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'cleanup-expired-sessions': {
        'task': 'apps.accounts.tasks.cleanup_expired_sessions',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
    'check-expiring-medicines': {
        'task': 'apps.pharmacy.tasks.check_expiring_medicines',
        'schedule': crontab(hour=6, minute=0),  # Run daily at 6 AM
    },
    'check-low-stock': {
        'task': 'apps.pharmacy.tasks.check_low_stock',
        'schedule': crontab(hour='*/6'),  # Run every 6 hours
    },
    'monitor-ml-models': {
        'task': 'apps.ml_governance.tasks.monitor_deployed_models',
        'schedule': crontab(hour='*/1'),  # Run every hour
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ipinfo_project.settings')

app = Celery('ipinfo_project')

# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery settings for async tasks
app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_annotations={'*': {'rate_limit': '10/s'}},  # Optional rate-limiting
    worker_concurrency=10,  # Adjust based on your expected load
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],  # Ensures that content is serialized properly
    worker_pool='solo',  # Use 'solo' for Celery 5.x async compatibility
    task_acks_late=True,  # Ensures that tasks are acknowledged late (after completion)
    task_track_started=True,  # Tracks task state for real-time updates
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

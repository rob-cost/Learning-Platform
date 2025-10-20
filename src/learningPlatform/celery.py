import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learningPlatform.settings')

app = Celery('learningPlatform')

# Load all config from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks
app.autodiscover_tasks()

# Debug: Print the broker URL being used
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    print(f"🔍 Celery Broker URL: {sender.conf.broker_url}")
    print(f"🔍 Celery Backend URL: {sender.conf.result_backend}")

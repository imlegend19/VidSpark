import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VidSpark.settings')

app = Celery('VidSpark')
app.config_from_object('django.conf:settings')

app.autodiscover_tasks()

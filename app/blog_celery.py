import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog.settings')
app = Celery('emails', broker_connection_rety=False, broker_connection_rety_on_startup=True)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()

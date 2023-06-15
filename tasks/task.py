import os
import django

from celery import Celery

config = "celery_test_second.settings"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', config)
django.setup()


app = Celery(
    'celery'
)

app.config_from_object(
    'tasks.celery_config', silent=True, force=True
)
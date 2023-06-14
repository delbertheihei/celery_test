import os
import django

from celery import Celery
from django.conf import settings

config = "celery_test_second.settings"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', config)
django.setup()

MQ_HOST = settings.REDIS_MQ_HOST
MQ_PORT = settings.REDIS_MQ_PORT
MQ_PASSWORD = settings.REDIS_MQ_PASSWORD
MQ_DB = settings.REDIS_MQ_DB

app = Celery(
    'celery',
    broker=f"redis://:{MQ_PASSWORD}@{MQ_HOST}:{MQ_PORT}/{MQ_DB}"
)

app.config_from_object(
    'tasks.celery_config', silent=True, force=True
)
app.conf.update(
    result_backend='db+postgresql://postgres:5252@localhost:5432/celery_test_2'
)

"""
celery 配置文件
"""
from datetime import timedelta

from kombu import Exchange, Queue
from django.conf import settings
import tasks.schedule_tasks

# timezone 时区
timezone = 'Asia/Shanghai'

# default exchange 默认交换机
default_exchange = Exchange('default', type='direct')

# 导入任务，可以导入多个任务
imports = ("tasks.async_tasks",)

# create queue
task_queues = (
    Queue('default', default_exchange, routing_key='default', max_priority=10),
)

# 配置
MQ_HOST = settings.REDIS_MQ_HOST
MQ_PORT = settings.REDIS_MQ_PORT
MQ_PASSWORD = settings.REDIS_MQ_PASSWORD
MQ_DB = settings.REDIS_MQ_DB

# 消息中间件 broker 的url， 可以配置redis，rabbitMQ等
broker_url = f"redis://:{MQ_PASSWORD}@{MQ_HOST}:{MQ_PORT}/{MQ_DB}"

# 工作线程池中的默认线程数
worker_concurrency = 2  # celery worker number

# create broker if not exists
task_create_missing_queues = True

worker_max_tasks_per_child = 100  # max tasks number per celery worker

CELERYD_FORCE_EXECV = True  # avoid deadlock

task_acks_late = True

worker_prefetch_multiplier = 4

# speed limit
worker_disable_rate_limits = True
# 任务的序列化方式
task_serializer = "pickle"
accept_content = ["json", "pickle"]

# 结果的序列化方式
result_serializer = "json"

# 结果保存
result_backend = 'db+postgresql://postgres:5252@localhost:5432/celery_test_2'
# 结果过期时间
result_expires = 60

task_default_queue = 'default'
task_default_exchange = 'default'
task_default_routing_key = 'default'

# 定时任务的配置
beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'

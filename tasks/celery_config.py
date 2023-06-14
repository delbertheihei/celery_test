from datetime import timedelta

from kombu import Exchange, Queue

import tasks.schedule_tasks

# timezone
timezone = 'UTC'

# default exchange
default_exchange = Exchange('default', type='direct')

imports = ("tasks.async_tasks",)

# create queue
task_queues = (
    Queue('default', default_exchange, routing_key='default', max_priority=10),
)

worker_concurrency = 2  # celery worker number

# create broker if not exists
task_create_missing_queues = True

worker_max_tasks_per_child = 100  # max tasks number per celery worker

CELERYD_FORCE_EXECV = True  # avoid deadlock

task_acks_late = True

worker_prefetch_multiplier = 4

# speed limit
worker_disable_rate_limits = True
task_serializer = "pickle"
accept_content = ["json", "pickle"]

task_default_queue = 'default'
task_default_exchange = 'default'
task_default_routing_key = 'default'

beat_schedule = {
    'task1': {
        'task': tasks.schedule_tasks.schedule_task_1,
        'schedule': timedelta(6)
    },
    'task2': {
        'task': 'tasks.schedule_tasks.schedule_task_2',
        'schedule': timedelta(3)
    },
    'task3': {
        'task': 'tasks.schedule_tasks.schedule_task_3',
        'schedule': timedelta(1)
    }
}

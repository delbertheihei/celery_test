# 异步任务（网站优化第二定律）

django框架的请求/响应的过程是同步的，但是需要执行耗时的任务比如发送邮件、调用第三方接口、批量处理文件等等，将这些任务异步化放在后台运行可以有效缩短请求响应时间

django应用celery一般用于处理异步任务或者定时任务

## celery

Celery是由Python开发、简单、灵活、可靠的分布式任务队列，是一个处理异步任务的框架，其本质是生产者消费者模型，生产者发送任务到消息队列，消费者负责处理任务。

celery的特点：

- 高可用：当任务执行失败或执行过程中发生连接中断，celery会自动尝试重新执行任务
- 快速：一个单进程的celery每分钟可处理上百万个任务
- 灵活：几乎celery的各个组件都可以被扩展及自定制

celery由三部分组成

- **消息中间件（Broker）**：Celery本身不提供消息服务，但是官方提供了很多备选方案，支持RabbitMQ、Redis、Amazon SQS、MongoDB、Memcached 等，官方推荐RabbitMQ，在Django项目中也推荐使用redis
- **任务执行单元（Worker）**：任务执行单元，负责从消息队列中取出任务执行，它可以启动一个或者多个，也可以启动在不同的机器节点，这就是其实现分布式的核心
- **任务执行结果存储（Backend）**：Celery支持以不同方式存储任务的结果，官方提供了诸多的存储方式支持：RabbitMQ、 Redis、Memcached,SQLAlchemy, Django ORM、Apache Cassandra、Elasticsearch等

![](E:\Study\Python\Django\image\celery.png)

- 任务模块Task包含异步任务和定时任务。其中，异步任务通常在业务逻辑中被触发并发往消息队列，而定时任务由Celery Beat进程周期性地将任务发往消息队列
- 任务执行单元Worker实时监视消息队列获取队列中的任务执行
- Woker执行完任务后将结果保存在Backend中

## 安装配置celery

- 安装celery

```
pip install celery
```

- 使用 Celery 库配置任务队列

```python
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

# 设置默认的交换机默认的队列默认的路由
task_default_queue = 'default'
task_default_exchange = 'default'
task_default_routing_key = 'default'

# 定时任务的配置
beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'
```

- 使用 Celery 配置应用程序

```python
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
```

- 在django项目的settings文件中配置如下信息

```python
REDIS_MQ_HOST = "localhost"
REDIS_MQ_PORT = "6379"
REDIS_MQ_PASSWORD = "123456"
REDIS_MQ_DB = "3"
```

- 自定义异步任务举例

```python
import csv

from tasks.task import app
from users.models import Users


@app.task
def export_users(email):
    users = Users.objects.all().values('email', 'first_name', 'last_name')
    if email:
        users = users.filter(email=email)
    import time
    time.sleep(5)
    with open('users.csv', 'w', encoding='utf-8') as f:
        user_csv = csv.DictWriter(f, fieldnames=['email', 'first_name', 'last_name'])
        user_csv.writeheader()
        for user in users:
            user_csv.writerow(user)
    return
```



- 在业务代码中执行异步任务，通过`delay()`方法调用异步任务，
- 也可以用`apply_async()`方法调用，指定调用时执行的参数，例如运行的时间，使用的任务队列等

```
export.apply_async(('test@test.com', ), queue='ex', countdown=10)
```

```python
class UserExportView(APIView):

    def post(self, request):
        email = request.data.get('email')
        from tasks.async_tasks import export_users
        export_users.delay(email)

        return Response({})
```

```python
    def get(self, request):
        # 提交异步任务
        ret = send_mail.delay('273323754@qq.com')

        # 获取任务结果
        print(ret, type(ret))
        # 任务是否已经执行
        print(ret.ready())
        # 任务的id
        print(ret.id)
        # 任务完成后return的内容
        print(ret.get())
        return HttpResponse('异步任务已执行')
```

- celery启动命令

```
celery -A apps.tasks.task worker -Q default --loglevel=debug
```

## celery调试

Windows对celery进行调试比较困难，似乎celery4.0 之后，已经不支持Windows得一些操作，大多数配置方案都不支持Windows

### 配置pycharm

![](E:\Study\Python\Django\image\pycharm配置celery调试.png)

- Name： 配置调试器的名字
- Module name（script name)：在Windows中如果配置的是script name 可能会出现未知错误，所以需要在下拉框中选择Module name 进行配置。一些网上配置方案在Module中配置的是celery.bin.celery，但是可能无法启动，需要改为 celery
- Parameters：配置celery的启动命令，将命令前缀 'celery'去掉，且 -P 只能配置为solo，不能配置多线程模式
- Working directory：当前项目的根目录
- 其余配置默认即可

配置完成后即可在异步任务中打断点调试

## celery 问题

### 启动celery后，能正确收到任务，但是不能执行任务

**问题原因：**Celery默认使用多进程或多线程的并发池来处理任务，以提高任务的并发性能，然而，在某些情况下，特别是任务涉及到一些与多进程或多线程不兼容的操作或依赖时，可能会出现问题

**解决办法：**

- 在启动命令中加入  --pool=solo  参数

  ```
  celery -A tasks.task worker -Q default --pool=solo -l info
  ```

- 添加并发框架，安装Eventlet库的主要目的是替代Celery默认使用的多线程模型或多进程模型。Eventlet使用**协程**的方式实现并发，可以在遇到I/O操作时进行非阻塞的切换，提高并发处理的效率

  ```
  celery -A tasks.task worker -Q default -P eventlet -l info -c 2
  ```

### 修改代码

修改异步任务相关代码后，不止要重启django项目，还需要重启celery

# 定时任务

## 安装

```
pip install django-celery-beat
```

## 配置定时任务

- 在settings中注册

  ```python
  # 注册app
  INSTALLED_APPS = (
      ...,
      'django_celery_beat',
  )
  
  
  # 在celery_config中配置
  beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'
  ```

- 创建数据迁移，在数据库中创建与定时任务相关的表

  ```python
  django_celery_beat.models.PeriodicTask # 周期性任务
  django_celery_beat.models.IntervalSchedule # 间隔性任务
  django_celery_beat.models.CrontabSchedule # 定时任务
  ```

- 创建定时任务

  ```python
  @app.task
  def send_mail(email):
      print(f'向{email}发送邮件！')
      time.sleep(5)
      print('发送完成')
      return '邮件发送成功 OK'
  ```

- 创建定时任务

  - 在admin管理后台创建

    ![](E:\Study\Python\Django\image\admin创建异步任务.png)

  - 通过代码在定时任务的数据库中插入定时任务

    ```python
    # 创建定时任务的执行时间
    schedule, created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)
    
    # 定时任务不需要参数
    PeriodicTask.objects.create(interval=schedule, name='Custom task', task='schedules.my_corn_minder')
    
    # 定时任务需要参数
    PeriodicTask.objects.create(interval=schedule, name='Custom task', task='schedules.my_corn_minder', args=json.dumps(['arg1', 'arg2']), kwargs=json.dumps({'abc': 12}))
    ```

- 启动任务

  ```she
  celery -A tasks.task worker -Q default -P solo -l info
  ```

  
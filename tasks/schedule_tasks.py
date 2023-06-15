from .task import app


# @app.task(name='schedule_task_1')
def schedule_task_1():
    print('task_1 ********** 6s')


# @app.task(name='schedule_task_2')
def schedule_task_2():
    print('task_2 ********** 3s')


# @app.task(name='schedule_task_3')
def schedule_task_3():
    print('task_3 ********** 1s')

from celery import Celery

app = Celery('tasks', broker='redis://redis', backend='redis://redis')


@app.task(name='tasks.add')
def add(x, y):
    return x+y

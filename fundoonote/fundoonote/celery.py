from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import environ
# # set the default Django settings module for the 'celery' program.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundoonote.settings')
app = Celery('fundoonote')
# # Using a string here means the worker will not have to serialize.
# #pickle the object when using Windows.

# load task modules from all django app config.
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.config_from_object('django.conf:settings')
# RabbitMQ is a message broker
app = Celery('fundooapp',
             broker='amqp://bhakti:bhakti123@localhost/bhakti_vhost',
             # broker=os.getenv('RABBIT_MQ'),
             backend='rpc://',
             include=['fundooapp.tasks'])

app.conf.update(
    CELERY_DEFAULT_QUEUE = "myapp",
    CELERY_DEFAULT_EXCHANGE = "myapp",
    CELERY_DEFAULT_EXCHANGE_TYPE = "direct",
    CELERY_DEFAULT_ROUTING_KEY = "myapp",
)



""" The task decorator will share tasks between apps by default """
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
@app.task
def send_notification():
    print('Hello How are you')

    app.conf.beat_schedule = {
        "see-you-in-ten-seconds-task": {
            "task": "periodic.send_notification",
            "schedule": 20.0
        }
    }

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundoonote.settings')
app = Celery('fundoonote')
#  Using a string here means the worker will not have to serialize.
# pickle the object when using Windows.

# load task modules from all django app config.
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.config_from_object('django.conf:settings')
# RabbitMQ is a message broker
app = Celery('fundooapp',
             broker='amqp://admin:admin123@localhost/15672',
             backend='rpc://',
             include=['fundooapp.tasks'],
             )
app.conf.update(
    CELERY_DEFAULT_QUEUE = "RABBIT_MQ",
    CELERY_DEFAULT_EXCHANGE = "RABBIT_MQ",
    CELERY_DEFAULT_EXCHANGE_TYPE = "direct",
    CELERY_DEFAULT_ROUTING_KEY = "RABBIT_MQ",
)   

# # The task decorator will share tasks between apps by default """
# @app.task(bind=True)
# def debug_task(self):
#     print(self.request)




from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundoonote.settings')
app = Celery('fundoonote')
# Using a string here means the worker will not have to serialize.
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')

# load task modules from all django app config.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
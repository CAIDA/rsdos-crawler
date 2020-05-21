#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Celery
------

This module initializes the the celery application of the DoS crawler.

"""

from celery import Celery
from doscrawler.tasks import Crawl


# set the default Django settings module for the 'celery' program.
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.local')

app = Celery("doscrawler", broker="amqp://", backend="rpc://", include=["doscrawler.tasks"], fixups=[])

# Using a string here means the worker will not have to
# pickle the object when using Windows.
#app.config_from_object('django.conf:settings', namespace='CELERY')
#app.autodiscover_tasks()
app.tasks.register(Crawl)

###########################
# TODO: point to settings #
###########################

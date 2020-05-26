#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Celery
------

This module initializes the the celery application of the DoS crawler.

"""

import os
from celery import Celery


# set default configuration
os.environ.setdefault("CELERY_CONFIG_MODULE", "config.development")

# create app with configuration
app = Celery("doscrawler")
app.config_from_envvar("CELERY_CONFIG_MODULE")

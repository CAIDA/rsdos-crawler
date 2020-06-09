#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Tables
------

This module defines the tables of the objects in the Swift containers for the DoS crawler.

"""

from datetime import timedelta
from simple_settings import settings
from doscrawler.app import app
from doscrawler.objects.models import Object


object_table = app.Table(
    name="doscrawler-objects",
    key_type=str,
    value_type=Object,
    default=bool
).tumbling(
    size=timedelta(seconds=settings.CONTAINER_GET_OBJECTS_TIMER),
    expires=timedelta(seconds=5*settings.CONTAINER_GET_OBJECTS_TIMER)
).relative_to_now()

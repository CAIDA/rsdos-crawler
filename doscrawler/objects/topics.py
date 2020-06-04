#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Topics
------

This module defines the topics of the objects in the Swift containers for the DoS crawler.

"""

from simple_settings import settings
from doscrawler.app import app
from doscrawler.objects.models import Object


object_topic = app.topic(
    "doscrawler-objects",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.OBJECT_RETENTION_INTERVAL,
    key_type=str,
    value_type=Object
)

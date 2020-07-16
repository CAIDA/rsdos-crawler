#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Tables
------

This module defines the tables of the objects in the Swift containers for the DoS crawler.

"""

from simple_settings import settings
from doscrawler.app import app
from doscrawler.objects.models import Object
from doscrawler.objects.topics import log_object_topic


object_table = app.Table(
    name="doscrawler-object",
    partitions=settings.TOPIC_PARTITIONS,
    key_type=str,
    value_type=Object,
    default=bool,
    changelog_topic=log_object_topic
)

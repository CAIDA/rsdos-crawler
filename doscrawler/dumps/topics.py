#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Topics
------

This module defines the topics for the dumps of the DoS crawler.

"""

from simple_settings import settings
from doscrawler.app import app
from doscrawler.dumps.models import Dump


change_dump_topic = app.topic(
    "doscrawler.dump.change",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    key_type=str,
    value_type=Dump
)

log_dump_topic = app.topic(
    "doscrawler.dump.log",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=Dump
)

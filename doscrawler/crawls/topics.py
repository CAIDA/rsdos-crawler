#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Topics
------

This module defines the topics of the crawls for the DoS crawler.

"""

from simple_settings import settings
from doscrawler.app import app
from doscrawler.targets.models import Target


find_crawl_topic = app.topic(
    "doscrawler-crawls-find",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=Target
)

retry_find_crawl_topic = app.topic(
    "doscrawler-crawls-find-retry",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=Target
)

repeat_find_crawl_topic = app.topic(
    "doscrawler-crawls-find-repeat",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=Target
)

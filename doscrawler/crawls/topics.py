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
from doscrawler.crawls.models import Crawl


get_crawl_topic = app.topic(
    "doscrawler-crawls-find",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=Target
)

wait_retry_crawl_topic = app.topic(
    "doscrawler-crawls-wait-retry",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=Target
)

wait_repeat_crawl_topic = app.topic(
    "doscrawler-crawls-wait-repeat",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=Target
)

update_crawl_topic = app.topic(
    "doscrawler-crawls-update",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=Crawl
)

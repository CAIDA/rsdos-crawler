#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Topics
------

This module defines the topics of the crawls for the DoS crawler.

"""

from simple_settings import settings
from doscrawler.app import app
from doscrawler.attacks.models import Attack
from doscrawler.crawls.models import Crawl


get_crawl_topic = app.topic(
    "doscrawler.crawl.get",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    key_type=str,
    value_type=Attack
)

change_crawl_topic = app.topic(
    "doscrawler.crawl.change",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.CRAWL_CACHE_INTERVAL,
    key_type=str,
    value_type=Crawl
)

change_wait_crawl_topic = app.topic(
    "doscrawler.crawl.wait.change",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    key_type=str,
    value_type=Attack
)

log_crawl_topic = app.topic(
    "doscrawler.crawl.log",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.CRAWL_CACHE_INTERVAL,
    allow_empty=True,
    value_type=Crawl
)

log_wait_crawl_topic = app.topic(
    "doscrawler.crawl.wait.log",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    allow_empty=True,
    value_type=Attack
)

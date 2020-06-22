#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Topics
------

This module defines the topics of the hosts for the DoS crawler.

"""

from simple_settings import settings
from doscrawler.app import app
from doscrawler.targets.models import Target
from doscrawler.hosts.models import HostGroup


get_host_topic = app.topic(
    "doscrawler-host-get",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.HOST_CACHE_INTERVAL,
    key_type=str,
    value_type=Target
)

change_host_topic = app.topic(
    "doscrawler-host-change",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.HOST_CACHE_INTERVAL,
    key_type=str,
    value_type=HostGroup
)

log_host_topic = app.topic(
    "doscrawler-host-log",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.HOST_CACHE_INTERVAL,
    value_type=HostGroup
)

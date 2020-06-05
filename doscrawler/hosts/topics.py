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


find_host_topic = app.topic(
    "doscrawler-hosts-find",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=Target
)

update_host_topic = app.topic(
    "doscrawler-hosts-update",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=HostGroup
)

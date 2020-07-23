#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Tables
------

This module defines the tables of the hosts for the DoS crawler.

"""

from simple_settings import settings
from doscrawler.app import app
from doscrawler.hosts.models import HostGroup
from doscrawler.hosts.topics import log_host_topic


host_table = app.Table(
    name="doscrawler.host",
    partitions=settings.TOPIC_PARTITIONS,
    key_type=str,
    value_type=HostGroup,
    default=bool,
    changelog_topic=log_host_topic
)

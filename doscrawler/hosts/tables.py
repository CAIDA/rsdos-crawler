#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Tables
------

This module defines the tables of the hosts for the DoS crawler.

"""

from doscrawler.app import app
from doscrawler.hosts.models import HostGroup
from doscrawler.hosts.topics import log_host_topic


host_table = app.Table(
    name="doscrawler-host",
    key_type=str,
    value_type=HostGroup,
    default=bool,
    changelog_topic=log_host_topic
)

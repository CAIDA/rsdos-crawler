#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Tables
------

This module defines the tables of the hosts for the DoS crawler.

"""

from doscrawler.app import app
from doscrawler.hosts.models import HostGroup


host_table = app.Table(
    name="doscrawler-hosts",
    key_type=str,
    value_type=HostGroup,
    default=bool
)

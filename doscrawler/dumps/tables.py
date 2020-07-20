#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Tables
------

This module defines the tables for the dumps of the DoS crawler.

"""

from doscrawler.app import app
from doscrawler.dumps.models import Dump
from doscrawler.dumps.topics import log_dump_topic


dump_table = app.Table(
    name="doscrawler-dump",
    key_type=str,
    value_type=Dump,
    default=bool,
    changelog_topic=log_dump_topic
)

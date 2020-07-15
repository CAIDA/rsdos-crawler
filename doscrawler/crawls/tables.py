#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Tables
------

This module defines the tables of the crawls for the DoS crawler.

"""

from doscrawler.app import app
from doscrawler.targets.models import Target
from doscrawler.crawls.models import Crawl
from doscrawler.crawls.topics import log_crawl_topic, log_wait_crawl_topic


crawl_table = app.Table(
    name="doscrawler-crawl",
    key_type=str,
    value_type=Crawl,
    default=bool,
    changelog_topic=log_crawl_topic
)

wait_crawl_table = app.Table(
    name="doscrawler-crawl-wait",
    key_type=str,
    value_type=Target,
    default=bool,
    changelog_topic=log_wait_crawl_topic
)

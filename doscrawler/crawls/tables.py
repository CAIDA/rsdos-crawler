#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Tables
------

This module defines the tables of the crawls for the DoS crawler.

"""

from doscrawler.app import app
from doscrawler.crawls.models import Crawl


crawl_table = app.Table(
    name="doscrawler-crawls",
    key_type=str,
    value_type=Crawl,
    default=bool
)

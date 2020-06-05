#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Tables
------

This module defines the tables of the targets for the DoS crawler.

"""

from doscrawler.app import app
from doscrawler.targets.models import Target


target_table = app.Table(
    name="doscrawler-targets",
    key_type=str,
    value_type=Target,
    default=bool
)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Topics
------

This module defines the topics of the targets for the DoS crawler.

"""

from simple_settings import settings
from doscrawler.app import app
from doscrawler.targets.models import TargetLine, Target


targetline_topic = app.topic(
    "doscrawler-targetlines",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=TargetLine
)

target_topic = app.topic(
    "doscrawler-targets",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=Target
)

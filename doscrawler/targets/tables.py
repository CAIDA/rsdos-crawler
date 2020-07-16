#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Tables
------

This module defines the tables of the targets for the DoS crawler.

"""

from simple_settings import settings
from doscrawler.app import app
from doscrawler.targets.models import Target
from doscrawler.targets.topics import log_target_topic, log_target_candidate_topic


target_table = app.Table(
    name="doscrawler-target",
    partitions=settings.TOPIC_PARTITIONS,
    key_type=str,
    value_type=Target,
    default=bool,
    changelog_topic=log_target_topic
)

target_candidate_table = app.Table(
    name="doscrawler-target-candidate",
    partitions=settings.TOPIC_PARTITIONS,
    key_type=str,
    value_type=Target,
    default=bool,
    changelog_topic=log_target_candidate_topic
)

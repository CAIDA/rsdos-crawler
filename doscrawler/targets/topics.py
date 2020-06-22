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


get_target_topic = app.topic(
    "doscrawler-target-get",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.CONTAINER_GET_OBJECTS_INTERVAL,
    value_type=TargetLine
)

change_target_topic = app.topic(
    "doscrawler-target-change",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    key_type=str,
    value_type=Target
)

log_target_topic = app.topic(
    "doscrawler-target-log",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=Target
)

change_target_candidate_topic = app.topic(
    "doscrawler-target-candidate-change",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.TARGET_MERGE_INTERVAL,
    key_type=str,
    value_type=Target
)

log_target_candidate_topic = app.topic(
    "doscrawler-target-candidate-log",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.TARGET_MERGE_INTERVAL,
    value_type=Target
)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Topics
------

This module defines the topics for the slack messages sent by the DoS crawler.

"""

from simple_settings import settings
from doscrawler.app import app
from doscrawler.slacks.models import Slack


get_slack_topic = app.topic(
    "doscrawler.slack.get",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=Slack
)

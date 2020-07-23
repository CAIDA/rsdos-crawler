#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Tables
------

This module defines the tables for the attacks in the DoS crawler.

"""

from simple_settings import settings
from doscrawler.app import app
from doscrawler.attacks.models import Attack
from doscrawler.attacks.topics import log_attack_topic, log_attack_candidate_topic


attack_table = app.Table(
    name="doscrawler.attack",
    partitions=settings.TOPIC_PARTITIONS,
    key_type=str,
    value_type=Attack,
    default=bool,
    changelog_topic=log_attack_topic
)

attack_candidate_table = app.Table(
    name="doscrawler.attack.candidate",
    partitions=settings.TOPIC_PARTITIONS,
    key_type=str,
    value_type=Attack,
    default=bool,
    changelog_topic=log_attack_candidate_topic
)

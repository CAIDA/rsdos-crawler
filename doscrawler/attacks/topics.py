#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Topics
------

This module defines the topics for the attacks in the DoS crawler.

"""

from simple_settings import settings
from doscrawler.app import app
from doscrawler.attacks.models import Attack
from doscrawler.attacks.schemas import AttackSchema


attack_topic = app.topic(
    "stardust.rsdos.attacks",
    value_type=bytes,
    schema=AttackSchema()
)

change_attack_topic = app.topic(
    "doscrawler.attack.change",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    key_type=str,
    value_type=Attack
)

log_attack_topic = app.topic(
    "doscrawler.attack.log",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    allow_empty=True,
    value_type=Attack
)

log_attack_candidate_topic = app.topic(
    "doscrawler.attack.candidate.log",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.ATTACK_MERGE_INTERVAL,
    allow_empty=True,
    value_type=Attack
)

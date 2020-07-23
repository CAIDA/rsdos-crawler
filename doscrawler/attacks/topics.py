#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Topics
------

This module defines the topics for the attacks in the DoS crawler.

"""

from simple_settings import settings
from doscrawler.app import app
from doscrawler.attacks.models import Attack, AttackVector

################################################################################
# TODO: change get_attack_topic to stardust.rsdos.attacks topic on other kafka #
################################################################################

attack_topic = app.topic(
    "doscrawler.attack",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.RETENTION_INTERVAL,
    value_type=AttackVector
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
    value_type=Attack
)

log_attack_candidate_topic = app.topic(
    "doscrawler.attack.candidate.log",
    partitions=settings.TOPIC_PARTITIONS,
    retention=settings.ATTACK_MERGE_INTERVAL,
    value_type=Attack
)

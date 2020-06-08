#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the targets for the DoS crawler.

"""

from faust import Record
from typing import List, Dict
from datetime import datetime, timedelta
from simple_settings import settings
from doscrawler.crawls.models import Crawl


class TargetLine(Record, coerce=True, serializer="json"):
    """
    Target line model class
    """

    target_ip: str
    nr_attacker_ips: int
    nr_attacker_ips_in_interval: int
    nr_attacker_ports: int
    nr_target_ports: int
    nr_packets: int
    nr_packets_in_interval: int
    nr_bytes: int
    nr_bytes_in_interval: int
    max_ppm: int
    start_time: datetime
    latest_time: datetime
    start_corsaro_interval: datetime


class Target(Record):
    """
    Target model class
    """

    ip: str
    start: datetime
    target_lines: List[TargetLine]
    hosts: Dict[str, List[Crawl]] = {}

    def get_ttl(self):
        """
        Get time to live for target and how long target is tracked

        :return: [float] time to live in seconds, can be negative
        """

        # get end time by latest time in latest target lines and target ttl in settings
        latest_time = max([target_line.latest_time for target_line in self.target_lines])
        end_time = latest_time + timedelta(seconds=settings.TARGET_TTL)

        # get remaining time
        current_time = datetime.now(settings.TIMEZONE).replace(tzinfo=None)
        remaining_time = (end_time - current_time).total_seconds()

        return remaining_time

    def get_no_retry_crawl(self):
        """
        Get number of retries to crawl target in recent time

        :return: [int] number of maximum retries on one of the hosts of the targets
        """

        interval_time = max(settings.CRAWL_REPEAT_INTERVAL, settings.CRAWL_RETRIES * settings.CRAWL_RETRIES_INTERVAL)
        interval_time_start = datetime.now(settings.TIMEZONE).replace(tzinfo=None) - timedelta(seconds=interval_time)

        retries = max([sum([crawl.time > interval_time_start for crawl in crawls_host]) for crawls_host in self.hosts.values()])

        return retries

########################################################################
# TODO:                                                                #
#   - create agent to resolve host names                               #
#   - create agent to crawl host names                                 #
#   - create agent to recrawl host names                               #
#   - create agent to retry crawl host names                           #
#   - create table for host name resolution                            #
#   - create table for crawl host names, look up if in last hour crawl #
########################################################################

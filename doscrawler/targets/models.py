#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the targets for the DoS crawler.

"""

from faust import Record
from typing import List, Dict
from datetime import datetime
from doscrawler.crawls.models import Crawl
from doscrawler.hosts.models import Host


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
    start_posix_time: datetime
    latest_posix_time: datetime
    start_corsaro_interval: datetime


class Target(Record):
    """
    Target model class
    """

    ip: str
    start: str
    target_lines: List[TargetLine]
    hosts: Dict[Host, List[Crawl]]


########################################################################
# TODO:                                                                #
#   - create agent to resolve host names                               #
#   - create agent to crawl host names                                 #
#   - create agent to recrawl host names                               #
#   - create agent to retry crawl host names                           #
#   - create table for host name resolution                            #
#   - create table for crawl host names, look up if in last hour crawl #
########################################################################

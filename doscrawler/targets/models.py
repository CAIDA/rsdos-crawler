#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the targets for the DoS crawler.

"""

import itertools
from faust import Record
from typing import List, Dict
from datetime import datetime, timedelta, timezone
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


class Target(Record, coerce=True, serializer="json"):
    """
    Target model class
    """

    ip: str
    start_time: datetime
    latest_time: datetime
    target_lines: List[TargetLine]
    hosts: Dict[str, List[Crawl]] = {}

    def is_mergable_target_line(self, target_line):
        """
        Checks if new target line can be merged with target

        :param target_line: [doscrawler.targets.models.TargetLine] target line to be checked if can be merged with target
        :return: [bool] boolean if target line is mergable with target
        """

        latest_merge_time = self.latest_time + timedelta(seconds=settings.TARGET_MERGE_INTERVAL)
        merge_time = target_line.start_time

        if latest_merge_time > merge_time:
            return True

        return False

    def get_time_latest_crawl(self):
        """
        Get time of latest crawl of any of the hosts of the target

        :return: [datetime.datetime]
        """

        crawls_all = [crawl.time for crawl in itertools.chain.from_iterable(self.hosts.values())]

        if crawls_all:
             # target has already been crawled
             return max(crawls_all)
        else:
            # target has not yet been crawled
            return

    def get_ttl(self, time=None):
        """
        Get time to live for target and how long target is tracked

        :param time: [datetime.datetime] time stamp to which time to live should refer to, default is current time
        :return: [float] time to live in seconds, can be negative
        """

        # get end time by latest time and target ttl in settings
        end_time = self.latest_time + timedelta(seconds=settings.TARGET_TTL)

        if not time:
            # get remaining time without time stamp
            current_time = datetime.now(timezone.utc)
            remaining_time = (end_time - current_time).total_seconds()
        else:
            # get ramaining time with time stamp
            remaining_time = (end_time - time).total_seconds()

        return remaining_time

    def get_time_next_crawl(self, crawl_type):
        """
        Get time to crawl target for the next time according to the type of crawl

        :param crawl_type: [str] type of crawl to be made, either "retry" or "recrawl"
        :return: [datetime.datetime] datetime when next crawl of specified type can be made
        """

        if crawl_type == "retry":
            # time should be computed for retry of target
            # get numbers of failed crawls in recent interval
            interval_start = datetime.now(timezone.utc) - timedelta(seconds=settings.CRAWL_REPEAT_INTERVAL)
            interval_crawls_failed = [sum([host_crawl.time > interval_start and host_crawl.status == "failed" for host_crawl in host_crawls]) for host_crawls in self.hosts.values()]

            if interval_crawls_failed:
                # target has already been crawled
                # get maximum number of crawls on any hosts of the target
                interval_crawls = max(interval_crawls_failed)

                if interval_crawls == 0:
                    # no crawls on target have failed
                    # return no retry
                    return
                elif interval_crawls > settings.CRAWL_RETRIES:
                    # target has already been crawled more than maximum number of retries
                    # return no retry
                    return
                else:
                    # target has failed crawls and has not yet been crawled more than maximum number of retries
                    # get time of latest crawl
                    time_latest = self.get_time_latest_crawl()

                    # get time of next crawl
                    time_backoff = 2 ** (interval_crawls - 1) * settings.CRAWL_RETRIES_BACKOFF
                    time_retry = time_latest + timedelta(seconds=time_backoff)

                    # verify time in ttl
                    if self.get_ttl(time=time_retry) < 0:
                        # at time of retry the target will not be alive anymore
                        # return no retry
                        return

                    return time_retry
            else:
                # target has not yet been crawled
                # get current time to crawl
                time_retry = datetime.now(timezone.utc)

                return time_retry

        elif crawl_type == "recrawl":
            # time should be computed for recrawl of target
            # get time of latest crawl
            time_latest = self.get_time_latest_crawl()

            if time_latest:
                # target has already been crawled
                # get time of next crawl
                time_recrawl = time_latest + timedelta(seconds=settings.CRAWL_REPEAT_INTERVAL)

                # verify time in ttl
                if self.get_ttl(time=time_recrawl) < 0:
                    # at time of recrawl the target will not be alive anymore
                    # return no recrawl
                    return

                return time_recrawl
            else:
                # target has not yet been crawled
                # get current time to recrawl
                time_recrawl = datetime.now(timezone.utc)

                return time_recrawl

        else:
            raise ValueError("Crawl type must either be retry of recrawl.")

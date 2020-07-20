#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the targets for the DoS crawler.

"""

import base64
import gzip
import itertools
from io import BytesIO
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

    @property
    def is_ready_crawl(self):
        """
        Check if target is ready to be crawled

        :return: [bool] target is ready to be crawled
        """

        current_time = datetime.now(timezone.utc)
        next_crawl_time, _ = self.get_next_crawl()

        if next_crawl_time <= current_time:
            return True

        return False

    @property
    def is_alive(self):
        """
        Check if target is alive

        :return: [bool] target is alive
        """

        time_current = datetime.now(timezone.utc)

        if self.get_ttl(time=time_current) > 0:
            return True

        return False

    def is_mergable_target_line(self, target_line):
        """
        Checks if new target line can be merged with target

        :param target_line: [doscrawler.targets.models.TargetLine] target line to be checked if can be merged with target
        :return: [bool] target line can be merged with target
        """

        if self.ip == target_line.target_ip:
            latest_merge_time = self.latest_time + timedelta(seconds=settings.TARGET_MERGE_INTERVAL)

            if latest_merge_time >= target_line.start_time:
                return True

        return False

    def get_decoded_dict(self):
        """
        Get dictionary with target and its decoded crawls, used for dumps
        :return: [dict] dictionary of target
        """

        target_dict = self.asdict()

        # prepare nested fields in dictionary
        # uncompress crawls
        target_dict["hosts"] = {host: sorted([{"record": gzip.GzipFile(fileobj=BytesIO(base64.b64decode(crawl.record))).read().decode("utf-8"), "status": crawl.status, "time": crawl.time} for crawl in crawls], key=lambda crawl: crawl.get("time")) for host, crawls in sorted(self.hosts.items())}
        target_dict["target_lines"] = sorted([target_line.asdict() for target_line in self.target_lines], key=lambda target_line: target_line.get("latest_time"))

        return target_dict

    def get_ttl(self, time=None):
        """
        Get time to live for target and how long target is tracked

        :param time: [datetime.datetime] time stamp to which time to live should refer to, default is current time
        :return: [float] time to live in seconds, can be negative
        """

        if not time:
            time = datetime.now(timezone.utc)

        end_time = self.latest_time + timedelta(seconds=settings.TARGET_TTL)
        remaining_time = (end_time - time).total_seconds()

        return remaining_time

    def get_time_latest_crawl(self, host_names=None):
        """
        Get time of latest crawl of any of the hosts of the target

        :param host_names: [list] list of host names to be checked for next crawl, default is to consider all host names
        :return: [datetime.datetime] time of latest crawl according to host names
        """

        if not host_names:
            host_names = self.hosts.keys()

        host_crawls = [self.hosts.get(host_name) for host_name in host_names]
        host_crawls_time = [crawl.time for crawl in itertools.chain.from_iterable(host_crawls)]

        if host_crawls_time:
            return max(host_crawls_time)

        return

    def get_time_initial_crawl(self, host_names=None):
        """
        Get time of initial crawl of any of the hosts of the target

        :param host_names: [list] list of host names to be checked for next crawl, default is to consider all host names
        :return: [datetime.datetime] time of initial crawl according to host names
        """

        if not host_names:
            host_names = self.hosts.keys()

        host_crawls = [self.hosts.get(host_name) for host_name in host_names]
        host_crawls_time = [crawl.time for crawl in itertools.chain.from_iterable(host_crawls)]

        if host_crawls_time:
            return min(host_crawls_time)

        return

    def get_next_crawl(self, host_names=None):
        """
        Get time and type of next crawl according to host names of target

        :param host_names: [list] list of host names to be checked for next crawl, default is to consider all host names
        :return: [datetime.datetime] datetime when next crawl can be made
        :return: [str] type of crawl of next crawl, e.g. "retry", "recrawl"
        """

        if not host_names:
            host_names = self.hosts.keys()

            if not host_names:
                # check if host names still empty
                # no host names to crawl
                return None, None

        # get number of crawls
        host_names_crawls_num = min([len(self.hosts.get(host_name)) for host_name in host_names])

        if not host_names_crawls_num:
            # target has not yet been crawled
            # return crawl
            next_crawl_type = "crawl"
            next_crawl_time = self.start_time

        else:
            # target has already been crawled
            # get if any most recent crawls failed
            host_names_crawls_failed = any([max(self.hosts.get(host_name), key=lambda crawl: crawl.time).is_success is False for host_name in host_names])

            if not host_names_crawls_failed:
                # all most recent crawls on hosts succeeded
                # return repeat
                next_crawl_type = "repeat"
                next_crawl_time = self.get_time_initial_crawl(host_names=host_names) + timedelta(seconds=settings.CRAWL_REPEAT_INTERVAL)

            else:
                # any of the most recent crawls on hosts failed
                if host_names_crawls_num <= settings.CRAWL_RETRIES:
                    # not yet been crawled more than maximum number of retries
                    if host_names_crawls_num == 1:
                        # return first retry
                        next_crawl_type = "retry-first"
                    else:
                        # return retry
                        next_crawl_type = "retry"
                    # compute time for retry
                    next_crawl_time = self.get_time_latest_crawl(host_names=host_names) + timedelta(seconds=2**(host_names_crawls_num-1)*settings.CRAWL_RETRIES_BACKOFF)

                else:
                    # already crawled more than maximum number of retries
                    # return repeat
                    next_crawl_type = "repeat"
                    # compute time for repeat
                    next_crawl_time = self.get_time_initial_crawl(host_names=host_names) + timedelta(seconds=settings.CRAWL_REPEAT_INTERVAL)

        if self.get_ttl(time=next_crawl_time) > 0:
            # target will still be alive at next crawl
            return next_crawl_time, next_crawl_type

        else:
            # target will not be alive at next crawl anymore
            return None, None

    def get_next_crawl_hosts(self, host_names=None):
        """
        Get host names for next crawl according to host names

        :param host_names: [list] list of host names to be checked for next crawl, default is to consider all host names
        :return: [list] list of host names which need to be recrawled on next crawl
        :return: [str] type of crawl of next crawl, e.g. "retry", "recrawl"
        """

        if not host_names:
            host_names = self.hosts.keys()

        # get next crawl type of all hosts
        _, next_crawl_type = self.get_next_crawl(host_names=host_names)

        if next_crawl_type:
            # any host needs crawl
            if next_crawl_type == "crawl":
                # any host needs initial crawl
                # get hosts
                next_crawl_hosts = [host_name for host_name in host_names if self.get_next_crawl(host_names=[host_name])[1] == "crawl"]
            elif next_crawl_type == "retry-first":
                # any host needs to retry first
                # get hosts
                next_crawl_hosts = [host_name for host_name in host_names if self.get_next_crawl(host_names=[host_name])[1] == "retry-first"]
            elif next_crawl_type == "retry":
                # any host needs to retry
                # get hosts
                next_crawl_hosts = [host_name for host_name in host_names if self.get_next_crawl(host_names=[host_name])[1] == "retry"]
            elif next_crawl_type == "repeat":
                # all host names need to repeat
                next_crawl_hosts = host_names
            else:
                # no host needs any crawl
                next_crawl_hosts = []
        else:
            # no host needs any crawl
            next_crawl_hosts = []

        return next_crawl_hosts, next_crawl_type

    def reset_crawls(self):
        """
        Reset crawls of hosts

        :return:
        """

        self.hosts = {host: [] for host in self.hosts.keys()}

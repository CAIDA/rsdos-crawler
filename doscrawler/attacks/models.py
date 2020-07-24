#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models for the attacks in the DoS crawler.

"""

import gzip
import base64
from io import BytesIO
from faust import Record
from typing import List
from datetime import datetime, timedelta, timezone
from simple_settings import settings
from doscrawler.crawls.models import Crawl


class AttackVector(Record, coerce=True, serializer="json"):
    """
    Attack vector model class
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


class Attack(Record, coerce=True, serializer="json"):
    """
    Attack model class
    """

    ip: str
    start_time: datetime
    latest_time: datetime
    attack_vectors: List[AttackVector] = []
    hosts: List[str] = []
    crawls: List[Crawl] = []

    @property
    def is_alive(self):
        """
        Check if attack is still alive in system and is actively followed

        :return: [bool] attack is alive
        """

        if self.get_ttl() > 0:
            return True

        return False

    @property
    def is_alive_soon(self):
        """
        Check if attack will still be alive in system and is actively followed soon

        :return: [bool] attack will still be alive
        """

        time = datetime.now(timezone.utc) + timedelta(seconds=5)

        if self.get_ttl(time=time) > 0:
            return True

        return False

    @property
    def is_need_crawl(self):
        """
        Check if attack is in need of crawl

        :return: [bool] needs crawl
        """

        time_current = datetime.now(timezone.utc)
        time_next_crawl, _ = self.get_next_crawl()

        if time_next_crawl and time_next_crawl <= time_current:
            return True

        return False

    def is_mergable_attack(self, attack):
        """
        Checks if new attack can be merged with this attack

        :param attack: [doscrawler.attacks.models.Attack] attack to be checked if can be merged with attack
        :return: [bool] attack can be merged with attack
        """

        if self.ip == attack.ip:
            time_soonest_merge = self.start_time - timedelta(seconds=settings.ATTACK_MERGE_INTERVAL)
            time_latest_merge = self.latest_time + timedelta(seconds=settings.ATTACK_MERGE_INTERVAL)

            if time_soonest_merge <= attack.latest_time and time_latest_merge >= attack.start_time:
                return True

        return False

    def get_decoded_dict(self):
        """
        Get dictionary with attack and its decoded crawls for dumps

        :return: [dict] attack as dictionary
        """

        attack_dict = self.asdict()

        # sort attack vector
        attack_dict["attack_vectors"] = sorted(
            [attack_vector.asdict() for attack_vector in self.attack_vectors],
            key=lambda attack_vector: attack_vector.get("start_time")
        )

        # sort and uncompress crawls
        attack_dict["crawls"] = sorted(
            [{
                "host": crawl.host,
                "status": crawl.status,
                "time": crawl.time,
                "record": gzip.GzipFile(fileobj=BytesIO(base64.b64decode(crawl.record))).read().decode("utf-8", errors="ignore")
            } for crawl in self.crawls],
            key=lambda crawl: crawl.get("time")
        )

        return attack_dict

    def get_ttl(self, time=None):
        """
        Get time to live of attack and how long it is still actively followed

        :param time: [datetime.datetime] time stamp to which time to live should refer to, default is current time
        :return: [float] time to live in seconds, can be negative too
        """

        if not time:
            time = datetime.now(timezone.utc)

        time_end = self.latest_time + timedelta(seconds=settings.ATTACK_TTL)
        time_live = (time_end - time).total_seconds()

        return time_live

    def get_time_latest_crawl(self, hosts=None):
        """
        Get time of latest crawl

        :param hosts: [list] list of hosts to be checked for next crawl, default is to consider all hosts
        :return: [datetime.datetime] time of latest crawl of hosts
        """

        if not hosts:
            hosts = self.hosts

        time_crawls = [crawl.time for crawl in self.crawls if crawl.host in hosts]

        if time_crawls:
            return max(time_crawls)

        return None

    def get_time_initial_crawl(self, hosts=None):
        """
        Get time of initial crawl

        :param hosts: [list] list of hosts to be checked for initial crawl, default is to consider all hosts
        :return: [datetime.datetime] time of initial crawl of hosts
        """

        if not hosts:
            hosts = self.hosts

        time_crawls = [crawl.time for crawl in self.crawls if crawl.host in hosts]

        if time_crawls:
            return min(time_crawls)

        return None

    def get_next_crawl(self, hosts=None):
        """
        Get time and type of next crawl

        :param hosts: [list] list of hosts to be checked for next crawl, default is to consider all hosts, but usually
        this function is called on attacks with one host only
        :return: [datetime.datetime] datetime when next crawl can be made
        :return: [str] type of crawl of next crawl, can be "crawl", "retry-first", "retry", "repeat"
        """

        if not hosts:
            hosts = self.hosts

        if hosts:
            # has hosts to crawl
            # get number of crawls
            num_crawls = min([len([crawl for crawl in self.crawls if crawl.host == host]) for host in hosts])

            if not num_crawls:
                # not yet been crawled
                # return crawl
                next_crawl_type = "crawl"
                next_crawl_time = self.start_time

            else:
                # has already been crawled
                # get if any most recent crawl failed
                failed_crawls = any([max([crawl for crawl in self.crawls if crawl.host == host], key=lambda crawl: crawl.time).is_success == False for host in hosts])

                if not failed_crawls:
                    # all most recent crawls on hosts succeeded
                    # return repeat
                    next_crawl_type = "repeat"
                    next_crawl_time = self.get_time_initial_crawl(hosts=hosts) + timedelta(seconds=settings.CRAWL_REPEAT_INTERVAL)

                else:
                    # any of the most recent crawls on hosts failed
                    if num_crawls <= settings.CRAWL_RETRIES:
                        # not yet been crawled more than maximum number of retries
                        if num_crawls == 1:
                            # return first retry
                            next_crawl_type = "retry-first"
                        else:
                            # return retry
                            next_crawl_type = "retry"
                        # compute time for retry
                        next_crawl_time = self.get_time_latest_crawl(hosts=hosts) + timedelta(seconds=2**(num_crawls-1)*settings.CRAWL_RETRIES_BACKOFF)

                    else:
                        # already crawled more than maximum number of retries
                        # return repeat
                        next_crawl_type = "repeat"
                        # compute time for repeat
                        next_crawl_time = self.get_time_initial_crawl(hosts=hosts) + timedelta(seconds=settings.CRAWL_REPEAT_INTERVAL)

            if self.get_ttl(time=next_crawl_time) > 0:
                # attack will still be alive at next crawl
                # return previously defined crawl time and type
                return next_crawl_time, next_crawl_type

        return None, None

    def reset_crawls(self):
        """
        Reset crawls

        :return:
        """

        self.crawls = []

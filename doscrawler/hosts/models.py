#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the hosts for the DoS crawler.

"""
import os
import socket
import random
from typing import List
from datetime import datetime, timezone, timedelta

import psycopg2
from simple_settings import settings
from faust import Record


def init_dns_db():
    cred = {
        'user': os.environ.get("REVERSE_DNS_DB_USER", None),
        'password': os.environ.get("REVERSE_DNS_DB_PASSWORD", None),
        'port': os.environ.get("REVERSE_DNS_DB_PORT", None),
        'host': os.environ.get("REVERSE_DNS_DB_HOST", None),
    }

    assert not any(v is None for v in cred.values())
    return psycopg2.connect(**cred)


# DNS database connection
DNS_DB_CONN = init_dns_db()


def get_names_common_crawl(ip):
    cur = DNS_DB_CONN.cursor()
    cmd = "SELECT * FROM common_crawl where ip='{}'".format(ip)
    cur.execute(cmd)
    return [domain for domain, ip in cur.fetchall()]


def update_lookup_count(ip, source):
    cur = DNS_DB_CONN.cursor()
    dt = datetime.now()
    cmd = f"insert into lookup_count (datetime, ip, datasource) values ('{dt}', '{ip}', '{source}')"
    cur.execute(cmd)
    DNS_DB_CONN.commit()


def get_names_reverse_dns(ip):
    """
    Get names of hosts in host group. Reverse DNS lookup.

    :param ip: [str] IP address used by host group
    :return: [list] host group as list of host names including the IP address itself
    """

    try:
        # get hosts
        hostname, aliaslist, _ = socket.gethostbyaddr(ip)
        names = list(set([hostname] + aliaslist))

    except socket.herror as e:
        # return only ip address on address-related errors
        names = []

    return [n for n in names if n is not None]


class HostGroup(Record, coerce=True, serializer="json"):
    """
    Host model class
    """

    ip: str
    names: List[str]
    time: datetime

    # datasources, order matter
    DATASOURCES = [
        ("common_crawl", get_names_common_crawl),
        ("reverse_dns_lookup", get_names_reverse_dns),
    ]

    @classmethod
    async def create_hostgroup_from_ip(cls, ip):
        """
        Create host group from ip

        :param ip: [str] IP address used by host group
        :return: [doscrawler.hosts.models.HostGroup] created host group from IP address
        """

        host_group = cls(ip=ip, names=cls._get_names(ip=ip), time=datetime.now(timezone.utc))

        return host_group

    @property
    def is_valid(self):
        """
        Check if host group is still valid according to expire interval

        :return: [bool] check if host group is still valid
        """

        expire_time = datetime.now(timezone.utc) - timedelta(seconds=settings.HOST_CACHE_INTERVAL)

        if self.time > expire_time:
            return True

        return False

    @staticmethod
    def _get_names(ip):
        found_source = "none"
        names = []
        for source_name, source_func in HostGroup.DATASOURCES:
            names = source_func(ip)
            if names:
                # use the first datasource that has a match
                found_source = source_name
                break

        if not names:
            # default to use IP has host name
            names = [ip]

        update_lookup_count(ip, found_source)

        if len(names) > settings.HOST_MAX_NUM:
            # hosts exceed number of maximum hosts
            # get random seed
            random.seed(ip)
            # get random sample of hosts
            names = random.sample(names, k=settings.HOST_MAX_NUM)

        return names

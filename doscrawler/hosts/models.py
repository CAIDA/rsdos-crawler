#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the hosts for the DoS crawler.

"""
#  This software is Copyright (c) 2020 The Regents of the University of
#  California. All Rights Reserved. Permission to copy, modify, and distribute this
#  software and its documentation for academic research and education purposes,
#  without fee, and without a written agreement is hereby granted, provided that
#  the above copyright notice, this paragraph and the following three paragraphs
#  appear in all copies. Permission to make use of this software for other than
#  academic research and education purposes may be obtained by contacting:
#
#  Office of Innovation and Commercialization
#  9500 Gilman Drive, Mail Code 0910
#  University of California
#  La Jolla, CA 92093-0910
#  (858) 534-5815
#  invent@ucsd.edu
#
#  This software program and documentation are copyrighted by The Regents of the
#  University of California. The software program and documentation are supplied
#  "as is", without any accompanying services from The Regents. The Regents does
#  not warrant that the operation of the program will be uninterrupted or
#  error-free. The end-user understands that the program was developed for research
#  purposes and is advised not to rely exclusively on the program for any reason.
#
#  IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR
#  DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST
#  PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF
#  THE UNIVERSITY OF CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
#  DAMAGE. THE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY WARRANTIES,
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#  FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON AN "AS
#  IS" BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO OBLIGATIONS TO PROVIDE
#  MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
#
#

import logging
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
        logging.info(f"getting host names for IP: {ip} ...")
        for source_name, source_func in HostGroup.DATASOURCES:
            names = source_func(ip)
            if names:
                # use the first datasource that has a match
                logging.info(f"\tfound hostnames using {source_name}: {names}")
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
            logging.info(f"\ttoo many hostnames (len>{settings.HOST_MAX_NUM}), reduced to {len(names)}")

        logging.info(f"return mapping of IP {ip} to hostnames {names}")
        return names

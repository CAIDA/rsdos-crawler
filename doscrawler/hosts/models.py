#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the hosts for the DoS crawler.

"""

import socket
import random
from typing import List
from datetime import datetime, timezone, timedelta
from simple_settings import settings
from faust import Record


class HostGroup(Record, coerce=True, serializer="json"):
    """
    Host model class
    """

    ip: str
    names: List[str]
    time: datetime

    @classmethod
    async def create_hostgroup_from_ip(cls, ip):
        """
        Create host group from ip

        :param ip: [str] IP address used by host group
        :return: [doscrawler.hosts.models.HostGroup] created host group from IP address
        """

        host_group = cls(ip=ip, names=cls._get_names(ip=ip), time=datetime.now(timezone.utc))

        return host_group

    @staticmethod
    def _get_names(ip):
        """
        Get names of hosts in host group

        :param ip: [str] IP address used by host group
        :return: [list] host group as list of host names including the IP address itself
        """

        try:
            # get hosts
            hostname, aliaslist, _ = socket.gethostbyaddr(ip)
            names = list(set([ip, hostname] + aliaslist))

            if len(names) > settings.HOST_MAX_NUM:
                # hosts exceed number of maximum hosts
                # get random seed
                random.seed(ip)
                # get random sample of hosts
                names = random.sample(names, k=settings.HOST_MAX_NUM)

        except socket.herror as e:
            # return only ip address on address-related errors
            names = [ip]

        return names

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

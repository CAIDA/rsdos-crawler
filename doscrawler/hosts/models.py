#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the hosts for the DoS crawler.

"""

import socket
from datetime import datetime, timezone
from faust import Record
from typing import List


class HostGroup(Record, coerce=True, serializer="json"):
    """
    Host model class
    """

    ip: str
    names: List[str]
    time: datetime

    @classmethod
    def create_hostgroup_from_ip(cls, ip):
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
            host_group = list(set([ip, hostname] + aliaslist))
            return host_group
        except socket.herror as e:
            # return only ip address on address-related errors
            return [ip]

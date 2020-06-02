#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Dumps
-----

This module provides the functionalities together with the dumps of the UCSD Telescope DDoS Metadata in the DoS crawler.

NOTE: This code is only temporary, because later no dumps with IP addresses should be read but rather IP addresses
should be sent directly.

"""

import re
import datetime
from itertools import compress
from subprocess import Popen, PIPE


class Dump(object):
    """
    Dump object
    """

    def __init__(self, container=None, start=None, end=None):
        """
        Initialize dump

        :param container: [str] name of swift container, e.g. datasource=ucsd-nt/year=2020/month=5/day=6/ucsd-nt.1588791600.dos.cors.gz, default = None
        :param start: [datetime, str] start date of included containers, if no container provided as argument, e.g. "2020-05-08 00:00:00", default "1970-01-01 00:00:00"
        :param end: [datetime, str] end date of included containers, if no container provided as argument, e.g. "2020-05-09 00:00:00", default current datetime
        """

        if container:
            self.ips = self._get_ips_from_container(container=container)
        elif start or end:
            self.ips = self._get_ips_from_datetime_range(start=start, end=end)

    def _get_ips_from_datetime_range(self, start=None, end=None):
        """
        Get IP addresses of targets from auto detected swift containers in datetime range

        :param start: [datetime, str] start date of included containers, e.g. "2020-05-08 00:00:00", default "1970-01-01 00:00:00"
        :param end: [datetime, str] end date of included containers, e.g. "2020-05-09 00:00:00", default current datetime
        :return: [list] list of IP addresses of targets in container
        """

        if start:
            if not isinstance(start, datetime.datetime):
                start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        else:
            start = datetime.datetime.utcfromtimestamp(0)

        if end:
            if not isinstance(end, datetime.datetime):
                end = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        else:
            end = datetime.datetime.now()

        # prepare list filter
        list_filter = ""
        if start.year == end.year:
            list_filter = "-p datasource=ucsd-nt/year={year}/".format(year=start.year)
            if start.month == end.month:
                list_filter = "-p datasource=ucsd-nt/year={year}/month={month}/".format(year=start.year, month=start.month)
                if start.day == end.day:
                    list_filter = "-p datasource=ucsd-nt/year={year}/month={month}/day={day}/".format(year=start.year, month=start.month, day=start.day)

        # get containers
        args = "swift list data-telescope-meta-dos {list_filter}".format(list_filter=list_filter)
        process = Popen(args=args, stdout=PIPE, shell=True)
        containers = [line.decode("utf-8").strip() for line in process.stdout]

        # filter containers on exact time
        containers_timestamps = [re.search(r"\b\d{10}\b", container) for container in containers]
        containers_datetimes = [datetime.datetime.utcfromtimestamp(int(timestamp.group(0))) if timestamp else None for timestamp in containers_timestamps]
        containers_filter = [True if time and start <= time < end else False for time in containers_datetimes]
        containers = list(compress(containers, containers_filter))

        # collect ips
        ips = []
        for container in containers:
            ips.extend(self._get_ips_from_container(container))

        return ips

    @staticmethod
    def _get_ips_from_container(container):
        """
        Get IP addresses of targets from one swift container

        :param container: name of swift container, e.g. datasource=ucsd-nt/year=2020/month=5/day=6/ucsd-nt.1588791600.dos.cors.gz, default = None
        :return: [list] list of IP addresses of targets in container
        """

        #######################################
        # CAREFUL: cors2ascii output modified #
        #######################################

        args = "cors2ascii swift://data-telescope-meta-dos/{container} | egrep -o '^([0-9]{{1,3}}\.){{3}}[0-9]{{1,3}}\\b'".format(container=container)
        process = Popen(args=args, stdout=PIPE, shell=True)
        ips = [ip.decode("utf-8").strip() for ip in process.stdout]

        return ips

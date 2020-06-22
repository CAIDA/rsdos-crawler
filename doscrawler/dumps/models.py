#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models for the dumps of the DoS crawler.

"""

import os
import json
import base64
import gzip
from io import BytesIO
from faust import Record
from datetime import datetime
from warcio.timeutils import datetime_to_iso_date
from simple_settings import settings
from doscrawler.targets.models import Target
from doscrawler.targets.tables import target_table
from doscrawler.targets.topics import change_target_topic


class Dump(Record):
    """
    Dump model class
    """

    name: str
    time: datetime

    @classmethod
    def create_dump_with_time(cls, time):
        """
        Create dump instance with specific time

        :param time: [datetime.datetime] time at which dump is created
        :return: [doscrawler.dumps.models.Dump] dump instance
        """

        dump = cls(name=cls._get_name(time=time), time=time)

        return dump

    @staticmethod
    def _get_time_str(time):
        """
        Get time string

        :param time: [datetime.datetime] datetime to be transformed in string
        :return: [str] transformed datetime string
        """

        time_str = datetime_to_iso_date(the_datetime=time)

        return time_str

    def _get_name(self, time):
        """
        Get name of dump with time

        :param time: [datetime.datetime] time at which dump is created
        :return: [str] name of dump
        """

        time_str = self._get_time_str(time=time)
        name = f"data-telescope-crawler-dos-{time_str}"

        return name

    def _get_default_dir(self):
        """
        Get default directory where to save dump

        :return: [os.path] directory where to save dump
        """

        dir = os.path.join(settings.DUMP_DIR, f"{self.name}.json.gz")

        return dir

    def _get_targets(self):
        """
        Get targets for dump

        :return: [list] list of targets to be saved in dump
        """

        targets = []

        # get all targets whose time to live has expired
        for target in target_table:
            # for every target in the target table
            if target.get_ttl(time=self.time) <= 0:
                # time to live has expired
                # prepare uncompressed hosts
                target_uncomp_hosts = {host: [gzip.GzipFile(fileobj=BytesIO(base64.b64decode(crawl))).read().decode("utf-8") for crawl in crawls] for host, crawls in target.hosts.items()}

                # create uncompressed target
                target_uncomp = Target(ip=target.ip, start_time=target.start_time, latest_time=target.latest_time, target_lines=target.target_lines, hosts=target_uncomp_hosts)

                # append uncompressed target to dump of targets
                targets.append(target_uncomp.dumps())

                # send target to change target topic for deletion
                await change_target_topic.send(key=f"delete/{target.ip}/{target.start_time}", value=target)

        return targets

    def write(self, dir=None):
        """
        Write dump in file

        :param dir: [str, os.path] file directory and name where to write dump
        :return: [float] time to live in seconds, can be negative
        """

        if not dir:
            dir = self._get_default_dir()

        # prepare dump as dictionary
        dump = {
            "name": self.name,
            "time": self._get_time_str(),
            "targets": self._get_targets()
        }

        # write dump as gzip
        with gzip.GzipFile(filename=dir, mode="w", compresslevel=settings.DUMP_COMPRESS_LEVEL) as file:
            file.write(bytes(json.dumps(dump), encoding="utf-8"))

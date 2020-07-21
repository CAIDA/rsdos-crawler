#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models for the dumps of the DoS crawler.

"""

import os
import json
import gzip
from faust import Record
from datetime import datetime, timezone, timedelta
from simple_settings import settings
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

    @property
    def is_valid(self):
        """
        Check if dump must still be considered according to expire interval

        :return: [bool] dump is still valid
        """

        expire_time = datetime.now(timezone.utc) - timedelta(seconds=settings.RETENTION_INTERVAL)

        if self.time > expire_time:
            return True

        return False

    @staticmethod
    def _get_name(time):
        """
        Get name of dump with time

        :param time: [datetime.datetime] time at which dump is created
        :return: [str] name of dump
        """

        time_str = time.strftime("%Y%m%d%H%M")
        name = f"data-telescope-crawler-dos-{time_str}"

        return name

    @staticmethod
    def json_serializer(field):
        """
        Serialize field in dictionary for JSON
        """

        if isinstance(field, datetime):
            return field.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def _get_default_dir(self):
        """
        Get default directory where to save dump

        :return: [os.path] directory where to save dump
        """

        dir = os.path.join(settings.DUMP_DIR, f"{self.name}.json.gz")

        os.makedirs(settings.DUMP_DIR, exist_ok=True)

        return dir

    async def _get_targets(self):
        """
        Get targets for dump

        :return: [list] list of targets to be saved in dump
        """

        targets = []

        # get all targets whose time to live has expired
        for target_key in list(target_table.keys()):
            # for each target
            # look up target in table
            target = target_table[target_key]

            if target and not target.is_alive:
                # target still exists in table and its time to live has expired
                # get decoded target as dictionary
                target_dict = target.get_decoded_dict()
                # append uncompressed target to dump of targets
                targets.append(target_dict)
                # reduce target for smaller message sizes
                target.reset_crawls()
                # send target to change target topic for deletion
                await change_target_topic.send(key=f"delete/{target.ip}/{target.start_time}", value=target)

        return targets

    async def write(self, dir=None):
        """
        Write dump in file

        :param dir: [str, os.path] file directory and name where to write dump
        :return: [str] name of written dump
        :return: [str] time of written dump
        :return: [int] number of targets in written dump
        """

        if not dir:
            dir = self._get_default_dir()

        # prepare dump as dictionary
        dump = {
            "name": self.name,
            "time": self.time,
            "targets": await self._get_targets()
        }

        # write dump as gzip
        with gzip.GzipFile(filename=dir, mode="w", compresslevel=settings.DUMP_COMPRESS_LEVEL) as file:
            file.write(bytes(json.dumps(dump, default=self.json_serializer), encoding="utf-8"))

        return dump["name"], dump["time"], len(dump["targets"])

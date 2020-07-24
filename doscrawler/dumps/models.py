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
from doscrawler.attacks.models import Attack
from doscrawler.attacks.tables import attack_table
from doscrawler.attacks.topics import change_attack_topic


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

    async def _get_attacks(self):
        """
        Get attacks for dump

        :return: [list] list of attacks to be saved in dump
        """

        attacks = []

        for attack_key in list(attack_table.keys()):
            # look up attack in attack table
            attack = attack_table[attack_key]

            if attack and attack.get_ttl() <= 0:
                # attack still exists in table and its time to live has expired
                # get decoded attack as dictionary
                attack_dict = attack.get_decoded_dict()
                # append dictionary to dump of attacks
                attacks.append(attack_dict)
                # get attack to send to change attack topic for deletion
                attack = Attack(ip=attack.ip, start_time=attack.start_time, latest_time=attack.latest_time)
                # send attack to change attack topic for deletion
                await change_attack_topic.send(key=f"delete/{attack.ip}/{attack.start_time}", value=attack)

        return attacks

    async def write(self, dir=None):
        """
        Write dump in file

        :param dir: [str, os.path] file directory and name where to write dump
        :return: [str] name of written dump
        :return: [str] time of written dump
        :return: [int] number of attacks in written dump
        """

        if not dir:
            dir = self._get_default_dir()

        # prepare dump as dictionary
        dump = {
            "name": self.name,
            "time": self.time,
            "attacks": await self._get_attacks()
        }

        # get descriptions
        num_attacks = len(dump["attacks"])
        num_hosts = sum([len(attack["hosts"]) for attack in dump["attacks"]])
        num_crawls = sum([len(attack["crawls"]) for attack in dump["attacks"]])

        # write dump as gzip
        with gzip.GzipFile(filename=dir, mode="w", compresslevel=settings.DUMP_COMPRESS_LEVEL) as file:
            file.write(bytes(json.dumps(dump, default=self.json_serializer), encoding="utf-8"))

        return self.name, self.time, num_attacks, num_hosts, num_crawls

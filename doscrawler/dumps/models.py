#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models for the dumps of the DoS crawler.

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

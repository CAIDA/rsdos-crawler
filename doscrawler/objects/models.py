#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the objects in the Swift containers for the DoS crawler.

"""

import re
from faust import Record
from subprocess import Popen, PIPE
from datetime import datetime, timedelta, timezone


class Object(Record, coerce=True, serializer="json"):
    """
    Object model class
    """

    name: str
    container: str
    time: datetime

    @classmethod
    def create_object_from_names(cls, name, container):
        """
        Create object instance from object name and container name

        :param name: [str] name of object
        :param container: [str] name of container where object is inside
        :return: [doscrawler.objects.models.Object] valid object with name, container and time
        """

        object = cls(name=name, container=container, time=cls._get_time(name=name))

        return object

    def get_target_lines(self):
        """
        Get target lines from object

        :return: [list] list of target lines as dictionaries
        """

        # get lines from object
        args = f"cors2ascii swift://{self.container}/{self.name}"
        process = Popen(args=args, stdout=PIPE, shell=True)
        lines = [line.decode("utf-8").strip() for line in process.stdout]

        # get corsaro start time
        start_corsaro_interval = self._get_corsaro_start_time(lines=lines)

        if not start_corsaro_interval:
            raise Exception(
                f"Object {self.container}/{self.name} has a problem because the start corsaro interval could not be " \
                f"found. The target lines from the object could not be processed."
            )

        # get target lines
        target_lines = self._get_target_lines(lines=lines, start_corsaro_interval=start_corsaro_interval)

        return target_lines

    def is_in_interval(self, start, end):
        """
        Check if object is in time interval between start and end

        :param start: [datetime.datetime] date time when interval begins, e.g. datetime.datetime.now() for now
        :param end: [datetime.datetime] date time when interval ends, e.g. ... for yesterday
        :return:
        """

        in_interval = True if start >= self.time > end else False

        return in_interval

    @staticmethod
    def _get_time(name):
        """
        Get time of object from its name

        :param name: [str] name of object
        :return: [datetime.datetime] time of object in utc
        """

        time = re.search(r"\b\d{10}\b", name)
        time = int(time.group(0))
        time = datetime.fromtimestamp(time, timezone.utc)

        return time

    @staticmethod
    def _get_corsaro_start_time(lines):
        """
        Get corsaro start time from lines in object

        :param lines: [list] list of lines in object, each line is one element in the list
        :return: [datetime.datetime] corsaro start time of object in utc
        """

        corsaro_start_time_pattern = re.compile(r"^# CORSARO_INTERVAL_START.*?(\b\d{10}\b)$")

        for line in lines:
            line_match = corsaro_start_time_pattern.match(line)
            if line_match:
                # parse time stamp
                start_corsaro_interval = int(line_match.group(1))
                start_corsaro_interval = datetime.fromtimestamp(start_corsaro_interval, timezone.utc)
                # subtract time difference of 4 minutes
                start_corsaro_interval -= timedelta(minutes=4)

                return start_corsaro_interval

        return

    @staticmethod
    def _get_target_lines(lines, start_corsaro_interval):
        """
        Get target lines from line sin object

        :param lines: [list] list of lines in object, each line is one element in the list
        :param start_corsaro_interval: [datetime.datetime] corsaro start time of object in utc
        :return: [list] list of target lines as dictionaries
        """

        # beautiful regex
        target_line_pattern = re.compile(r"^(\d+(?:\.\d+){3}),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),([\d\.]+),([\d\.]+)$")

        target_lines = []

        for line in lines:
            line_match = target_line_pattern.match(line)
            if line_match:
                # parse target line
                target_line = {}
                target_line["target_ip"] = str(line_match.group(1))
                target_line["nr_attacker_ips"] = int(line_match.group(2))
                target_line["nr_attacker_ips_in_interval"] = int(line_match.group(3))
                target_line["nr_attacker_ports"] = int(line_match.group(4))
                target_line["nr_target_ports"] = int(line_match.group(5))
                target_line["nr_packets"] = int(line_match.group(6))
                target_line["nr_packets_in_interval"] = int(line_match.group(7))
                target_line["nr_bytes"] = int(line_match.group(8))
                target_line["nr_bytes_in_interval"] = int(line_match.group(9))
                target_line["max_ppm"] = int(line_match.group(10))
                target_line["start_time"] = datetime.fromtimestamp(float(line_match.group(11)), timezone.utc)
                target_line["latest_time"] = datetime.fromtimestamp(float(line_match.group(12)), timezone.utc)
                target_line["start_corsaro_interval"] = start_corsaro_interval
                # append target line
                target_lines.append(target_line)

        return target_lines

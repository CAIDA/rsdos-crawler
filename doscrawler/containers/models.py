#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the SWIFT containers for the DoS crawler.

"""

import datetime
from faust import Record
from itertools import compress
from subprocess import Popen, PIPE
from simple_settings import settings
from doscrawler.objects.models import Object


class Container(Record):
    """
    Container model class
    """

    name: str = "data-telescope-meta-dos"

    def get_latest_objects(self, interval):
        """
        Get latest objects from container

        :param interval: [int, datetime.timedelta] time to look back for objects from now, e.g. 3,600 for all objects in
        last hour
        :return: [list] list of objects
        """

        # prepare interval
        if not isinstance(interval, datetime.timedelta):
            interval = datetime.timedelta(seconds=interval)

        # prepare start and end time of interval
        start = datetime.datetime.now(settings.TIMEZONE).replace(tzinfo=None)
        end = start - interval

        # prepare filter by start and end time (precise up until day)
        list_filter = ""
        if start.year == end.year:
            list_filter = f"-p datasource=ucsd-nt/year={start.year}/"
            if start.month == end.month:
                list_filter = f"-p datasource=ucsd-nt/year={start.year}/month={start.month}/"
                if start.day == end.day:
                    list_filter = f"-p datasource=ucsd-nt/year={start.year}/month={start.month}/day={start.day}/"

        # get objects with list filter
        args = f"swift list {self.name} {list_filter}"
        process = Popen(args=args, stdout=PIPE, shell=True)
        object_names = [line.decode("utf-8").strip() for line in process.stdout]

        # get static objects for testing
        #names = [
        #    "swift://data-telescope-meta-dos/datasource=ucsd-nt/year=2020/month=5/day=8/ucsd-nt.1588953600.dos.cors.gz",
        #    "swift://data-telescope-meta-dos/datasource=ucsd-nt/year=2020/month=5/day=9/ucsd-nt.1588959000.dos.cors.gz"
        #]

        # parse objects
        objects = [Object.create_object_from_names(name=object_name, container=self.name) for object_name in object_names]

        # filter objects by exact time (precise until millisecond)
        objects_filter = [object.is_in_interval(start=start, end=end) for object in objects]
        objects = list(compress(objects, objects_filter))

        return objects

######################################
# TODO:                              #
#   - remove code for static objects #
######################################

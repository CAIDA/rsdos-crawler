#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the SWIFT containers for the DoS crawler.

"""

from faust import Record
from itertools import compress
from subprocess import Popen, PIPE
from datetime import datetime, timedelta, timezone
from doscrawler.objects.models import Object


class Container(Record, serializer="json"):
    """
    Container model class
    """

    name: str

    def get_objects(self, interval):
        """
        Get latest objects from container

        :param interval: [int, datetime.timedelta] time to look back for objects from now, e.g. 3600 for all objects in
        last hour
        :return: [list] list of objects
        """

        # prepare interval
        if not isinstance(interval, timedelta):
            interval = timedelta(seconds=interval)

        # prepare start and end time of interval
        start = datetime.now(timezone.utc)
        end = start - interval

        # prepare filter by start and end time (precise up until day)
        list_filter = ""
        if start.year == end.year:
            list_filter = f"-p datasource=ucsd-nt/year={start.year}/"
            if start.month == end.month:
                list_filter = f"-p datasource=ucsd-nt/year={start.year}/month={start.month}/"
                if start.day == end.day:
                    list_filter = f"-p datasource=ucsd-nt/year={start.year}/month={start.month}/day={start.day}/"

        ################################################################################################################
        # TODO: use non-random objects                                                                                 #
        ################################################################################################################

        ## get objects with list filter
        #args = f"swift list {self.name} {list_filter}"
        #process = Popen(args=args, stdout=PIPE, shell=True)
        #object_names = [line.decode("utf-8").strip() for line in process.stdout]
        ## parse objects
        #objects = [Object.create_object_from_names(name=object_name, container=self.name) for object_name in object_names]

        ################################################################################################################

        # create random object
        objects = [Object.create_random_object(container=self.name)]

        ################################################################################################################

        # filter objects by exact time (precise until millisecond)
        objects_filter = [object.is_in_interval(start=start, end=end) for object in objects]
        objects = list(compress(objects, objects_filter))

        return objects

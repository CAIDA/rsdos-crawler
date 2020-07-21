#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Services
------

This module defines the services of the objects in the Swift containers for the DoS crawler.

"""

import logging
from mode import Service
from simple_settings import settings
from doscrawler.app import app
from doscrawler.objects.tables import object_table
from doscrawler.objects.topics import change_object_topic


@app.service
class ObjectService(Service):
    """
    Object service
    """

    async def on_start(self):
        """
        Process when service is started

        :return:
        """

        logging.info("Service to maintain objects is starting.")

    async def on_stop(self):
        """
        Process when service is stopped

        :return:
        """

        logging.info("Service to maintain objects is stopping.")

    @Service.timer(settings.OBJECT_CLEAN_TIMER)
    async def _clean_objects(self):
        """
        Clean objects which will not be considered anymore

        :return:
        """

        logging.info("Service to maintain objects is starting to clean objects.")

        for object_key in list(object_table.keys()):
            # for each object
            # look up object in table
            object = object_table[object_key]

            if object and not object.is_valid:
                # for each expired object
                # send object to change object topic for deletion
                await change_object_topic.send(key=f"delete/{object.container}/{object.name}", value=object)

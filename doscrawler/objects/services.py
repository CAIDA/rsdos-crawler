#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Services
------

This module defines the services of the objects in the Swift containers for the DoS crawler.

"""

import logging
from mode import Service
from datetime import datetime, timedelta, timezone
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

        # get clean time
        clean_time = datetime.now(timezone.utc) - timedelta(seconds=settings.CONTAINER_GET_OBJECTS_INTERVAL)

        for object_key, object in object_table.items():
            if object.time < clean_time:
                # for each expired object
                # send object to change object topic for deletion
                await change_object_topic.send(key=f"delete/{object.container}/{object.name}", value=object)

        logging.info(f"Service to maintain objects has send the objects for deletion.")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Services
--------

This module defines the services on the Swift containers for the DoS crawler.

"""

import logging
from mode import Service
from simple_settings import settings
from doscrawler.app import app
from doscrawler.containers.models import Container
from doscrawler.objects.topics import change_object_topic


@app.service
class StreamContainer(Service):
    """
    Stream container service
    """

    async def on_start(self):
        """
        Process when service is started

        :return:
        """

        logging.info("Service to stream container is starting.")

    async def on_stop(self):
        """
        Process when service is stopped

        :return:
        """

        logging.info("Service to stream container is stopping.")

    @Service.timer(settings.CONTAINER_GET_OBJECTS_TIMER)
    async def _get_objects(self, interval=settings.CONTAINER_GET_OBJECTS_INTERVAL):
        """
        Get latest objects periodically from container

        :param interval: [int, datetime.timedelta] time to look back for objects from now, e.g. 3,600 for all objects in
        last hour, default is taken from variable CONTAINER_GET_OBJECTS_INTERVAL in settings
        :return:
        """

        logging.info("Service to stream container is starting to get latest objects.")

        # get latest objects from container
        objects = Container().get_objects(interval=interval)

        for object in objects:
            # for each recent object in container
            # send object to change object topic
            await change_object_topic.send(key=f"add/{object.container}/{object.name}", value=object)

        logging.info(f"Service to stream container has sent {len(objects)} objects to the object topic.")

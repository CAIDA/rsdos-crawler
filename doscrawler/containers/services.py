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
    async def _get_objects(self, container=settings.CONTAINER_NAME, interval=settings.CONTAINER_GET_OBJECTS_INTERVAL):
        """
        Get latest objects periodically from container

        :param container: [str] name of container where objects should be taken from, default is taken from variable
        CONTAINER_NAME in settings
        :param interval: [int, datetime.timedelta] time to look back for objects from now, e.g. 3600 for all objects in
        last hour, default is taken from variable CONTAINER_GET_OBJECTS_INTERVAL in settings
        :return:
        """

        # get latest objects from container
        objects = await Container(name=container).get_objects(interval=interval)

        # sort latest objects in ascending order of times
        objects.sort(key=lambda object: object.time)

        for object in objects:
            # for each recent object in container
            # send object to change object topic
            await change_object_topic.send(key=f"add/{object.container}/{object.name}", value=object)

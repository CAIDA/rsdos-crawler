#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Services
------

This module defines the services of the hosts for the DoS crawler.

"""

import logging
from mode import Service
from datetime import datetime, timedelta, timezone
from simple_settings import settings
from doscrawler.app import app
from doscrawler.hosts.tables import host_table
from doscrawler.objects.topics import change_object_topic


@app.service
class HostService(Service):
    """
    Host service
    """

    async def on_start(self):
        """
        Process when service is started

        :return:
        """

        logging.info("Service to maintain hosts is starting.")

    async def on_stop(self):
        """
        Process when service is stopped

        :return:
        """

        logging.info("Service to maintain hosts is stopping.")

    @Service.timer(settings.HOST_CLEAN_TIMER)
    async def _clean_hosts(self):
        """
        Clean hosts which must not be memorized anymore

        :return:
        """

        logging.info("Service to maintain hosts is starting to clean hosts.")

        # get clean time
        clean_time = datetime.now(timezone.utc) - timedelta(seconds=settings.HOST_CACHE_INTERVAL)

        for host_key, host in host_table.items():
            if host.time < clean_time:
                # for each expired host
                # send host to change object topic for deletion
                await change_object_topic.send(key=f"delete/{host.ip}", value=host)

        logging.info(f"Service to maintain hosts has send the hosts for deletion.")

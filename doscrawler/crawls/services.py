#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Services
--------

This module defines the services of the crawls for the DoS crawler.

"""

import logging
from mode import Service
from simple_settings import settings
from doscrawler.app import app
from doscrawler.crawls.topics import change_wait_crawl_topic
from doscrawler.crawls.tables import wait_crawl_table
from doscrawler.crawls.topics import get_crawl_topic


@app.service
class CrawlService(Service):
    """
    Crawl service
    """

    async def on_start(self):
        """
        Process when service is started

        :return:
        """

        logging.info("Service to resend waiting crawls is starting.")

    async def on_stop(self):
        """
        Process when service is stopped

        :return:
        """

        logging.info("Service to resend waiting crawls is stopping.")

    @Service.timer(settings.CRAWL_GET_WAIT_TIMER)
    async def _get_wait_crawls(self):
        """
        Get crawls from targets which are ready to be resend

        :return:
        """

        for target_key in list(wait_crawl_table.keys()):
            # for each target waiting for crawl
            # look up target in table
            target = wait_crawl_table[target_key]

            if target:
                # target still exists in table
                if target.is_ready_crawl:
                    # target has finished waiting
                    # send target to get crawl topic to crawl hosts
                    await get_crawl_topic.send(key=target_key, value=target)
                    # send target to change object topic for deletion
                    await change_wait_crawl_topic.send(key=f"delete/{target_key}", value=target)

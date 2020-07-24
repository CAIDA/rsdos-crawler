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
from doscrawler.crawls.topics import change_crawl_topic, change_wait_crawl_topic
from doscrawler.crawls.tables import crawl_table, wait_crawl_table


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

        logging.info("Service to maintain crawls is starting.")

    async def on_stop(self):
        """
        Process when service is stopped

        :return:
        """

        logging.info("Service to maintain crawls is stopping.")

    @Service.timer(settings.CRAWL_GET_WAIT_TIMER)
    async def _get_wait_crawls(self):
        """
        Get crawls for attacks which are ready to be get crawled

        :return:
        """

        for attack_key in list(wait_crawl_table.keys()):
            # for each attack waiting for crawl
            # look up attack in wait crawl table
            attack = wait_crawl_table[attack_key]

            if attack and attack.is_need_crawl:
                # attack has finished waiting
                # send attack to change wait crawl topic for deletion
                await change_wait_crawl_topic.send(key=f"delete/{attack.ip}/{attack.start_time}/{'/'.join(attack.hosts)}", value=attack)

    @Service.timer(settings.CRAWL_CLEAN_TIMER)
    async def _clean_crawls(self):
        """
        Clean crawls which will not be considered anymore

        :return:
        """

        logging.info("Service to maintain crawls is starting to clean crawls.")

        for crawl_key in list(crawl_table.keys()):
            # for each crawl
            # look up crawl in crawl table
            crawl = crawl_table[crawl_key]

            if crawl and not crawl.is_valid:
                # for each invalid crawl
                # send crawl to change crawl topic for deletion
                await change_crawl_topic.send(key=f"delete/{crawl.host}", value=crawl)

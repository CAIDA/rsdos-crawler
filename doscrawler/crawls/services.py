#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Services
--------

This module defines the services of the crawls for the DoS crawler.

"""

import logging
from simple_settings import settings
from doscrawler.app import app
from doscrawler.crawls.topics import change_crawl_topic, change_wait_crawl_topic
from doscrawler.crawls.tables import crawl_table, wait_crawl_table


@app.timer(settings.CRAWL_GET_WAIT_TIMER, on_leader=True)
async def get_wait_crawls(self):
    """
    Get crawls for attacks which are ready to be get crawled.

    This function triggers by timer with settings.CRAWL_GET_WAIT_TIMER (30s) interval.

    :return:
    """

    logging.info("Service to send waiting attacks which are ready to be crawled again is starting to send attacks.")

    for attack_key in list(wait_crawl_table.keys()):
        # for each attack waiting for crawl
        # look up attack in wait crawl table
        attack = wait_crawl_table[attack_key]

        if attack and attack.finished_wait_crawl:
            # attack has finished waiting
            # send attack to change wait crawl topic for deletion
            await change_wait_crawl_topic.send(key=f"delete/{attack.ip}/{attack.start_time}/{'/'.join(attack.hosts)}", value=attack)


@app.timer(settings.CRAWL_CLEAN_TIMER, on_leader=True)
async def clean_crawls(self):
    """
    Clean crawls which will not be considered anymore.

    This function triggers by timer with settings.CRAWL_CLEAN_TIMER (1 hour) interval.

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

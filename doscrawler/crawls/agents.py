#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents working on the crawls for the DoS crawler.

"""

import asyncio
import itertools
import logging
from datetime import datetime, timedelta
from simple_settings import settings
from doscrawler.app import app
from doscrawler.targets.topics import target_topic
from doscrawler.crawls.topics import get_crawl_topic, update_crawl_topic, wait_retry_crawl_topic, wait_repeat_crawl_topic
from doscrawler.crawls.tables import crawl_table
from doscrawler.crawls.models import Crawl
from doscrawler.targets.models import Target


@app.agent(get_crawl_topic)
async def get_crawls(targets):
    """
    Process targets in order to crawl them

    :param targets:
    :return:
    """

    logging.info("Agent to get crawls from targets is ready to receive targets.")

    async for target in targets:
        # prepare target with failed hosts only
        hosts_failed = {}
        for host in target.hosts.keys():
            # for each host in host group
            # look up host in crawl table
            target_host_crawl = crawl_table[host]
            if target_host_crawl:
                # host of target has already been crawled
                # check timestamp
                expire_time = datetime.now(settings.TIMEZONE).replace(tzinfo=None) - timedelta(seconds=settings.CRAWL_EXPIRE_INTERVAL - 1)
                if target_host_crawl.request_time < expire_time:
                    # renew expired crawl
                    target_host_crawl = Crawl.get_crawl(host=host, ip=target.ip)
                    # append crawl to host of target
                    target.hosts[host].append(target_host_crawl)
                    if target_host_crawl.status == "succeeded":
                        # crawl successful
                        # write crawl in crawl table
                        await update_crawl_topic.send(value=target_host_crawl)
                    else:
                        # crawl unsuccessful
                        # add host to failed hosts
                        hosts_failed[host] = target.hosts[host]
                else:
                    # still valid crawl
                    # append crawl to host of target
                    target.hosts[host].append(target_host_crawl)
            else:
                # host of target has no yet been crawled
                target_host_crawl = Crawl.get_crawl(host=host, ip=target.ip)
                # append crawl to host of target
                target.hosts[host].append(target_host_crawl)
                if target_host_crawl.status == "succeeded":
                    # crawl successful
                    # write crawl in crawl table
                    await update_crawl_topic.send(value=target_host_crawl)
                else:
                    # crawl unsuccessful
                    # add host to failed hosts
                    hosts_failed[host] = target.hosts[host]

        # send to target topic to change target by crawls
        await target_topic.send(value=target)

        if target.get_no_retry_crawl() < settings.CRAWL_RETRIES:
            # all hosts of target have been crawled less than maximum retries
            # prepare target with failed host only
            target_failed = Target(ip=target.ip, start=target.start, target_lines=target.target_lines, hosts=hosts_failed)
            # send to wait retry crawl topic to retry crawl hosts later
            await wait_retry_crawl_topic.send(value=target_failed)

        # check if repeats needed for target
        if target.get_ttl() > settings.CRAWL_REPEAT_INTERVAL:
            # send to wait repeat crawl topic to repeat crawl
            await wait_repeat_crawl_topic.send(value=target)


@app.agent(wait_retry_crawl_topic)
async def wait_retry_crawls(targets):
    """
    Wait for delay before retrying crawling target again

    :param targets:
    :return:
    """

    logging.info("Agent to wait to retry crawls is ready to receive targets.")

    async for target in targets:
        # get delay from latest request time and desired delay in settings
        latest_time = max([crawl.time for crawl in itertools.chain.from_iterable(target.hosts.values())])
        retry_time = latest_time + timedelta(seconds=settings.CRAWL_RETRIES_INTERVAL)
        delay = (retry_time - datetime.now(settings.TIMEZONE).replace(tzinfo=None)).total_seconds()

        # wait
        if delay > 0:
            await asyncio.sleep(delay)

        # send to get crawl topic to crawl target again
        await get_crawl_topic.send(value=target)


@app.agent(wait_repeat_crawl_topic)
async def wait_repeat_crawls(targets):
    """
    Wait for delay before repeating crawling target

    :param targets:
    :return:
    """

    logging.info("Agent to wait to repeat crawls is ready to receive targets.")

    async for target in targets:
        # get delay from latest request time and desired delay in settings
        latest_time = max([crawl.request_time for crawl in itertools.chain.from_iterable(target.hosts.values())])
        retry_time = latest_time + timedelta(seconds=settings.CRAWL_REPEAT_INTERVAL)
        delay = (retry_time - datetime.now(settings.TIMEZONE).replace(tzinfo=None)).total_seconds()

        # wait
        if delay > 0:
            await asyncio.sleep(delay)

        # send to get crawl topic to crawl target
        await get_crawl_topic.send(value=target)


@app.agent(update_crawl_topic)
async def update_crawls(crawls):
    """
    Update crawl table by crawled and changed crawls

    :param crawls:
    :return:
    """

    logging.info("Agent to update crawls is ready to receive crawls.")

    async for crawl in crawls:
        # update host group in host table
        crawl_table[crawl.host] = crawl

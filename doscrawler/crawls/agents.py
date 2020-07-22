#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents working on the crawls for the DoS crawler.

"""

import logging
import aiohttp
from simple_settings import settings
from doscrawler.app import app
from doscrawler.targets.topics import change_target_topic
from doscrawler.crawls.topics import get_crawl_topic, change_crawl_topic, change_wait_crawl_topic
from doscrawler.crawls.tables import crawl_table, wait_crawl_table
from doscrawler.crawls.models import Crawl


@app.agent(get_crawl_topic, concurrency=settings.CRAWL_CONCURRENCY)
async def get_crawls(targets):
    """
    Process targets in order to crawl them

    :param targets: [faust.types.streams.StreamT] stream of targets from get crawl topic
    :return:
    """

    logging.info("Agent to get crawls from targets is ready to receive targets.")

    # share connector for http client which keeps track of simultaneous crawls and dns cache across threads
    connector = aiohttp.TCPConnector(limit=settings.CRAWL_CONCURRENCY, ttl_dns_cache=settings.HOST_CACHE_INTERVAL, force_close=True, enable_cleanup_closed=True)

    async for target_key, target in targets.items():
        # for each target to get crawled
        # get host names for next crawl
        next_crawl_hosts, next_crawl_type = target.get_next_crawl_hosts()

        if next_crawl_type == "repeat":
            # reset crawls on repeat
            target.reset_crawls()

        for host in next_crawl_hosts:
            # for each host name of next crawl
            # look up host in crawl table
            target_host_crawl = crawl_table[host]

            if target_host_crawl and target_host_crawl.is_valid:
                # crawl of host is in table and still valid
                # append crawl to host of target
                target.hosts[host].append(target_host_crawl)

            else:
                # crawl of host is not in table or is not valid anymore
                # get crawl
                target_host_crawl = await Crawl.get_crawl(host=host, ip=target.ip, connector=connector)
                # append crawl to host of target
                target.hosts[host].append(target_host_crawl)
                # write crawl in crawl table
                await change_crawl_topic.send(key=f"add/{host}", value=target_host_crawl)

        # send to change target topic to update target
        await change_target_topic.send(key=f"add/{target.ip}/{target.start_time}", value=target)

        # send to wait crawl topic to retry and repeat crawls
        await change_wait_crawl_topic.send(key=f"add/{target.ip}/{target.start_time}", value=target)


@app.agent(change_wait_crawl_topic, concurrency=1)
async def change_wait_crawls(targets):
    """
    Change wait crawl table in order to wait for retries and repeats

    :param targets: [faust.types.streams.StreamT] stream of targets from change wait crawl topic
    :return:
    """

    logging.info("Agent to change waiting crawls is ready to receive targets.")

    async for target_key, target in targets.items():
        if target_key.startswith("add"):
            # target should be added
            # get next crawl
            target_next_time, target_next_type = target.get_next_crawl()

            if target_next_time:
                # target indeed needs to be retried or recrawled
                # get currently waiting target
                target_current = wait_crawl_table[f"{target.ip}/{target.start_time}"]

                if target_current:
                    # target is already waiting
                    # get next crawl of already waiting target
                    target_current_time, target_current_type = target_current.get_next_crawl()

                    if target_next_type == target_current_type:
                        # both targets have the same type
                        if target_current_time > target_next_time:
                            # next crawl is earlier than current crawl
                            # replace target in table
                            wait_crawl_table[f"{target.ip}/{target.start_time}"] = target

                    else:
                        # targets have different type
                        if target_next_type == "retry-first":
                            # target resets retry counter
                            # replace target in table
                            wait_crawl_table[f"{target.ip}/{target.start_time}"] = target

                else:
                    # target is not yet waiting
                    # add target in table
                    wait_crawl_table[f"{target.ip}/{target.start_time}"] = target

        elif target_key.startswith("delete"):
            # target has to be deleted
            # get target from table and compare
            target_current = wait_crawl_table[f"{target.ip}/{target.start_time}"]

            if target_current:
                # get currently waiting target
                target_current_time, _ = target_current.get_next_crawl()
                # get next target
                target_next_time, _ = target.get_next_crawl()

                if target_current_time == target_next_time:
                    # delete host from host table when has not changed
                    wait_crawl_table.pop(f"{target.ip}/{target.start_time}")


@app.agent(change_crawl_topic)
async def change_crawls(crawls):
    """
    Change crawl table by crawled and changed crawls

    :param crawls: [faust.types.streams.StreamT] stream of crawls from change crawl topic
    :return:
    """

    logging.info("Agent to change crawls is ready to receive crawls.")

    async for crawl_key, crawl in crawls.items():
        if crawl_key.startswith("add"):
            # crawl has to be added
            # update crawl in crawl table
            crawl_table[crawl.host] = crawl

        elif crawl_key.startswith("delete"):
            # crawl has to be deleted
            # look up crawl in crawl table
            crawl_current = crawl_table[crawl.host]

            if crawl_current and crawl_current.time == crawl.time:
                # delete crawl from crawl table
                crawl_table.pop(crawl.host)

        else:
            raise Exception(
                f"Agent to change crawls raised an exception because a crawl has an unknown action. The key of the " \
                f"crawl is {crawl_key}."
            )

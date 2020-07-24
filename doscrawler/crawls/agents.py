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
from doscrawler.crawls.models import Crawl
from doscrawler.attacks.topics import change_attack_topic
from doscrawler.crawls.topics import get_crawl_topic, change_crawl_topic, change_wait_crawl_topic
from doscrawler.crawls.tables import crawl_table, wait_crawl_table


@app.agent(get_crawl_topic, concurrency=settings.CRAWL_CONCURRENCY)
async def get_crawls(attacks):
    """
    Process attacks in order to crawl them

    :param attacks: [faust.types.streams.StreamT] stream of attacks from get crawl topic
    :return:
    """

    logging.info("Agent to get crawls from attacks is ready to receive attacks.")

    # share connector for http client which keeps track of simultaneous crawls and dns cache across threads
    connector = aiohttp.TCPConnector(limit=settings.CRAWL_CONCURRENCY, ttl_dns_cache=settings.HOST_CACHE_INTERVAL, force_close=True, enable_cleanup_closed=True)

    async for attack_key, attack in attacks.items():
        # get next crawl
        # use get_next_crawl_hosts if multiple hosts are sent in an attack
        # for now only attacks with single hosts are forwarded from get hosts agent
        _, next_crawl_type = attack.get_next_crawl()

        if next_crawl_type == "repeat":
            # reset crawls on repeat
            attack.reset_crawls()

        for host in attack.hosts:
            # for each host name of attack
            # for now only attacks with single hosts are forwarded from get hosts agent
            # look up host in crawl table
            attack_host_crawl = crawl_table[host]

            if attack_host_crawl and attack_host_crawl.is_valid:
                # crawl of host is in crawl table and still valid
                if f"{attack_host_crawl.host}/{attack_host_crawl.time}" not in [f"{crawl.host}/{crawl.time}" for crawl in attack.crawls]:
                    # crawl is not in attack yet
                    # append crawl to attack
                    attack.crawls.append(attack_host_crawl)

            else:
                # crawl of host is not in table or is not valid anymore
                # get crawl
                attack_host_crawl = await Crawl.get_crawl(host=host, ip=attack.ip, connector=connector)
                # append crawl to attack
                attack.crawls.append(attack_host_crawl)
                # send crawl to change crawl topic
                await change_crawl_topic.send(key=f"add/{host}", value=attack_host_crawl)

        # send to change attack topic to change attack
        await change_attack_topic.send(key=f"add/{attack.ip}/{attack.start_time}", value=attack)
        # send to wait crawl topic to retry and repeat crawls
        await change_wait_crawl_topic.send(key=f"add/{attack.ip}/{attack.start_time}/{'/'.join(attack.hosts)}", value=attack)


@app.agent(change_wait_crawl_topic, concurrency=1)
async def change_wait_crawls(attacks):
    """
    Change wait crawl table in order to wait for retries and repeats

    :param attacks: [faust.types.streams.StreamT] stream of attacks from change wait crawl topic
    :return:
    """

    logging.info("Agent to change waiting crawls is ready to receive attacks.")

    async for attack_key, attack in attacks.items():
        if attack_key.startswith("add"):
            # attack should be added
            # get next crawl
            attack_next_time, attack_next_type = attack.get_next_crawl()

            if attack_next_time:
                # attack indeed needs to be retried or recrawled
                # get currently waiting attack
                attack_current = wait_crawl_table[f"{attack.ip}/{attack.start_time}/{'/'.join(attack.hosts)}"]

                if attack_current:
                    # attack is already waiting
                    if attack_current.latest_time < attack.latest_time:
                        # new attack is newer than current attack
                        # replace attack in table
                        wait_crawl_table[f"{attack.ip}/{attack.start_time}/{'/'.join(attack.hosts)}"] = attack

                else:
                    # attack is not yet waiting
                    # add attack to wait crawl table
                    wait_crawl_table[f"{attack.ip}/{attack.start_time}/{'/'.join(attack.hosts)}"] = attack

        elif attack_key.startswith("delete"):
            # attack has to be deleted
            # get current attack from wait crawl table
            attack_current = wait_crawl_table[f"{attack.ip}/{attack.start_time}/{'/'.join(attack.hosts)}"]

            if attack_current and attack_current.is_need_crawl:
                # attack waiting for crawl is in need of crawl
                # delete wait crawl from wait crawl table when has not changed
                wait_crawl_table.pop(f"{attack.ip}/{attack.start_time}/{'/'.join(attack.hosts)}")
                # send attack to get crawl topic to crawl hosts
                await get_crawl_topic.send(key=f"{attack.ip}/{attack.start_time}/{'/'.join(attack.hosts)}", value=attack)


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
            # get current crawl from crawl table
            crawl_current = crawl_table[crawl.host]

            if not (crawl_current and crawl_current.time > crawl.time):
                # update host group in host table
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

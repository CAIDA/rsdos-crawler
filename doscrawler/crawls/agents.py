#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents working on the crawls for the DoS crawler.

"""

#  This software is Copyright (c) 2020 The Regents of the University of
#  California. All Rights Reserved. Permission to copy, modify, and distribute this
#  software and its documentation for academic research and education purposes,
#  without fee, and without a written agreement is hereby granted, provided that
#  the above copyright notice, this paragraph and the following three paragraphs
#  appear in all copies. Permission to make use of this software for other than
#  academic research and education purposes may be obtained by contacting:
#
#  Office of Innovation and Commercialization
#  9500 Gilman Drive, Mail Code 0910
#  University of California
#  La Jolla, CA 92093-0910
#  (858) 534-5815
#  invent@ucsd.edu
#
#  This software program and documentation are copyrighted by The Regents of the
#  University of California. The software program and documentation are supplied
#  "as is", without any accompanying services from The Regents. The Regents does
#  not warrant that the operation of the program will be uninterrupted or
#  error-free. The end-user understands that the program was developed for research
#  purposes and is advised not to rely exclusively on the program for any reason.
#
#  IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR
#  DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST
#  PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF
#  THE UNIVERSITY OF CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
#  DAMAGE. THE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY WARRANTIES,
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#  FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON AN "AS
#  IS" BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO OBLIGATIONS TO PROVIDE
#  MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
#
#

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
        next_crawl_time, next_crawl_type = attack.get_next_crawl()

        if next_crawl_time:
            # attack indeed needs to be crawled
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

                    if attack_host_crawl.is_success:
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

            if attack_current and attack_current.finished_wait_crawl:
                # attack waiting for crawl has finished waiting for crawl
                # delete wait crawl from wait crawl table when has not changed
                wait_crawl_table.pop(f"{attack.ip}/{attack.start_time}/{'/'.join(attack.hosts)}")
                # send attack to get crawl topic to crawl hosts
                await get_crawl_topic.send(key=f"{attack.ip}/{attack.start_time}/{'/'.join(attack.hosts)}", value=attack)


@app.agent(change_crawl_topic, concurrency=1)
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

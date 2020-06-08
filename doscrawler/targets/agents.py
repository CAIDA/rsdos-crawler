#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents working on the targets for the DoS crawler.

"""

import logging
from doscrawler.app import app
from doscrawler.targets.models import Target
from doscrawler.targets.topics import targetline_topic, target_topic
from doscrawler.targets.tables import target_table
from doscrawler.hosts.topics import find_host_topic


@app.agent(targetline_topic)
async def get_targets_from_targetlines(target_lines):
    """
    Get targets from target lines

    :param objects:
    :return:
    """

    logging.info("Agent to get targets from target lines is ready to receive target lines.")

    async for target_line in target_lines:
        # create target from target line
        target = Target(ip=target_line.target_ip, start=target_line.start_time, target_lines=[target_line])
        # send to target topic to change target
        await target_topic.send(value=target)
        # send to host topic to get host names
        await find_host_topic.send(value=target)


@app.agent(target_topic)
async def update_targets(targets):
    """
    Update target table by resolved, crawled, retried and recrawled targets

    :param targets:
    :return:
    """

    logging.info("Agent to update targets is ready to receive targets.")

    async for target in targets:
        # look up target in target table
        target_key = f"{target.ip}: {target.start}"
        target_current = target_table[target_key]

        if target_current:
            # target has already been stored in target table
            # get all targetlines
            targetlines_current_start_corsaro = [targetline.start_corsaro_interval for targetline in
                                                 target_current.target_lines]
            targetlines_new = [target_line for target_line in target.target_lines if
                               target_line.start_corsaro_interval not in targetlines_current_start_corsaro]
            targetlines_all = target_current.target_lines + targetlines_new

            # get all hosts
            hosts_current = target_current.hosts.keys()
            hosts_new = [host for host in target.hosts.keys() if host not in hosts_current]
            hosts_update = [host for host in target.hosts.keys() if host in hosts_current]
            hosts_all = {host: target_current.hosts[host] for host in hosts_new}
            for host in hosts_update:
                crawls_current_time = [crawl.time for crawl in target_current.hosts[host]]
                crawls_new = [crawl for crawl in target.hosts[host] if crawl.time not in crawls_current_time]
                hosts_all[host] = target_current.hosts[host] + crawls_new

            # update target in target table
            target_updated = Target(ip=target.ip, start=target.start, target_lines=targetlines_all, hosts=hosts_all)
            target_table[target_key] = target_updated
        else:
            # target has not yet been stored in target table
            # add target to target table
            target_table[target_key] = target

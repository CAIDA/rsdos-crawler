#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents working on the hosts for the DoS crawler.

"""

import logging
from doscrawler.app import app
from doscrawler.hosts.tables import host_table
from doscrawler.targets.topics import target_topic
from doscrawler.crawls.topics import get_crawl_topic
from doscrawler.hosts.topics import find_host_topic, update_host_topic
from doscrawler.hosts.models import HostGroup


@app.agent(find_host_topic)
async def find_hosts_from_targets(targets):
    """
    Process targets in order to get their host names

    :param targets:
    :return:
    """

    logging.info("Agent to get hosts from targets is ready to receive targets.")

    async for target in targets:
        # look up target in host table
        target_host_group = host_table[target.ip]
        if target_host_group:
            # hosts of target have already been resolved
            # add hosts to target with empty crawls
            target.hosts = {host: [] for host in target_host_group.names}
        else:
            # hosts of target have not yet been resolved
            # create and resolve host group
            target_host_group = HostGroup.create_hostgroup_from_ip(ip=target.ip)
            # send to host topic to update hosts
            await update_host_topic.send(value=target_host_group)
            # add hosts to target with empty crawls
            target.hosts = {host: [] for host in target_host_group.names}

        # send to target topic to change target
        await target_topic.send(value=target)
        # send to crawl topic to crawl hosts
        await get_crawl_topic.send(value=target)


@app.agent(update_host_topic)
async def update_hosts(host_groups):
    """
    Update host table by resolved and changed host groups

    :param host_groups:
    :return:
    """

    logging.info("Agent to update hosts is ready to receive host groups.")

    async for host_group in host_groups:
        # update host group in host table
        host_table[host_group.ip] = host_group

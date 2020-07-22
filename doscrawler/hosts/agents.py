#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents working on the hosts for the DoS crawler.

"""

import logging
from simple_settings import settings
from doscrawler.app import app
from doscrawler.hosts.tables import host_table
from doscrawler.targets.topics import change_target_topic
from doscrawler.crawls.topics import get_crawl_topic
from doscrawler.hosts.topics import get_host_topic, change_host_topic
from doscrawler.hosts.models import HostGroup


@app.agent(get_host_topic, concurrency=settings.HOST_CONCURRENCY)
async def get_hosts(targets):
    """
    Get host names from targets

    :param targets: [faust.types.streams.StreamT] stream of targets from get host topic
    :return:
    """

    logging.info("Agent to get hosts from targets is ready to receive targets.")

    async for target_key, target in targets.items():
        # look up host group for target in host table
        target_host_group_current = host_table[target.ip]

        if target_host_group_current and target_host_group_current.is_valid:
            # host group is still valid
            # add hosts to target with empty crawls
            target.hosts = {host: [] for host in target_host_group_current.names}

        else:
            # no current host group or not valid anymore
            # create and resolve host group
            target_host_group = await HostGroup.create_hostgroup_from_ip(ip=target.ip)
            # send host group to host topic
            await change_host_topic.send(key=f"add/{target.ip}", value=target_host_group)
            # add hosts to target with empty crawls
            target.hosts = {host: [] for host in target_host_group.names}

        # send to change target topic to update target with intermediate result of host names
        await change_target_topic.send(key=f"add/{target.ip}/{target.start_time}", value=target)
        # send to get crawl topic to crawl hosts
        await get_crawl_topic.send(key=f"{target.ip}/{target.start_time}", value=target)


@app.agent(change_host_topic)
async def change_hosts(host_groups):
    """
    Change host table by resolved and changed host groups

    :param host_groups: [faust.types.streams.StreamT] stream of host groups from change host topic
    :return:
    """

    logging.info("Agent to update hosts is ready to receive host groups.")

    async for host_group_key, host_group in host_groups.items():
        if host_group_key.startswith("add"):
            # host has to be added
            # update host group in host table
            host_table[host_group.ip] = host_group

        elif host_group_key.startswith("delete"):
            # host has to be deleted
            # get current host group
            host_group_current = host_table[host_group.ip]

            if host_group_current and host_group_current.time == host_group.time:
                # delete host from host table when has not changed
                host_table.pop(host_group_current.ip)

        else:
            raise Exception(
                f"Agent to update hosts raised an exception because a host group has an unknown action. The " \
                f"key of the host group is {host_group_key}."
            )

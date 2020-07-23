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
from doscrawler.attacks.models import Attack
from doscrawler.hosts.models import HostGroup
from doscrawler.hosts.tables import host_table
from doscrawler.attacks.topics import change_attack_topic
from doscrawler.crawls.topics import get_crawl_topic
from doscrawler.hosts.topics import get_host_topic, change_host_topic


@app.agent(get_host_topic, concurrency=settings.HOST_CONCURRENCY)
async def get_hosts(attacks):
    """
    Get host names for attacks

    :param attacks: [faust.types.streams.StreamT] stream of attacks from get host topic
    :return:
    """

    logging.info("Agent to get hosts for attacks is ready to receive attacks.")

    async for attack_key, attack in attacks.items():
        # look up host group for attack in host table
        host_group_current = host_table[attack.ip]

        if host_group_current and host_group_current.is_valid:
            # host group in table is still valid
            # get attack with hosts from host group
            attack = Attack(ip=attack.ip, start_time=attack.start_time, latest_time=attack.latest_time, hosts=host_group_current.names)

        else:
            # no current host group or not valid anymore
            # get host group for attack
            attack_host_group = await HostGroup.create_hostgroup_from_ip(ip=attack.ip)
            # get attack with hosts from host group
            attack = Attack(ip=attack.ip, start_time=attack.start_time, latest_time=attack.latest_time, hosts=attack_host_group.names)
            # send host group to change host topic
            await change_host_topic.send(key=f"add/{attack.ip}", value=attack_host_group)

        # send to change attack topic to change attack with intermediate result of host names
        await change_attack_topic.send(key=f"add/{attack.ip}/{attack.start_time}", value=attack)

        for host in attack.hosts:
            # for each host in attack
            # get attack with only one host from host group of attack (too many hosts, and too long timeouts cause asyncio timeouts)
            attack_host = Attack(ip=attack.ip, start_time=attack.start_time, latest_time=attack.latest_time, hosts=[host])
            # send attack to get crawl topic to crawl host of attack
            await get_crawl_topic.send(key=f"{attack.ip}/{attack.start_time}/{'/'.join(attack_host.hosts)}", value=attack_host)


@app.agent(change_host_topic, concurrency=1)
async def change_hosts(host_groups):
    """
    Change host table by resolved host groups

    :param host_groups: [faust.types.streams.StreamT] stream of host groups from change host topic
    :return:
    """

    logging.info("Agent to change hosts is ready to receive host groups.")

    async for host_group_key, host_group in host_groups.items():
        if host_group_key.startswith("add"):
            # host has to be added
            # get current host group from host table
            host_group_current = host_table[host_group.ip]

            if not (host_group_current and host_group_current.time > host_group.time):
                # update host group in host table
                host_table[host_group.ip] = host_group

        elif host_group_key.startswith("delete"):
            # host has to be deleted
            # get current host group from host table
            host_group_current = host_table[host_group.ip]

            if host_group_current and host_group_current.time == host_group.time:
                # delete host group from host table when has not changed
                host_table.pop(host_group_current.ip)

        else:
            raise Exception(
                f"Agent to change hosts raised an exception because a host group has an unknown action. The " \
                f"key of the host group is {host_group_key}."
            )

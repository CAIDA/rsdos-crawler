#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Services
------

This module defines the services of the hosts for the DoS crawler.

"""

import logging
from simple_settings import settings
from doscrawler.app import app
from doscrawler.hosts.tables import host_table
from doscrawler.hosts.topics import change_host_topic


@app.timer(settings.HOST_CLEAN_TIMER, on_leader=True)
async def clean_hosts(self):
    """
    Clean hosts which must not be memorized anymore

    :return:
    """

    logging.info("Service to maintain hosts is starting to clean hosts.")

    for host_key in list(host_table.keys()):
        # look up host in host table
        host = host_table[host_key]

        if host and not host.is_valid:
            # for each expired host
            # send host to change host topic for deletion
            await change_host_topic.send(key=f"delete/{host.ip}", value=host)

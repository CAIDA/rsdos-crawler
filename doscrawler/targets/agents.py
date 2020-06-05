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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents for the slack messages sent by the DoS crawler.

"""

import logging
from doscrawler.app import app
from doscrawler.slacks.topics import get_slack_topic


@app.agent(get_slack_topic, concurrency=1)
async def get_slacks(slacks):
    """
    Get slack messages

    :param slacks: [faust.types.streams.StreamT] stream of slack messages from get slack topic
    :return:
    """

    logging.info("Agent to get slack messages is ready to receive slack messages.")

    async for slack in slacks:
        # send slack message
        slack.send()

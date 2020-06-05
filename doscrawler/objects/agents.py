#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents working on the objects in the Swift containers for the DoS crawler.

"""

import logging
from doscrawler.app import app
from doscrawler.objects.topics import object_topic
from doscrawler.objects.tables import object_table
from doscrawler.targets.models import TargetLine
from doscrawler.targets.topics import targetline_topic


@app.agent(object_topic)
async def get_targetlines_from_objects(objects):
    """
    Process target lines from object

    :param objects:
    :return:
    """

    logging.info("Agent to process objects is ready to get target lines.")

    async for object in objects:
        # check in table if object not already processed
        logging.info(f"Object {object.name} is in table {object_table[object.name].value()}")
        if not object_table[object.name].value():
            logging.info(f"Agent to process objects is working on a new unprocessed object {object.name}.")

            # get target lines from object
            target_lines = object.get_target_lines()

            # sanity check
            if not target_lines:
                logging.warning(
                    f"Agent to process objects has not received any target lines from object {object.name}. Please " \
                    f"make sure that this is the expected behavior. I will consider this object still as processed."
                )

            # send target lines to topic
            for target_line in target_lines:
                await targetline_topic.send(value=TargetLine(**target_line))

            # mark in table object as processed
            object_table[object.name] = object

            logging.info(
                f"Agent to process objects has sent from object {object.name} in total {len(target_lines)} " \
                f"target lines to the target line topic."
            )

#####################################
# TODO:                             #
#   - make table changelog of topic #
#   - consider need for concurrency #
#####################################

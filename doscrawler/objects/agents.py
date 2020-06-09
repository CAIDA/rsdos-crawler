#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents working on the objects in the Swift containers for the DoS crawler.

"""

import logging
from datetime import datetime
from doscrawler.app import app
from doscrawler.objects.topics import object_topic
from doscrawler.objects.tables import object_table
from doscrawler.targets.models import TargetLine
from doscrawler.targets.topics import targetline_topic


@app.agent(object_topic)
async def get_targetlines_from_objects(objects):
    """
    Process target lines from object

    :param objects: [faust.types.streams.StreamT] stream of objects from object topic
    :return:
    """

    logging.info("Agent to process objects is ready to get target lines.")

    async for object in objects:
        # create object key
        object_key = f"{object.container}:{object.name}"
        # check in table if object not already processed
        if not object_table[object_key].value():
            logging.info(f"Agent to process objects is working on a new unprocessed object {object.name}.")

            ############################################################################################################
            # TODO: use dynamic objects                                                                                #
            ############################################################################################################

            ## get target lines from object
            #target_lines = object.get_target_lines()
            #
            ## sanity check
            #if not target_lines:
            #    logging.warning(
            #        f"Agent to process objects has not received any target lines from object {object.name}. Please " \
            #        f"make sure that this is the expected behavior. I will consider this object still as processed."
            #    )
            #
            ## send target lines to topic
            #for target_line in target_lines:
            #    await targetline_topic.send(value=TargetLine(**target_line))

            ############################################################################################################

            # send one target line for testing
            targetline = TargetLine(
                target_ip="172.217.23.163",
                nr_attacker_ips=1,
                nr_attacker_ips_in_interval=1,
                nr_attacker_ports=1,
                nr_target_ports=1,
                nr_packets=1,
                nr_packets_in_interval=1,
                nr_bytes=1,
                nr_bytes_in_interval=1,
                max_ppm=1,
                start_time=datetime(2020, 6, 8, 10, 2, 1),
                latest_time=datetime(2020, 6, 8, 10, 20, 55),
                start_corsaro_interval=datetime(2020, 6, 8, 10)
            )

            target_lines = [targetline]

            for target_line in target_lines:
                await targetline_topic.send(value=target_line)

            ############################################################################################################

            # mark in table object as processed
            object_table[object_key] = object

            logging.info(
                f"Agent to process objects has sent from object {object.name} in total {len(target_lines)} " \
                f"target lines to the target line topic."
            )

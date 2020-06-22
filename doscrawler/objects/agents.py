#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents working on the objects in the Swift containers for the DoS crawler.

"""

import logging
from datetime import datetime, timezone
from doscrawler.app import app
from doscrawler.objects.topics import change_object_topic
from doscrawler.objects.tables import object_table
from doscrawler.targets.models import TargetLine
from doscrawler.targets.topics import get_target_topic


@app.agent(change_object_topic, concurrency=1)
async def change_objects(objects):
    """
    Change objects and process their target lines

    :param objects: [faust.types.streams.StreamT] stream of objects from change object topic
    :return:
    """

    logging.info("Agent to change objects is ready to get objects.")

    async for object_key, object in objects.items():
        if object_key.startswith("add"):
            # object has to be added
            # look up object in object table
            object_current = object_table[f"{object.container}/{object.name}"]

            if not object_current:
                # object has not yet been processed
                logging.info(
                    f"Agent to process objects is working on a new unprocessed object {object.container}/{object.name}."
                )

                ########################################################################################################
                # TODO: use dynamic objects                                                                            #
                ########################################################################################################

                ## get target lines from object
                #target_lines = object.get_target_lines()
                #
                ## sanity check
                #if not target_lines:
                #    logging.warning(
                #        f"Agent to process objects has not received any target lines from object {object.container}/" \
                #        f"{object.name}. Please make sure that this is the expected behavior. I will consider this " \
                #        f"object still as processed."
                #    )
                #
                ## send target lines to topic
                #for target_line in target_lines:
                #    await targetline_topic.send(value=TargetLine(**target_line))

                ########################################################################################################

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
                    start_time=datetime(2020, 6, 8, 10, 2, 1).replace(tzinfo=timezone.utc),
                    latest_time=datetime(2020, 6, 8, 10, 20, 55).replace(tzinfo=timezone.utc),
                    start_corsaro_interval=datetime(2020, 6, 8, 10).replace(tzinfo=timezone.utc)
                )

                target_lines = [targetline]

                for target_line in target_lines:
                    # for each target line in object
                    # send target line to get target topic
                    await get_target_topic.send(key=target_line.target_ip, value=target_line)

                ########################################################################################################

                # mark in table object as processed
                object_table[f"{object.container}/{object.name}"] = object

                logging.info(
                    f"Agent to process objects has sent from object {object.container}/{object.name} in total " \
                    f"{len(target_lines)} target lines to the target line topic."
                )
        elif object_key.startswith("delete"):
            # object has to be deleted
            # look up object in object table
            object_current = object_table[f"{object.container}/{object.name}"]

            if object_current:
                # delete object from object table
                object_table.pop(f"{object.container}/{object.name}")
        else:
            raise Exception(
                f"Agent to change objects raised an exception because an object has an unknown action. The key of the "\
                f"object is {object_key}."
            )

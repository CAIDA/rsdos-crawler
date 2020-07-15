#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents working on the objects in the Swift containers for the DoS crawler.

"""

import logging
from doscrawler.app import app
from doscrawler.objects.topics import change_object_topic
from doscrawler.objects.tables import object_table
from doscrawler.targets.topics import get_target_topic
from doscrawler.slacks.models import Slack
from doscrawler.slacks.topics import get_slack_topic


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
                # log got new unprocessed object
                logging.info(f"Agent to process objects is working on a new unprocessed object {object.container}/{object.name}.")

                ########################################################################################################
                # TODO: use non-random target lines                                                                    #
                ########################################################################################################

                ## get target lines from object
                #target_lines = object.get_target_lines()
                #
                ## send target lines to topic
                #for target_line in target_lines:
                #   # for each target line in object
                #   # send target line to get target topic
                #    await get_target_topic.send(key=target_line.target_ip, value=target_line)

                ########################################################################################################

                target_lines = object.get_random_target_lines()

                for target_line in target_lines:
                    # for each target line in object
                    # send target line to get target topic
                    await get_target_topic.send(key=target_line.target_ip, value=target_line)

                ########################################################################################################

                # mark in table object as processed
                object_table[f"{object.container}/{object.name}"] = object

                # log finished new unprocessed object
                logging.info(
                    f"Agent to process objects has sent from object {object.container}/{object.name} in total " \
                    f"{len(target_lines)} target lines to the target line topic."
                )

                # slack finished new unprocessed object
                await get_slack_topic.send(value=Slack(status="success",
                                                       title="I processed a new object!",
                                                       descriptions=[f"Container: {object.container}", f"Object: {object.name}", f"Target Lines: {len(target_lines)}"]))

        elif object_key.startswith("delete"):
            # object has to be deleted
            # look up object in object table
            object_current = object_table[f"{object.container}/{object.name}"]

            if object_current:
                # delete object from object table
                object_table.pop(f"{object.container}/{object.name}")

        else:
            raise Exception(
                f"Agent to change objects raised an exception because an object in the change object topic has an " \
                f"unknown action. The key of the object is {object_key}."
            )

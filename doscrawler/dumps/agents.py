#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents for the dumps of the DoS crawler.

"""

import logging
from doscrawler.app import app
from doscrawler.dumps.topics import change_dump_topic
from doscrawler.dumps.tables import dump_table
from doscrawler.slacks.models import Slack
from doscrawler.slacks.topics import get_slack_topic


@app.agent(change_dump_topic, concurrency=1)
async def change_dumps(dumps):
    """
    Change dumps and dump attacks into files

    :param objects: [faust.types.streams.StreamT] stream of dumps from change dump topic
    :return:
    """

    logging.info("Agent to change dumps is ready to get dumps.")

    async for dump_key, dump in dumps.items():
        if dump_key.startswith("add"):
            # dump has to be added
            # look up dump in dump table
            dump_current = dump_table[dump.name]

            if not dump_current:
                # dump has not yet been processed
                # log got new unprocessed object
                logging.info(f"Agent to process dumps is working on a new unprocessed dump {dump.name}.")
                # get attacks and write dump
                name, time, attacks, hosts, crawls = await dump.write(dir=None)
                # mark in table dump as processed
                dump_table[dump.name] = dump
                # log dump
                logging.info(f"Agent to process dumps has dumped {attacks} attacks with {hosts} hosts, {crawls} crawls "\
                    f"at {time} in {name}.")
                # slack dump
                await get_slack_topic.send(value=Slack(status="success", title="I saved a new dump!",
                    descriptions=[f"Dump: {name}", f"Attacks: {attacks}", f"Hosts: {hosts}", f"Crawls: {crawls}"]))

        elif dump_key.startswith("delete"):
            # dump has to be deleted
            # look up dump in dump table
            dump_current = dump_table[dump.name]

            if dump_current and not dump_current.is_valid:
                # delete dump from dump table
                dump_table.pop(dump_current.name)

        else:
            raise Exception(
                f"Agent to change dumps raised an exception because a dump in the change dump topic has an " \
                f"unknown action. The key of the dump is {dump_key}."
            )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents for the dumps of the DoS crawler.

"""

#  This software is Copyright (c) 2020 The Regents of the University of
#  California. All Rights Reserved. Permission to copy, modify, and distribute this
#  software and its documentation for academic research and education purposes,
#  without fee, and without a written agreement is hereby granted, provided that
#  the above copyright notice, this paragraph and the following three paragraphs
#  appear in all copies. Permission to make use of this software for other than
#  academic research and education purposes may be obtained by contacting:
#
#  Office of Innovation and Commercialization
#  9500 Gilman Drive, Mail Code 0910
#  University of California
#  La Jolla, CA 92093-0910
#  (858) 534-5815
#  invent@ucsd.edu
#
#  This software program and documentation are copyrighted by The Regents of the
#  University of California. The software program and documentation are supplied
#  "as is", without any accompanying services from The Regents. The Regents does
#  not warrant that the operation of the program will be uninterrupted or
#  error-free. The end-user understands that the program was developed for research
#  purposes and is advised not to rely exclusively on the program for any reason.
#
#  IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR
#  DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST
#  PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF
#  THE UNIVERSITY OF CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
#  DAMAGE. THE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY WARRANTIES,
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#  FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON AN "AS
#  IS" BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO OBLIGATIONS TO PROVIDE
#  MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
#
#

import logging
from simple_settings import settings
from doscrawler.app import app
from doscrawler.dumps.topics import change_dump_topic
from doscrawler.dumps.tables import dump_table
from doscrawler.slacks.models import Slack
from doscrawler.slacks.topics import get_slack_topic


@app.agent(change_dump_topic, concurrency=settings.DUMP_CONCURRENCY)
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

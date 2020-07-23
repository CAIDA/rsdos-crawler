#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Services
--------

This module defines the services for the dumps of the DoS crawler.

"""

import logging
from mode import Service
from datetime import datetime, timezone
from simple_settings import settings
from doscrawler.app import app
from doscrawler.dumps.models import Dump
from doscrawler.dumps.tables import dump_table
from doscrawler.dumps.topics import change_dump_topic


@app.crontab(settings.DUMP_CRON)
async def _get_dumps(self):
    """
    Cron job to get dumps of targets from DoS crawler

    :return:
    """

    logging.info("Service to make dumps is initializing a dump.")

    # create dump
    time_dump = datetime.now(tz=timezone.utc)
    dump = Dump.create_dump_with_time(time=time_dump)

    # send dump to change dump topic
    await change_dump_topic.send(key=f"add/{dump.name}", value=dump)


@Service.timer(settings.DUMP_CLEAN_TIMER)
async def _clean_dumps(self):
    """
    Clean dumps which will not be considered anymore

    :return:
    """

    logging.info("Service to maintain dumps is starting to clean dumps.")

    for dump_key in list(dump_table.keys()):
        # for each dump
        # look up dump in table
        dump = dump_table[dump_key]

        if dump and not dump.is_valid:
            # for each expired dump
            # send dump to change dump topic for deletion
            await change_dump_topic.send(key=f"delete/{dump.name}", value=dump)

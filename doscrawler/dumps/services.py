#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Services
--------

This module defines the services for the dumps of the DoS crawler.

"""

import logging
from datetime import datetime, timezone
from simple_settings import settings
from doscrawler.app import app
from doscrawler.dumps.models import Dump
from doscrawler.dumps.topics import change_dump_topic


@app.crontab(settings.DUMP_CRON, on_leader=True)
async def get_dumps(self):
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

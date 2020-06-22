#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Crons
-----

This module defines the cron jobs for the dumps of the DoS crawler.

"""

import logging
from datetime import datetime, timezone
from simple_settings import settings
from doscrawler.app import app
from doscrawler.dumps.models import Dump


@app.crontab(settings.DUMP_CRON, tz=timezone.utc)
async def make_dump():
    """
    Cron job to make dump of targets from DoS crawler

    :return:
    """

    logging.info("Cron job to make dumps is starting.")

    # create dump
    dump_time = datetime.now(tz=timezone.utc)
    dump = Dump.create_dump_with_time(time=dump_time)

    # get targets and write dump
    dump.write(dir=None)

    logging.info(f"Cron job to make dumps has dumped targets at {dump_time} in {dump.name}.")

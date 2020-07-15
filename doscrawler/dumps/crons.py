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
from doscrawler.slacks.models import Slack
from doscrawler.slacks.topics import get_slack_topic


@app.crontab(settings.DUMP_CRON)
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
    name, time, targets = await dump.write(dir=None)

    # log dump
    logging.info(f"Cron job to make dumps has dumped {targets} targets at {time} in {name}.")

    # slack dump
    await get_slack_topic.send(value=Slack(status="success",
                                       title="I saved a new dump!",
                                       descriptions=[f"Dump: {name}", f"Targets: {targets}"]))

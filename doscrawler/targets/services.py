#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Services
------

This module defines the services of the targets for the DoS crawler.

"""

import logging
from mode import Service
from datetime import datetime, timedelta, timezone
from simple_settings import settings
from doscrawler.app import app
from doscrawler.targets.tables import target_candidate_table
from doscrawler.targets.topics import change_target_candidate_topic


@app.service
class TargetService(Service):
    """
    Target service
    """

    async def on_start(self):
        """
        Process when service is started

        :return:
        """

        logging.info("Service to maintain targets is starting.")

    async def on_stop(self):
        """
        Process when service is stopped

        :return:
        """

        logging.info("Service to maintain targets is stopping.")

    @Service.timer(settings.TARGET_CANDIDATE_CLEAN_TIMER)
    async def _clean_target_candidates(self):
        """
        Clean target candidates which cannot be merged anymore

        :return:
        """

        logging.info("Service to maintain target candidates is starting to clean target candidates.")

        # get target candidates to be cleaned
        clean_time = datetime.now(timezone.utc) - timedelta(seconds=settings.TARGET_MERGE_INTERVAL)

        for target_candidate_key, target_candidate in target_candidate_table.items():
            if target_candidate.latest_time < clean_time:
                # for each expired target candidate
                # send target candidate to change target candidate topic for deletion
                await change_target_candidate_topic.send(key=f"delete/{target_candidate.ip}", value=target_candidate)

        logging.info(f"Service to maintain targets has send target candidates for deletion.")

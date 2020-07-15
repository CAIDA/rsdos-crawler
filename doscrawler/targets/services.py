#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Services
------

This module defines the services of the targets for the DoS crawler.

"""

import logging
from mode import Service
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

        for target_candidate_key in list(target_candidate_table.keys()):
            # for each target candidate
            # look up target candidate in table
            target_candidate = target_candidate_table[target_candidate_key]

            if target_candidate and not target_candidate.is_alive:
                # for each expired target candidate in table
                # send target candidate to change target candidate topic for deletion
                await change_target_candidate_topic.send(key=f"delete/{target_candidate.ip}", value=target_candidate)

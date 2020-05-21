#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Tasks
-----

This module defines the tasks by the DoS crawler.

"""

import requests
import logging
from celery import Task, states
from doscrawler.targets import Target


logger = logging.getLogger(__name__)


class Crawl(Task):
    """
    Crawl task
    """

    name = "Crawl"
    type = "regular"
    ignore_result = True
    retry_kwargs = {"max_retries": 5}
    retry_backoff = False

    def __init__(self):
        """
        Initialize crawl task
        """

        pass

    def run(self, ip=None, file=None):
        """
        Run crawl task

        :param ip: [str] IP address, if None then file needs to be given, default = None
        :param file: [str] directory to file with hosts, if None then ip needs to be given, default = None
        :return: [list] list of tuples with (host name, response status code, response)
        """

        self.update_state(state=states.PENDING)

        target = Target(file=file)
        logger.info("Crawl target at IP address {}".format(target.ip))

        results = []

        for host in target.hosts:
            try:
                ## too slow
                #if not re.match('(?:http|ftp|https)://', host):
                #    host = 'http://{}'.format(host)
                host = "http://{}".format(host)
                response = requests.get(host)
                results.append((host, response.status_code, response.json()))
            except requests.exceptions.MissingSchema:
                continue

        logger.info("Received from target at IP address {} following host names and status codes {}".format(
            target.ip,
            [(result[0], result[1]) for result in results]
        ))

        return results

#####################################################
# TODO:                                             #
#  create sub tasks for single hosts                #
#  raise exception on non 2xx responses             #
#  implement on success save response               #
#  implement on failure retry with changed priority #
#####################################################

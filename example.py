#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Example
-------

This module provides an example for the DoS crawler.

"""

import logging
from celery.signals import after_setup_logger
from doscrawler.tasks import Crawl
from doscrawler.celery import app


# create logger
logger = logging.getLogger(__name__)


@after_setup_logger.connect
def setup_loggers(*args, **kwargs):
    logger = logging.getLogger()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # add stream handler
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # add file handler
    fh = logging.FileHandler("logs/example.log")
    fh.setFormatter(formatter)
    logger.addHandler(fh)


if __name__ == "__main__":
    # discard all waiting tasks
    app.control.purge()

    # queue crawl task
    task = Crawl().apply_async(kwargs={"file": "data/example_hosts.txt"}, queue="doscrawler")
    print("Started task {}".format(task))

    # wait for result and then print
    print(task.get())

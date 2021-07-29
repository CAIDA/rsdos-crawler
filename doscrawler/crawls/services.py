#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Services
--------

This module defines the services of the crawls for the DoS crawler.

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
from doscrawler.crawls.topics import change_crawl_topic, change_wait_crawl_topic
from doscrawler.crawls.tables import crawl_table, wait_crawl_table


@app.timer(settings.CRAWL_GET_WAIT_TIMER, on_leader=True)
async def get_wait_crawls(self):
    """
    Get crawls for attacks which are ready to be get crawled.

    This function triggers by timer with settings.CRAWL_GET_WAIT_TIMER (30s) interval.

    :return:
    """

    logging.info("Service to send waiting attacks which are ready to be crawled again is starting to send attacks.")

    for attack_key in list(wait_crawl_table.keys()):
        # for each attack waiting for crawl
        # look up attack in wait crawl table
        attack = wait_crawl_table[attack_key]

        if attack and attack.finished_wait_crawl:
            # attack has finished waiting
            # send attack to change wait crawl topic for deletion
            await change_wait_crawl_topic.send(key=f"delete/{attack.ip}/{attack.start_time}/{'/'.join(attack.hosts)}", value=attack)


@app.timer(settings.CRAWL_CLEAN_TIMER, on_leader=True)
async def clean_crawls(self):
    """
    Clean crawls which will not be considered anymore.

    This function triggers by timer with settings.CRAWL_CLEAN_TIMER (1 hour) interval.

    :return:
    """

    logging.info("Service to maintain crawls is starting to clean crawls.")

    for crawl_key in list(crawl_table.keys()):
        # for each crawl
        # look up crawl in crawl table
        crawl = crawl_table[crawl_key]

        if crawl and not crawl.is_valid:
            # for each invalid crawl
            # send crawl to change crawl topic for deletion
            await change_crawl_topic.send(key=f"delete/{crawl.host}", value=crawl)

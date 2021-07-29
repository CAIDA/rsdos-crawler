#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Application
-----------

This module sets up the application of the DoS crawler.

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

import faust
import logging
from simple_settings import settings


app = faust.App(id="doscrawler")


@app.on_configured.connect
def configure(app, conf, **kwargs):
    """
    Configure application

    :param app: [faust.App]
    :param conf: [faust.Settings]
    :param kwargs:
    :return:
    """

    conf.debug = settings.DEBUG
    conf.broker = settings.BROKER
    conf.store = settings.STORE
    conf.cache = settings.CACHE
    conf.processing_guarantee = settings.PROCESSING_GUARANTEE
    conf.autodiscover = settings.AUTODISCOVER
    conf.logging = settings.LOGGING
    conf.key_serializer = settings.KEY_SERIALIZER
    conf.value_serializer = settings.VALUE_SERIALIZER
    conf.topic_partitions = settings.TOPIC_PARTITIONS
    conf.topic_disable_leader = settings.TOPIC_DISABLE_LEADER
    conf.broker_commit_every = settings.BROKER_COMMIT_EVERY
    conf.broker_commit_interval = settings.BROKER_COMMIT_INTERVAL
    conf.broker_request_timeout = settings.BROKER_REQUEST_TIMEOUT
    conf.broker_heartbeat_interval = settings.BROKER_HEARTBEAT_INTERVAL
    conf.broker_session_timeout = settings.BROKER_SESSION_TIMEOUT
    conf.broker_max_poll_records = settings.BROKER_MAX_POLL_RECORDS
    conf.broker_max_poll_interval = settings.BROKER_MAX_POLL_INTERVAL
    conf.consumer_max_fetch_size = settings.CONSUMER_MAX_FETCH_SIZE
    conf.consumer_auto_offset_reset = settings.CONSUMER_AUTO_OFFSET_RESET
    conf.producer_acks = settings.PRODUCER_ACKS
    conf.producer_request_timeout = settings.PRODUCER_REQUEST_TIMEOUT
    conf.producer_max_request_size = settings.PRODUCER_MAX_REQUEST_SIZE
    conf.table_cleanup_interval = settings.TABLE_CLEANUP_INTERVAL
    conf.table_standby_replicas = settings.TABLE_STANDBY_REPLICAS
    conf.table_key_index_size = settings.TABLE_KEY_INDEX_SIZE
    conf.stream_buffer_maxsize = settings.STREAM_BUFFER_MAXSIZE
    conf.worker_redirect_stdouts = settings.WORKER_REDIRECT_STDOUTS
    conf.worker_redirect_stdouts_level = settings.WORKER_REDIRECT_STDOUTS_LEVEL
    conf.web_enabled = settings.WEB_ENABLED


@app.on_before_configured.connect
def before_configuration(app, **kwargs):
    """
    Process before configure application

    :param app: [faust.App]
    :param kwargs:
    :return:
    """

    logging.info(f"App {app} is being configured.")


@app.on_after_configured.connect
def after_configuration(app, **kwargs):
    """
    Process after configured application

    :param app: [faust.App]
    :param kwargs:
    :return:
    """

    logging.info(f"App {app} has been configured.")


@app.on_partitions_revoked.connect
async def on_partitions_revoked(app, revoked, **kwargs):
    """
    Process when application revokes partitions

    :param app: [faust.App]
    :param revoked: [Set[TP]]
    :param kwargs:
    :return:
    """

    logging.info(f"App {app} revokes partitions {revoked}.")


@app.on_partitions_assigned.connect
async def on_partitions_assigned(app, assigned, **kwargs):
    """
    Process when application assigns partitions

    :param app: [faust.App]
    :param assigned: [Set[TP]]
    :param kwargs:
    :return:
    """

    logging.info(f"App {app} assigns partitions {assigned}.")


@app.on_worker_init.connect
def on_worker_init(app, **kwargs):
    """
    Process when worker starts with application

    :param app: [faust.App]
    :param kwargs:
    :return:
    """

    logging.info(f"App {app} is being worked on.")

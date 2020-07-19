#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Application
-----------

This module sets up the application of the DoS crawler.

"""

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

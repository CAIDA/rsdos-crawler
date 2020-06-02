#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Development
-----------

This module defines the development settings of the DoS crawler.

"""

import datetime
from logging.config import dictConfig


DEBUG = True

BROKER = "kafka://localhost:9092"
STORE = "memory://"
CACHE = "memory://"

PROCESSING_GUARANTEE = "at_least_once"
ORIGIN = "doscrawler.app"
AUTODISCOVER = True
TIMEZONE = datetime.timezone.utc
DATADIR = "data/app-{app.conf.id}"

LOGGING = dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"default": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}},
        "handlers": {"console": {"level": "INFO", "class": "logging.StreamHandler", "formatter": "default",}},
    } # "loggers": {"page_views": {"handlers": ["console"], "level": "INFO"}},
)

KEY_SERIALIZER = "raw" # "json" maybe not URL-safe because of encoding
VALUE_SERIALIZER = "json" #

TOPIC_PARTITIONS = 8 # defines maximum number of workers
TOPIC_DISABLE_LEADER = False

BROKER_COMMIT_EVERY = 10000
BROKER_COMMIT_INTERVAL = 2.8

BROKER_REQUEST_TIMEOUT = 300
BROKER_HEARTBEAT_INTERVAL = 10
BROKER_SESSION_TIMEOUT = 120
BROKER_MAX_POLL_RECORDS = 50
BROKER_MAX_POLL_INTERVAL = 1000

CONSUMER_MAX_FETCH_SIZE = 4194304
CONSUMER_AUTO_OFFSET_RESET = "earliest"

# ConsumerScheduler

PRODUCER_ACKS = -1
PRODUCER_REQUEST_TIMEOUT = 1200

TABLE_CLEANUP_INTERVAL = 30
TABLE_STANDBY_REPLICAS = 1
TABLE_KEY_INDEX_SIZE = 1000

STREAM_BUFFER_MAXSIZE = 100000


WORKER_REDIRECT_STDOUTS = True
WORKER_REDIRECT_STDOUTS_LEVEL = "INFO"

WEB_PORT = 6066
WEB_IN_THREAD = True

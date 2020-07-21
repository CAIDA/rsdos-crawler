#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Production
----------

This module defines the production settings of the DoS crawler.

"""


SIMPLE_SETTINGS = {
    "OVERRIDE_BY_ENV": True,
    "CONFIGURE_LOGGING": True,
    "REQUIRED_SETTINGS": ("BROKER",),
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "example": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

DEBUG = True
BROKER = "kafka://localhost:9092"
STORE = "memory://"
CACHE = "memory://"
PROCESSING_GUARANTEE = "exactly_once"
ORIGIN = "doscrawler.app"
AUTODISCOVER = ["doscrawler.containers", "doscrawler.objects", "doscrawler.targets", "doscrawler.hosts", "doscrawler.crawls", "doscrawler.dumps", "doscrawler.slacks"]
KEY_SERIALIZER = "raw"
VALUE_SERIALIZER = "json"
TOPIC_PARTITIONS = 4
TOPIC_DISABLE_LEADER = False
BROKER_COMMIT_EVERY = 10000
BROKER_COMMIT_INTERVAL = 2.8
BROKER_REQUEST_TIMEOUT = 300
BROKER_HEARTBEAT_INTERVAL = 10
BROKER_SESSION_TIMEOUT = 120
BROKER_MAX_POLL_RECORDS = 1
BROKER_MAX_POLL_INTERVAL = 2000
CONSUMER_MAX_FETCH_SIZE = 209715200
CONSUMER_AUTO_OFFSET_RESET = "earliest"
# ConsumerScheduler
PRODUCER_ACKS = -1
PRODUCER_REQUEST_TIMEOUT = 3600
PRODUCER_MAX_REQUEST_SIZE = 209715200
TABLE_CLEANUP_INTERVAL = 60
TABLE_STANDBY_REPLICAS = 1
TABLE_KEY_INDEX_SIZE = 8192
STREAM_BUFFER_MAXSIZE = 4096
WORKER_REDIRECT_STDOUTS = True
WORKER_REDIRECT_STDOUTS_LEVEL = "INFO"
WEB_ENABLED = False
RETENTION_INTERVAL = 21600 # 6 hours

# containers
CONTAINER_NAME = "data-telescope-meta-dos"
CONTAINER_GET_OBJECTS_TIMER = 30
CONTAINER_GET_OBJECTS_INTERVAL = 3600 # 1 hour

# objects
OBJECT_CLEAN_TIMER = 3600 # 1 hour

# crawls
CRAWL_CONCURRENCY = 60
CRAWL_RETRIES = 3
CRAWL_RETRIES_BACKOFF = 20 # 20 -> 40 -> 80 seconds delay
CRAWL_REPEAT_INTERVAL = 1200 # 20 minutes
CRAWL_CLEAN_TIMER = 3600
CRAWL_CACHE_INTERVAL = 10
CRAWL_REQUEST_HEADER = {}
CRAWL_REQUEST_TIMEOUT = 15
CRAWL_BODY_MAX_BYTES = 2097152
CRAWL_GET_WAIT_TIMER = 10

# targets
TARGET_MERGE_INTERVAL = 1800 # 30 minutes
TARGET_TTL = 10800 # 3 hours # how long to follow target from latest time of latest target line (including delay of reporting, also determines number of retries
TARGET_CANDIDATE_CLEAN_TIMER = 3600 # 1 hour
TARGET_CONCURRENCY = 2

# hosts
HOST_CLEAN_TIMER = 3600 # 1 hour
HOST_CACHE_INTERVAL = 3600 # 1 hour
HOST_MAX_NUM = 10
HOST_CONCURRENCY = 2

# dumps
DUMP_CRON = "0 * * * *" # every hour
DUMP_DIR = "data/"
DUMP_COMPRESS_LEVEL = 7
DUMP_CLEAN_TIMER = 3600 # 1 hour

# slacks
SLACK_TOKEN = ""
SLACK_CHANNEL = ""

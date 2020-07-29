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
    "REQUIRED_SETTINGS": (),
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

DEBUG = False
BROKER = "kafka://localhost:9092"
BROKER_CONSUMER = "kafka://localhost:9092;kafka://kafka.rogues.caida.org:9392"
BROKER_PRODUCER = "kafka://localhost:9092"
STORE = "memory://"
CACHE = "memory://"
PROCESSING_GUARANTEE = "exactly_once"
ORIGIN = "doscrawler.app"
AUTODISCOVER = ["doscrawler.attacks", "doscrawler.hosts", "doscrawler.crawls", "doscrawler.dumps", "doscrawler.slacks"]
KEY_SERIALIZER = "raw"
VALUE_SERIALIZER = "json"
TOPIC_PARTITIONS = 4
TOPIC_DISABLE_LEADER = False
BROKER_COMMIT_EVERY = 10000
BROKER_COMMIT_INTERVAL = 2.8
BROKER_REQUEST_TIMEOUT = 300
BROKER_HEARTBEAT_INTERVAL = 10
BROKER_SESSION_TIMEOUT = 120
BROKER_MAX_POLL_RECORDS = 10
BROKER_MAX_POLL_INTERVAL = 1000
CONSUMER_MAX_FETCH_SIZE = 52428800
CONSUMER_AUTO_OFFSET_RESET = "earliest"
PRODUCER_ACKS = -1
PRODUCER_REQUEST_TIMEOUT = 3600
PRODUCER_MAX_REQUEST_SIZE = 52428800
TABLE_CLEANUP_INTERVAL = 3600
TABLE_STANDBY_REPLICAS = 1
TABLE_KEY_INDEX_SIZE = 8192
STREAM_BUFFER_MAXSIZE = 4096
WORKER_REDIRECT_STDOUTS = True
WORKER_REDIRECT_STDOUTS_LEVEL = "INFO"
WEB_ENABLED = False
RETENTION_INTERVAL = 10800 # 3 hours

# attacks
ATTACK_MERGE_INTERVAL = 1800 # 30 minutes
ATTACK_TTL = 7200 # 2 hours # how long to follow attack from latest time of latest attack vector
ATTACK_CONCURRENCY = 1

# hosts
HOST_CLEAN_TIMER = 3600
HOST_CACHE_INTERVAL = 3600
HOST_MAX_NUM = 10
HOST_CONCURRENCY = 5

# crawls
CRAWL_RETRIES = 3
CRAWL_RETRIES_BACKOFF = 20 # 20 -> 40 -> 80 seconds delay
CRAWL_REPEAT_INTERVAL = 1200 # 20 minutes
CRAWL_REQUEST_HEADER = {}
CRAWL_REQUEST_TIMEOUT = 20
CRAWL_BODY_MAX_BYTES = 2097152
CRAWL_GET_WAIT_TIMER = 10
CRAWL_CONCURRENCY = 60
CRAWL_CACHE_INTERVAL = 900 # 15 minutes
CRAWL_CLEAN_TIMER = 1800

# dumps
DUMP_CRON = "0 * * * *" # every hour
DUMP_DIR = "data/"
DUMP_COMPRESS_LEVEL = 7
DUMP_CLEAN_TIMER = 3600

# slacks
SLACK_TOKEN = ""
SLACK_CHANNEL = ""

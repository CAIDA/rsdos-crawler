#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Development
-----------

This module defines the development settings of the DoS crawler.

"""

from logging.config import dictConfig


DEBUG = True
BROKER = "kafka://localhost:9092"
STORE = "memory://"
CACHE = "memory://"
PROCESSING_GUARANTEE = "exactly_once"
ORIGIN = "doscrawler.app"
AUTODISCOVER = ["doscrawler.containers", "doscrawler.objects", "doscrawler.targets", "doscrawler.hosts", "doscrawler.crawls", "doscrawler.dumps", "doscrawler.slacks"]
LOGGING = dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"default": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}},
        "handlers": {"console": {"level": "INFO", "class": "logging.StreamHandler", "formatter": "default",}},
    } # "loggers": {"page_views": {"handlers": ["console"], "level": "INFO"}},
)
KEY_SERIALIZER = "raw"
VALUE_SERIALIZER = "json"
TOPIC_PARTITIONS = 1
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
TABLE_CLEANUP_INTERVAL = 60
TABLE_STANDBY_REPLICAS = 1
TABLE_KEY_INDEX_SIZE = 1000
STREAM_BUFFER_MAXSIZE = 100000
WORKER_REDIRECT_STDOUTS = True
WORKER_REDIRECT_STDOUTS_LEVEL = "INFO"
WEB_PORT = 6066
WEB_IN_THREAD = True
RETENTION_INTERVAL = 86400 # 1 day

# containers
CONTAINER_NAME = "data-telescope-meta-dos"
CONTAINER_GET_OBJECTS_TIMER = 20
CONTAINER_GET_OBJECTS_INTERVAL = 3600 # 1 hour

# objects
OBJECT_CLEAN_TIMER = 60

# crawls
CRAWL_CONCURRENCY = 3
CRAWL_RETRIES = 3
CRAWL_RETRIES_BACKOFF = 5 # 5 -> 10 -> 20 seconds delay
CRAWL_REPEAT_INTERVAL = 60
CRAWL_CACHE_INTERVAL = 15
CRAWL_REQUEST_HEADER = {}
CRAWL_REQUEST_TIMEOUT = 20
CRAWL_GET_WAIT_TIMER = 5

# targets
TARGET_MERGE_INTERVAL = 10
TARGET_TTL = 180 # how long to follow target from latest time of latest target line (including delay of reporting, also determines number of retr
TARGET_CANDIDATE_CLEAN_TIMER = 60
TARGET_CONCURRENCY = 2

# hosts
HOST_CLEAN_TIMER = 60
HOST_CACHE_INTERVAL = 15
HOST_MAX_NUM = 10
HOST_CONCURRENCY = 2

# dumps
DUMP_CRON = "* * * * *" # every minute
DUMP_DIR = "data/"
DUMP_COMPRESS_LEVEL = 7

SLACK_TOKEN = ""
SLACK_CHANNEL = ""

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
STORE = "memory://"
CACHE = "memory://"
PROCESSING_GUARANTEE = "exactly_once"
ORIGIN = "doscrawler.app"
AUTODISCOVER = ["doscrawler.attacks", "doscrawler.hosts", "doscrawler.crawls", "doscrawler.dumps", "doscrawler.slacks"]
KEY_SERIALIZER = "raw"
VALUE_SERIALIZER = "json"
TOPIC_PARTITIONS = 5
TOPIC_DISABLE_LEADER = False
BROKER_COMMIT_EVERY = 10000
BROKER_COMMIT_INTERVAL = 2.8
BROKER_REQUEST_TIMEOUT = 300
BROKER_HEARTBEAT_INTERVAL = 30
BROKER_SESSION_TIMEOUT = 120
BROKER_MAX_POLL_RECORDS = 10
BROKER_MAX_POLL_INTERVAL = 1000
CONSUMER_MAX_FETCH_SIZE = 20971520
CONSUMER_AUTO_OFFSET_RESET = "earliest"
PRODUCER_ACKS = -1
PRODUCER_REQUEST_TIMEOUT = 3600
PRODUCER_MAX_REQUEST_SIZE = 20971520
TABLE_CLEANUP_INTERVAL = 3600
TABLE_STANDBY_REPLICAS = 1
TABLE_KEY_INDEX_SIZE = 8192
STREAM_BUFFER_MAXSIZE = 4096
WORKER_REDIRECT_STDOUTS = True
WORKER_REDIRECT_STDOUTS_LEVEL = "INFO"
WEB_ENABLED = False
RETENTION_INTERVAL = 10800 # 3 hours

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

# attacks
ATTACK_MERGE_INTERVAL = 1800 # 30 minutes
ATTACK_TTL = 10800 # 3 hours # how long to follow attack from latest time of latest attack vector
ATTACK_CONCURRENCY = 3

# hosts
HOST_CLEAN_TIMER = 3600
HOST_CACHE_INTERVAL = 3600
HOST_MAX_NUM = 10
HOST_CONCURRENCY = 3

# crawls
CRAWL_RETRIES = 0
CRAWL_RETRIES_BACKOFF = 60 # 60 -> 120 seconds delay
CRAWL_REPEAT_INTERVAL = 1200 # 20 minutes
CRAWL_REQUEST_HEADER = {}
CRAWL_REQUEST_TIMEOUT = 20
CRAWL_BODY_MAX_BYTES = 2097152
CRAWL_GET_WAIT_TIMER = 30
CRAWL_CONCURRENCY = 30
CRAWL_CACHE_INTERVAL = 900 # 15 minutes
CRAWL_CLEAN_TIMER = 3600

# dumps
# DUMP_CRON = "0 * * * *" # every hour
DUMP_CRON = "*/5 * * * *" # every five minutes
DUMP_DIR = "data/"
DUMP_COMPRESS_LEVEL = 7
DUMP_CONCURRENCY = 3

# slacks
SLACK_TOKEN = ""
SLACK_CHANNEL = ""

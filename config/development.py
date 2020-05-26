#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Development Configuration
-------------------------

This module defines the development configuration of the DoS crawler.

"""

import os
import requests
from kombu import Exchange, Queue


imports = [
    "doscrawler.tasks"
]

timezone = "US/Pacific"

worker_concurrency = 8

broker_user = os.environ.get("BROKER_USER", "guest")
broker_password = os.environ.get("BROKER_PASSWORD", "guest")
broker_host = os.environ.get("BROKER_HOST", "localhost")
broker_port = os.environ.get("BROKER_PORT", "5672")
broker_vhost = os.environ.get("BROKER_VHOST", "doscrawler")
broker_url = f"amqp://{broker_user}:{broker_password}@{broker_host}:{broker_port}/{broker_vhost}"

task_queues = (
    Queue(name="doscrawler.resolve_target", exchange=Exchange("doscrawler")),
    Queue(name="doscrawler.map_hosts", exchange=Exchange("doscrawler")),
    Queue(name="doscrawler.crawl_host", exchange=Exchange("doscrawler"), queue_arguments={"x-message-deduplication": True}),
)
task_annotations = {
    "doscrawler.tasks.resolve_target": {
        "queue": "doscrawler.resolve_target"
    },
    "doscrawler.tasks.map_hosts": {
        "queue": "doscrawler.resolve_target"
    },
    "doscrawler.tasks.crawl_host": {
        "queue": "doscrawler.crawl_host",
        "autoretry_for": (requests.exceptions.RequestException,),
        "retry_backoff": 5,
        "max_retries": 0,
        "soft_time_limit": 20
    }
}
task_compression = None
task_queue_ha_policy = None
task_queue_max_priority = None
task_default_priority = None
task_inherit_parent_priority = False
task_ignore_result = False

result_backend = None # "rpc://"
result_serializer = "json"
result_compression = None
result_expires = 20 # 10800 # 3 hours
result_persistent = False

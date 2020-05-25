#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Example
-------

This module provides an example for the DoS crawler.

"""

from celery import chain
from doscrawler.tasks import resolve_target, crawl_host, map_hosts


# dump = Dump(start="2020-05-24 00:00:00")
# for ip in dump.ips:
#   job = chain(resolve_target.signature(kwargs={"ip": ip}), map_hosts.s(crawl_host.s()))
#   job.apply_async()

# create job with single random ip
job = chain(resolve_target.signature(kwargs={"file": "data/example_hosts.txt"}), map_hosts.s(crawl_host.s()))
job.apply_async()

# create job with single deterministic ip
#job = chain(resolve_target.signature(kwargs={"ip": "172.217.23.99"}), map_hosts.s(crawl_host.s()))
#job.apply_async()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Tasks
-----

This module defines the tasks by the DoS crawler.

"""

import os
import requests
from io import StringIO
from celery import states, task, subtask, group
from celery.utils.log import get_task_logger
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
from doscrawler.targets import Target


@task(bind=True, queue="doscrawler.resolve_target")
def resolve_target(self, ip=None, file=None):
    """
    Task to resolve target's host names

    :param ip: [str] IP address, if None then file needs to be given, default = None
    :param file: [str] directory to file with hosts, if None then ip needs to be given, default = None
    :return: [tuple] target with string of IP address and list of strings related host names
    """

    # get logger
    logger = get_task_logger(__name__)

    # validate inputs
    if (ip and file) or (not ip and not file):
        raise ValueError("You must initialize a target either with an IP address or file directory.")

    # update status of task
    self.update_state(state=states.PENDING)

    # create target for ip
    if ip:
        target = Target(ip=ip)

    # create random target from file
    if file:
        target = Target(file=file)

    # log summary of resolution
    logger.info("Resolved for target at IP address {} following hosts {}".format(target.ip, target.hosts))

    return target.ip, target.hosts


@task(bind=True, queue="doscrawler.map_hosts")
def map_hosts(self, target, callback):
    """
    Task to map each target's host name to a separate crawl

    :param target: [tuple] target with string of IP address and list of strings related host names
    :param callback: [task] task to be called on IP address and host names, must accept tuple of IP address and host name
    :return: [group] group of tasks which crawls each host name in one task
    """

    # get logger
    logger = get_task_logger(__name__)

    # no status update

    # prepare inputs
    ip, hosts = target

    # create group of tasks
    callback = subtask(callback)
    crawl_hosts = group(callback.clone(args=((ip, host),), headers={"x-deduplication-header": host}) for host in hosts)()

    # log summary of mapping
    logger.info("Mapped for target at IP address {} its resolved hosts {} to separate tasks to crawl them".format(ip, hosts))

    return crawl_hosts


@task(bind=True, queue="doscrawler.crawl_host", autoretry_for=(requests.exceptions.RequestException,), retry_backoff=5, max_retries=2, soft_time_limit=20)
def crawl_host(self, host):
    """
    Task to crawl host name

    :param host: [str] host name
    :return: [tuple] tuple with (host name, response status code, response)
    """

    # get logger
    logger = get_task_logger(__name__)

    # update status of task
    self.update_state(state=states.PENDING)

    # prepare inputs
    ip, host = host

    # add schema to host name
    ## too slow
    # if not re.match('(?:http|ftp|https)://', host):
    #    host = 'http://{}'.format(host)
    host_schema = "http://{}".format(host)

    # make request
    response = requests.get(host_schema, timeout=10)

    # check status of response
    response.raise_for_status()

    # log summary of crawl on success
    logger.info("Crawled for target at IP address {} its resolved host {} with status code {}".format(ip, host, response.status_code))

    # define file name
    file_dir = os.path.join("data/", "warc_{}.warc.gz".format(host))

    # if self.request.retries > 0:

    with open(file_dir, "wb") as file:
        # prepare writer (directly in file --> should be first in memory)
        writer = WARCWriter(file, gzip=True)
        # prepare http header resp.raw.headers.items()
        #StatusAndHeaders(statusline=statusline,
        #                 headers=headers,
        #                 protocol=protocol_status[0],
        #                 total_len=total_read)
        # create request # record type = response / revisit / request
        req = writer.create_warc_record(uri=host, record_type="request")
        # create response
        resp = writer.create_warc_record(uri=host, record_type="response", payload=StringIO(response.text))
        # write
        writer.write_request_response_pair(req=req, resp=resp, params=None)

    # log summary of save on success
    logger.info("Saved for target at IP address {} its resolved host {} in file {}".format(ip, host, file_dir))

    return host, response.status_code, response.text



#####################################################
# TODO:                                             #
#  implement all meta information for records       #
#  implement on error save metadata                 #
#  implement on retry make as retry                 #
#  implement on success save response               #
#  implement on failure retry with changed priority #
#####################################################

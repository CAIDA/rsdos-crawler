#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the crawls for the DoS crawler.

"""

import json
import base64
import aiohttp
from io import BytesIO
from faust import Record
from datetime import datetime, timezone, timedelta
from simple_settings import settings
from warcio.warcwriter import BufferWARCWriter
from warcio.statusandheaders import StatusAndHeaders
from warcio.timeutils import iso_date_to_datetime


class Crawl(Record, coerce=True, serializer="json"):
    """
    Crawl model class
    """

    host: str
    record: str
    status: int
    time: datetime

    @classmethod
    async def get_crawl(cls, host, ip, connector):
        """
        Get crawl from host

        :param host: [str] host name of target
        :param ip: [str] IP address from which the host name is resolved
        :param connector: [aiohttp.TCPConnector] connector which keeps track of simultaneous crawls and dns cache
        :return: [doscrawler.crawls.models.Crawl] crawl of host of target
        """

        record, status, time = await cls._crawl_host(host, ip, connector)
        crawl = cls(host=host, record=record, status=status, time=time)

        return crawl

    @property
    def is_success(self):
        """
        Check if crawl is success

        :return: [bool] crawl is success
        """

        if self.status > 0:
            return True

        return False

    @property
    def is_valid(self):
        """
        Check if crawl is still valid according to status and expire interval

        :return: [bool] crawl is still valid
        """

        if self.is_success:
            # crawl has been successful
            # get expire time by expire interval
            expire_time = datetime.now(timezone.utc) - timedelta(seconds=settings.CRAWL_CACHE_INTERVAL)

        else:
            # crawl has been unsuccessful
            # get expire time by minimum retry time
            expire_time = datetime.now(timezone.utc) - timedelta(seconds=settings.CRAWL_RETRIES_BACKOFF)

        if self.time > expire_time:
            return True

        return False

    @staticmethod
    async def _crawl_host(host, ip, connector):
        """
        Crawl host

        :param host: [str] host name of target
        :param ip: [str] IP address from which the host name is resolved
        :param connector: [aiohttp.TCPConnector] connector which keeps track of simultaneous crawls and dns cache
        :return: [str] record of response or metadata from host as WARC, gzipped, base64 encoded
        :return: [int] status code of crawl, e.g. negative code indicates no response from host could be recorded
        :return: [datetime.datetime] time of request sent to crawl host
        """

        # set default status
        status = -1

        # set default truncated
        truncated = False

        # add schema to host name
        ## check existing schema
        #if not re.match(r"(?:http|ftp|https)://", host):
        #   host_schema = f"http://{host}"
        host_schema = f"http://{host}"

        # define warc writer
        warc_writer = BufferWARCWriter(warc_version="1.1", gzip=True)

        # prepare write request
        warc_request_headers = StatusAndHeaders("GET / HTTP/1.1", settings.CRAWL_REQUEST_HEADER, is_http_request=True)
        warc_request = warc_writer.create_warc_record(host_schema, "request", http_headers=warc_request_headers, warc_content_type="application/http; msgtype=request")

        try:
            # try to get response on request
            # send request
            async with aiohttp.ClientSession(connector=connector, connector_owner=False) as session:
                async with session.get(host_schema, timeout=aiohttp.ClientTimeout(total=settings.CRAWL_REQUEST_TIMEOUT), headers=settings.CRAWL_REQUEST_HEADER, ssl=False) as response:
                    warc_response_payload = await response.text()
                    warc_response_payload = warc_response_payload.encode("utf-8")

                    if len(warc_response_payload) > settings.CRAWL_BODY_MAX_BYTES:
                        # response must be truncated
                        truncated = True
                        warc_response_payload = warc_response_payload[:settings.CRAWL_BODY_MAX_BYTES]

                    warc_response_status = f"{response.status} {response.reason}"
                    warc_response_headers = StatusAndHeaders(warc_response_status, response.headers, protocol="HTTP/1.1")
                    warc_response = warc_writer.create_warc_record(uri=host_schema, record_type="response",
                                                                   payload=BytesIO(warc_response_payload),
                                                                   length=len(warc_response_payload),
                                                                   http_headers=warc_response_headers,
                                                                   warc_content_type="application/http; msgtype=response")

            # change status
            status = response.status
        except Exception as e:
            # raised exception while request
            # prepare write metadata as response
            warc_response_payload = json.dumps({"error": str(type(e)), "error_desc": str(e)}).encode("utf-8")

            warc_response = warc_writer.create_warc_record(uri=host_schema, record_type="metadata",
                                                           payload=BytesIO(warc_response_payload),
                                                           length=len(warc_response_payload),
                                                           warc_content_type="application/json; msgtype=metadata")

            ## change status on bad request
            #if hasattr(e, "response"):
            #   if hasattr(e.response, "status_code"):
            #       # change status
            #       status = e.response.status_code

        # get request time
        warc_request_date = warc_request.rec_headers.get_header("WARC-Date")
        time = iso_date_to_datetime(warc_request_date).replace(tzinfo=timezone.utc)

        # associate request and response
        warc_response_id = warc_response.rec_headers.get_header("WARC-Record-ID")
        warc_request.rec_headers.add_header("WARC-Concurrent-To", warc_response_id)

        # add ip address of target
        warc_request.rec_headers.add_header("WARC-IP-Address", ip)
        warc_response.rec_headers.add_header("WARC-IP-Address", ip)

        # add truncated
        warc_response.rec_headers.add_header("WARC-Truncated", str(truncated))

        # write request and response in warc
        warc_writer.write_record(warc_request)
        warc_writer.write_record(warc_response)

        record = warc_writer.get_contents()
        record = base64.encodebytes(record).decode("ascii")

        return record, status, time

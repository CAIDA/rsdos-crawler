#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the crawls for the DoS crawler.

"""

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
    status: int
    time: datetime
    record: str

    @classmethod
    async def get_crawl(cls, host, ip, connector):
        """
        Get crawl from host

        :param host: [str] host name of attack
        :param ip: [str] IP address from which the host name is resolved
        :param connector: [aiohttp.TCPConnector] connector which keeps track of simultaneous crawls and dns cache
        :return: [doscrawler.crawls.models.Crawl] crawl of host of attack
        """

        record, status, time = await cls._crawl_host(host=host, ip=ip, connector=connector)
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
            time_expire = datetime.now(timezone.utc) - timedelta(seconds=settings.CRAWL_CACHE_INTERVAL)

        else:
            # crawl has been unsuccessful
            # get expire time by minimum retry time
            time_expire = datetime.now(timezone.utc) - timedelta(seconds=settings.CRAWL_RETRIES_BACKOFF)

        if self.time > time_expire:
            return True

        return False

    @staticmethod
    async def _crawl_host(host, ip, connector):
        """
        Crawl host

        :param host: [str] host name of attack
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
                    # prepare iterate over response
                    warc_response_payload = b""
                    chunk_bytes = 20480
                    chunk_last_limit = settings.CRAWL_BODY_MAX_BYTES - chunk_bytes

                    async for chunk in response.content.iter_chunked(chunk_bytes):
                        # for chunk in iterated response
                        warc_response_payload += chunk

                        if len(warc_response_payload) > chunk_last_limit:
                            # response has to be truncated
                            truncated = True
                            break

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
        # add ip address of attack
        warc_request.rec_headers.add_header("WARC-IP-Address", ip)
        warc_response.rec_headers.add_header("WARC-IP-Address", ip)
        # add truncated
        warc_response.rec_headers.add_header("WARC-Truncated", str(truncated))
        # write request and response in warc
        warc_writer.write_record(warc_request)
        warc_writer.write_record(warc_response)
        # prepare record for message
        record = warc_writer.get_contents()
        record = base64.encodebytes(record).decode("ascii")

        return record, status, time

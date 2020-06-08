#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the crawls for the DoS crawler.

"""

import json
import requests
import logging
from io import BytesIO
from faust import Record
from datetime import datetime
from pytz import timezone
from simple_settings import settings
from warcio.warcwriter import BufferWARCWriter
from warcio.statusandheaders import StatusAndHeaders
from warcio.timeutils import iso_date_to_datetime


class Crawl(Record, coerce=True, serializer="raw"):
    """
    Crawl model class
    """

    host: str
    record: bytes
    time: datetime
    status: str

    @classmethod
    def get_crawl(cls, host, ip):
        """
        Get crawl from host

        :param host: [str] host name of target
        :param ip: [str] IP address from which the host name is resolved
        :return: [doscrawler.crawls.models.Crawl]
        """

        record, time, status = cls._crawl_host(host, ip)

        crawl = cls(host=host, record=record, time=time, status=status)

        return crawl

    def is_success(self):
        """
        Checks if crawl has been successful

        :return: [bool]
        """

        return True

    @staticmethod
    def crawl_host(host, ip):
        """
        Crawl host

        :param host: [str] host name of target
        :param ip: [str] IP address from which the host name is resolved
        :return: [tuple] request, response, request_time
        """

        # get status
        status = "failed"

        # add schema to host name
        ## too slow
        # if not re.match(r"(?:http|ftp|https)://", host):
        #    host_schema = f"http://{host}"
        host_schema = f"http://{host}"

        # define warc writer
        # warc_string = BytesIO()
        # warc_writer = WARCWriter(warc_string, warc_version='1.1', gzip=False)
        warc_writer = BufferWARCWriter(warc_version="1.1", gzip=True)

        # prepare request
        request = requests.Request(method="GET", url=host_schema, headers=settings.CRAWL_REQUEST_HEADER).prepare()

        # prepare write request
        warc_request_headers = StatusAndHeaders("GET / HTTP/1.0", request.headers, is_http_request=True)
        warc_request = warc_writer.create_warc_record(host_schema, "request", http_headers=warc_request_headers,
                                                      warc_content_type="application/http; msgtype=request")

        try:
            # try to get response on request
            # send request
            session = requests.Session()
            response = session.send(request, stream=True, timeout=settings.CRAWL_REQUEST_TIMEOUT)

            # prepare write response
            warc_response_payload = response.text.encode("utf-8")
            warc_response_headers = StatusAndHeaders("200 OK", response.headers, protocol="HTTP/1.0")
            warc_response = warc_writer.create_warc_record(uri=host_schema, record_type="response",
                                                           payload=BytesIO(warc_response_payload),
                                                           length=len(warc_response_payload),
                                                           http_headers=warc_response_headers,
                                                           warc_content_type="application/http; msgtype=response")

            # change status
            status = "succeeded"
        except Exception as e:
            # raised exception while request
            # prepare write metadata as response
            warc_response_payload = json.dumps({"error": str(type(e)), "error_desc": str(e)}).encode("utf-8")

            warc_response = warc_writer.create_warc_record(uri=host_schema, record_type="metadata",
                                                           payload=BytesIO(warc_response_payload),
                                                           length=len(warc_response_payload),
                                                           warc_content_type="application/json; msgtype=metadata")
            logging.warning(f"Request failed with {warc_response_payload}")

        # get request time
        warc_request_date = warc_request.rec_headers.get_header("WARC-Date")
        time = iso_date_to_datetime(warc_request_date).replace(tzinfo=timezone("Etc/UTC")).astimezone(
            timezone("Etc/UTC")).replace(tzinfo=None)

        # associate request and response
        warc_response_id = warc_response.rec_headers.get_header("WARC-Record-ID")
        warc_request.rec_headers.add_header("WARC-Concurrent-To", warc_response_id)

        # add ip address of target
        warc_ip_address = ip
        warc_request.rec_headers.add_header("WARC-IP-Address", warc_ip_address)
        warc_response.rec_headers.add_header("WARC-IP-Address", warc_ip_address)

        # write request and response in warc
        warc_writer.write_record(warc_request)
        warc_writer.write_record(warc_response)

        record = warc_writer.get_contents()

        return record, time, status

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the crawls for the DoS crawler.

"""

from faust import Record
from datetime import datetime
from dateutil.parser import parse as parse_date


class Crawl(Record, coerce=True, date_parser=parse_date):
    """
    Crawl model class
    """

    host: str
    request: str
    response: str
    request_time: datetime

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the WARCs for the DoS crawler.

"""

from faust import Record


class WARC(Record):
    """
    WARC model class
    """

    ip_address: str
    attack_start: str


#######################################################################
# TODO:                                                               #
#   - create service to write WARC for all targets whose attack ended #
#######################################################################

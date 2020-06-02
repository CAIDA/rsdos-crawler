#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the hosts for the DoS crawler.

"""

from faust import Record


class Host(Record):
    """
    Host model class
    """

    name: str
    ip: str

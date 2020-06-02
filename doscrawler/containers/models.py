#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the SWIFT containers for the DoS crawler.

"""

from faust import Record
from typing import List
from doscrawler.objects.models import Object


class Container(Record):
    """
    Container model class
    """

    name: str = "data-telescope-meta-dos"
    objects: List[Object]


##############################################################
# TODO:                                                      #
#   - get objects in container in date range                 #
#   - run periodic service to collect objects from container #
##############################################################

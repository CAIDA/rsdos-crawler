#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models of the objects in the Swift containers for the DoS crawler.

"""

from faust import Record
from typing import List
from doscrawler.targets.models import TargetLine


class Object(Record):
    """
    Object model class
    """

    name: str
    time: str
    targets: List[TargetLine]


########################################
# TODO:                                #
#   - get meta information from object #
#   - create targets from object       #
########################################

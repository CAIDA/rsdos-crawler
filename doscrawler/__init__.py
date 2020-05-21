#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

DoS Crawler
-----------

This module initializes the DoS crawler.

"""

__all__ = ["app"]
__author__ = "Stefan Scholz <stefan.scholz@uni.kn>"
__version__ = "0.1"

from .celery import app

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Schemas
-------

This module defines the schemas for the attacks in the DoS crawler.

"""

import io
import faust
import fastavro


class AttackSchema(faust.Schema):
    """
    Attack schema to parse attack vectors from other system
    """

    def loads_value(self, app, message, *, loads=None, serializer=None):
        """
        Loads values with attack schema

        :param app:
        :param message:
        :param loads:
        :param serializer:
        :return: [fastavro.reader]
        """

        return fastavro.reader(io.BytesIO(message.value))

    def loads_key(self, app, message, *, loads=None, serializer=None):
        """
        Loads keys with attack schema

        :param app:
        :param message:
        :param loads:
        :param serializer:
        :return: None
        """

        return None

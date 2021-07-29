#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models for the slack messages sent by the DoS crawler.

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

import logging
from typing import List
from slack import WebClient
from simple_settings import settings
from faust import Record


class Slack(Record, coerce=True, serializer="json"):
    """
    Slack model class
    """

    status: str
    title: str
    descriptions: List[str]

    @property
    def text(self):
        """
        Text of slack

        :return: [str] text of slack
        """

        text = ""

        if self.status == "success":
            text += f"*Hello! {self.title}* :tada:\n"
        elif self.status == "error":
            text += f"*Oops! {self.title}* :grimacing:\n"

        if self.descriptions:
            text += "--\n"
            text += "\n".join([f":arrow_right: {description}" for description in self.descriptions])
            text += "\n--\n"

        return text

    async def send(self):
        """
        Send slack

        :return:
        """

        if settings.SLACK_TOKEN and settings.SLACK_CHANNEL:
            # slack is configured in settings
            # get client
            client = WebClient(token=settings.SLACK_TOKEN)

            try:
                # post text with client
                client.chat_postMessage(channel=settings.SLACK_CHANNEL, text=self.text)
            except Exception as e:
                logging.error(f"Slack could not be send with text {self.text} because {e}")

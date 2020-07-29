#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Models
------

This module defines the models for the slack messages sent by the DoS crawler.

"""

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

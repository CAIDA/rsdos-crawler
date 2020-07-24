#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Services
--------

This module defines the services for the attacks in the DoS crawler.

"""

import random
import logging
from mode import Service
from datetime import datetime, timedelta, timezone
from simple_settings import settings
from doscrawler.app import app
from doscrawler.attacks.models import AttackVector
from doscrawler.attacks.topics import attack_topic


@app.service
class AttackService(Service):
    """
    Attack service
    """

    async def on_start(self):
        """
        Process when service is started

        :return:
        """

        logging.info("Service to maintain attacks is starting.")

    async def on_stop(self):
        """
        Process when service is stopped

        :return:
        """

        logging.info("Service to maintain attacks is stopping.")

    @Service.timer(settings.ATTACK_RANDOM_ATTACK_INTERVAL)
    async def _send_random_attack_vectors(self):
        """
        Send random attack vectors

        :return:
        """

        logging.info("Service to maintain attacks is sending random attack vectors.")

        attack_num = random.randint(0, 2)
        attack_ips = random.sample(["172.217.23.163", "208.80.154.232", "54.187.154.195", "192.172.226.78", "194.59.37.35"], attack_num)

        for attack_ip in attack_ips:
            # for each random attack ip
            # get latest time
            latest_time = datetime.now(timezone.utc) + timedelta(seconds=random.randint(-settings.ATTACK_RANDOM_ATTACK_INTERVAL+1, 0))
            # get start time
            start_time = latest_time + timedelta(seconds=random.randint(-2*settings.ATTACK_RANDOM_ATTACK_INTERVAL+1, -1))
            # get random attack vector
            attack_vector = AttackVector(
                target_ip=attack_ip,
                nr_attacker_ips=random.randint(0, 10000),
                nr_attacker_ips_in_interval=random.randint(0, 10000),
                nr_attacker_ports=random.randint(0, 10000),
                nr_target_ports=random.randint(0, 10000),
                nr_packets=random.randint(0, 10000),
                nr_packets_in_interval=random.randint(0, 10000),
                nr_bytes=random.randint(0, 10000),
                nr_bytes_in_interval=random.randint(0, 10000),
                max_ppm=random.randint(0, 10000),
                start_time=start_time,
                latest_time=latest_time,
            )
            # send random attack vector to get attack topic
            await attack_topic.send(value=attack_vector)

            logging.info(f"Service to maintain attacks has sent random attack vector with ip {attack_ip} start time {start_time} latest time {latest_time}.")

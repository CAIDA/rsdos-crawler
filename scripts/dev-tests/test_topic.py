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

import io
import json
import asyncio
import faust
import logging
import fastavro
import ipaddress
from faust import Record
from datetime import datetime, timezone, timedelta


class AttackVector(Record, coerce=True, serializer="json"):
    """
    Attack vector model class
    """

    target_ip: str
    start_time: datetime
    latest_time: datetime
    bin_time: datetime
    initial_packet_len: int
    target_protocol: int
    attacker_ip_cnt: int
    attack_port_cnt: int
    target_port_cnt: int
    packet_cnt: int
    icmp_mismatches: int
    byte_cnt: int
    max_ppm_interval: int

    @classmethod
    async def create_attack_vector(cls, attack):
        """
        Create attack vector from other format

        :param attack: [dict] attack
        :return: [doscrawler.attacks.models.AttackVector] created attack vector from attack
        """

        attack_vector = cls(**cls._get_parsed_attack(attack=attack))

        return attack_vector

    @staticmethod
    def _get_parsed_attack(attack):
        """
        Get parsed dictionary with attributes of attack vector from attack

        :param attack: [dict] attack
        :return: [dict] parsed dictionary with attributes of attack vector
        """

        logging.info(f"Raw attack {attack}")

        parsed_attack = {}

        parsed_attack["target_ip"] = str(ipaddress.IPv4Address(int(attack["target_ip"])))
        parsed_attack["start_time"] = datetime.fromtimestamp(int(attack["start_time_sec"]), timezone.utc) + timedelta(microseconds=int(attack["start_time_usec"]))
        parsed_attack["latest_time"] = datetime.fromtimestamp(int(attack["latest_time_sec"]), timezone.utc) + timedelta(microseconds=int(attack["latest_time_usec"]))
        parsed_attack["bin_time"] = datetime.fromtimestamp(int(attack["bin_timestamp"]), timezone.utc)
        parsed_attack["initial_packet_len"] = int(attack["initial_packet_len"])
        parsed_attack["target_protocol"] = int(attack["target_protocol"])
        parsed_attack["attacker_ip_cnt"] = int(attack["attacker_ip_cnt"])
        parsed_attack["attack_port_cnt"] = int(attack["attack_port_cnt"])
        parsed_attack["target_port_cnt"] = int(attack["target_port_cnt"])
        parsed_attack["packet_cnt"] = int(attack["packet_cnt"])
        parsed_attack["icmp_mismatches"] = int(attack["icmp_mismatches"])
        parsed_attack["byte_cnt"] = int(attack["byte_cnt"])
        parsed_attack["max_ppm_interval"] = int(attack["max_ppm_interval"])

        logging.info(f"Parsed attack {parsed_attack}")

        return parsed_attack



class AvroSchemaDecoder(faust.Schema):
    """An extension of Faust Schema class. The class is used by Faust when
    creating streams from Kafka topics. The decoder deserializes each message
    according to the AVRO schema injected in each message's header.
    """

    def loads_value(self, app, message, *, loads=None, serializer=None):
        return fastavro.reader(io.BytesIO(message.value))

    def loads_key(self, app, message, *, loads=None, serializer=None):
        return None


app = faust.App("test35", broker="kafka://kafka.rogues.caida.org:9392", topic_disable_leader=True)

attack_topic = app.topic("stardust.rsdos.attacks", value_type=bytes, schema=AvroSchemaDecoder())


@app.agent(attack_topic, concurrency=1)
async def get_attacks(attack_batches):
    async for attack_batch in attack_batches:
        for attack_vector in attack_batch:
            # get parsed attack vector from attack vector
            attack_vector = await AttackVector.create_attack_vector(attack=attack_vector)
            logging.info(attack_vector.asdict())

        await asyncio.sleep(5)

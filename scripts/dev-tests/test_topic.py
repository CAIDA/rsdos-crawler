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

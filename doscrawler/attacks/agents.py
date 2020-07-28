#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents working on the attacks in the DoS crawler.

"""

import logging
from simple_settings import settings
from doscrawler.app import app
from doscrawler.hosts.topics import get_host_topic
from doscrawler.attacks.models import Attack, AttackVector
from doscrawler.attacks.topics import attack_topic, change_attack_topic
from doscrawler.attacks.tables import attack_table, attack_candidate_table


@app.agent(attack_topic, concurrency=settings.ATTACK_CONCURRENCY)
async def get_attacks(attack_batches):
    """
    Get attacks from attack vectors

    :param attack_batches: [faust.types.streams.StreamT] stream of attack batches with attack vectors from attack topic
    :return:
    """

    logging.info("Agent to get attacks from attack vectors is ready to receive attack vectors.")

    async for attack_batch in attack_batches:
        for attack_vector in attack_batch:
            # get parsed attack vector from attack vector
            attack_vector = await AttackVector.create_attack_vector(attack=attack_vector)
            # get attack from attack vector for change attack topic
            attack = Attack(ip=attack_vector.target_ip, start_time=attack_vector.start_time, latest_time=attack_vector.latest_time, attack_vectors=[attack_vector])
            # send attack to change attack topic
            await change_attack_topic.send(key=f"add/{attack.ip}/{attack.start_time}", value=attack)


@app.agent(change_attack_topic, concurrency=1)
async def change_attacks(attacks):
    """
    Change attacks and attack candidates by new, newer, continuing, resolved, crawled attacks

    :param attacks: [faust.types.streams.StreamT] stream of attacks from change attack topic
    :return:
    """

    logging.info("Agent to change attacks is ready to receive attacks.")

    async for attack_key, attack in attacks.items():
        if attack_key.startswith("add"):
            # attack should be added
            if attack.is_alive_soon:
                # attack will be still alive after processing
                # look up attack candidate for attack
                attack_candidate = attack_candidate_table[attack.ip]

                if attack_candidate and attack_candidate.is_mergable_attack(attack=attack):
                    # attack candidate can be merged with new attack
                    if attack_candidate.start_time != attack.start_time or attack_candidate.latest_time != attack.latest_time:
                        # attack candidate has to be updated
                        # get start time
                        attack_start_time = min([attack_candidate.start_time, attack.start_time])
                        # get latest time
                        attack_latest_time = max([attack_candidate.latest_time, attack.latest_time])

                        if attack_candidate.start_time > attack.start_time:
                            # attack candidate started later than new attack
                            # get current attack
                            attack_current = attack_table[f"{attack_candidate.ip}/{attack_candidate.start_time}"]
                            # change attack in attack table
                            attack_table[f"{attack.ip}/{attack.start_time}"] = Attack(
                                ip=attack.ip, start_time=attack_start_time, latest_time=attack_latest_time,
                                attack_vectors=attack_current.attack_vectors, hosts=attack_current.hosts,
                                crawls=attack_current.crawls
                            )
                            # delete outdated attack
                            attack_table.pop(f"{attack_candidate.ip}/{attack_candidate.start_time}")

                        # get attack candidate
                        attack_candidate = Attack(ip=attack_candidate.ip, start_time=attack_start_time, latest_time=attack_latest_time)
                        # change attack candidate in attack candidate table
                        attack_candidate_table[attack_candidate.ip] = attack_candidate
                        # send attack candidate to get host topic
                        await get_host_topic.send(key=f"{attack_candidate.ip}/{attack_candidate.start_time}", value=attack_candidate)

                elif attack_candidate and attack_candidate.start_time > attack.latest_time:
                    # attack candidate cannot be merged with older attack
                    # older attack has no effect on current attack candidate and has no attack candidate thus
                    attack_candidate = None

                else:
                    # attack candidate cannot be merged with new attack or no attack candidate yet
                    # get attack candidate
                    attack_candidate = Attack(ip=attack.ip, start_time=attack.start_time, latest_time=attack.latest_time)
                    # change attack candidate in attack candidate table
                    attack_candidate_table[attack_candidate.ip] = attack_candidate
                    # send attack candidate to get host topic
                    await get_host_topic.send(key=f"{attack_candidate.ip}/{attack_candidate.start_time}", value=attack_candidate)

                if attack_candidate:
                    # attack has a valid candidate
                    # look up current attack for attack
                    attack_current = attack_table[f"{attack_candidate.ip}/{attack_candidate.start_time}"]

                    if attack_current:
                        # attack has already been added to attack table
                        # get attack vectors
                        attack_attack_vectors_current_keys = [f"{attack_vector.start_time}/{attack_vector.latest_time}" for attack_vector in attack_current.attack_vectors]
                        attack_attack_vectors_new = [attack_vector for attack_vector in attack.attack_vectors if f"{attack_vector.start_time}/{attack_vector.latest_time}" not in attack_attack_vectors_current_keys]
                        attack_attack_vectors = attack_current.attack_vectors + attack_attack_vectors_new
                        # get hosts
                        attack_hosts_current = attack_current.hosts
                        attack_hosts_new = [host for host in attack.hosts if host not in attack_hosts_current]
                        attack_hosts = attack_current.hosts + attack_hosts_new
                        # get crawls
                        attack_crawls_current_keys = [f"{crawl.host}/{crawl.time}" for crawl in attack_current.crawls]
                        attack_crawls_new = [crawl for crawl in attack.crawls if f"{crawl.host}/{crawl.time}" not in attack_crawls_current_keys]
                        attack_crawls = attack_current.crawls + attack_crawls_new
                        # get attack
                        attack = Attack(
                            ip=attack_candidate.ip, start_time=attack_candidate.start_time,
                            latest_time=attack_candidate.latest_time, attack_vectors=attack_attack_vectors,
                            hosts=attack_hosts, crawls=attack_crawls
                        )

                    else:
                        # attack has not yet been added to attack table
                        # get attack
                        attack = Attack(
                            ip=attack_candidate.ip, start_time=attack_candidate.start_time,
                            latest_time=attack_candidate.latest_time, attack_vectors=attack.attack_vectors,
                            hosts=attack.hosts, crawls=attack.crawls
                        )

                    # change attack in attack table
                    attack_table[f"{attack.ip}/{attack.start_time}"] = attack

                else:
                    # attack has no valid candidate
                    # look up current attack for attack
                    attack_current = attack_table[f"{attack.ip}/{attack.start_time}"]

                    if attack_current:
                        # attack has already been added to attack table
                        # get attack vectors
                        attack_attack_vectors_current_keys = [f"{attack_vector.start_time}/{attack_vector.latest_time}" for attack_vector in attack_current.attack_vectors]
                        attack_attack_vectors_new = [attack_vector for attack_vector in attack.attack_vectors if f"{attack_vector.start_time}/{attack_vector.latest_time}" not in attack_attack_vectors_current_keys]
                        attack_attack_vectors = attack_current.attack_vectors + attack_attack_vectors_new
                        # get hosts
                        attack_hosts_current = attack_current.hosts
                        attack_hosts_new = [host for host in attack.hosts if host not in attack_hosts_current]
                        attack_hosts = attack_current.hosts + attack_hosts_new
                        # get crawls
                        attack_crawls_current_keys = [f"{crawl.host}/{crawl.time}" for crawl in attack_current.crawls]
                        attack_crawls_new = [crawl for crawl in attack.crawls if f"{crawl.host}/{crawl.time}" not in attack_crawls_current_keys]
                        attack_crawls = attack_current.crawls + attack_crawls_new
                        # get attack
                        attack = Attack(
                            ip=attack.ip, start_time=attack.start_time, latest_time=attack.latest_time,
                            attack_vectors=attack_attack_vectors, hosts=attack_hosts, crawls=attack_crawls
                        )
                        # change attack in attack table
                        attack_table[f"{attack.ip}/{attack.start_time}"] = attack

        elif attack_key.startswith("delete"):
            # attack should be deleted
            # look up attack in attack candidate table
            attack_candidate_current = attack_candidate_table[attack.ip]

            if attack_candidate_current and attack_candidate_current.latest_time == attack.latest_time:
                # delete attack from attack candidate table
                attack_candidate_table.pop(f"{attack.ip}")

            # look up attack in attack table
            attack_current = attack_table[f"{attack.ip}/{attack.start_time}"]

            if attack_current and attack_current.latest_time == attack.latest_time:
                # delete attack from attack table
                attack_table.pop(f"{attack.ip}/{attack.start_time}")

        else:
            raise Exception(
                f"Agent to change attacks raised an exception because an attack has an unknown action. The key of the " \
                f"attack is {attack_key}."
            )

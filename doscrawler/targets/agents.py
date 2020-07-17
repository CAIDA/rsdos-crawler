#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Agents
------

This module defines the agents working on the targets for the DoS crawler.

"""

import logging
from simple_settings import settings
from doscrawler.app import app
from doscrawler.hosts.topics import get_host_topic
from doscrawler.targets.models import Target
from doscrawler.targets.topics import get_target_topic, change_target_candidate_topic, change_target_topic
from doscrawler.targets.tables import target_table, target_candidate_table


@app.agent(get_target_topic, concurrency=settings.TARGET_CONCURRENCY)
async def get_targets(target_lines):
    """
    Get targets from target lines

    :param target_lines: [faust.types.streams.StreamT] stream of target lines from target line topic
    :return:
    """

    logging.info("Agent to get targets from target lines is ready to receive target lines.")

    async for target_line_key, target_line in target_lines.items():
        # look up target candidate for target line
        target_line_target_candidate = target_candidate_table[target_line.target_ip]

        if target_line_target_candidate and target_line_target_candidate.is_mergable_target_line(target_line=target_line):
            # target candidate is within time window to merge with target candidate
            # update target
            target_target_lines = target_line_target_candidate.target_lines + [target_line]
            target_latest_time = max([target_line.latest_time for target_line in target_target_lines])
            target = Target(ip=target_line_target_candidate.ip, start_time=target_line_target_candidate.start_time,
                            latest_time=target_latest_time, target_lines=target_target_lines)

        else:
            # exists no mergable target candidate or target candidate is not within time window
            # create target
            target = Target(ip=target_line.target_ip, start_time=target_line.start_time, latest_time=target_line.latest_time,
                            target_lines=[target_line])

        # send target candidate to change target candidate topic for update
        await change_target_candidate_topic.send(key=f"add/{target.ip}", value=target)

        # send to change target topic to update target with intermediate result of target lines
        await change_target_topic.send(key=f"add/{target.ip}/{target.start_time}", value=target)

        # send target to get host topic to get host names
        await get_host_topic.send(key=f"{target.ip}/{target.start_time}", value=target)


@app.agent(change_target_candidate_topic, concurrency=1)
async def change_target_candidates(target_candidates):
    """
    Change target candidates from targets

    :param target_candidates: [faust.types.streams.StreamT] stream of targets from change target candidate topic
    :return:
    """

    logging.info("Agent to change target candidates is ready to receive target candidates.")

    async for target_candidate_key, target_candidate in target_candidates.items():
        if target_candidate_key.startswith("add"):
            # target candidate has to be added
            # update target candidate in target candidate table
            target_candidate_table[f"{target_candidate.ip}"] = target_candidate

        elif target_candidate_key.startswith("delete"):
            # target candidate has to be deleted
            # look up target candidate in target candidate table
            target_candidate_current = target_candidate_table[f"{target_candidate.ip}"]

            if target_candidate_current and target_candidate_current.latest_time == target_candidate.latest_time:
                # current target candidates has not changed in table
                # delete target candidate from target candidate table
                target_candidate_table.pop(f"{target_candidate_current.ip}")

        else:
            raise Exception(
                f"Agent to change target candidates raised an exception because a target has an unknown action. The " \
                f"key of the target candidate is {target_candidate_key}."
            )


@app.agent(change_target_topic, concurrency=1)
async def change_targets(targets):
    """
    Change target table by merged, resolved, crawled, retried and recrawled targets

    :param targets: [faust.types.streams.StreamT] stream of targets from target topic
    :return:
    """

    logging.info("Agent to change targets is ready to receive targets.")

    async for target_key, target in targets.items():
        if target_key.startswith("add"):
            # target should be added
            if target.get_ttl() < 5:
                # ignore targets after ttl and close to after ttl
                continue
            # target has to be added
            # look up target in target table
            target_current = target_table[f"{target.ip}/{target.start_time}"]

            if target_current:
                # target has already been stored in target table
                # get all target lines
                targetlines_current_keys = [f"{target_line.start_time}/{target_line.latest_time}" for target_line in target_current.target_lines]
                targetlines_new = [target_line for target_line in target.target_lines if f"{target_line.start_time}/{target_line.latest_time}" not in targetlines_current_keys]
                targetlines_all = target_current.target_lines + targetlines_new

                # get latest time
                latest_time = max([target_line.latest_time for target_line in targetlines_all])

                # get all hosts
                hosts_current = target_current.hosts.keys()
                hosts_new = [host for host in target.hosts.keys() if host not in hosts_current]
                hosts_update = [host for host in target.hosts.keys() if host in hosts_current]
                hosts_all = {host: list(set(target.hosts[host])) for host in hosts_new}

                for host in hosts_update:
                    crawls_current_time = [crawl.time for crawl in target_current.hosts[host]]
                    crawls_new = [crawl for crawl in target.hosts[host] if crawl.time not in crawls_current_time]
                    hosts_all[host] = list(set(target_current.hosts[host] + crawls_new))

                # update target in target table
                target_updated = Target(ip=target.ip, start_time=target.start_time, latest_time=latest_time,
                                        target_lines=targetlines_all, hosts=hosts_all)
                target_table[f"{target.ip}/{target.start_time}"] = target_updated

            else:
                # target has not yet been stored in target table
                for host in target.hosts.keys():
                    # for each host
                    # deduplicate crawls
                    target.hosts[host] = list(set(target.hosts[host]))
                # add target to target table
                target_table[f"{target.ip}/{target.start_time}"] = target

        elif target_key.startswith("delete"):
            # target has to be deleted
            # look up target in target table
            target_current = target_table[f"{target.ip}/{target.start_time}"]

            if target_current and target_current.latest_time == target.latest_time:
                # delete target from target table
                target_table.pop(f"{target_current.ip}/{target_current.start_time}")
        else:
            raise Exception(
                f"Agent to change targets raised an exception because a target has an unknown action. The key of the "\
                f"target is {target_key}."
            )

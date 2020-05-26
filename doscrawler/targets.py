#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Targets
-------

This module provides the functionalities together with targets in the DoS crawler.

NOTE: The target iterator is only temporary, because later IP addresses should be sent directly.

"""

import socket
import random


class TargetIterator(object):
    """
    Target iterator
    """

    def __init__(self, file, seed=None):
        """
        Initialize target iterator with IP addresses

        :param file: [str] directory to file with host names
        :param seed: [int] random seed, default = None
        :return: [iter] iterable with IP addresses
        """

        self.hosts = self.get_hosts(file)
        self.seed = random.seed(seed)

    def __iter__(self):
        """
        Iterate target iterator

        :return: [iter] iterable with IP addresses
        """

        return self

    def __next__(self):
        """
        Return next IP address in target iterator

        :return: [str] random IP address
        """

        try:
            # get random ip
            random_ip = self.get_random_ip()
            return random_ip
        except socket.gaierror as e:
            # skip host on address-related errors
            #print(e)
            return self.__next__()

    def get_random_ip(self):
        """
        Get random IP address

        :return: [str] random IP address
        :raises: [socket.gaierror] address-related errors
        """

        random_host = random.choice(self.hosts)
        random_ip = socket.gethostbyname(random_host)
        return random_ip

    @staticmethod
    def get_hosts(file):
        """
        Get host names from file

        :param file: [str] directory to file with host names
        :return: [list] list of host names
        """

        with open(file, mode="r") as file:
            hosts = [line.strip() for line in file.readlines()]
        return hosts


class Target(object):
    """
    Target object
    """

    def __init__(self, ip=None, file=None):
        """
        Initialize target

        :param ip: [str] IP address, if None then file needs to be given, default = None
        :param file: [str] directory to file with hosts, if None then ip needs to be given, default = None
        """

        if (ip and file) or (not ip and not file):
            raise ValueError("You must initialize a target either with an IP address or file directory.")

        if file:
            ip = next(TargetIterator(file=file, seed=None))

        self.ip = ip
        self.hosts = self.get_hosts()

    def get_hosts(self):
        """
        Get host names of IP address

        :return: [list] host names
        """

        try:
            # get hosts
            hostname, aliaslist, _ = socket.gethostbyaddr(self.ip)
            hosts = list(set([hostname] + aliaslist))
            return hosts
        except socket.herror as e:
            # return no hosts on address-related errors
            #print(e)
            return []

        ###############################################################
        # TODO: implement custom exception for address-related errors #
        ###############################################################

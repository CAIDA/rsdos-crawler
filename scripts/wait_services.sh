#!/bin/bash
# -*- coding: utf-8 -*-

#
# Wait services
# -------------
#
# This script makes sure that the doscrawler does not start before kafka is available.
#


set -e

cmd="$@"

until nc -vz ${BROKER_NAME} ${BROKER_PORT}; do
  >&2 echo "Waiting for Kafka to be ready..."
  sleep 2
done

>&2 echo "Kafka is available!"

echo "Executing command ${cmd}"
exec $cmd

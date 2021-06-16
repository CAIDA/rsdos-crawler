#!/bin/bash
# This is a script that automatically sends an email to an admin when the disk usage is
# higher than a designated THRESHOLD.

CURRENT=$(df / | grep / | awk '{ print $5}' | sed 's/%//g')
THRESHOLD=80

if [ "$CURRENT" -gt "$THRESHOLD" ] ; then
  mail -s 'Disk Space Alert' -a "From: rsdos-crawler <limbo@stardust-dos-crawler>" mingwei@caida.org << EOF
Your root partition remaining free space is critically low. Used: $CURRENT%
EOF
fi

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

import os
import json
import gzip
import pprint
import itertools
from datetime import datetime

# get dumps
dumps_dir = "doscrawler/data/"
dumps = [os.path.join(dumps_dir, file) for file in os.listdir(dumps_dir) if file.endswith(".json.gz")]


def date_parser(value):
    """
    Parse dates in dump
    """

    if isinstance(value, dict):
        for k, v in value.items():
            value[k] = date_parser(v)
    elif isinstance(value, list):
        for index, row in enumerate(value):
            value[index] = date_parser(row)
    elif isinstance(value, str) and value:
        try:
            if value.startswith("WARC"):
                value = ""
            else:
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
        except (ValueError, AttributeError):
            pass
    return value


# get attacks
attacks = [json.load(gzip.open(dump, "rt", encoding="utf-8"), object_hook=date_parser)["attacks"] for dump in dumps]

# print data
pp = pprint.PrettyPrinter(depth=10)
pp.pprint(attacks[0][:10])

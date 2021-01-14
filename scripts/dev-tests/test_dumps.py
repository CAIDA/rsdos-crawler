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

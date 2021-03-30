import argparse
import gzip
import ipaddress
import json
import os
import sys
import requests

import wandio
from dotenv import load_dotenv
from swiftclient.service import SwiftService, SwiftError


class SwiftUtils:
    def __init__(self, env=None):
        # load swift credentials
        load_dotenv(env, override=True)
        swift_auth_options = {
            "auth_version": '3',
            "os_username": os.environ.get('OS_USERNAME', None),
            "os_password": os.environ.get('OS_PASSWORD', None),
            "os_project_name": os.environ.get('OS_PROJECT_NAME', None),
            "os_auth_url": os.environ.get('OS_AUTH_URL', None),
        }

        self.auth_options = swift_auth_options
        assert not any([option is None for option in self.auth_options.values()])
        self.swift_service = SwiftService(self.auth_options)
        print(self.auth_options)

    def swift_files_generator(self, container_name):
        """
        Generate swift files in the specified container within start and end time range (inclusive).
        :param container_name:
        :return:
        """
        try:
            list_parts_gen = self.swift_service.list(container=container_name)
            for page in list_parts_gen:
                if page["success"]:
                    for item in page["listing"]:
                        yield item["name"]
                else:
                    raise page["error"]
        except SwiftError as e:
            os.error(e.value)
        except ValueError as e:
            os.error(e)
        except:
            e = sys.exc_info()[0]
            print(e)
            raise e


def host_is_url(host_str: str):
    if host_str == "":
        return False
    try:
        ipaddress.ip_address(host_str)
        return False
    except ValueError:
        # not IP
        return True


domain_count_cache = {}


def lookup_domain_count(ip_str):
    if ip_str in domain_count_cache:
        return domain_count_cache[ip_str]
    count = requests.get(f"http://hammer.caida.org:8080/count/{ip_str}").json()["count"]
    domain_count_cache[ip_str] = count
    return count


def main():
    parser = argparse.ArgumentParser(description="""
    Generates entities for the Charthouse Metadata Database
    """)

    parser.add_argument('-e', '--env',
                        nargs='?', required=True,
                        help='envfile path',
                        default="/home/limbo/.stardust-creds")

    opts, _ = parser.parse_known_args()

    swift = SwiftUtils(opts.env)
    of = gzip.open("filtered_attacks.jsonl.gz", "wt")
    for fn in swift.swift_files_generator("data-telescope-meta-dos-crawler"):
        print(fn)
        with wandio.open(f"swift://data-telescope-meta-dos-crawler/{fn}", options=swift.auth_options) as in_file:
            for line in in_file:
                data = json.loads(line)
                for attack in data["attacks"]:

                    # make sure attacked ip is on commoncrawl db and has less than 5 matches
                    count = lookup_domain_count(attack["ip"])
                    if count > 5 or count < 1:
                        continue

                    if len(attack["hosts"]) == 0 or not any([host_is_url(h) for h in attack['hosts']]):
                        # not hosts, or all hosts are ips
                        continue

                    # filter for successful crawls to URLs, not IPs
                    crawls = [
                        crawl for crawl in attack["crawls"] if
                        host_is_url(crawl["host"]) and 200 <= crawl["status"] < 300
                    ]

                    if len(crawls) > 0:
                        print(f"outputting attack with {len(crawls)} good crawls")
                        attack["crawls"] = crawls
                        of.write(json.dumps(attack) + "\n")
                        of.flush()
    of.close()


if __name__ == '__main__':
    main()

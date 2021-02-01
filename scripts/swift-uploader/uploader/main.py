#!/usr/bin/env python3
import argparse
import glob
import os
from swiftclient.service import SwiftService, SwiftUploadObject
from dotenv import load_dotenv


class SwiftUtils:
    def __init__(self, env):
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

    def upload(self, filename, delete_on_success=True):
        timestr = filename.split("-")[-1].split(".")[0]
        year = timestr[0:4]
        month = timestr[4:6]
        day = timestr[6:8]
        dir_path = "year={}/month={}/day={}".format(year, month, day)
        dst = "{}/{}".format(dir_path, filename.split("/")[-1])
        for r in self.swift_service.upload("data-telescope-meta-dos-crawler", [SwiftUploadObject(filename, dst)]):
            if r['success']:
                if 'object' in r:
                    print("\tuploaded: {}".format(r['object']))
                if delete_on_success and (os.path.isfile(filename) or os.path.islink(filename)):
                    print("\toriginal file deleted {}".format(filename))
                    os.remove(filename)


def main():
    parser = argparse.ArgumentParser(description="""
    Generates entities for the Charthouse Metadata Database
    """)

    parser.add_argument('-d', '--dir',
                        nargs='?', required=False,
                        help='directory to watch',
                        default="/home/limbo/rsdos-crawler/data/dumps")
    parser.add_argument('-e', '--env',
                        nargs='?', required=False,
                        help='envfile path',
                        default="/home/limbo/.stardust-creds")
    parser.add_argument("-D", "--delete", action="store_true", default=False,
                        help="delete original file on upload success")

    opts, _ = parser.parse_known_args()

    swift_utils = SwiftUtils(env=opts.env)
    files = []
    for filename in glob.glob("{}/*.gz".format(opts.dir)):
        print("to upload: {}".format(filename))
        files.append(filename)
        swift_utils.upload(filename, delete_on_success=opts.delete)

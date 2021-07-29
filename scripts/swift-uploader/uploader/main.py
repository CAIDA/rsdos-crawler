#!/usr/bin/env python3

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

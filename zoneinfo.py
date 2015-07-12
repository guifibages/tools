#!/usr/bin/env python
from __future__ import print_function

import argparse
import logging
import os
import time

import requests
import libcnml


# http://stackoverflow.com/a/16695277
def DownloadFile(url, local_filename):
    logging.warning("Downloading %s to %s" % (url, local_filename))
    r = requests.get(url)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return


class ZoneInfo():
    def __init__(self, zone, cnml_cache="/tmp",
                 cnml_base="http://guifi.net/ca/guifi/cnml"):
        self.zone = zone
        self.cnml_base = cnml_base
        self.cnml_cache = cnml_cache
        self.zone_id = self.get_zone_id()
        self.cnml = self.get_zone(self.zone_id)

    def get_zone_id(self):
        try:
            zone_id = int(self.zone)
        except ValueError:
            zones = self.get_zone(3671, "zones")
            result = sorted(filter(lambda z: self.zone in z.title.lower(),
                                   zones.getZones()), key=lambda z: z.id)
            zone_id = result[0].id
        return zone_id

    def get_zone(self, zone, kind="detail"):
        cnml_file = "{}/{}.{}.cnml".format(self.cnml_cache, zone, kind)
        cnml_url = "{}/{}/{}".format(self.cnml_base, zone, kind)
        try:
            age = time.time() - os.path.getmtime(cnml_file)
            if age > 24*3600:
                logging.warning("File age %s" % age)
                logging.warning("Too old, redownload")
                DownloadFile(cnml_url, cnml_file)
        except OSError:
            logging.warning("%s does not exist" % cnml_file)
            DownloadFile(cnml_url, cnml_file)
        return libcnml.CNMLParser(cnml_file)

    def list(self, kind):
        getattr(self, kind)()

    def zones(self):
        for z in self.cnml.getZones():
            print(z.title, z.id)

    def nodes(self):
        for n in self.cnml.getNodes():
            print(n.title, n.id)

    def multi(self):
        for sn in filter(lambda n: n.totalLinks > 1, self.cnml.getNodes()):
            print(sn.title, "http://guifi.net/en/node/{0}".format(sn.id))

    def st(self):
        for st in filter(lambda n: len(n.radios) > 1, self.cnml.getDevices()):
            print("{} {} http://guifi.net/en/node/{}".format(
                st.parentNode.title, st.title, st.id))


def main():
    parser = argparse.ArgumentParser(
        description='Get information from Guifi Zones.')
    opt_list = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('zone', nargs="?", default=3671,
                        help="Zone to work with")
    opt_list.add_argument('-z', dest='kind', action="store_const",
                          const='zones', default="zones",
                          help="List zones")
    opt_list.add_argument('-n', dest='kind', action="store_const",
                          const='nodes', default="zones",
                          help="List nodes")
    opt_list.add_argument('-m', dest='kind', action="store_const",
                          const='multi', default="zones",
                          help="List nodes with multiple links")
    opt_list.add_argument('-s', dest='kind', action="store_const",
                          const='st', default="zones",
                          help="List sts")

    args = parser.parse_args()
    zi = ZoneInfo(args.zone)
    zi.list(args.kind)

if __name__ == "__main__":
    main()

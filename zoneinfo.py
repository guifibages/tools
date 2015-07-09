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
    def __init__(self, zone):
        self.zone = zone
        self.zone_id = self.get_zone_id()
        self.cnml = ZoneInfo.get_zone(self.zone_id)

    def get_zone_id(self):
        try:
            zone_id = int(self.zone)
        except ValueError:
            zones = ZoneInfo.get_zone(3671, "zones")
            result = sorted(filter(lambda z: self.zone in z.title.lower(),
                                   zones.getZones()), key=lambda z: z.id)
            zone_id = result[0].id
        return zone_id

    def zones(self):
        for z in self.cnml.getZones():
            print(z.title, z.id)

    def multi(self):
        for sn in filter(lambda n: n.totalLinks > 1, self.cnml.getNodes()):
            print(sn.title, "http://guifi.net/en/node/{0}".format(sn.id))

    def get_zone(zone, kind="detail"):
        cnml_file = "/tmp/{0}.{1}.cnml".format(zone, kind)
        cnml_url = "http://guifi.net/ca/guifi/cnml/{0}/{1}".format(zone, kind)
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
        m = getattr(self, kind)
        m()


def main():
    parser = argparse.ArgumentParser(
        description='Get information from Guifi Zones.')
    parser.add_argument('zone', nargs="?", default=3671,
                        help="Zone to work with")
    parser.add_argument('-z', dest='kind', action="store_const",
                        const='zones', default="zones",
                        help="List zones")
    parser.add_argument('-m', dest='kind', action="store_const",
                        const='multi', default="zones",
                        help="List ndoes with multiple links")

    args = parser.parse_args()
    zi = ZoneInfo(args.zone)
    zi.list(args.kind)

if __name__ == "__main__":
    main()

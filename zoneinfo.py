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


def get_zone(zone=3671, kind="detail"):
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


def get_zone_id(zone):
    try:
        zone_id = int(zone)
    except ValueError:
        zones = get_zone(3671, "zones")
        result = sorted(filter(lambda z: zone in z.title.lower(),
                               zones.getZones()), key=lambda z: z.id)
        zone_id = result[0].id
    return zone_id


def list_zones(zone_id):
    cnml = get_zone(zone_id, "zones")
    for z in cnml.getZones():
        print(z.title, z.id)


def display_zone(zone_id):
    cnml = get_zone(zone_id)
    for sn in filter(lambda n: n.totalLinks > 1, cnml.getNodes()):
        print(sn.title, "http://guifi.net/en/node/{0}".format(sn.id))


def main():
    parser = argparse.ArgumentParser(
        description='Get information from Guifi Zones.')
    parser.add_argument('zone', nargs="?", default=3671,
                        help="Zone to work with")
    parser.add_argument('-z', dest='zone_list', action="store_true",
                        help="List zones")
    args = parser.parse_args()
    zone_id = get_zone_id(args.zone)
    if (args.zone_list):
        list_zones(zone_id)
    else:
        display_zone(zone_id)

if __name__ == "__main__":
    main()

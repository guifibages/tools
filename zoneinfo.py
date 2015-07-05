#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# Requires the following modules
#   apt-get install python-requests python-bs4
#   pip install requests beautifulsoup4 netaddr
from __future__ import print_function
import sys
import argparse
import os
import time

import requests
import libcnml


# http://stackoverflow.com/a/14981125
def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)


# http://stackoverflow.com/a/16695277
def DownloadFile(url, local_filename):
    warning("Downloading %s to %s" % (url, local_filename))
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
            warning("File age %s" % age)
            warning("Too old, redownload")
            DownloadFile(cnml_url, cnml_file)
    except OSError:
        warning("%s does not exist" % cnml_file)
        DownloadFile(cnml_url, cnml_file)
    return libcnml.CNMLParser(cnml_file)


def list_zones():
    cnml = get_zone(3671, "zones")
    for z in cnml.getZones():
        print(z.title, z.id)


def display_zone(zone):
    try:
        zone_id = int(zone)
    except ValueError:
        zones = get_zone(3671, "zones")
        result = filter(lambda z: zone in z.title.lower(), zones.getZones())
        zone_id = next(result).id
    cnml = get_zone(zone_id)
    for sn in filter(lambda n: n.totalLinks > 1, cnml.getNodes()):
        print(sn.title, "http://guifi.net/en/node/{0}".format(sn.id))


def main():
    parser = argparse.ArgumentParser(description='Get information from Guifi Zones.')
    parser.add_argument('zone', nargs="?", help="Zone to work with")
    parser.add_argument('-l', '--list', action="store_true", help="List zones")
    args = parser.parse_args()
    if (args.list):
        list_zones()
    else:
        display_zone(args.zone)

if __name__ == "__main__":
    main()

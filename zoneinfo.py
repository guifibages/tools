#!/usr/bin/env python
from __future__ import print_function

import argparse
import ipaddress
import json
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


class SuperTrasto(dict):
    def __init__(self, device):
        self.device = device
        self['node'] = self.node = dict(title=device.parentNode.title,
                                        id=device.parentNode.id)
        self['id'] = self.id = device.id
        self['title'] = self.title = device.title
        self['ips'] = self.ips = [i.ipv4 for i in device.interfaces.values()]
        self['main_ip'] = self.main_ip = str(sorted([ipaddress.IPv4Address(ip)
                                                     for ip in self.ips])[0])

    def __str__(self):
        return self.title

    def output_csv(self):
        return ",".join([str(self.id), str(self.title), str(self.main_ip)])


class ZoneInfo():
    def __init__(self, zone, cnml_cache="/tmp",
                 cnml_base="http://guifi.net/ca/guifi/cnml",
                 node_base="http://guifi.net/en/node",
                 output_format="json"):

        self.output = getattr(self, "output_" + output_format)
        self.zone = zone
        self.node_base = cnml_base
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

    def output_json(self, r):
        print(json.dumps(r, indent=True))

    def output_csv(self, r):
        for l in r:
            try:
                print(l.output_csv())
            except AttributeError:
                print("{},{}".format(l['id'], l['title']))

    def output_human(self, r):
        for l in r:
            try:
                print(l.output_human())
            except AttributeError:
                print("{:>6} {:>18}".format(l['id'], l['title']))

    def list(self, kind):
        r = getattr(self, "list_" + kind)()
        self.output(r)

    def list_zones(self):
        return [dict(id=z.id, title=z.title) for z in self.cnml.getZones()]

    def list_nodes(self):
        return [dict(id=n.id, title=n.title) for n in self.cnml.getNodes()]

    def list_st(self):
        return [SuperTrasto(st)
                for st in filter(lambda n: len(n.radios) > 1,
                                 self.cnml.getDevices())]


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
    opt_list.add_argument('-s', dest='kind', action="store_const",
                          const='st', default="zones",
                          help="List sts")
    parser.add_argument('-f', dest='output_format', default="json",
                        help="Output format")

    args = parser.parse_args()
    zi = ZoneInfo(args.zone, output_format=args.output_format)
    zi.list(args.kind)

if __name__ == "__main__":
    main()

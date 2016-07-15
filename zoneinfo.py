#!/usr/bin/env python3

import argparse
from ipaddress import ip_address, ip_network
import json
import logging
import os
import pathlib
import time

import requests
import libcnml

if os.getenv('DEBUG'):
    libcnml.logger.setLevel(logging.DEBUG)
cnml_cache = pathlib.Path.home() / '.local/guifibages/cnml_cache'


# http://stackoverflow.com/a/16695277
def DownloadFile(url, local_file, chunk_size=8192):
    logging.warning("Downloading %s to %s" % (url, local_file))
    r = requests.get(url)
    with local_file.open('wb') as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return


class SuperTrasto(dict):
    def __init__(self, device):
        guifi_public_network = ip_network('10.0.0.0/8')
        self.device = device
        self['node'] = self.node = dict(title=device.parentNode.title,
                                        id=device.parentNode.id)
        self['id'] = self.id = device.id
        self['title'] = self.title = device.title
        self['ips'] = self.ips = [
            i.ipv4 for i in device.interfaces.values()
            if i.ipv4 != ''
        ]
        self['mainipv4'] = self.mainipv4 = (
            None if device.mainipv4 == '' else device.mainipv4
        )

    def __str__(self):
        return self.title

    def output_human(self):
        return("{:>6} {:<18} {:<18}".format(self.id, self.title,
                                            self.mainipv4))

    def output_csv(self):
        return ",".join([str(self.id), str(self.title), str(self.mainipv4)])


class ZoneInfo():
    def __init__(self, zone, cnml_cache=cnml_cache,
                 cnml_base="http://guifi.net/ca/guifi/cnml",
                 node_base="http://guifi.net/en/node",
                 output_format="json"):

        self.output = getattr(self, "output_" + output_format)
        self.zone = zone
        self.node_base = cnml_base
        self.cnml_base = cnml_base
        if not cnml_cache.exists():
            cnml_cache.mkdir(parents=True)
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
        filename = '{}.{}.cnml'.format(zone, kind)
        cnml_file = self.cnml_cache / filename
        cnml_url = "{}/{}/{}".format(self.cnml_base, zone, kind)
        try:
            age = time.time() - cnml_file.stat().st_mtime
            if age > 24*3600:
                logging.warning("File age %s" % age)
                logging.warning("Too old, redownload")
                DownloadFile(cnml_url, cnml_file)
        except OSError:
            logging.warning("%s does not exist" % cnml_file)
            DownloadFile(cnml_url, cnml_file)
        return libcnml.CNMLParser(str(cnml_file))

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
                print("{:>6} {:<18}".format(l['id'], l['title']))

    def list(self, kind):
        r = getattr(self, "list_" + kind)()
        self.output(r)

    def list_zones(self):
        return [dict(id=z.id, title=z.title) for z in self.cnml.get_zones()]

    def list_nodes(self):
        return [dict(id=n.id, title=n.title) for n in self.cnml.get_nodes()]

    def list_st(self):
        return [SuperTrasto(st)
                for st in filter(lambda n: len(n.radios) > 1,
                                 self.cnml.get_devices())]


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
    parser.add_argument('-f', dest='output_format', default="human",
                        help="Output format")

    args = parser.parse_args()

    zi = ZoneInfo(args.zone, cnml_cache=cnml_cache,
                  output_format=args.output_format)
    zi.list(args.kind)

if __name__ == "__main__":
    main()

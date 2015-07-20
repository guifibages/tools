#!/usr/bin/env python

import argparse

import zoneinfo


def main():
    parser = argparse.ArgumentParser(
        description='Backup Guifi SuperTrastos in a zone.')
    parser.add_argument('zone', nargs="?", default=3671,
                        help="Zone to backup")

    args = parser.parse_args()
    zi = zoneinfo.ZoneInfo(args.zone)
    zi.list("st")

if __name__ == "__main__":
    main()

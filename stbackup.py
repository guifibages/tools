#!/usr/bin/env python

import argparse
import pathlib
import datetime

import zoneinfo


class STBackup(zoneinfo.SuperTrasto):
    def __init__(self, st, backup_root="/tmp"):
        self.st = st
        backup_path = pathlib.Path(backup_root,
                                   datetime.date.today().isoformat())
        self.file = pathlib.Path(backup_path,
                                 st.node['title'], st.title + ".rsrc")

    def write(self):
        pass

    def check(self):
        pass


def main():
    parser = argparse.ArgumentParser(
        description='Backup Guifi SuperTrastos in a zone.')
    parser.add_argument('zone', nargs="?", default=3671,
                        help="Zone to backup")

    args = parser.parse_args()
    zi = zoneinfo.ZoneInfo(args.zone)

    for st in zi.list_st():
        backup = STBackup(st)
        print(backup.file)

if __name__ == "__main__":
    main()

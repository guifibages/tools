#!/usr/bin/env python

import argparse
import pathlib
import datetime

import paramiko
import zoneinfo


class STBackup():
    def __init__(self, st, backup_root="/tmp"):
        self.st = st
        backup_path = pathlib.Path(backup_root,
                                   datetime.date.today().isoformat())
        self.dir = pathlib.Path(backup_path, st.node['title'])
        self.file = pathlib.Path(self.dir, st.title + ".rsrc")

    def export(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.st.mainipv4, username='guest', password="",
                    allow_agent=False, look_for_keys=False, timeout=5)
        stdin, stdout, stderr = ssh.exec_command("/export")
        self.rsrc = stdout.read()
        self.write()

    def write(self):
        if not self.dir.exists():
            self.dir.mkdir(parents=True)

        with self.file.open("wb") as f:
            f.write(self.rsrc)

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
        backup.export()
        print(backup.st)

if __name__ == "__main__":
    main()

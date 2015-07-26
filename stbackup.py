#!/usr/bin/env python

import argparse
import pathlib
import datetime
import json
import logging

import paramiko
import zoneinfo


class STBackup():
    def __init__(self, st, backup_root="/tmp/stbackup"):
        self.st = st
        self.dir = pathlib.Path(backup_root, st.node['title'])
        if not self.dir.exists():
            self.dir.mkdir(parents=True)

        filename = ".".join([st.title, datetime.date.today().isoformat(),
                             "rsrc"])
        self.file = pathlib.Path(self.dir, filename)
        self.current = pathlib.Path(self.dir, ".".join([st.title, "rsrc"]))
        self.last = ""
        self.rsrc = ""
        if self.current.exists():
            with self.current.open(newline='') as r:
                self.last = str(r.read())
        self.error = None

    def export(self):
        ssh = paramiko.SSHClient()
        logging.getLogger("paramiko.transport").disabled = True
        try:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.st.mainipv4, username='guest', password="",
                        allow_agent=False, look_for_keys=False, timeout=5)
            stdin, stdout, stderr = ssh.exec_command("/export")
            # The first line includes the time
            self.rsrc = "".join(stdout.readlines()[1:])
            if self.need_backup():
                self.write()
        except paramiko.ssh_exception.AuthenticationException:
            self.error = "Authentication Error"
        except paramiko.ssh_exception.SSHException as e:
            self.error = e

    def write(self):
        with self.file.open("w") as f:
            f.write(self.rsrc)
        if self.current.exists():
            self.current.unlink()
        self.current.symlink_to(self.file.relative_to(self.dir))

    def need_backup(self):
        return self.last != self.rsrc

    def status(self):
        return dict(st=self.st.title, changes=self.need_backup(),
                    error=str(self.error))

    def __str__(self):
        return json.dumps(self.status())

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
        print(backup)

if __name__ == "__main__":
    main()

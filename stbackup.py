#!/usr/bin/env python3

import argparse
from collections import UserDict
import datetime
import json
import logging
from os import getenv
import pathlib

import paramiko
import zoneinfo


class GBConfig(UserDict):
    def __init__(self):
        config_file = pathlib.Path.home() / '.local/guifibages/config.json'
        with config_file.open() as f:
            self.data = json.load(f)

class STBackup():
    def __init__(self, st, backup_root="/tmp/stbackup", username='guest',
                 password=''):
        self.st = st
        self.username = username
        self.password = password
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
            ssh.connect(self.st.mainipv4, username=self.username,
                        password=self.password, allow_agent=False,
                        look_for_keys=False, timeout=5)
            stdin, stdout, stderr = ssh.exec_command("/export")
            # The first line includes the time
            self.rsrc = "".join(stdout.readlines()[1:])
            if self.need_backup():
                self.write()
        except paramiko.ssh_exception.AuthenticationException:
            self.error = "Authentication Error"
        except (paramiko.ssh_exception.NoValidConnectionsError,
                paramiko.ssh_exception.SSHException) as e:
            self.error = e
        except OSError as error:
            if error.errno == 113:
                self.error = "No route to host."
            else:
                raise error

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
    config = GBConfig()
    parser = argparse.ArgumentParser(
        description='Backup Guifi SuperTrastos in a zone.')
    parser.add_argument('zone', nargs="?", default=3671,
                        help="Zone to backup")

    args = parser.parse_args()
    zi = zoneinfo.ZoneInfo(args.zone)
    password = getenv('GBPASSWORD', '')
    for st in zi.list_st():
        backup_root = pathlib.Path.home() / '.local/guifibages/stbackup'
        backup = STBackup(
            st, backup_root=backup_root,
            username=config['stbackup']['username'],
            password=config['stbackup']['password'],
        )
        backup.export()
        print(backup)

if __name__ == "__main__":
    main()

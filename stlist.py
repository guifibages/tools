#!/usr/bin/env py
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# Requires the following modules
#   apt-get install python-requests python-bs4
#   pip install requests beautifulsoup4 netaddr
from __future__ import print_function
import sys
import requests
import os
import time
from bs4 import BeautifulSoup

zone=2426
cnml_file="/tmp/%s.cnml" % zone
cnml_url="http://guifi.net/ca/guifi/cnml/%s/detail" % zone

# http://stackoverflow.com/a/14981125
def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

# http://stackoverflow.com/a/16695277
def DownloadFile(url, local_filename):
    warning( "Downloading %s to %s" % ( url, local_filename) )
    r = requests.get(url)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return 
try:
    age=time.time() - os.path.getmtime(cnml_file)
    if age > 3600*4:
        warning( "File age %s" % age )
        warning( "Too old, redownload")
        DownloadFile(cnml_url, cnml_file)
except OSError:
    warning( "%s does not exist" % cnml_file)
    DownloadFile(cnml_url, cnml_file)


def is_st(tag):
    if tag.name == "device" and len(tag.find_all("radio")) > 1:
        return True
    else:
        return False
with open(cnml_file, 'r') as f:
    cnml = BeautifulSoup(f.read())
for st in cnml.find_all(is_st):
    print("%6s %30s http://guifi.net/ca/guifi/device/%s" % (st["id"], st["title"], st["id"]))

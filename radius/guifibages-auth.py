#!/usr/bin/env python
import os

def log(logstring):
    with open("/var/log/freeradius/guifibages-radius-auth.log", "a") as myfile:
        myfile.write("%s\n" % logstring)

for key, val in os.environ.items():
    log("%s = %s" % (key, val))

valid_users=[
        '"ignacio.torres"',
        '"albert.homs"',
        '"francisco.delaguila"',
        '"gil.obradors"',
        '"josep.figueres"',
        '"xavier.martinez"'
        ]
valid_stations=[
        '"10.228.17.24"']
if os.environ['USER_NAME'] in valid_users:
    if os.environ['CALLING_STATION_ID'] in valid_stations:
        print "Auth-Type := Accept"
        log("!Ignacio")
else:
    log(os.environ['USER_NAME'])

exit(0)

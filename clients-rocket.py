#!/usr/bin/env python
# Requires the requests module
#   apt-get install python-requests
#   pip install requests

import requests
import sys
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 

class Antenna:
	def __init__(self,host,username="guest", password=""):
		self.host = host
		self.http_client = requests.Session()
		self.http_client.get("https://%s/login.cgi" % host, verify=False)
		login = self.http_client.post("https://%s/login.cgi" % host, verify=False,
			data={'username': username, 'password': password, 'uri': 'sta.cgi'}, files={'b': 'b'}) # use files to force multipart/form-data
		self.status()

	def status(self):
		self.status = self.http_client.get("https://%s/status.cgi" % self.host, verify=False).json()
		self.links  = self.http_client.get("https://%s/sta.cgi" % self.host, verify=False).json()
		self.hostname = self.status['host']['hostname']
		self.fwversion = self.status['host']['fwversion']

	def acl(self):
		r = self.http_client.get("https://%s/macacl.cgi" % self.host, verify=False)
		print r.content

	def __str__(self):
		r = "### %s (%s AirOS %s)\n" % (self.hostname, self.host, self.fwversion)
		r = r + "%14s %15s  %8s %7s  %3s %6s %8s\n" % ("Name", "IP", "Priority", "Quality", "CCQ", "Signal", "Distance")
		airmax_priorities = ["High","Medium","Low","None"]
		for l in self.links:
			priority = airmax_priorities[l['airmax']['priority']]
			if l['airmax']['priority'] == 0 and l['airmax']['quality'] == 0:
				priority = "N/A"
			r = r + "%14s %15s  %8s %7.0f  %3.0f %6.2f %6.1fKm\n" % (
				l['name'], l['lastip'], priority, l['airmax']['quality'],
				l['ccq'], l['signal'], l['distance']/1000)
		return r

if __name__ == "__main__":	
	hosts = sys.argv[1:]
	pool = ThreadPool(12)
	results=[]
	def next(address):
		a=Antenna(address)
		results.append(a)

	pool.map(next,hosts)
	pool.close()
	pool.join()
	for r in results:
		print r

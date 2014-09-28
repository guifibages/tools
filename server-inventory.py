#!/usr/bin/env python
from __future__ import print_function
import sys
import paramiko
import socket
from pprint import pprint
from netaddr import IPNetwork
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 

def connect(ip):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	# print("Testing",ip)
	for password in passwords:
		try:
			ssh.connect(ip, username='root', password=password,allow_agent=False,look_for_keys=False,timeout=5)
			stdin, stdout, stderr = ssh.exec_command("uname -n")
			results[ip] ={"hostname":"".join(stdout.readlines()).strip(),"password": password}
			return
		except paramiko.ssh_exception.AuthenticationException:
			pass
		except Exception,e:
			results[ip] = {"error": e}
			return
	results[ip] = {"error": "cannot login"}

def usage():
	print("""Usage: %s <passwords> <ip>
	<passwords>	a password or a comma separated password list
	<ip>		an ip address or a network in cidr notation
Examples:
	%s password 192.168.1.1
	%s password,secondpassword 172.16.1.0/25
""" % (sys.argv[0],sys.argv[0],sys.argv[0]))

if __name__ == "__main__":
	try:
		passwords = sys.argv[1].split(",")
		ips = [str(i) for i in IPNetwork(sys.argv[2])]
	except Exception, e:
		usage()
		sys.exit(-1)

	if len(ips) > 1: # get rid of network and broadcast addresses
		ips=ips[1:-1]
	results={}
	print ("Testing", sys.argv[2])
	pool = ThreadPool(24)
	pool.map(connect,ips)
	pool.close()
	pool.join()
	for ip in results:
		print(ip, results[ip])
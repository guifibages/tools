#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# Requires the following modules
#   apt-get install python-requests python-bs4 python-netaddr
#   pip install requests beautifulsoup4 netaddr
import requests
import sys
from netaddr import IPNetwork
from multiprocessing.dummy import Pool as ThreadPool
from bs4 import BeautifulSoup

if __name__ == "__main__":
    hosts = sys.argv[1:]
    pool = ThreadPool(12)
    results = []

    def next(address):
        e = None
        ip = IPNetwork('%s/27' % address)
        host = requests.get('http://guifi.net/ca/guifi/menu/ip/ipsearch/%s'
                            % address)
        # network = requests.get('http://guifi.net/ca/guifi/menu/ip/ipsearch/%s' % ip.network)
        s = BeautifulSoup(host.text, 'lxml')
        h = s.find("th", text="nipv4").find_parent("table").find_all("td")
        if len(h) == 0 and address != ip.network+1:
            next(ip.network+1)
            return
        node = "%s (http://guifi.net%s)" % (h[5].a.text, h[5].a["href"])
        results.append({
            'ip': ip.ip,
            'network': ip.network,
            'broadcast': ip.broadcast,
            'netmask': ip.netmask,
            'information': h,
            'node': node,
            'errors': e
        })

    pool.map(next, hosts)
    pool.close()
    pool.join()
    for r in results:
        print ("%s: Network: %s Node: %s\n" %
               (r['ip'], r['network'], r['node']))

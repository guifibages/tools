#!/usr/bin/env bash

lxcname=$1
lxcip=$2
lxcdir=/var/lib/lxc/${lxcname}
lxcconf=/guifibages/etc/lxc/${lxcname}.base.conf


if [ -z "$lxcname" ]; then
  echo "Usage: $0 <container-name> <ip/bitmask>"
  exit 1
fi

if [ -z "$lxcip" ]; then
  echo "Usage: $0 <container-name> <ip/bitmask>"
  exit 1
fi

if [ -d $lxcdir ]; then
  echo "Error: Ja existeix el contenidor $lxcname: $lxcdir"
  exit 1
fi

tmp_ip=$(echo $lxcip | cut -d/ -f1)
tmp_mask=$(echo $lxcip | cut -d/ -f2)
CONTAINER_MAC="00:50:56$(awk -v ip="$tmp_ip" 'BEGIN{n=split(ip,d,".");for(i=2;i<=n;i++) printf ":%02X",d[i];print ""}')"

cat /guifibages/etc/lxc/net.tpl \
	| sed "s/CONTAINER_MAC/$CONTAINER_MAC/" \
	| sed "s/CONTAINER_IPMASK/$tmp_ip\/$tmp_mask/" \
	| sed "s/CONTAINER_NAME/$lxcname/" \
	> $lxcconf

cat $lxcconf

lxc-create -t guifibages-squeeze -n $lxcname -f $lxcconf

if [ $? -ne 0 ]; then
  echo "Error: S'ha produit un error a l'executar lxc-create"
  exit 1
fi

/guifibages/sbin/guifibages-lxc-platform.sh $lxcname
if [ $? -ne 0 ]; then
  echo "Error: S'ha produit un error a l'executar guifibages-lxc-platform"
  exit 1
fi

ln -s ${lxcdir}/config /etc/lxc/${lxcname}.conf
sed  -i "s/\"$/ ${lxcname}\"/" /etc/default/lxc

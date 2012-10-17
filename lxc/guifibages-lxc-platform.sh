#!/usr/bin/env bash
. /guifibages/lib/netlib.sh

lxcname=$1
lxcdir=/var/lib/lxc/${lxcname}
lxcconfig=/var/lib/lxc/${lxcname}/config
lxcroot=/var/lib/lxc/${lxcname}/rootfs

if [ -z "$lxcname" ]; then
  echo "Usage: $0 <container-name>" >&2
  exit 1
fi

if [ ! -d $lxcdir ]; then
  echo "Error: No existeix el contenidor $lxcname" >&2
  exit 1
fi

if [ ! -f $lxcconfig ]; then
  echo "Error: El contenidor $lxcname no té arxiu de configuració" >&2
  exit 1
fi

# Configurar interfaces del contendor
lxccidr=$(grep lxc.network.ipv4 /var/lib/lxc/${lxcname}/config | cut -d "=" -f 2)
lxcip=$(echo $lxccidr | cut -d '/' -f 1)
lxcmask=$(cidr2mask $(echo $lxccidr | cut -d '/' -f 2))
echo "IP: $lxcip"
echo "Mask: $lxcmask"

# TODO: Calcular gateway, broadcast y network
cat > $lxcroot/etc/network/interfaces << EOF_NETWORK_INTERFACES
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
	address $lxcip
	netmask $lxcmask
        network 10.228.17.0
        broadcast 10.228.17.31
	gateway 10.228.17.1
EOF_NETWORK_INTERFACES

mkdir -p $lxcroot/guifibages/sbin

find /guifibages -path /guifibages/users -prune -o -print | cpio -dump $lxcroot

chroot $lxcroot /guifibages/sbin/firstboot.sh

cat >> $lxcroot/etc/hosts << EOF_ETC_HOSTS
$lxcip	$lxcname	$lxcname.guifibages.net
EOF_ETC_HOSTS


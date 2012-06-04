#!/usr/bin/env bash
. netlib.sh

lxcname=$1
lxcdir=/var/lib/lxc/${lxcname}
lxcconfig=/var/lib/lxc/${lxcname}/config
lxcroot=/var/lib/lxc/${lxcname}/rootfs

if [ -z "$lxcname" ]; then
  echo "Usage: $0 <container-name>"
  exit 1
fi

if [ ! -d $lxcdir ]; then
  echo "Error: No existeix el contenidor $lxcname"
  exit 1
fi

if [ ! -f $lxcconfig ]; then
  echo "Error: El contenidor $lxcname no té arxiu de configuració"
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

cat > $lxcroot/etc/resolv.conf << EOF_RESOLV_CONF
domain guifibages.net
nameserver 10.228.17.4
EOF_RESOLV_CONF

cat > $lxcroot/etc/locale.gen << EOF_LOCALE_GEN
ca_ES.UTF-8 UTF-8
en_US.UTF-8 UTF-8
es_ES.UTF-8 UTF-8
EOF_LOCALE_GEN

cat > $lxcroot/etc/apt/apt.conf.d/02proxy << EOF_APT_PROXY
Acquire::http{ Proxy "http://10.228.17.4:3142"; };
EOF_APT_PROXY

cat > $lxcroot/etc/libnss-ldap.conf << EOF_LIBNSS_LDAP
base dc=guifibages,dc=net
uri ldaps://aaa.guifibages.net:636/
ssl on
sslpath /etc/ssl/certs
tls_checkpeer no
ldap_version 3
rootbinddn uid=nscd,ou=Services,ou=net,dc=guifibages,dc=net
nss_schema rfc2307bis
nss_base_passwd ou=Users,ou=auth,dc=guifibages,dc=net?one?memberOf=cn=ldapAdmin,ou=Groups,ou=auth,dc=guifibages,dc=net
nss_base_shadow ou=Users,ou=auth,dc=guifibages,dc=net
nss_base_group          ou=Groups,ou=auth,dc=guifibages,dc=net
nss_base_hosts          ou=Hosts,ou=net,dc=guifibages,dc=net
nss_map_attribute       rfc2307attribute        mapped_attribute
nss_map_objectclass     rfc2307objectclass      mapped_objectclass
nss_map_attribute uniqueMember member
EOF_LIBNSS_LDAP

for service in passwd group shadow; do
  sed -i "s/\($service:.*\)compat/\1files ldap/" $lxcroot/etc/nsswitch.conf
done

echo "session required                      pam_mkhomedir.so skel=/etc/skel umask=0022" >> $lxcroot/etc/pam.d/common-session

cat > $lxcroot/root/firstboot.sh << EOF_FIRST_BOOT
#!/usr/bin/env bash
echo "root:cambiame" | chpasswd
locale-gen
EOF_FIRST_BOOT
chmod +x $lxcroot/root/firstboot.sh
chroot $lxcroot /root/firstboot.sh
apt-get install -y rsyslog
rm $lxcroot/root/firstboot.sh

cat > $lxcroot/etc/rc.local << EOF_RC_LOCAL
#!/bin/sh -e
[ -x /root/firstboot.sh ] && /root/firstboot.sh
exit 0
EOF_RC_LOCAL
chmod +x $lxcroot/etc/rc.local

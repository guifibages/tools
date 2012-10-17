#!/usr/bin/env bash
if [ -f /etc/guifibages-firstboot ] ; then
  echo "Ja hem plataformat aquest servidor" >&2
  exit 1
fi

echo "root:cambiame" | chpasswd

cp /guifibages/etc/lxc-etc/locale.gen /etc && locale-gen

debconf-set-selections < /guifibages/etc/debconf-selections
apt-get update -y --force-yes
apt-get install -y --force-yes rsyslog vim less iputils-ping screen sudo libnss-ldap libpam-ldap ca-certificates

touch /etc/guifibages-firstboot

cd /guifibages/etc/lxc-etc
find . | cpio -dump /etc

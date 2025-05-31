#!/bin/bash

source gen-util.sh

container_name="webpa"

########################################################################################
# create the base image if not exists

if ! lxc image list | grep -q "webpa-base"; then
    echo "Creating webpa-base image"
    webpa-base.sh
fi

########################################################################################
# delete container

lxc delete ${container_name} -f 2>/dev/null

########################################################################################
# create profile

lxc profile delete ${container_name} &> /dev/null

lxc profile copy default ${container_name}

cat << EOF | lxc profile edit ${container_name}
name: webpa
description: "webpa"
config:
    boot.autostart: "false"
    limits.cpu: ""            # "" effectively means no CPU limits, allowing access to all available CPUs
    limits.memory: ""
devices:
    eth0:
        name: eth0
        nictype: bridged
        parent: lxdbr1
        type: nic
        ## ip addressing is static and configured in /etc/network/interfaces
    root:
        path: /
        pool: default
        type: disk
        size: 512MB
EOF

########################################################################################
# set timezone

#lxc profile set ${container_name} environment.TZ $(date +%z | awk '{printf("PST8PDT,M3.2.0,M11.1.0")}')

########################################################################################
#

lxc launch webpa-base ${container_name} -p ${container_name}

########################################################################################
#  reconfigure network

sleep 5

lxc file push $M_ROOT/gen/configs/webpa.eth0.nmconnection ${container_name}/etc/NetworkManager/system-connections/eth0.nmconnection

lxc exec ${container_name} -- chmod 600 /etc/NetworkManager/system-connections/eth0.nmconnection
lxc exec ${container_name} -- chown root:root /etc/NetworkManager/system-connections/eth0.nmconnection

lxc exec ${container_name} -- systemctl restart NetworkManager

lxc exec ${container_name} -- nmcli connection modify eth0 +ipv4.routes "10.100.200.0/24 10.10.10.100"
lxc exec ${container_name} -- nmcli connection modify eth0 +ipv4.routes "10.107.200.0/24 10.10.10.107"
lxc exec ${container_name} -- nmcli connection modify eth0 +ipv4.routes "10.108.200.0/24 10.10.10.108"
lxc exec ${container_name} -- nmcli connection modify eth0 +ipv4.routes "10.120.200.0/24 10.10.10.120"
lxc exec ${container_name} -- nmcli connection modify eth0 +ipv4.routes "10.177.200.0/24 10.10.10.109"
lxc exec ${container_name} -- nmcli connection modify eth0 +ipv4.routes "10.178.200.0/24 10.10.10.109"

lxc exec ${container_name} -- nmcli connection modify eth0 +ipv6.routes "2001:dae:0:1::/64 2001:dbf:0:1::100"
lxc exec ${container_name} -- nmcli connection modify eth0 +ipv6.routes "2001:dae:7:1::/64 2001:dbf:0:1::107"
lxc exec ${container_name} -- nmcli connection modify eth0 +ipv6.routes "2001:dae:8:1::/64 2001:dbf:0:1::108" 
lxc exec ${container_name} -- nmcli connection modify eth0 +ipv6.routes "2001:dae:20:1::/64 2001:dbf:0:1::120"
lxc exec ${container_name} -- nmcli connection modify eth0 +ipv6.routes "2001:dbd:0:1::/64 2001:dbf:0:1::109"
lxc exec ${container_name} -- nmcli connection modify eth0 +ipv6.routes "2001:dbe:0:1::/64 2001:dbf:0:1::109"

lxc exec ${container_name} -- nmcli connection up eth0

########################################################################################
#

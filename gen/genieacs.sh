#!/bin/bash

source gen-util.sh

container_name="genieacs"

########################################################################################
# create the base image if not exists

if ! lxc image list | grep -q "genieacs-base"; then
    echo "Creating genieacs-base image"
    #genieacs-base.sh
    genieacs-base-mongodb44.sh
fi

########################################################################################
# delete container

lxc delete ${container_name} -f 2>/dev/null

########################################################################################
# create profile

lxc profile delete ${container_name} &> /dev/null

lxc profile copy default ${container_name}

cat << EOF | lxc profile edit ${container_name}
name: genieacs
description: "GenieACS TR-069 Auto Configuration Server"
config:
    boot.autostart: "false"
    raw.lxc: |
      lxc.apparmor.profile=unconfined
    security.privileged: "false"
    security.nesting: "false"

    limits.cpu: ""      # "" effectively means no CPU limits, allowing access to all available CPUs
    limits.memory: ""   #
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
        size: ""
    # Port forwards for GenieACS services
    cwmp-port:
        type: proxy
        listen: tcp:0.0.0.0:7547
        connect: tcp:127.0.0.1:7547
    ui-port:
        type: proxy
        listen: tcp:0.0.0.0:3000
        connect: tcp:127.0.0.1:3000
    nbi-port:
        type: proxy
        listen: tcp:0.0.0.0:7557
        connect: tcp:127.0.0.1:7557
    fs-port:
        type: proxy
        listen: tcp:0.0.0.0:7567
        connect: tcp:127.0.0.1:7567
EOF

########################################################################################
# launch container

lxc launch genieacs-base ${container_name} -p ${container_name}

########################################################################################
# reconfigure network

sleep 5

lxc file push "$M_ROOT/gen/configs/genieacs-50-cloud-init.yaml" "${container_name}/etc/netplan/50-cloud-init.yaml" --uid 0 --gid 0 --mode 600
lxc exec ${container_name} -- netplan apply

########################################################################################
# set timezone

lxc exec ${container_name} -- timedatectl set-timezone America/Los_Angeles

########################################################################################
# start GenieACS services

echo "Starting MongoDB..."
lxc exec ${container_name} -- systemctl start mongod
sleep 10

echo "Verifying MongoDB is running..."
lxc exec ${container_name} -- systemctl status mongod --no-pager -l

echo "Starting GenieACS services..."
lxc exec ${container_name} -- systemctl start genieacs-cwmp
sleep 5
lxc exec ${container_name} -- systemctl start genieacs-nbi
sleep 5
lxc exec ${container_name} -- systemctl start genieacs-fs
sleep 5
lxc exec ${container_name} -- systemctl start genieacs-ui

########################################################################################
# verify services

sleep 15
echo "Checking GenieACS service status..."
echo "=== MongoDB Status ==="
lxc exec ${container_name} -- systemctl status mongod --no-pager -l
echo ""
echo "=== GenieACS CWMP Status ==="
lxc exec ${container_name} -- systemctl status genieacs-cwmp --no-pager -l
echo ""
echo "=== GenieACS NBI Status ==="
lxc exec ${container_name} -- systemctl status genieacs-nbi --no-pager -l
echo ""
echo "=== GenieACS FS Status ==="
lxc exec ${container_name} -- systemctl status genieacs-fs --no-pager -l
echo ""
echo "=== GenieACS UI Status ==="
lxc exec ${container_name} -- systemctl status genieacs-ui --no-pager -l

echo ""
echo "Checking for any connection issues..."
lxc exec ${container_name} -- ss -tlnp | grep -E "(27017|7547|7557|7567|3000)"

echo ""
echo "GenieACS container is ready!"
echo "Web UI: http://$(lxc list ${container_name} -c 4 --format csv | cut -d' ' -f1):3000"
echo "CWMP (for devices): http://$(lxc list ${container_name} -c 4 --format csv | cut -d' ' -f1):7547"
echo "To access container: lxc exec ${container_name} -- bash"

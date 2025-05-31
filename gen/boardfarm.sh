#!/bin/bash

source gen-util.sh

container_name="boardfarm"

########################################################################################
# create the base image if not exists

if ! lxc image list | grep -q "boardfarm-base"; then
    echo "Creating boardfarm-base image"
    boardfarm-base.sh
fi

########################################################################################
# delete container

lxc delete ${container_name} -f 2>/dev/null

########################################################################################
# create profile

lxc profile delete ${container_name} &> /dev/null

lxc profile copy default ${container_name}

cat << EOF | lxc profile edit ${container_name}
name: boardfarm
description: "boardfarm"
config:
    boot.autostart: "false"
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
EOF

########################################################################################
# launch container

lxc launch boardfarm-base ${container_name} -p ${container_name}

########################################################################################
# reconfigure network

sleep 5

lxc file push "$M_ROOT/gen/configs/boardfarm-50-cloud-init.yaml" "${container_name}/etc/netplan/50-cloud-init.yaml" --uid 0 --gid 0 --mode 600
lxc exec ${container_name} -- netplan apply

########################################################################################
# set timezone

# lxc exec ${container_name} -- timedatectl set-timezone America/Los_Angeles

########################################################################################
#

lxc exec ${container_name} -- bash -c '
    apt update
    apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    systemctl enable docker
    systemctl start docker
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
'

#!/bin/bash

source gen-util.sh

container_name="boardfarm"
lxd_endpoint="192.168.2.120:8443"

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
    raw.lxc: |
      lxc.apparmor.profile=unconfined
      lxc.cgroup.devices.allow = a
    security.privileged: "true"
    security.nesting: "true"

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
lxc exec ${container_name} -- bash -c "netplan apply >/dev/null 2>&1 || ip link set eth0 up" 2>/dev/null

########################################################################################
# set timezone

# lxc exec ${container_name} -- timedatectl set-timezone America/Los_Angeles

########################################################################################
# copy LXD certificates to container (assumes they're already set up by gen-util.sh)

echo "Copying LXD certificates to container..."
lxc file push ~/.config/lxc/client.crt "${container_name}/root/.config/lxc/client.crt" --create-dirs --uid 0 --gid 0 --mode 644
lxc file push ~/.config/lxc/client.key "${container_name}/root/.config/lxc/client.key" --create-dirs --uid 0 --gid 0 --mode 600

# Test LXD API access from within container
echo "Testing LXD API access from container..."
lxc exec ${container_name} -- bash -c "
    # Quick LXD API test with timeout
    echo 'Testing LXD API with certificates...'
    API_RESULT=\$(timeout 5 curl -s -k --cert /root/.config/lxc/client.crt --key /root/.config/lxc/client.key https://${lxd_endpoint}/1.0/instances 2>/dev/null)

    if echo \"\$API_RESULT\" | grep -q '\"type\":\"sync\"' 2>/dev/null; then
        echo 'LXD API test SUCCESSFUL'
        echo 'Instance count:' \$(echo \"\$API_RESULT\" | grep -o '/1.0/instances/' | wc -l)
    else
        echo 'LXD API test FAILED or timed out'
    fi
"

########################################################################################
# install boardfarm and dependencies

echo "Installing boardfarm and dependencies..."
lxc exec ${container_name} -- bash -c "
    # Force reinstall pexpect to avoid conflicts
    pip install --force-reinstall --no-deps --ignore-installed pexpect

    # Clone boardfarm3 branch
    git clone https://github.com/robvogelaar/boardfarm.git -b boardfarm3

    # Install boardfarm with all development dependencies
    pip install -e boardfarm[dev,doc,test]

    # Install pytest-boardfarm plugin
    pip install git+https://github.com/robvogelaar/pytest-boardfarm.git@boardfarm3

    echo
    echo 'Boardfarm installation completed!'
    echo
    echo 'Run a test using:'
    echo
    echo 'sed -i 's/192\.168\.2\.120:8443/<<HOST_IP>>:8443/g' boardfarm/vcpe/vcpe_only_inventory.json'
    echo 'pytest -c boardfarm/vcpe/vcpe_only_pytest.ini boardfarm/vcpe/tests/vcpe_only_tests/'
    echo
"

########################################################################################
#

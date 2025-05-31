#!/bin/bash

source gen-util.sh

container_name="client-wlan"
profile_name="$container_name"

# create client-base image if not exist
if ! lxc image list | grep -q "client-base"; then
    echo "Creating client-base image"
    client-base.sh
fi

# Delete existing container, and profile
lxc delete -f "${container_name}" > /dev/null 2>&1
lxc profile delete "${profile_name}" > /dev/null 2>&1

# Create new profile and configure
lxc profile create "${profile_name}" >/dev/null 2>&1 || true

# Set basic configuration
lxc profile set "${profile_name}" boot.autostart false
lxc profile set "${profile_name}" limits.memory=128MB
lxc profile set "${profile_name}" limits.cpu=1

# Create devices
###lxc profile device add "${profile_name}" eth0 nic nictype=bridged parent=lxdbr0
lxc profile device add "${profile_name}" root disk path=/ pool=default
lxc profile device add "${profile_name}" wlan0 nic nictype=physical parent=virt-wlan4 name=wlan0

# Launch container using client-base image
lxc launch "client-base" "${container_name}" "--profile=${profile_name}"

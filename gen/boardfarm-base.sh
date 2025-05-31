#!/bin/bash

# https://wiki.rdkcentral.com/display/RDK/RDKM+boardfarm+Server+Setup

source gen-util.sh

container_name="boardfarm-base-container"

image_name="ubuntu22.04"

########################################################################################
# obtain the image if it does not exist

if ! lxc image list | grep -q "$image_name"; then
    echo "Obtaining image: $image_name"
    lxc image copy ubuntu:22.04/Minimal local: --alias "$image_name"
fi

########################################################################################
#

lxc delete "${container_name}" -f 2>/dev/null

lxc launch "${image_name}" "${container_name}"

check_network "${container_name}"

###################################################################################################################################
# alias

lxc exec ${container_name} -- sh -c 'sed -i '\''#alias c=#d'\'' ~/.bashrc && echo '\''alias c="clear && printf \"\033[3J\033[0m\""'\'' >> ~/.bashrc'

###################################################################################################################################
#

lxc exec ${container_name} -- apt update

lxc exec ${container_name} -- sh -c 'DEBIAN_FRONTEND=noninteractive apt install -y tig build-essential python3-dev python3-pip'
lxc exec ${container_name} -- sh -c 'DEBIAN_FRONTEND=noninteractive apt install -y libsnmp-dev libsnmp40 snmp snmp-mibs-downloader'

###################################################################################################################################
#

lxc exec ${container_name} -- sh -c 'ln -s /usr/bin/python3 /usr/bin/python'


# exit 0

###################################################################################################################################
# Publish the image

lxc stop ${container_name}
lxc image delete boardfarm-base 2> /dev/null
lxc publish ${container_name} --alias boardfarm-base
lxc delete ${container_name}

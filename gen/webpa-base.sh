#!/bin/bash

source gen-util.sh

container_name="webpa-base-container"
image_name="centos9"

########################################################################################
# Obtain the image if it does not exist

if ! lxc image list | grep -q $image_name; then
    echo "Obtaining image: centos/9-Stream"
    lxc image copy images:centos/9-Stream local: --alias $image_name
fi

########################################################################################
#

lxc delete ${container_name} -f 2>/dev/null

lxc launch ${image_name} ${container_name}

check_network "${container_name}"


########################################################################################
# alias

lxc exec ${container_name} -- sh -c 'sed -i '\''#alias c=#d'\'' ~/.bashrc && echo '\''alias c="clear && printf \"\033[3J\033[0m\""'\'' >> ~/.bashrc'


########################################################################################
#

lxc exec ${container_name} -- dnf install -y ncurses
lxc exec ${container_name} -- yum install -y wget tcpdump

lxc exec ${container_name} -- yum install -y --nogpgcheck https://github.com/xmidt-org/talaria/releases/download/v0.1.3/talaria-0.1.3-1.el7.x86_64.rpm
lxc exec ${container_name} -- yum install -y --nogpgcheck https://github.com/xmidt-org/scytale/releases/download/v0.1.4/scytale-0.1.4-1.el7.x86_64.rpm
lxc exec ${container_name} -- yum install -y --nogpgcheck https://github.com/xmidt-org/tr1d1um/releases/download/v0.1.2/tr1d1um-0.1.2-1.el7.x86_64.rpm

lxc file push $M_ROOT/gen/configs/tr1d1um.yaml ${container_name}/etc/tr1d1um/tr1d1um.yaml
lxc file push $M_ROOT/gen/configs/scytale.yaml ${container_name}/etc/scytale/scytale.yaml
lxc file push $M_ROOT/gen/configs/talaria.yaml ${container_name}/etc/talaria/talaria.yaml

lxc exec ${container_name} -- systemctl enable tr1d1um
lxc exec ${container_name} -- systemctl enable scytale 
lxc exec ${container_name} -- systemctl enable talaria

#exit 0

###################################################################################################################################
# Publish the image

lxc stop ${container_name}
lxc image delete webpa-base 2> /dev/null
lxc publish ${container_name} --alias webpa-base
lxc delete ${container_name}

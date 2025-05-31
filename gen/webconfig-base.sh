#!/bin/bash

# https://wiki.rdkcentral.com/display/RDK/RDKM+Webconfig+Server+Setup

source gen-util.sh

container_name="webconfig-base-container"

image_name="ubuntu20.04"

########################################################################################
# obtain the image if it does not exist

if ! lxc image list | grep -q "$image_name"; then
    echo "Obtaining image: $image_name"
    lxc image copy ubuntu:20.04 local: --alias "$image_name"
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
lxc exec ${container_name} -- apt install -y openjdk-11-jdk

lxc exec ${container_name} -- wget https://golang.org/dl/go1.20.3.linux-amd64.tar.gz
lxc exec ${container_name} -- tar -C /usr/local -xzf go1.20.3.linux-amd64.tar.gz

lxc exec ${container_name} -- bash -c 'echo "export PATH=\$PATH:/usr/local/go/bin" >> /etc/profile'
lxc exec ${container_name} -- bash -c 'echo "export PATH=\$PATH:/usr/local/go/bin" >> ~/.bashrc'

# Test
lxc exec ${container_name} -- /usr/local/go/bin/go version
lxc exec ${container_name} -- sh -c 'source /etc/profile && go version'
lxc exec ${container_name} -- java -version



# Cassandra installation (modern approach)

# Option A: Using modern GPG key management (Recommended)
lxc exec ${container_name} -- sh -c 'wget -q -O - https://downloads.apache.org/cassandra/KEYS | gpg --dearmor > /tmp/cassandra.gpg'
lxc exec ${container_name} -- sh -c 'mv /tmp/cassandra.gpg /etc/apt/trusted.gpg.d/'
lxc exec ${container_name} -- sh -c 'echo "deb https://debian.cassandra.apache.org 41x main" > /etc/apt/sources.list.d/cassandra.sources.list'

# Option B: Current approach (works but deprecated)
#lxc exec ${container_name} -- bash -c 'echo "deb https://debian.cassandra.apache.org 41x main" | tee -a /etc/apt/sources.list.d/cassandra.sources.list'
#lxc exec ${container_name} -- bash -c 'curl https://downloads.apache.org/cassandra/KEYS | apt-key add'

lxc exec ${container_name} -- apt-get update
lxc exec ${container_name} -- apt-get install -y cassandra

exit 0

###################################################################################################################################
# Publish the image

lxc stop ${container_name}
lxc image delete webconfig-base 2> /dev/null
lxc publish ${container_name} --alias webconfig-base
lxc delete ${container_name}

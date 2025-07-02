#!/bin/bash

source gen-util.sh

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 path/to/vcpe-image-qemux86.lxc.tar.bz2 or user@host:/path/to/vcpe-image-qemux86.lxc.tar.bz2>"
    exit 1
fi

imagefile=$1

# Check if imagefile matches SCP URL pattern (user@host:)
if [[ $imagefile =~ ^[^@]+@[^:]+:.+ ]]; then
    mkdir -p ./tmp
    # Extract filename from path
    filename="${imagefile##*/}"
    if ! scp "$imagefile" "./tmp/$filename"; then
        echo "SCP download failed"
        exit 1
    fi
    imagefile="./tmp/$filename"
fi

# Verify file exists
if [ ! -f "$imagefile" ]; then
    echo "Error: File not found: $imagefile"
    exit 1
fi

#
imagename="${imagefile##*/}"; imagename="${imagename%.tar.bz2}"
containername="vcpe"
profilename="vcpe"
volumename="${containername}-nvram"

eth0_mac="00:16:3e:20:79:68"
eth1_mac="00:16:3e:16:5f:7c"

#
lxc delete ${containername} -f 2>/dev/null


#
sudo bridge vlan add vid 100 dev lan-p1 self

# Nvram
if ! lxc storage volume show default $volumename > /dev/null 2>&1; then
    lxc storage volume create default $volumename size=4MiB
fi

lxc image delete ${imagename} 2> /dev/null
lxc image import $imagefile --alias ${imagename}

# Profile
lxc profile create "$profilename" 2>/dev/null || true
lxc profile edit "$profilename" < "$M_ROOT/gen/profiles/$profilename.yaml"

# eth0 interface
lxc profile device add "$profilename" eth0 nic \
    nictype=bridged \
    parent=wan \
    hwaddr=$eth0_mac \
    name=eth0 \
    > /dev/null

# eth1 interface  
lxc profile device add "$profilename" eth1 nic \
    nictype=bridged \
    parent=lan-p1 \
    hwaddr=$eth1_mac \
    name=eth1 \
    vlan=100 \
    > /dev/null


# Initialize the container without starting it

lxc init ${imagename} ${containername} -p ${profilename}

# Create a custom configuration file
cat << EOF > ./vcpe-config
CREATION_DATE=$(date +"%Y-%m-%d_%H:%M:%S")
SERIAL_NUMBER=$(echo ${eth0_mac//:/} | tr '[:lower:]' '[:upper:]')
HARDWARE_VERSION=1.0
EOF

lxc file push ./vcpe-config ${containername}/etc/vcpe-config
rm -f ./vcpe-config

# Start the container
lxc start ${containername}

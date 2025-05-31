#!/bin/bash

source gen-util.sh


image_name="axiros"
container_name="acs"


########################################################################################
# Obtain image
if ! lxc image info "${image_name}" &> /dev/null; then
    echo "Creating ${image_name} image"


    if [ -z "$ACS_URL" ] || [ -z "$ACS_KEY" ]; then
        if [ -z "$ACS_URL" ]; then
            echo "ACS_URL is empty"
        fi
        if [ -z "$ACS_KEY" ]; then
            echo "ACS_KEY is empty"
        fi
        echo "no credentials populated. exiting.."
        exit 1
    fi



    encfile="$M_ROOT/tmp/723196ff96fb6032e6b7b99afabf05b66adc09b06359b71495457bb7edfb0e88.tar.gz.enc"
    [ -e "$encfile" ] || curl -L -o "$encfile" ${ACS_URL}

    ## image was encoded with:
    ## openssl enc -aes-256-cbc -salt -in 723196ff96fb6032e6b7b99afabf05b66adc09b06359b71495457bb7edfb0e88.tar.gz \
    ## -out 723196ff96fb6032e6b7b99afabf05b66adc09b06359b71495457bb7edfb0e88.tar.gz.enc -k ${ACS_KEY}
    file="$M_ROOT/tmp/723196ff96fb6032e6b7b99afabf05b66adc09b06359b71495457bb7edfb0e88.tar.gz"
    [ -e "$file" ] || openssl enc -aes-256-cbc -d -salt -in $encfile -out $file -k ${ACS_KEY} 2>/dev/null

    rm $encfile

    lxc image import "${file}" --alias "${image_name}"

    rm $file

fi

########################################################################################
# Delete acs container if exists

if lxc list --format csv | grep -q "^${container_name}"; then
    echo "Deleting ${container_name}"
    lxc delete ${container_name} -f 1>/dev/null
fi

########################################################################################
# Recreate acs profile

if lxc profile list --format csv | grep -q "^${container_name}"; then
    lxc profile delete ${container_name} 1> /dev/null
fi

lxc profile copy default ${container_name}

cat << EOF | lxc profile edit acs
name: acs
description: "acs"
config:
    boot.autostart: "false"
    limits.cpu: "0"               # "0" effectively means no CPU limits, allowing access to all available CPUs
    limits.memory: 4GB            # Restrict memory usage to 4GB
devices:
    eth0:
        name: eth0
        nictype: bridged
        parent: lxdbr1
        type: nic
        ## ip addressing is static and configured in /etc/network/interfaces
        ## ipv4.address: 10.10.10.200
        ## ipv6.address: 2001:dbf:0:1::200
    root:
        path: /
        pool: default
        type: disk
        size: 2GB
EOF


lxc launch axiros acs -p acs

echo "Configuring ${container_name}"

##################################################################################

lxc file push $M_ROOT/gen/configs/acs-interfaces acs/etc/network/interfaces 1> /dev/null

## openssl enc -aes-256-cbc -salt -in axess_wsgi -out axess_wsgi.enc -k ${ACS_KEY}
## openssl enc -aes-256-cbc -salt -in axess_default_host -out axess_default_host.enc -k ${ACS_KEY}
openssl enc -aes-256-cbc -d -salt -in $M_ROOT/gen/configs/axess_wsgi.enc -out $M_ROOT/tmp/axess_wsgi -k ${ACS_KEY} 2>/dev/null
openssl enc -aes-256-cbc -d -salt -in $M_ROOT/gen/configs/axess_default_host.enc -out $M_ROOT/tmp/axess_default_host -k ${ACS_KEY} 2>/dev/null

lxc file push $M_ROOT/tmp/axess_wsgi acs/etc/apache2/sites-available/ 1> /dev/null
lxc file push $M_ROOT/tmp/axess_default_host acs/etc/apache2/sites-available/ 1> /dev/null

rm $M_ROOT/tmp/axess_wsgi
rm $M_ROOT/tmp/axess_default_host

lxc exec acs -- sh -c "sed -i '/^[[:space:]]*if \$APACHE2CTL start; then$/s/^/sleep 3; /' /etc/init.d/apache2"
lxc exec acs -- sh -c "rm /etc/resolv.conf"
lxc exec acs -- sh -c "echo \"net.ipv6.conf.eth0.accept_ra = 0\" >> /etc/sysctl.conf"

## Add an alias
lxc exec ${container_name} -- bash -c "echo \"alias c='clear && printf '\\''\033[3J'\\''; printf '\\''\033[0m'\\'''\" >> /root/.bashrc"

########################################################################################
# disable root password
lxc exec ${container_name} -- bash -c "sed -i 's/^root:x:/root::/' /etc/passwd"

########################################################################################
# enable console
lxc exec ${container_name} -- bash -c "sed -i 's/1:2345:respawn:\/sbin\/getty 38400 tty1/1:2345:respawn:\/sbin\/getty 38400 console/' /etc/inittab"

########################################################################################
########################################################################################

echo "Restarting ${container_name}"

lxc restart acs -f 2> /dev/null

########################################################################################
##
## wget -4 http://archive.debian.org/debian/pool/main/t/tcpdump/tcpdump_4.3.0-1+deb7u1_amd64.deb
## dpkg -i tcpdump_4.3.0-1+deb7u2_amd64.deb
## wget -4 http://archive.debian.org/debian/pool/main/libp/libpcap/libpcap0.8_1.3.0-1_amd64.deb
## dpkg -i libpcap0.8_1.3.0-1_amd64.deb
## tcpdump
##

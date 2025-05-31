#!/bin/bash

source gen-util.sh

container_name="client-base-container"
image_name="alpine"

########################################################################################
# Obtain the image if it does not exist

if ! lxc image list | grep -q $image_name; then
    echo "Obtaining image: alpine/3.19"
    lxc image copy "images:alpine/3.19" local: --alias "${image_name}" || {
        echo "Failed to pull image from remote" >&2
        exit 1
    }
fi

########################################################################################
#
lxc delete ${container_name} -f 2>/dev/null

lxc launch ${image_name} ${container_name}

check_network client-base-container

########################################################################################
#

lxc exec ${container_name} -- apk update
lxc exec ${container_name} -- apk add iw wpa_supplicant wireless-tools
lxc exec ${container_name} -- apk add iperf3
lxc exec ${container_name} -- apk add openssh-server openssh-client
lxc exec ${container_name} -- apk add bash

lxc exec ${container_name} -- sh -c 'echo '\''alias c="clear && printf \"\033[3J\033[0m\""'\'' > ~/.bashrc'

# Configure SSH for passwordless root access
lxc exec ${container_name} -- sh -c '
    sed -i "s/#PermitRootLogin prohibit-password/PermitRootLogin yes/" /etc/ssh/sshd_config
    sed -i "s/#PasswordAuthentication yes/PasswordAuthentication yes/" /etc/ssh/sshd_config  
    sed -i "s/#PermitEmptyPasswords no/PermitEmptyPasswords yes/" /etc/ssh/sshd_config
'

lxc exec ${container_name} -- passwd -d root
lxc exec ${container_name} -- ssh-keygen -A
lxc exec ${container_name} -- rc-update add sshd default

# Configure wpa supplicant (for wlan client container)
lxc exec ${container_name} -- sh -c 'cat > /etc/wpa_supplicant/wpa_supplicant.conf << EOF
network={
    ssid="RPi3_RDKB-AP0"
    psk="rdk@1234"
    priority=10
}
network={
    ssid="RPi3_RDKB-AP1"
    psk="rdk@1234"
    priority=10
}
EOF'

lxc exec ${container_name} -- chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf

lxc exec ${container_name} -- rc-update add wpa_supplicant default

# Add wlan0 to network interfaces
lxc exec ${container_name} -- sh -c 'cat >> /etc/network/interfaces << EOF

auto wlan0
iface wlan0 inet dhcp
    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
EOF'

# exit 0

########################################################################################
# publish the image

lxc stop ${container_name}

lxc image delete client-base 2> /dev/null
lxc publish client-base-container --alias client-base
lxc delete client-base-container

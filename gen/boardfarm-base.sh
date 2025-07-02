#!/bin/bash

source gen-util.sh

container_name="boardfarm-base-container"
image_name="ubuntu22.04"

########################################################################################
# obtain the image if it does not exist
if ! lxc image list | grep -q "$image_name"; then
    echo "Obtaining image: $image_name"
    lxc image copy ubuntu:22.04 local: --alias "$image_name"
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
# Initial updates and basic packages
lxc exec ${container_name} -- apt update
lxc exec ${container_name} -- sh -c 'DEBIAN_FRONTEND=noninteractive apt install -y bridge-utils tig build-essential python3-dev python3-pip'
lxc exec ${container_name} -- sh -c 'DEBIAN_FRONTEND=noninteractive apt install -y libsnmp-dev libsnmp40 snmp snmp-mibs-downloader'

###################################################################################################################################
# Python 3.11 installation
echo "Installing Python 3.11..."
lxc exec ${container_name} -- sh -c 'DEBIAN_FRONTEND=noninteractive apt install -y software-properties-common'
lxc exec ${container_name} -- add-apt-repository -y ppa:deadsnakes/ppa
lxc exec ${container_name} -- apt update
lxc exec ${container_name} -- sh -c 'DEBIAN_FRONTEND=noninteractive apt install -y python3.11 python3.11-dev python3.11-venv python3.11-distutils'
echo "Installing pip for Python 3.11..."
lxc exec ${container_name} -- sh -c 'curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11'
echo "Verifying Python 3.11 installation..."
lxc exec ${container_name} -- python3.11 --version
lxc exec ${container_name} -- python3.11 -m pip --version

###################################################################################################################################
# Docker installation steps
echo "Installing Docker prerequisites..."
lxc exec ${container_name} -- sh -c 'DEBIAN_FRONTEND=noninteractive apt install -y ca-certificates curl gnupg lsb-release'
echo "Setting up Docker repository..."
lxc exec ${container_name} -- mkdir -p /etc/apt/keyrings
lxc exec ${container_name} -- sh -c 'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg'
lxc exec ${container_name} -- sh -c 'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null'
echo "Installing Docker..."
lxc exec ${container_name} -- apt update
lxc exec ${container_name} -- sh -c 'DEBIAN_FRONTEND=noninteractive apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin'
echo "Starting and enabling Docker service..."
lxc exec ${container_name} -- systemctl start docker
lxc exec ${container_name} -- systemctl enable docker
echo "Installing standalone Docker Compose..."
lxc exec ${container_name} -- sh -c 'curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose'
lxc exec ${container_name} -- chmod +x /usr/local/bin/docker-compose
echo "Verifying Docker installation..."
lxc exec ${container_name} -- docker --version
lxc exec ${container_name} -- docker compose version
lxc exec ${container_name} -- docker-compose --version

###################################################################################################################################
#
lxc exec ${container_name} -- sh -c 'ln -s /usr/bin/python3 /usr/bin/python'

lxc exec ${container_name} -- git clone --branch boardfarm3 --single-branch https://github.com/lgirdk/boardfarm.git &&

#lxc exec ${container_name} -- docker-compose -f boardfarm/resources/deploy/prplos/docker-compose.yaml pull

lxc exec ${container_name} -- sh -c '
    python3.11 -m venv venv3.11 &&
    . venv3.11/bin/activate &&
    pip install -U pip &&
    pip install -e boardfarm[dev,doc,test] &&
    pip install git+https://github.com/lgirdk/pytest-boardfarm.git@boardfarm3 &&
    pip install git+https://github.com/lgirdk/boardfarm-docsis.git@boardfarm3
'

# exit 0

###################################################################################################################################
# Publish the image
echo "Publishing the container as boardfarm-base image..."
lxc stop ${container_name}
lxc image delete boardfarm-base 2> /dev/null
lxc publish ${container_name} --alias boardfarm-base
lxc delete ${container_name}
echo "Setup complete! The boardfarm-base image now includes Docker, Docker Compose, and Python 3.11."

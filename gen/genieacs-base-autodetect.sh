#!/bin/bash

source gen-util.sh

container_name="genieacs-base-container"
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
echo "Updating system and installing basic packages..."
lxc exec ${container_name} -- apt update
lxc exec ${container_name} -- sh -c 'DEBIAN_FRONTEND=noninteractive apt upgrade -y'
lxc exec ${container_name} -- sh -c 'DEBIAN_FRONTEND=noninteractive apt install -y curl wget gnupg2 software-properties-common ca-certificates lsb-release'

###################################################################################################################################
# Node.js installation
echo "Installing Node.js 18..."
lxc exec ${container_name} -- sh -c 'curl -fsSL https://deb.nodesource.com/setup_18.x | bash -'
lxc exec ${container_name} -- sh -c 'DEBIAN_FRONTEND=noninteractive apt install -y nodejs'
echo "Verifying Node.js installation..."
lxc exec ${container_name} -- node --version
lxc exec ${container_name} -- npm --version

###################################################################################################################################
# MongoDB installation with CPU detection
echo "Detecting CPU capabilities..."

# Check if host CPU supports AVX (required for MongoDB 5.0+)
if lscpu | grep -q -i avx; then
    echo "AVX support detected - Installing MongoDB 6.0..."
    lxc exec ${container_name} -- sh -c 'wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -'
    lxc exec ${container_name} -- sh -c 'echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list'
else
    echo "No AVX support detected - Installing MongoDB 4.4 (compatible with older CPUs)..."
    echo "Note: Your CPU ($(lscpu | grep 'Model name' | cut -d: -f2 | xargs)) does not support AVX instructions required by MongoDB 5.0+"
    lxc exec ${container_name} -- sh -c 'wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | apt-key add -'
    lxc exec ${container_name} -- sh -c 'echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.4.list'
fi

lxc exec ${container_name} -- apt update
lxc exec ${container_name} -- sh -c 'DEBIAN_FRONTEND=noninteractive apt install -y mongodb-org'
echo "Enabling MongoDB service..."
lxc exec ${container_name} -- systemctl enable mongod

###################################################################################################################################
# GenieACS installation
echo "Installing GenieACS..."
lxc exec ${container_name} -- npm install -g genieacs

###################################################################################################################################
# Create genieacs user and directories
echo "Setting up GenieACS user and directories..."
lxc exec ${container_name} -- useradd --system --no-create-home --user-group genieacs
lxc exec ${container_name} -- mkdir -p /opt/genieacs/ext
lxc exec ${container_name} -- mkdir -p /var/log/genieacs
lxc exec ${container_name} -- chown genieacs:genieacs /opt/genieacs/ext
lxc exec ${container_name} -- chown genieacs:genieacs /var/log/genieacs

###################################################################################################################################
# Configure environment variables
echo "Setting up GenieACS environment configuration..."
lxc exec ${container_name} -- sh -c 'cat > /opt/genieacs/genieacs.env << EOF
GENIEACS_CWMP_ACCESS_LOG_FILE=/var/log/genieacs/genieacs-cwmp-access.log
GENIEACS_NBI_ACCESS_LOG_FILE=/var/log/genieacs/genieacs-nbi-access.log
GENIEACS_FS_ACCESS_LOG_FILE=/var/log/genieacs/genieacs-fs-access.log
GENIEACS_UI_ACCESS_LOG_FILE=/var/log/genieacs/genieacs-ui-access.log
GENIEACS_DEBUG_FILE=/var/log/genieacs/genieacs-debug.yaml
NODE_OPTIONS=--enable-source-maps
GENIEACS_EXT_DIR=/opt/genieacs/ext
EOF'

# Generate JWT secret
echo "Generating JWT secret..."
lxc exec ${container_name} -- sh -c 'node -e "console.log(\"GENIEACS_UI_JWT_SECRET=\" + require(\"crypto\").randomBytes(128).toString(\"hex\"))" >> /opt/genieacs/genieacs.env'

###################################################################################################################################
# Create systemd service files
echo "Creating systemd service files..."

# CWMP Service
lxc exec ${container_name} -- sh -c 'cat > /etc/systemd/system/genieacs-cwmp.service << EOF
[Unit]
Description=GenieACS CWMP
After=network.target mongod.service
Requires=mongod.service

[Service]
User=genieacs
EnvironmentFile=/opt/genieacs/genieacs.env
ExecStart=/usr/bin/genieacs-cwmp
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

# NBI Service
lxc exec ${container_name} -- sh -c 'cat > /etc/systemd/system/genieacs-nbi.service << EOF
[Unit]
Description=GenieACS NBI
After=network.target mongod.service
Requires=mongod.service

[Service]
User=genieacs
EnvironmentFile=/opt/genieacs/genieacs.env
ExecStart=/usr/bin/genieacs-nbi
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

# FS Service
lxc exec ${container_name} -- sh -c 'cat > /etc/systemd/system/genieacs-fs.service << EOF
[Unit]
Description=GenieACS FS
After=network.target mongod.service
Requires=mongod.service

[Service]
User=genieacs
EnvironmentFile=/opt/genieacs/genieacs.env
ExecStart=/usr/bin/genieacs-fs
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

# UI Service
lxc exec ${container_name} -- sh -c 'cat > /etc/systemd/system/genieacs-ui.service << EOF
[Unit]
Description=GenieACS UI
After=network.target mongod.service
Requires=mongod.service

[Service]
User=genieacs
EnvironmentFile=/opt/genieacs/genieacs.env
ExecStart=/usr/bin/genieacs-ui
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

###################################################################################################################################
# Configure log rotation
echo "Setting up log rotation..."
lxc exec ${container_name} -- sh -c 'cat > /etc/logrotate.d/genieacs << EOF
/var/log/genieacs/*.log /var/log/genieacs/*.yaml {
    daily
    rotate 30
    compress
    delaycompress
    dateext
}
EOF'

###################################################################################################################################
# Enable services
echo "Enabling GenieACS services..."
lxc exec ${container_name} -- systemctl daemon-reload
lxc exec ${container_name} -- systemctl enable mongod
lxc exec ${container_name} -- systemctl enable genieacs-cwmp
lxc exec ${container_name} -- systemctl enable genieacs-nbi
lxc exec ${container_name} -- systemctl enable genieacs-fs
lxc exec ${container_name} -- systemctl enable genieacs-ui

###################################################################################################################################
# Test MongoDB connection (start it temporarily for testing)
echo "Testing MongoDB connection..."
lxc exec ${container_name} -- systemctl start mongod
sleep 5
lxc exec ${container_name} -- systemctl status mongod --no-pager -l

###################################################################################################################################
# Verify installation
echo "Verifying GenieACS installation..."
lxc exec ${container_name} -- which genieacs-cwmp
lxc exec ${container_name} -- which genieacs-nbi
lxc exec ${container_name} -- which genieacs-fs
lxc exec ${container_name} -- which genieacs-ui

# Stop MongoDB to clean up the image
lxc exec ${container_name} -- systemctl stop mongod

###################################################################################################################################
# Publish the image
echo "Publishing the container as genieacs-base image..."
lxc stop ${container_name}
lxc image delete genieacs-base 2> /dev/null
lxc publish ${container_name} --alias genieacs-base
lxc delete ${container_name}
echo "Setup complete! The genieacs-base image is ready with GenieACS, MongoDB, and Node.js."
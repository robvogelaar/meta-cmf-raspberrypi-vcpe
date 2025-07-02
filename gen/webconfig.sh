#!/bin/bash

# https://wiki.rdkcentral.com/display/RDK/RDKM+Webconfig+Server+Setup

source gen-util.sh

container_name="webconfig"

########################################################################################
# create the base image if not exists

if ! lxc image list | grep -q "webconfig-base"; then
    echo "Creating webconfig-base image"
    webconfig-base.sh
fi

########################################################################################
# delete container

lxc delete ${container_name} -f 2>/dev/null

########################################################################################
# create profile

lxc profile delete ${container_name} &> /dev/null

lxc profile copy default ${container_name}

cat << EOF | lxc profile edit ${container_name}
name: webconfig
description: "webconfig"
config:
    boot.autostart: "false"
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
        size: 4GiB
EOF

########################################################################################
# launch container

lxc launch webconfig-base ${container_name} -p ${container_name}

########################################################################################
# reconfigure network

sleep 5
lxc file push "$M_ROOT/gen/configs/webconfig-50-cloud-init.yaml" "${container_name}/etc/netplan/50-cloud-init.yaml" --uid 0 --gid 0 --mode 644
lxc exec ${container_name} -- netplan apply

########################################################################################
# set timezone

# lxc exec ${container_name} -- timedatectl set-timezone America/Los_Angeles

########################################################################################
# start cassandra service

lxc exec ${container_name} -- systemctl start cassandra
lxc exec ${container_name} -- systemctl enable cassandra

# Wait for Cassandra to be ready
lxc exec ${container_name} -- sh -c "
    echo 'Waiting for Cassandra to be ready...'
    while ! cqlsh -e 'describe cluster' > /dev/null 2>&1; do
        sleep 5
        echo 'Still waiting for Cassandra...'
    done
    echo 'Cassandra is ready!'
"

########################################################################################
# install webconfig server

lxc exec ${container_name} -- sh -c "
    cd ~ &&
    export PATH=\$PATH:/usr/local/go/bin &&
    git clone https://github.com/rdkcentral/webconfig.git &&
    cd webconfig &&
    go mod tidy &&
    go build -o webconfig
"

########################################################################################
# create webconfig configuration

lxc exec ${container_name} -- sh -c "
    mkdir -p /etc/webconfig &&
    cat > /etc/webconfig/webconfig.conf << 'EOF'
# Webconfig Server Configuration
server:
  port: 8080
  host: 0.0.0.0

database:
  type: cassandra
  host: 127.0.0.1
  port: 9042
  keyspace: webconfig
  username: 
  password: 

logging:
  level: info
  file: /var/log/webconfig/webconfig.log

# Document storage settings
documents:
  max_size: 10MB
  compression: true
EOF
"

########################################################################################
# create systemd service for webconfig

lxc exec ${container_name} -- sh -c "
    cat > /etc/systemd/system/webconfig.service << 'EOF'
[Unit]
Description=Webconfig Server
After=network.target cassandra.service
Requires=cassandra.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/webconfig
ExecStart=/root/webconfig/webconfig -config /etc/webconfig/webconfig.conf
Restart=always
RestartSec=10
Environment=PATH=/usr/local/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

[Install]
WantedBy=multi-user.target
EOF
"

########################################################################################
# create cassandra keyspace and tables for webconfig

lxc exec ${container_name} -- sh -c "
    cqlsh -e \"
    CREATE KEYSPACE IF NOT EXISTS webconfig 
    WITH REPLICATION = {
        'class': 'SimpleStrategy', 
        'replication_factor': 1
    };
    
    USE webconfig;
    
    CREATE TABLE IF NOT EXISTS documents (
        id text PRIMARY KEY,
        document text,
        created_time timestamp,
        updated_time timestamp
    );
    
    CREATE TABLE IF NOT EXISTS device_configs (
        device_id text PRIMARY KEY,
        config text,
        version int,
        created_time timestamp,
        updated_time timestamp
    );
    \"
"

########################################################################################
# create log directory and start webconfig service

lxc exec ${container_name} -- sh -c "
    mkdir -p /var/log/webconfig &&
    systemctl daemon-reload &&
    systemctl enable webconfig &&
    systemctl start webconfig
"

########################################################################################
# verify services are running

lxc exec ${container_name} -- sh -c "
    echo 'Checking service status...'
    systemctl is-active cassandra
    systemctl is-active webconfig
    sleep 2
    echo 'Checking if webconfig is listening on port 8080...'
    ss -tlnp | grep :8080 || echo 'Webconfig may still be starting up'
"
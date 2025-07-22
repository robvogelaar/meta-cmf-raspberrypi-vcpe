#!/bin/bash

# JIRA Container Creation Script
# Creates a JIRA instance from the base container

set -e

source "$(dirname "$0")/gen-util.sh"

CONTAINER_NAME="jira"
BASE_CONTAINER="jira-base"
PROFILE="jira"
IP_ADDRESS="10.10.10.27"

# Create JIRA profile if it doesn't exist
create_jira_profile() {
    if ! lxc profile list --format csv | grep -q "^${PROFILE},"; then
        echo "Creating JIRA profile..."
        
        lxc profile create "${PROFILE}"
        
        cat << EOF | lxc profile edit "${PROFILE}"
config:
  limits.cpu: "2"
  limits.memory: 4GB
  user.user-data: |
    #cloud-config
    package_upgrade: false
    network:
      version: 2
      ethernets:
        eth0:
          addresses:
            - ${IP_ADDRESS}/24
          gateway4: 10.10.10.1
          nameservers:
            addresses:
              - 8.8.8.8
              - 8.8.4.4
    runcmd:
      - systemctl start postgresql
      - systemctl start supervisor
      - sleep 10
      - systemctl start jira
description: JIRA Server Profile
devices:
  eth0:
    name: eth0
    nictype: bridged
    parent: lxdbr1
    type: nic
  root:
    path: /
    pool: default
    type: disk
name: ${PROFILE}
used_by: []
EOF
    else
        echo "JIRA profile already exists"
    fi
}

create_jira_container() {
    echo "Creating JIRA container from base..."
    
    # Check if container already exists
    if lxc list --format csv | grep -q "^${CONTAINER_NAME},"; then
        echo "Container ${CONTAINER_NAME} already exists. Stopping and deleting..."
        lxc stop "${CONTAINER_NAME}" --force || true
        lxc delete "${CONTAINER_NAME}" || true
    fi
    
    # Check if base image exists
    if ! lxc image list --format csv | grep -q "^${BASE_CONTAINER},"; then
        echo "Base image ${BASE_CONTAINER} not found. Creating..."
        
        # Create base container
        "$(dirname "$0")/jira-base.sh"
        
        # Stop base container if running
        if lxc list --format csv | grep "^${BASE_CONTAINER}," | grep -q "RUNNING"; then
            echo "Stopping base container..."
            lxc stop "${BASE_CONTAINER}"
        fi
        
        # Export base container to image
        echo "Exporting base container to image..."
        lxc publish "${BASE_CONTAINER}" --alias "${BASE_CONTAINER}"
        
        # Delete base container
        echo "Removing base container..."
        lxc delete "${BASE_CONTAINER}"
    fi
    
    # Launch container from base image
    echo "Launching JIRA container from base image..."
    lxc launch "${BASE_CONTAINER}" "${CONTAINER_NAME}"
    
    # Apply profile
    lxc profile add "${CONTAINER_NAME}" "${PROFILE}"
    
    # Start container
    echo "Starting JIRA container..."
    lxc start "${CONTAINER_NAME}"
    
    # Wait for container to be ready
    wait_for_container "${CONTAINER_NAME}"
    
    # Wait for services to start
    echo "Waiting for services to initialize..."
    sleep 30
    
    # Check if JIRA is accessible
    echo "Checking JIRA accessibility..."
    for i in {1..12}; do
        if curl -s -o /dev/null -w "%{http_code}" "http://${IP_ADDRESS}:8080" | grep -q "200\|302"; then
            echo "JIRA is accessible!"
            break
        fi
        echo "Waiting for JIRA to start... (attempt $i/12)"
        sleep 10
    done
}

configure_firewall() {
    echo "Configuring firewall rules for JIRA..."
    
    # Allow HTTP access to JIRA
    lxc exec "${CONTAINER_NAME}" -- ufw allow 8080/tcp || true
    
    # Allow PostgreSQL access (internal)
    lxc exec "${CONTAINER_NAME}" -- ufw allow 5432/tcp || true
}

display_access_info() {
    echo ""
    echo "============================================"
    echo "JIRA Container Created Successfully!"
    echo "============================================"
    echo ""
    echo "Access Information:"
    echo "  URL: http://${IP_ADDRESS}:8080"
    echo "  Container: ${CONTAINER_NAME}"
    echo ""
    echo "Database Information:"
    echo "  Type: PostgreSQL"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  Database: jiradb"
    echo "  Username: jirauser"
    echo "  Password: jira@123456"
    echo ""
    echo "Setup Instructions:"
    echo "1. Open http://${IP_ADDRESS}:8080 in your browser"
    echo "2. Choose 'I'll set it up myself'"
    echo "3. Select PostgreSQL database"
    echo "4. Use the database credentials above"
    echo "5. Generate a free evaluation license from Atlassian"
    echo "6. Complete the setup wizard"
    echo ""
    echo "Container Management:"
    echo "  Start:   lxc start ${CONTAINER_NAME}"
    echo "  Stop:    lxc stop ${CONTAINER_NAME}"
    echo "  Shell:   lxc exec ${CONTAINER_NAME} bash"
    echo "  Logs:    lxc exec ${CONTAINER_NAME} -- tail -f /opt/atlassian/jira/logs/catalina.out"
    echo ""
    echo "For SSH tunnel access:"
    echo "  ssh -L 8080:${IP_ADDRESS}:8080 user@host"
    echo "  Then access: http://localhost:8080"
    echo ""
}

main() {
    echo "Starting JIRA container creation..."
    
    check_lxd_running
    
    create_jira_profile
    create_jira_container
    configure_firewall
    
    display_access_info
}

main "$@"
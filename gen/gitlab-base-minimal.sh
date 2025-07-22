#!/bin/bash

# GitLab Base Container Creation Script - Minimal Version
# Creates a base Ubuntu container with GitLab CE using minimal space

set -e

source "$(dirname "$0")/gen-util.sh"

CONTAINER_NAME="gitlab-base"
IMAGE_ALIAS="ubuntu/22.04"
GITLAB_VERSION="18.2.0-ce.0"
GITLAB_HOME="/var/opt/gitlab"
GITLAB_CONFIG="/etc/gitlab"
GITLAB_LOGS="/var/log/gitlab"

create_gitlab_base_container() {
    echo "Creating GitLab base container (minimal version)..."
    
    # Check available disk space first
    local available_space=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if (( available_space < 10 )); then
        echo "ERROR: Insufficient disk space. At least 10GB required, only ${available_space}GB available"
        echo "GitLab requires:"
        echo "  - 1.4GB for package download"
        echo "  - 3.9GB for installation"
        echo "  - Additional space for operation"
        echo ""
        echo "Options:"
        echo "1. Free up disk space by removing unused containers/images:"
        echo "   lxc list"
        echo "   lxc delete <unused-containers>"
        echo "   lxc image list"
        echo "   lxc image delete <unused-images>"
        echo ""
        echo "2. Clean up Docker if installed:"
        echo "   docker system prune -a"
        echo ""
        echo "3. Clean up apt cache:"
        echo "   sudo apt-get clean"
        echo "   sudo apt-get autoremove"
        echo ""
        echo "4. Use external storage volume"
        exit 1
    fi
    
    # Check if container already exists
    if lxc list --format csv | grep -q "^${CONTAINER_NAME},"; then
        echo "Container ${CONTAINER_NAME} already exists. Stopping and deleting..."
        lxc stop "${CONTAINER_NAME}" --force || true
        lxc delete "${CONTAINER_NAME}" || true
    fi
    
    # Launch base container with storage pool and more resources
    echo "Launching Ubuntu 22.04 container with storage optimization..."
    
    # Create container with a larger root disk
    lxc launch "${IMAGE_ALIAS}" "${CONTAINER_NAME}" \
        -c limits.memory=4GB \
        -c limits.cpu=2 \
        -s default \
        -d root,size=20GB
    
    # Wait for container to be ready
    wait_for_container "${CONTAINER_NAME}"
    
    # Clean up container before installation
    echo "Preparing container and cleaning up unnecessary files..."
    lxc exec "${CONTAINER_NAME}" -- bash -c "
        # Set non-interactive
        export DEBIAN_FRONTEND=noninteractive
        ln -fs /usr/share/zoneinfo/UTC /etc/localtime
        echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
        
        # Update and clean
        apt-get update
        apt-get upgrade -y
        apt-get clean
        apt-get autoremove -y
        
        # Remove unnecessary packages and files
        rm -rf /var/lib/apt/lists/*
        rm -rf /usr/share/doc/*
        rm -rf /usr/share/man/*
        rm -rf /var/cache/apt/*
        
        # Install only essential prerequisites
        apt-get update
        apt-get install -y --no-install-recommends \
            ca-certificates \
            curl \
            openssh-server \
            tzdata \
            perl \
            postfix
        
        # Clean again
        apt-get clean
        rm -rf /var/lib/apt/lists/*
    "
    
    # Configure SSH
    configure_ssh
    
    # Install GitLab with space optimization
    install_gitlab_minimal
    
    # Configure GitLab
    configure_gitlab
    
    echo "GitLab base container created successfully"
}

configure_ssh() {
    echo "Configuring SSH..."
    
    # Enable and start SSH
    lxc exec "${CONTAINER_NAME}" -- systemctl enable ssh
    lxc exec "${CONTAINER_NAME}" -- systemctl start ssh
    
    # Configure SSH for GitLab
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee -a /etc/ssh/sshd_config
# GitLab SSH configuration
Port 22
Port 2222
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication yes
EOF
    
    lxc exec "${CONTAINER_NAME}" -- systemctl restart ssh
}

install_gitlab_minimal() {
    echo "Installing GitLab CE with space optimization..."
    
    # Add GitLab repository
    lxc exec "${CONTAINER_NAME}" -- bash -c "
        curl -sS https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | bash
    "
    
    # Download package to host first to check space
    echo "Downloading GitLab package..."
    local temp_dir="/tmp/gitlab-install-$$"
    mkdir -p "$temp_dir"
    
    # Clean any previous downloads
    rm -f "$temp_dir/gitlab-ce*.deb"
    
    # Download the package
    wget -O "$temp_dir/gitlab-ce.deb" \
        "https://packages.gitlab.com/gitlab/gitlab-ce/packages/ubuntu/jammy/gitlab-ce_${GITLAB_VERSION}_amd64.deb/download.deb"
    
    # Copy to container
    echo "Copying GitLab package to container..."
    lxc file push "$temp_dir/gitlab-ce.deb" "${CONTAINER_NAME}/tmp/gitlab-ce.deb"
    
    # Install with cleanup during process
    echo "Installing GitLab (this may take some time)..."
    lxc exec "${CONTAINER_NAME}" -- bash -c "
        # Install the package
        DEBIAN_FRONTEND=noninteractive dpkg -i /tmp/gitlab-ce.deb || true
        
        # Fix any dependency issues
        DEBIAN_FRONTEND=noninteractive apt-get install -f -y
        
        # Remove the package file immediately
        rm -f /tmp/gitlab-ce.deb
        
        # Clean up
        apt-get clean
        rm -rf /var/lib/apt/lists/*
    "
    
    # Clean up host temp files
    rm -rf "$temp_dir"
    
    # Disable automatic start (we'll configure first)
    lxc exec "${CONTAINER_NAME}" -- systemctl disable gitlab-runsvdir || true
}

configure_gitlab() {
    echo "Configuring GitLab..."
    
    # Create minimal GitLab configuration
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee /etc/gitlab/gitlab.rb
# Minimal GitLab configuration

## GitLab URL
external_url 'http://gitlab.local'

## Reduce memory usage
gitlab_rails['time_zone'] = 'UTC'

## Minimal database configuration
postgresql['shared_buffers'] = "256MB"
postgresql['max_worker_processes'] = 4

## Minimal Redis configuration
redis['maxmemory'] = "200mb"
redis['maxmemory_policy'] = "allkeys-lru"

## Reduce Puma workers
puma['worker_processes'] = 2
puma['per_worker_max_memory_mb'] = 400

## Reduce Sidekiq concurrency
sidekiq['max_concurrency'] = 5

## Disable unnecessary services
gitlab_kas['enable'] = false
sentinel['enable'] = false
alertmanager['enable'] = false
pgbouncer_exporter['enable'] = false

## Container Registry (disabled)
registry['enable'] = false

## GitLab Pages (disabled)
gitlab_pages['enable'] = false

## Mattermost (disabled)
mattermost['enable'] = false

## Monitoring (minimal)
prometheus_monitoring['enable'] = false
grafana['enable'] = false

## Reduce logging
logging['svlogd_size'] = 10 * 1024 * 1024 # 10MB
logging['svlogd_num'] = 5
logging['logrotate_frequency'] = "weekly"
logging['logrotate_maxsize'] = "10MB"
logging['logrotate_rotate'] = 5

## Package registry (disabled to save space)
gitlab_rails['packages_enabled'] = false
gitlab_rails['dependency_proxy_enabled'] = false
gitlab_rails['terraform_state_enabled'] = false
EOF
}

main() {
    echo "Starting GitLab base container creation (minimal version)..."
    echo "This version uses minimal resources and disk space"
    
    check_lxd_running
    
    create_gitlab_base_container
    
    # Stop the base container
    echo "Stopping base container..."
    lxc stop "${CONTAINER_NAME}"
    
    # Export base container to image
    echo "Exporting base container to image..."
    # Remove existing image if it exists
    if lxc image list --format csv | grep -q "${CONTAINER_NAME}"; then
        echo "Removing existing ${CONTAINER_NAME} image..."
        lxc image delete "${CONTAINER_NAME}"
    fi
    lxc publish "${CONTAINER_NAME}" --alias "${CONTAINER_NAME}"
    
    # Delete base container
    echo "Removing base container..."
    lxc delete "${CONTAINER_NAME}"
    
    echo "GitLab base container setup complete!"
    echo ""
    echo "IMPORTANT: First time setup:"
    echo "1. Create instance: ./gen/gitlab.sh"
    echo "2. Start the container"
    echo "3. Run: lxc exec <container> -- gitlab-ctl reconfigure"
    echo "4. Default login: root / <see initial root password>"
    echo ""
    echo "Note: This minimal version has many features disabled to save space"
}

main "$@"
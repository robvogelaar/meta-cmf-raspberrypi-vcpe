#!/bin/bash

# GitLab Container Creation Script
# Creates a GitLab instance from the base container

set -e

source "$(dirname "$0")/gen-util.sh"

CONTAINER_NAME="gitlab"
BASE_CONTAINER="gitlab-base"
PROFILE="gitlab"
IP_ADDRESS="10.10.10.29"
DOMAIN="gitlab.vcpe.local"

# Create GitLab profile if it doesn't exist
create_gitlab_profile() {
    if ! lxc profile list --format csv | grep -q "^${PROFILE},"; then
        echo "Creating GitLab profile..."
        
        lxc profile create "${PROFILE}"
        
        cat << EOF | lxc profile edit "${PROFILE}"
config:
  limits.cpu: "4"
  limits.memory: 8GB
  security.privileged: "false"
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
      - systemctl start ssh
      - systemctl start postfix
      - systemctl start supervisor
      - sleep 30
      - gitlab-ctl reconfigure
      - sleep 60
      - /opt/gitlab/embedded/bin/setup-admin.rb
description: GitLab CE Server Profile
devices:
  eth0:
    name: eth0
    nictype: bridged
    parent: lxdbr1
    type: nic
  root:
    path: /
    pool: default
    size: 20GB
    type: disk
name: ${PROFILE}
used_by: []
EOF
    else
        echo "GitLab profile already exists"
    fi
}

create_gitlab_container() {
    echo "Creating GitLab container from base..."
    echo "This process may take 20-30 minutes for initial configuration..."
    
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
        "$(dirname "$0")/gitlab-base.sh"
        
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
    echo "Launching GitLab container from base image..."
    lxc launch "${BASE_CONTAINER}" "${CONTAINER_NAME}"
    
    # Apply profile
    lxc profile add "${CONTAINER_NAME}" "${PROFILE}"
    
    # Configure GitLab for this instance
    configure_gitlab_instance
    
    # Start container
    echo "Starting GitLab container..."
    lxc start "${CONTAINER_NAME}"
    
    # Wait for container to be ready
    wait_for_container "${CONTAINER_NAME}"
    
    # Wait for GitLab to initialize
    echo "Waiting for GitLab to initialize (this may take several minutes)..."
    wait_for_gitlab_ready
    
    # Setup initial configuration
    setup_initial_configuration
    
    # Create example project
    create_example_project
}

configure_gitlab_instance() {
    echo "Configuring GitLab instance..."
    
    # Update GitLab configuration with correct URL
    cat << EOF | lxc file push - "${CONTAINER_NAME}/etc/gitlab/gitlab.rb"
# GitLab configuration file

## GitLab URL
external_url 'http://${IP_ADDRESS}'

## Roles
roles ['application_role', 'redis_sentinel_role', 'redis_master_role']

## GitLab configuration
gitlab_rails['time_zone'] = 'UTC'
gitlab_rails['backup_keep_time'] = 604800
gitlab_rails['gitlab_email_enabled'] = false

## Database settings
postgresql['enable'] = true
postgresql['data_dir'] = "/var/opt/gitlab/postgresql/data"
postgresql['shared_preload_libraries'] = 'pg_stat_statements'

## Redis settings
redis['enable'] = true
redis['bind'] = '127.0.0.1'
redis['port'] = 6379

## Nginx settings
nginx['enable'] = true
nginx['listen_port'] = 80
nginx['listen_https'] = false
nginx['client_max_body_size'] = '250m'

## Git settings
git_data_dirs({
  "default" => {
    "path" => "/var/opt/gitlab/git-data"
  }
})

## SSH settings
gitlab_rails['gitlab_shell_ssh_port'] = 2222

## Monitoring
prometheus_monitoring['enable'] = true
grafana['enable'] = false

## Container Registry (disabled for resource conservation)
registry['enable'] = false

## GitLab Pages (disabled for resource conservation)
gitlab_pages['enable'] = false

## Mattermost (disabled for resource conservation)
mattermost['enable'] = false

## Performance settings
unicorn['worker_processes'] = 2
unicorn['worker_memory_limit_min'] = "400 * 1 << 20"
unicorn['worker_memory_limit_max'] = "650 * 1 << 20"

sidekiq['max_concurrency'] = 10

## Backup settings
gitlab_rails['manage_backup_path'] = true
gitlab_rails['backup_path'] = "/var/opt/gitlab/backups"

## Package registry settings
gitlab_rails['packages_enabled'] = true
gitlab_rails['dependency_proxy_enabled'] = true

## Logging
logging['svlogd_size'] = 50 * 1024 * 1024 # 50MB
logging['svlogd_num'] = 10
logging['logrotate_frequency'] = "daily"
logging['logrotate_rotate'] = 10
EOF
}

wait_for_gitlab_ready() {
    echo "Waiting for GitLab services to start..."
    
    # Wait for GitLab to be accessible
    local max_attempts=60
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        echo "Checking GitLab availability... (attempt $attempt/$max_attempts)"
        
        if curl -s -o /dev/null -w "%{http_code}" "http://${IP_ADDRESS}" | grep -q "200\|302"; then
            echo "GitLab is accessible!"
            break
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            echo "GitLab failed to start within expected time"
            echo "Check logs with: lxc exec ${CONTAINER_NAME} -- gitlab-ctl tail"
            exit 1
        fi
        
        sleep 30
        ((attempt++))
    done
    
    # Additional wait for GitLab to be fully ready
    echo "Waiting for GitLab to be fully ready..."
    sleep 60
}

setup_initial_configuration() {
    echo "Setting up initial GitLab configuration..."
    
    # Create admin user and example project
    lxc exec "${CONTAINER_NAME}" -- /opt/gitlab/embedded/bin/setup-admin.rb || true
    
    # Create GitLab CI/CD configuration examples
    lxc exec "${CONTAINER_NAME}" -- mkdir -p /tmp/examples
    
    # Copy example CI configuration
    lxc file push /tmp/gitlab-ci.yml.example "${CONTAINER_NAME}/tmp/examples/.gitlab-ci.yml" || true
}

create_example_project() {
    echo "Creating example vCPE project..."
    
    # Create a script to setup example project with GitLab API
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee /tmp/create-project.sh
#!/bin/bash

# Wait for GitLab API to be available
sleep 30

# Get root user token (this is a simplified approach for demo)
# In production, use proper authentication
PROJECT_NAME="vcpe-example"
PROJECT_DESCRIPTION="Example vCPE project for CI/CD demonstration"

# Create project using GitLab Rails console
gitlab-rails runner "
user = User.find_by(username: 'root')
if user
  project = user.projects.find_by(name: '${PROJECT_NAME}')
  unless project
    project = Projects::CreateService.new(
      user,
      name: '${PROJECT_NAME}',
      path: '${PROJECT_NAME}',
      description: '${PROJECT_DESCRIPTION}',
      visibility_level: Gitlab::VisibilityLevel::INTERNAL
    ).execute
    
    if project.persisted?
      puts 'Example project created successfully'
      
      # Add example files
      Files::CreateService.new(
        project,
        user,
        start_branch: 'main',
        branch_name: 'main',
        commit_message: 'Add example GitLab CI configuration',
        file_path: '.gitlab-ci.yml',
        file_content: File.read('/tmp/examples/.gitlab-ci.yml')
      ).execute if File.exist?('/tmp/examples/.gitlab-ci.yml')
      
      # Add README
      Files::CreateService.new(
        project,
        user,
        start_branch: 'main',
        branch_name: 'main',
        commit_message: 'Add README',
        file_path: 'README.md',
        file_content: '# vCPE Example Project

This is an example project demonstrating GitLab CI/CD integration with the vCPE environment.

## Features

- Automated container building
- Testing pipeline
- Deployment automation
- Integration with vCPE test infrastructure

## Getting Started

1. Clone this repository
2. Configure your vCPE environment
3. Run the CI/CD pipeline

## Pipeline Stages

- **Build**: Create vCPE containers
- **Test**: Run unit and integration tests
- **Deploy**: Deploy to staging/production environments
'
      ).execute
      
    else
      puts 'Failed to create example project'
    end
  else
    puts 'Example project already exists'
  end
else
  puts 'Root user not found'
end
"
EOF
    
    lxc exec "${CONTAINER_NAME}" -- chmod +x /tmp/create-project.sh
    lxc exec "${CONTAINER_NAME}" -- /tmp/create-project.sh || true
}

configure_firewall() {
    echo "Configuring firewall rules for GitLab..."
    
    # Allow HTTP access to GitLab
    lxc exec "${CONTAINER_NAME}" -- ufw allow 80/tcp || true
    
    # Allow HTTPS access (if needed later)
    lxc exec "${CONTAINER_NAME}" -- ufw allow 443/tcp || true
    
    # Allow SSH access for Git operations
    lxc exec "${CONTAINER_NAME}" -- ufw allow 2222/tcp || true
}

display_access_info() {
    echo ""
    echo "============================================"
    echo "GitLab Container Created Successfully!"
    echo "============================================"
    echo ""
    echo "Access Information:"
    echo "  URL: http://${IP_ADDRESS}"
    echo "  Container: ${CONTAINER_NAME}"
    echo ""
    echo "Login Credentials:"
    echo "  Username: root"
    echo "  Password: gitlab123"
    echo ""
    echo "Getting Started:"
    echo "1. Open http://${IP_ADDRESS} in your browser"
    echo "2. Log in with the credentials above"
    echo "3. Change the default password"
    echo "4. Create additional users and groups"
    echo "5. Import or create new projects"
    echo ""
    echo "Features Available:"
    echo "  - Git repository hosting"
    echo "  - GitLab CI/CD pipelines"
    echo "  - Issue tracking"
    echo "  - Merge request management"
    echo "  - Package registry"
    echo "  - Built-in monitoring"
    echo ""
    echo "Example Project:"
    echo "  - 'vcpe-example' project created with sample CI/CD configuration"
    echo "  - Demonstrates integration with vCPE environment"
    echo ""
    echo "Git Clone URLs:"
    echo "  HTTP: http://${IP_ADDRESS}/root/vcpe-example.git"
    echo "  SSH:  git@${IP_ADDRESS}:root/vcpe-example.git"
    echo ""
    echo "Container Management:"
    echo "  Start:     lxc start ${CONTAINER_NAME}"
    echo "  Stop:      lxc stop ${CONTAINER_NAME}"
    echo "  Shell:     lxc exec ${CONTAINER_NAME} bash"
    echo "  Logs:      lxc exec ${CONTAINER_NAME} -- gitlab-ctl tail"
    echo "  Status:    lxc exec ${CONTAINER_NAME} -- gitlab-ctl status"
    echo "  Restart:   lxc exec ${CONTAINER_NAME} -- gitlab-ctl restart"
    echo ""
    echo "For SSH tunnel access:"
    echo "  ssh -L 80:${IP_ADDRESS}:80 user@host"
    echo "  Then access: http://localhost"
    echo ""
    echo "Integration with vCPE:"
    echo "  - Host vCPE source code repositories"
    echo "  - Automate vCPE container builds and deployments"
    echo "  - Track issues and manage merge requests"
    echo "  - Integrate with Jenkins for advanced CI/CD"
    echo ""
    echo "Resource Usage:"
    echo "  - Memory: 8GB (can be reduced to 4GB for small teams)"
    echo "  - CPU: 4 cores (can be reduced to 2 cores for light usage)"
    echo "  - Storage: ~5GB for installation + repositories"
    echo ""
}

main() {
    echo "Starting GitLab container creation..."
    echo "Note: GitLab requires significant resources and time to initialize"
    
    check_lxd_running
    
    create_gitlab_profile
    create_gitlab_container
    configure_firewall
    
    display_access_info
}

main "$@"
#!/bin/bash

# GitLab Base Container Creation Script
# Creates a base Ubuntu container with GitLab CE (Community Edition - Free)

set -e

source "$(dirname "$0")/gen-util.sh"

CONTAINER_NAME="gitlab-base"
IMAGE_ALIAS="ubuntu/22.04"
GITLAB_VERSION="18.2.0-ce.0"
GITLAB_HOME="/var/opt/gitlab"
GITLAB_CONFIG="/etc/gitlab"
GITLAB_LOGS="/var/log/gitlab"
# Alternative mirror for GitLab packages
GITLAB_MIRROR="https://packages.gitlab.com/gitlab/gitlab-ce/ubuntu/pool/jammy/main/g/gitlab-ce"

create_gitlab_base_container() {
    echo "Creating GitLab base container..."
    
    # Check if container already exists
    if lxc list --format csv | grep -q "^${CONTAINER_NAME},"; then
        echo "Container ${CONTAINER_NAME} already exists. Stopping and deleting..."
        lxc stop "${CONTAINER_NAME}" --force || true
        lxc delete "${CONTAINER_NAME}" || true
    fi
    
    # Launch base container with more resources and storage
    echo "Launching Ubuntu 22.04 container..."
    lxc launch "${IMAGE_ALIAS}" "${CONTAINER_NAME}" -c limits.memory=4GB -c limits.cpu=2 -s default
    
    # Wait for container to be ready
    wait_for_container "${CONTAINER_NAME}"
    
    # Set non-interactive environment
    echo "Setting non-interactive environment..."
    lxc exec "${CONTAINER_NAME}" -- bash -c "echo 'export DEBIAN_FRONTEND=noninteractive' >> /etc/environment"
    lxc exec "${CONTAINER_NAME}" -- bash -c "ln -fs /usr/share/zoneinfo/UTC /etc/localtime"
    lxc exec "${CONTAINER_NAME}" -- bash -c "echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections"
    
    # Update system
    echo "Updating system packages..."
    lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive apt-get update"
    lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive apt-get upgrade -y"
    
    # Install prerequisites
    echo "Installing prerequisites..."
    lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive apt-get install -y \
        ca-certificates \
        curl \
        openssh-server \
        tzdata \
        perl \
        wget \
        git \
        postfix \
        supervisor \
        apt-transport-https \
        gnupg"
    
    # Configure DNS for better connectivity
    echo "Configuring DNS..."
    lxc exec "${CONTAINER_NAME}" -- bash -c "echo 'nameserver 8.8.8.8' > /etc/resolv.conf"
    lxc exec "${CONTAINER_NAME}" -- bash -c "echo 'nameserver 8.8.4.4' >> /etc/resolv.conf"
    
    # Configure SSH
    configure_ssh
    
    # Install GitLab
    install_gitlab
    
    # Configure GitLab
    configure_gitlab
    
    # Configure supervisor
    create_supervisor_config
    
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

install_gitlab() {
    echo "Installing GitLab CE..."
    
    # Check available disk space
    local available_space=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if (( available_space < 6 )); then
        echo "WARNING: Low disk space detected (${available_space}GB available)"
        echo "GitLab installation requires at least 6GB free space"
        echo "Attempting to proceed with cleanup..."
    fi
    
    # Add GitLab repository with retry
    echo "Adding GitLab repository..."
    local retry_count=0
    local max_retries=3
    while [ $retry_count -lt $max_retries ]; do
        # First check if we can reach the GitLab server
        echo "Testing connectivity to packages.gitlab.com..."
        if ! lxc exec "${CONTAINER_NAME}" -- bash -c "curl -s --connect-timeout 10 -o /dev/null -w '%{http_code}' https://packages.gitlab.com/" | grep -q "200\|301\|302"; then
            echo "WARNING: Cannot reach packages.gitlab.com - checking DNS and connectivity"
            lxc exec "${CONTAINER_NAME}" -- bash -c "nslookup packages.gitlab.com || true"
            lxc exec "${CONTAINER_NAME}" -- bash -c "ping -c 1 8.8.8.8 || true"
        fi
        
        # Download and execute the script in one command
        if lxc exec "${CONTAINER_NAME}" -- bash -c "curl -fsSL https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | bash"; then
            echo "GitLab repository added successfully"
            break
        else
            retry_count=$((retry_count + 1))
            echo "Failed to add GitLab repository (attempt $retry_count/$max_retries)"
            if [ $retry_count -lt $max_retries ]; then
                echo "Waiting 30 seconds before retry..."
                sleep 30
            fi
        fi
    done
    
    if [ $retry_count -eq $max_retries ]; then
        echo "ERROR: Failed to add GitLab repository via script"
        echo "Attempting manual repository configuration..."
        
        # Try manual repository setup
        if add_gitlab_repo_manually; then
            echo "GitLab repository added manually"
        else
            echo "ERROR: Failed to add GitLab repository"
            return 1
        fi
    fi
    
    # Clean up package cache to save space
    lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive apt-get clean"
    lxc exec "${CONTAINER_NAME}" -- bash -c "rm -rf /var/lib/apt/lists/*"
    
    # Update package lists
    lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive apt-get update"
    
    # Install GitLab CE with retry and alternative methods
    echo "Installing GitLab CE package..."
    retry_count=0
    while [ $retry_count -lt $max_retries ]; do
        # Try to install with version if specified
        if lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive apt-get install -y \
            --no-install-recommends \
            -o Acquire::http::Timeout=120 \
            -o Acquire::https::Timeout=120 \
            -o Acquire::Retries=3 \
            gitlab-ce=${GITLAB_VERSION} 2>&1"; then
            echo "GitLab CE installed successfully"
            break
        else
            retry_count=$((retry_count + 1))
            echo "Failed to install GitLab CE (attempt $retry_count/$max_retries)"
            
            if [ $retry_count -lt $max_retries ]; then
                # Try without specific version on retry
                echo "Retrying without version specification..."
                if lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive apt-get install -y \
                    --no-install-recommends \
                    -o Acquire::http::Timeout=120 \
                    -o Acquire::https::Timeout=120 \
                    -o Acquire::Retries=3 \
                    gitlab-ce 2>&1"; then
                    echo "GitLab CE installed successfully (latest version)"
                    break
                fi
                echo "Waiting 60 seconds before next retry..."
                sleep 60
            fi
        fi
    done
    
    if [ $retry_count -eq $max_retries ]; then
        echo "ERROR: Failed to install GitLab CE via apt"
        echo "Attempting alternative installation method..."
        
        # Try direct download as fallback
        if install_gitlab_direct; then
            echo "GitLab CE installed successfully via direct download"
        else
            echo "ERROR: All installation methods failed"
            return 1
        fi
    fi
    
    # Disable automatic start (we'll configure first)
    lxc exec "${CONTAINER_NAME}" -- systemctl disable gitlab-runsvdir || true
}

add_gitlab_repo_manually() {
    echo "Configuring GitLab repository manually..."
    
    # Add GitLab GPG key
    echo "Adding GitLab GPG key..."
    if ! lxc exec "${CONTAINER_NAME}" -- bash -c "curl -fsSL https://packages.gitlab.com/gitlab/gitlab-ce/gpgkey | gpg --dearmor -o /usr/share/keyrings/gitlab_gitlab-ce-archive-keyring.gpg"; then
        echo "Failed to add GPG key, trying alternative method..."
        lxc exec "${CONTAINER_NAME}" -- bash -c "wget -qO- https://packages.gitlab.com/gitlab/gitlab-ce/gpgkey | apt-key add -" || return 1
    fi
    
    # Add repository configuration
    echo "Adding repository configuration..."
    lxc exec "${CONTAINER_NAME}" -- bash -c "cat > /etc/apt/sources.list.d/gitlab_gitlab-ce.list << 'EOF'
deb [signed-by=/usr/share/keyrings/gitlab_gitlab-ce-archive-keyring.gpg] https://packages.gitlab.com/gitlab/gitlab-ce/ubuntu/ jammy main
deb-src [signed-by=/usr/share/keyrings/gitlab_gitlab-ce-archive-keyring.gpg] https://packages.gitlab.com/gitlab/gitlab-ce/ubuntu/ jammy main
EOF"
    
    # Update package lists
    echo "Updating package lists..."
    if lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive apt-get update"; then
        return 0
    else
        echo "Failed to update package lists after adding repository"
        return 1
    fi
}

install_gitlab_direct() {
    echo "Attempting direct download of GitLab package..."
    
    # Get latest available version
    local gitlab_url="${GITLAB_MIRROR}/gitlab-ce_${GITLAB_VERSION}_amd64.deb"
    local temp_file="/tmp/gitlab-ce.deb"
    
    # Try to download the package
    echo "Downloading from: $gitlab_url"
    if lxc exec "${CONTAINER_NAME}" -- wget -T 120 --tries=3 -O "$temp_file" "$gitlab_url"; then
        echo "Download successful, installing package..."
        
        # Install the downloaded package
        if lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive dpkg -i $temp_file || apt-get install -f -y"; then
            lxc exec "${CONTAINER_NAME}" -- rm -f "$temp_file"
            return 0
        else
            echo "Failed to install downloaded package"
            lxc exec "${CONTAINER_NAME}" -- rm -f "$temp_file"
            return 1
        fi
    else
        echo "Failed to download GitLab package"
        
        # Try to get the latest version instead
        echo "Attempting to find latest available version..."
        local latest_url="${GITLAB_MIRROR}/"
        
        # List available versions
        echo "Checking available versions at GitLab mirror..."
        lxc exec "${CONTAINER_NAME}" -- curl -s "$latest_url" | grep -oP 'gitlab-ce_[\d\.]+-ce\.0_amd64\.deb' | head -5 || true
        
        return 1
    fi
}

configure_gitlab() {
    echo "Configuring GitLab..."
    
    # Create GitLab configuration
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee /etc/gitlab/gitlab.rb
# GitLab configuration file

## GitLab URL
external_url 'http://gitlab.local'

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
pages_external_url 'http://pages.gitlab.local'
gitlab_pages['enable'] = false

## Mattermost (disabled for resource conservation)
mattermost['enable'] = false

## Performance settings (reduced for limited resources)
puma['worker_processes'] = 2
puma['per_worker_max_memory_mb'] = 400

sidekiq['max_concurrency'] = 5

## Backup settings
gitlab_rails['manage_backup_path'] = true
gitlab_rails['backup_path'] = "/var/opt/gitlab/backups"

## LDAP (disabled by default)
gitlab_rails['ldap_enabled'] = false

## Email settings (disabled by default)
gitlab_rails['smtp_enable'] = false

## Package registry settings
gitlab_rails['packages_enabled'] = true
gitlab_rails['dependency_proxy_enabled'] = true

## Feature flags
gitlab_rails['feature_flags_unleash_enabled'] = false

## Logging
logging['svlogd_size'] = 50 * 1024 * 1024 # 50MB
logging['svlogd_num'] = 10
logging['svlogd_timeout'] = 24 * 60 * 60 # 1 day
logging['logrotate_frequency'] = "daily"
logging['logrotate_maxsize'] = "50MB"
logging['logrotate_rotate'] = 10

## Cleanup
gitlab_rails['env'] = {
  'BUNDLE_GEMFILE' => "/opt/gitlab/embedded/service/gitlab-rails/Gemfile",
  'PATH' => "/opt/gitlab/bin:/opt/gitlab/embedded/bin:/bin:/usr/bin",
  'ICU_DATA' => "/opt/gitlab/embedded/share/icu/current",
  'PYTHONPATH' => "/opt/gitlab/embedded/lib/python3.9/site-packages"
}
EOF
    
    # Create initial configuration
    create_initial_gitlab_config
}

create_initial_gitlab_config() {
    echo "Creating initial GitLab configuration..."
    
    # Create admin user setup script
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee /opt/gitlab/embedded/bin/setup-admin.rb
#!/opt/gitlab/embedded/bin/ruby

# Setup initial admin user for GitLab

require '/opt/gitlab/embedded/service/gitlab-rails/config/environment'

# Create root user if it doesn't exist
user = User.find_by(username: 'root')
if user.nil?
  user = User.new(
    username: 'root',
    email: 'admin@gitlab.local',
    name: 'Administrator',
    admin: true,
    password: 'gitlab123',
    password_confirmation: 'gitlab123',
    confirmed_at: Time.now
  )
  
  if user.save
    puts "Admin user created successfully"
    puts "Username: root"
    puts "Password: gitlab123"
  else
    puts "Failed to create admin user: #{user.errors.full_messages}"
  end
else
  puts "Admin user already exists"
end

# Create example project
project = Project.find_by(name: 'vcpe-example')
if project.nil?
  project = Projects::CreateService.new(
    user,
    name: 'vcpe-example',
    path: 'vcpe-example',
    description: 'Example vCPE project for CI/CD demonstration',
    visibility_level: Gitlab::VisibilityLevel::INTERNAL
  ).execute
  
  if project.persisted?
    puts "Example project created successfully"
  else
    puts "Failed to create example project: #{project.errors.full_messages}"
  end
end
EOF
    
    lxc exec "${CONTAINER_NAME}" -- chmod +x /opt/gitlab/embedded/bin/setup-admin.rb
    
    # Create GitLab CI configuration example
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee /tmp/gitlab-ci.yml.example
# Example GitLab CI configuration for vCPE project

stages:
  - build
  - test
  - deploy

variables:
  VCPE_ENV: "development"
  LXD_REMOTE: "local"

before_script:
  - echo "Setting up vCPE environment..."
  - export PATH="$PATH:/usr/local/bin"

build:
  stage: build
  script:
    - echo "Building vCPE containers..."
    - # ./gen/bridges.sh
    - # ./gen/bng.sh 7
    - echo "Build completed"
  artifacts:
    paths:
      - logs/
    expire_in: 1 week

test:unit:
  stage: test
  script:
    - echo "Running unit tests..."
    - # python3 -m pytest tests/unit/
    - echo "Unit tests passed"

test:integration:
  stage: test
  script:
    - echo "Running integration tests..."
    - # python3 -m pytest tests/integration/
    - echo "Integration tests passed"

test:security:
  stage: test
  script:
    - echo "Running security scan..."
    - # Run security scanning tools
    - echo "Security scan completed"

deploy:staging:
  stage: deploy
  script:
    - echo "Deploying to staging..."
    - # Deploy containers to staging environment
    - echo "Staging deployment completed"
  environment:
    name: staging
    url: http://staging.vcpe.local
  only:
    - develop

deploy:production:
  stage: deploy
  script:
    - echo "Deploying to production..."
    - # Deploy containers to production environment
    - echo "Production deployment completed"
  environment:
    name: production
    url: http://prod.vcpe.local
  only:
    - main
  when: manual
EOF
}

create_supervisor_config() {
    echo "Creating supervisor configuration..."
    
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee /etc/supervisor/conf.d/gitlab.conf
[program:gitlab]
command=/opt/gitlab/embedded/bin/runsvdir-start
user=root
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/gitlab.log
stderr_logfile=/var/log/supervisor/gitlab_error.log
killasgroup=true
stopasgroup=true
EOF
    
    lxc exec "${CONTAINER_NAME}" -- systemctl enable supervisor
}

main() {
    echo "Starting GitLab base container creation..."
    echo "Note: This process may take 15-30 minutes due to GitLab's size and complexity"
    
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
    echo "You can now create GitLab instances using gitlab.sh"
    echo ""
    echo "Default credentials:"
    echo "  Username: root"
    echo "  Password: gitlab123"
    echo ""
    echo "Note: Change the default password after first login!"
    echo "GitLab requires significant resources (8GB RAM, 4 CPU cores recommended)"
}

main "$@"
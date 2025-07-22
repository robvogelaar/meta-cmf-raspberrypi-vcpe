#!/bin/bash

# Jenkins Base Container Creation Script
# Creates a base Ubuntu container with Jenkins LTS

set -e

source "$(dirname "$0")/gen-util.sh"

CONTAINER_NAME="jenkins-base"
IMAGE_ALIAS="ubuntu/22.04"
JENKINS_VERSION="lts"
JENKINS_HOME="/var/lib/jenkins"
JENKINS_USER="jenkins"
JENKINS_PORT="8080"

create_jenkins_base_container() {
    echo "Creating Jenkins base container..."
    
    # Check if container already exists
    if lxc list --format csv | grep -q "^${CONTAINER_NAME},"; then
        echo "Container ${CONTAINER_NAME} already exists. Stopping and deleting..."
        lxc stop "${CONTAINER_NAME}" --force || true
        lxc delete "${CONTAINER_NAME}" || true
    fi
    
    # Launch base container
    echo "Launching Ubuntu 22.04 container..."
    lxc launch "${IMAGE_ALIAS}" "${CONTAINER_NAME}"
    
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
    
    # Install Java 11 (required for Jenkins)
    echo "Installing Java 11..."
    lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive apt-get install -y \
        openjdk-11-jdk \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        wget \
        git \
        unzip \
        build-essential \
        python3 \
        python3-pip \
        nodejs \
        npm \
        docker.io \
        supervisor"
    
    # Add Jenkins repository and install Jenkins
    install_jenkins
    
    # Install additional tools
    install_additional_tools
    
    # Configure Jenkins
    configure_jenkins
    
    # Create systemd service override
    create_jenkins_service_override
    
    # Configure supervisor
    create_supervisor_config
    
    echo "Jenkins base container created successfully"
}

install_jenkins() {
    echo "Installing Jenkins LTS..."
    
    # Add Jenkins repository key (using new method for Ubuntu 22.04)
    lxc exec "${CONTAINER_NAME}" -- wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | \
    lxc exec "${CONTAINER_NAME}" -- tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
    
    # Add Jenkins repository
    lxc exec "${CONTAINER_NAME}" -- sh -c 'echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
    
    # Update package list and install Jenkins
    lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive apt-get update"
    lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive apt-get install -y jenkins"
    
    # Start and enable Jenkins
    lxc exec "${CONTAINER_NAME}" -- systemctl enable jenkins
}

install_additional_tools() {
    echo "Installing additional development tools..."
    
    # Install Docker Compose
    lxc exec "${CONTAINER_NAME}" -- curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    lxc exec "${CONTAINER_NAME}" -- chmod +x /usr/local/bin/docker-compose
    
    # Install Ansible
    lxc exec "${CONTAINER_NAME}" -- pip3 install ansible
    
    # Install AWS CLI
    lxc exec "${CONTAINER_NAME}" -- pip3 install awscli
    
    # Install kubectl
    lxc exec "${CONTAINER_NAME}" -- bash -c "curl -LO \"https://dl.k8s.io/release/\$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl\""
    lxc exec "${CONTAINER_NAME}" -- install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    lxc exec "${CONTAINER_NAME}" -- rm kubectl
    
    # Install Terraform
    lxc exec "${CONTAINER_NAME}" -- bash -c "wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor > /usr/share/keyrings/hashicorp-archive-keyring.gpg"
    lxc exec "${CONTAINER_NAME}" -- bash -c "echo 'deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com jammy main' > /etc/apt/sources.list.d/hashicorp.list"
    lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive apt-get update"
    lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive apt-get install -y terraform"
    
    # Add jenkins user to docker group
    lxc exec "${CONTAINER_NAME}" -- usermod -aG docker jenkins
}

configure_jenkins() {
    echo "Configuring Jenkins..."
    
    # Create Jenkins directories
    lxc exec "${CONTAINER_NAME}" -- mkdir -p "${JENKINS_HOME}/init.groovy.d"
    lxc exec "${CONTAINER_NAME}" -- chown -R jenkins:jenkins "${JENKINS_HOME}"
    
    # Configure Jenkins JVM options
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee /etc/default/jenkins
# defaults for Jenkins automation server

# pulled in from the init script; don't change here unless you know
# what you're doing.
NAME=jenkins

# arguments to pass to java
JAVA_ARGS="-Djava.awt.headless=true"

# jenkins home location
JENKINS_HOME=/var/lib/jenkins

# set this to false if you don't want Jenkins to run by itself
# in this set up, you are expected to provide a servlet container
# to host jenkins.
RUN_STANDALONE=true

# log location.  this may be a file, or stdout
JENKINS_LOG=/var/log/jenkins/jenkins.log

# whether to enable web access logging or not.
# Set to "yes" to enable logging to /var/log/jenkins/access_log
JENKINS_ENABLE_ACCESS_LOG="no"

# OS LIMITS SETUP
#   comment this out to observe /etc/security/limits.conf
#   this is on by default because
#   http://github.com/jenkinsci/jenkins/commit/2fb288474e980d0e7ff9c4a3b768874835a3e92e
#   reported that Ubuntu's PAM configuration doesn't include
#   pam_limits.so, and as a result the # of file
#   descriptors are forced to 1024 regardless of /etc/security/limits.conf
MAXOPENFILES=8192

# set the umask to control permission bits of files that Jenkins creates.
#   027 makes files read-only for group and inaccessible for others, which some security sensitive users
#   might consider benefitial, especially if Jenkins is running in a
#   restricted environment, such as chroot.  Unfortunately, server types for
#   which this script is used, including Debian and Ubuntu, create users with
#   umask 022, which means that the files that Jenkins creates will be readable for everyone.
#UMASK=027

# port for HTTP connector (default 8080; disable with -1)
HTTP_PORT=8080

# servlet context, important if you want to use apache proxying
PREFIX=/

# arguments to pass to jenkins.
# --javahome=$JAVA_HOME
# --httpListenAddress=$HTTP_HOST (default 0.0.0.0)
# --httpPort=$HTTP_PORT (default 8080; disable with -1)
# --httpsPort=$HTTPS_PORT
# --argumentsRealm.passwd.$ADMIN_USER=[password]
# --argumentsRealm.roles.$ADMIN_USER=admin
# --webroot=~/.jenkins/war
# --prefix=$PREFIX

JENKINS_ARGS="--webroot=/var/cache/$NAME/war --httpPort=$HTTP_PORT"
EOF
    
    # Create basic Jenkins configuration
    create_jenkins_initial_config
    
    # Create plugins list
    create_plugins_list
}

create_jenkins_initial_config() {
    echo "Creating Jenkins initial configuration..."
    
    # Create basic security configuration
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee "${JENKINS_HOME}/init.groovy.d/basic-security.groovy"
#!groovy

import jenkins.model.*
import hudson.security.*
import hudson.security.csrf.DefaultCrumbIssuer
import jenkins.security.s2m.AdminWhitelistRule

def instance = Jenkins.getInstance()

// Enable slave to master security
instance.getInjector().getInstance(AdminWhitelistRule.class).setMasterKillSwitch(false)

// Enable CSRF protection
instance.setCrumbIssuer(new DefaultCrumbIssuer(true))

// Create admin user
def hudsonRealm = new HudsonPrivateSecurityRealm(false)
hudsonRealm.createAccount("admin", "admin123")
instance.setSecurityRealm(hudsonRealm)

// Set authorization strategy
def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
strategy.setAllowAnonymousRead(false)
instance.setAuthorizationStrategy(strategy)

instance.save()
EOF
    
    # Create plugin installation script
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee "${JENKINS_HOME}/init.groovy.d/install-plugins.groovy"
#!groovy

import jenkins.model.*
import java.util.logging.Logger

def logger = Logger.getLogger("")
def installed = false
def initialized = false

def pluginParameter="git workflow-aggregator pipeline-stage-view blueocean docker-workflow ansible terraform"
def plugins = pluginParameter.split()
logger.info("" + plugins)
def instance = Jenkins.getInstance()
def pm = instance.getPluginManager()
def uc = instance.getUpdateCenter()
plugins.each {
  logger.info("Checking " + it)
  if (!pm.getPlugin(it)) {
    logger.info("Looking UpdateCenter for " + it)
    if (!initialized) {
      uc.updateAllSites()
      initialized = true
    }
    def plugin = uc.getPlugin(it)
    if (plugin) {
      logger.info("Installing " + it)
      plugin.deploy()
      installed = true
    }
  }
}
if (installed) {
  logger.info("Plugins installed, restarting Jenkins")
  instance.restart()
}
EOF
    
    # Set ownership
    lxc exec "${CONTAINER_NAME}" -- chown -R jenkins:jenkins "${JENKINS_HOME}"
}

create_plugins_list() {
    echo "Creating plugins list..."
    
    # Create plugins.txt for later use
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee "${JENKINS_HOME}/plugins.txt"
git
workflow-aggregator
pipeline-stage-view
blueocean
docker-workflow
ansible
terraform
build-timeout
timestamper
ws-cleanup
ant
gradle
nodejs
maven-plugin
email-ext
mailer
slack
github
bitbucket
gitlab-plugin
ssh-slaves
matrix-auth
pam-auth
ldap
role-strategy
build-user-vars-plugin
envinject
parameterized-trigger
conditional-buildstep
copyartifact
junit
jacoco
sonar
checkstyle
warnings-ng
performance
htmlpublisher
EOF
    
    lxc exec "${CONTAINER_NAME}" -- chown jenkins:jenkins "${JENKINS_HOME}/plugins.txt"
}

create_jenkins_service_override() {
    echo "Creating Jenkins systemd service override..."
    
    lxc exec "${CONTAINER_NAME}" -- mkdir -p /etc/systemd/system/jenkins.service.d/
    
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee /etc/systemd/system/jenkins.service.d/override.conf
[Service]
Environment="JAVA_OPTS=-Djava.awt.headless=true -Xmx2048m -XX:+UseG1GC -XX:+UseStringDeduplication"
LimitNOFILE=8192
EOF
    
    lxc exec "${CONTAINER_NAME}" -- systemctl daemon-reload
}

create_supervisor_config() {
    echo "Creating supervisor configuration..."
    
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee /etc/supervisor/conf.d/jenkins.conf
[program:jenkins]
command=/usr/bin/java -Djava.awt.headless=true -Xmx2048m -XX:+UseG1GC -XX:+UseStringDeduplication -jar /usr/share/jenkins/jenkins.war --httpPort=8080 --webroot=/var/cache/jenkins/war
user=jenkins
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/jenkins.log
stderr_logfile=/var/log/supervisor/jenkins_error.log
environment=JENKINS_HOME="/var/lib/jenkins"
directory=/var/lib/jenkins
EOF
    
    lxc exec "${CONTAINER_NAME}" -- systemctl enable supervisor
}

main() {
    echo "Starting Jenkins base container creation..."
    
    check_lxd_running
    
    create_jenkins_base_container
    
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
    
    echo "Jenkins base container setup complete!"
    echo "You can now create Jenkins instances using jenkins.sh"
    echo ""
    echo "Default credentials:"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo ""
    echo "Note: Change the default password after first login!"
}

main "$@"
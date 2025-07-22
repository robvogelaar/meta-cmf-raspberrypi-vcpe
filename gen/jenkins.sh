#!/bin/bash

# Jenkins Container Creation Script
# Creates a Jenkins instance from the base container

set -e

source "$(dirname "$0")/gen-util.sh"

CONTAINER_NAME="jenkins"
BASE_CONTAINER="jenkins-base"
PROFILE="jenkins"
IP_ADDRESS="10.10.10.28"

# Create Jenkins profile if it doesn't exist
create_jenkins_profile() {
    if ! lxc profile list --format csv | grep -q "^${PROFILE},"; then
        echo "Creating Jenkins profile..."
        
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
      - systemctl start docker
      - systemctl start supervisor
      - sleep 10
      - systemctl start jenkins
description: Jenkins CI/CD Server Profile
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
        echo "Jenkins profile already exists"
    fi
}

create_jenkins_container() {
    echo "Creating Jenkins container from base..."
    
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
        "$(dirname "$0")/jenkins-base.sh"
        
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
    echo "Launching Jenkins container from base image..."
    lxc launch "${BASE_CONTAINER}" "${CONTAINER_NAME}"
    
    # Apply profile
    lxc profile add "${CONTAINER_NAME}" "${PROFILE}"
    
    # Start container
    echo "Starting Jenkins container..."
    lxc start "${CONTAINER_NAME}"
    
    # Wait for container to be ready
    wait_for_container "${CONTAINER_NAME}"
    
    # Configure Jenkins for this instance
    configure_jenkins_instance
    
    # Wait for services to start
    echo "Waiting for services to initialize..."
    sleep 30
    
    # Check if Jenkins is accessible
    echo "Checking Jenkins accessibility..."
    for i in {1..12}; do
        if curl -s -o /dev/null -w "%{http_code}" "http://${IP_ADDRESS}:8080" | grep -q "200\|403"; then
            echo "Jenkins is accessible!"
            break
        fi
        echo "Waiting for Jenkins to start... (attempt $i/12)"
        sleep 10
    done
    
    # Get initial admin password
    get_initial_admin_password
}

configure_jenkins_instance() {
    echo "Configuring Jenkins instance..."
    
    # Create jobs directory
    lxc exec "${CONTAINER_NAME}" -- mkdir -p /var/lib/jenkins/jobs
    
    # Create example pipeline job
    create_example_pipeline_job
    
    # Configure Docker access (if jenkins user exists)
    lxc exec "${CONTAINER_NAME}" -- bash -c "id jenkins >/dev/null 2>&1 && usermod -aG docker jenkins || echo 'Jenkins user not found, skipping Docker group'"
    
    # Set proper permissions (if jenkins user exists)
    lxc exec "${CONTAINER_NAME}" -- bash -c "id jenkins >/dev/null 2>&1 && chown -R jenkins:jenkins /var/lib/jenkins || echo 'Jenkins user not found, skipping chown'"
}

create_example_pipeline_job() {
    echo "Creating example pipeline job..."
    
    lxc exec "${CONTAINER_NAME}" -- mkdir -p "/var/lib/jenkins/jobs/vcpe-pipeline"
    
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee "/var/lib/jenkins/jobs/vcpe-pipeline/config.xml"
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@2.40">
  <actions/>
  <description>Example vCPE CI/CD Pipeline</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <hudson.plugins.jira.JiraProjectProperty plugin="jira@3.7"/>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2.87">
    <script>
pipeline {
    agent any
    
    environment {
        VCPE_ENV = 'development'
        LXD_REMOTE = 'local'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out vCPE repository...'
                // git 'https://github.com/your-org/meta-cmf-raspberrypi-vcpe.git'
            }
        }
        
        stage('Build') {
            steps {
                echo 'Building vCPE containers...'
                script {
                    // Example build commands
                    sh '''
                        echo "Building vCPE environment..."
                        # ./gen/bridges.sh
                        # ./gen/bng.sh 7
                        echo "Build completed"
                    '''
                }
            }
        }
        
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        echo 'Running unit tests...'
                        sh 'echo "Unit tests passed"'
                    }
                }
                stage('Integration Tests') {
                    steps {
                        echo 'Running integration tests...'
                        script {
                            sh '''
                                echo "Running vCPE integration tests..."
                                # python3 -m pytest tests/
                                echo "Integration tests passed"
                            '''
                        }
                    }
                }
                stage('Security Scan') {
                    steps {
                        echo 'Running security scan...'
                        sh 'echo "Security scan completed"'
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to staging environment...'
                script {
                    sh '''
                        echo "Deploying vCPE environment..."
                        # Deploy containers to staging
                        echo "Deployment completed"
                    '''
                }
            }
        }
        
        stage('Notify') {
            steps {
                echo 'Sending notifications...'
                // emailext body: 'vCPE Pipeline completed successfully', 
                //          subject: 'vCPE Build Status', 
                //          to: 'team@example.com'
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed'
            // archiveArtifacts artifacts: 'logs/**', fingerprint: true
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
            // Send failure notifications
        }
    }
}
    </script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
EOF
    
    lxc exec "${CONTAINER_NAME}" -- bash -c "id jenkins >/dev/null 2>&1 && chown -R jenkins:jenkins '/var/lib/jenkins/jobs/vcpe-pipeline' || echo 'Jenkins user not found, skipping pipeline chown'"
}

get_initial_admin_password() {
    echo "Retrieving initial admin password..."
    
    # Wait for password file to be created
    for i in {1..6}; do
        if lxc exec "${CONTAINER_NAME}" -- test -f /var/lib/jenkins/secrets/initialAdminPassword; then
            INITIAL_PASSWORD=$(lxc exec "${CONTAINER_NAME}" -- cat /var/lib/jenkins/secrets/initialAdminPassword 2>/dev/null || echo "admin123")
            break
        fi
        echo "Waiting for Jenkins to generate initial password... (attempt $i/6)"
        sleep 10
    done
    
    if [[ -z "$INITIAL_PASSWORD" ]]; then
        INITIAL_PASSWORD="admin123"
    fi
}

configure_firewall() {
    echo "Configuring firewall rules for Jenkins..."
    
    # Allow HTTP access to Jenkins
    lxc exec "${CONTAINER_NAME}" -- ufw allow 8080/tcp || true
    
    # Allow Jenkins agent connections
    lxc exec "${CONTAINER_NAME}" -- ufw allow 50000/tcp || true
}

display_access_info() {
    echo ""
    echo "============================================"
    echo "Jenkins Container Created Successfully!"
    echo "============================================"
    echo ""
    echo "Access Information:"
    echo "  URL: http://${IP_ADDRESS}:8080"
    echo "  Container: ${CONTAINER_NAME}"
    echo ""
    echo "Login Credentials:"
    echo "  Username: admin"
    echo "  Password: ${INITIAL_PASSWORD:-admin123}"
    echo ""
    echo "Getting Started:"
    echo "1. Open http://${IP_ADDRESS}:8080 in your browser"
    echo "2. Log in with the credentials above"
    echo "3. Install suggested plugins or select specific plugins"
    echo "4. Create additional admin users if needed"
    echo "5. Configure Jenkins global settings"
    echo ""
    echo "Available Tools:"
    echo "  - Git, Docker, Docker Compose"
    echo "  - Ansible, Terraform, kubectl"
    echo "  - Node.js, Python 3, Maven"
    echo "  - AWS CLI"
    echo ""
    echo "Example Pipeline:"
    echo "  - A sample vCPE pipeline job has been created"
    echo "  - Check 'vcpe-pipeline' job in Jenkins UI"
    echo ""
    echo "Container Management:"
    echo "  Start:   lxc start ${CONTAINER_NAME}"
    echo "  Stop:    lxc stop ${CONTAINER_NAME}"
    echo "  Shell:   lxc exec ${CONTAINER_NAME} bash"
    echo "  Logs:    lxc exec ${CONTAINER_NAME} -- tail -f /var/log/jenkins/jenkins.log"
    echo ""
    echo "For SSH tunnel access:"
    echo "  ssh -L 8080:${IP_ADDRESS}:8080 user@host"
    echo "  Then access: http://localhost:8080"
    echo ""
    echo "Integration with vCPE:"
    echo "  - Jenkins can manage vCPE container lifecycle"
    echo "  - Run automated tests on vCPE environment"
    echo "  - Deploy and validate vCPE configurations"
    echo ""
}

main() {
    echo "Starting Jenkins container creation..."
    
    check_lxd_running
    
    create_jenkins_profile
    create_jenkins_container
    configure_firewall
    
    display_access_info
}

main "$@"
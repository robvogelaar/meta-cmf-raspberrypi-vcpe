#!/bin/bash

# JIRA Base Container Creation Script
# Creates a base Ubuntu container with JIRA Server (free license)

set -e

source "$(dirname "$0")/gen-util.sh"

CONTAINER_NAME="jira-base"
IMAGE_ALIAS="ubuntu/22.04"
JIRA_VERSION="9.12.1"
JIRA_HOME="/var/atlassian/application-data/jira"
JIRA_INSTALL="/opt/atlassian/jira"

# Configuration
POSTGRES_DB="jiradb"
POSTGRES_USER="jirauser"
POSTGRES_PASS="jira@123456"

create_jira_base_container() {
    echo "Creating JIRA base container..."
    
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
    
    # Install required packages
    echo "Installing prerequisites..."
    lxc exec "${CONTAINER_NAME}" -- bash -c "DEBIAN_FRONTEND=noninteractive apt-get install -y \
        openjdk-11-jdk \
        postgresql \
        postgresql-contrib \
        wget \
        curl \
        unzip \
        fontconfig \
        ca-certificates \
        tzdata \
        supervisor"
    
    # Configure PostgreSQL
    echo "Configuring PostgreSQL..."
    lxc exec "${CONTAINER_NAME}" -- systemctl start postgresql
    lxc exec "${CONTAINER_NAME}" -- systemctl enable postgresql
    
    # Create JIRA database and user
    lxc exec "${CONTAINER_NAME}" -- sudo -u postgres psql -c "CREATE DATABASE ${POSTGRES_DB};"
    lxc exec "${CONTAINER_NAME}" -- sudo -u postgres psql -c "CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASS}';"
    lxc exec "${CONTAINER_NAME}" -- sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};"
    lxc exec "${CONTAINER_NAME}" -- sudo -u postgres psql -c "ALTER USER ${POSTGRES_USER} CREATEDB;"
    
    # Create JIRA user and directories
    echo "Creating JIRA user and directories..."
    lxc exec "${CONTAINER_NAME}" -- useradd --create-home --home-dir "${JIRA_HOME}" --shell /bin/bash jira
    lxc exec "${CONTAINER_NAME}" -- mkdir -p "${JIRA_INSTALL}"
    lxc exec "${CONTAINER_NAME}" -- mkdir -p "${JIRA_HOME}"
    
    # Download and install JIRA
    echo "Downloading JIRA ${JIRA_VERSION}..."
    lxc exec "${CONTAINER_NAME}" -- wget -O /tmp/jira.tar.gz \
        "https://product-downloads.atlassian.com/software/jira/downloads/atlassian-jira-software-${JIRA_VERSION}.tar.gz"
    
    echo "Installing JIRA..."
    lxc exec "${CONTAINER_NAME}" -- mkdir -p /opt/atlassian/jira
    lxc exec "${CONTAINER_NAME}" -- tar -xzf /tmp/jira.tar.gz -C "${JIRA_INSTALL}" --strip-components=1
    lxc exec "${CONTAINER_NAME}" -- rm /tmp/jira.tar.gz
    
    # Set ownership
    lxc exec "${CONTAINER_NAME}" -- chown -R jira:jira "${JIRA_INSTALL}"
    lxc exec "${CONTAINER_NAME}" -- chown -R jira:jira "${JIRA_HOME}"
    
    # Configure JIRA
    configure_jira
    
    # Create systemd service
    create_jira_service
    
    # Configure supervisor
    create_supervisor_config
    
    echo "JIRA base container created successfully"
}

configure_jira() {
    echo "Configuring JIRA..."
    
    # Set JIRA home directory
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee "${JIRA_INSTALL}/atlassian-jira/WEB-INF/classes/jira-application.properties"
jira.home=/var/atlassian/application-data/jira
EOF
    
    # Configure server.xml for proper connector
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee "${JIRA_INSTALL}/conf/server.xml"
<?xml version="1.0" encoding="utf-8"?>
<Server port="8005" shutdown="SHUTDOWN">
    <Listener className="org.apache.catalina.startup.VersionLoggerListener"/>
    <Listener className="org.apache.catalina.core.AprLifecycleListener" SSLEngine="on"/>
    <Listener className="org.apache.catalina.core.JreMemoryLeakPreventionListener"/>
    <Listener className="org.apache.catalina.mbeans.GlobalResourcesLifecycleListener"/>
    <Listener className="org.apache.catalina.core.ThreadLocalLeakPreventionListener"/>

    <Service name="Catalina">
        <Connector port="8080"
                   maxThreads="150"
                   minSpareThreads="25"
                   connectionTimeout="20000"
                   enableLookups="false"
                   maxHttpHeaderSize="8192"
                   protocol="HTTP/1.1"
                   useBodyEncodingForURI="true"
                   redirectPort="8443"
                   acceptCount="100"
                   disableUploadTimeout="true"
                   bindOnInit="false"/>

        <Engine name="Catalina" defaultHost="localhost">
            <Host name="localhost" appBase="webapps" unpackWARs="true" autoDeploy="true">
                <Context path="" docBase="${catalina.home}/atlassian-jira" reloadable="false" useHttpOnly="true">
                    <Resource name="UserTransaction" auth="Container" type="javax.transaction.UserTransaction"
                              factory="org.objectweb.jotm.UserTransactionFactory" jotm.timeout="60"/>
                    <Manager pathname=""/>
                    <JarScanner scanManifest="false"/>
                    <Valve className="org.apache.catalina.valves.StuckThreadDetectionValve" threshold="120"/>
                </Context>
            </Host>
        </Engine>
    </Service>
</Server>
EOF
    
    # Configure JVM options
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee "${JIRA_INSTALL}/bin/setenv.sh"
#!/bin/bash

# JVM options for JIRA
CATALINA_OPTS="-Xms1024m -Xmx2048m -Datlassian.plugins.enable.wait=300 ${CATALINA_OPTS}"
CATALINA_OPTS="-Djava.awt.headless=true ${CATALINA_OPTS}"
CATALINA_OPTS="-XX:+UseG1GC ${CATALINA_OPTS}"
CATALINA_OPTS="-XX:MaxGCPauseMillis=200 ${CATALINA_OPTS}"
CATALINA_OPTS="-XX:G1HeapRegionSize=16m ${CATALINA_OPTS}"
CATALINA_OPTS="-XX:G1NewSizePercent=23 ${CATALINA_OPTS}"
CATALINA_OPTS="-XX:G1MaxNewSizePercent=44 ${CATALINA_OPTS}"
CATALINA_OPTS="-XX:G1HeapWastePercent=3 ${CATALINA_OPTS}"
CATALINA_OPTS="-XX:G1MixedGCCountTarget=8 ${CATALINA_OPTS}"
CATALINA_OPTS="-XX:G1MixedGCLiveThresholdPercent=70 ${CATALINA_OPTS}"
CATALINA_OPTS="-XX:G1OldCSetRegionThresholdPercent=1 ${CATALINA_OPTS}"
CATALINA_OPTS="-XX:G1RSetUpdatingPauseTimePercent=5 ${CATALINA_OPTS}"
CATALINA_OPTS="-XX:G1ReservePercent=15 ${CATALINA_OPTS}"
CATALINA_OPTS="-XX:InitiatingHeapOccupancyPercent=40 ${CATALINA_OPTS}"
CATALINA_OPTS="-XX:+UseStringDeduplication ${CATALINA_OPTS}"

export CATALINA_OPTS
EOF
    
    lxc exec "${CONTAINER_NAME}" -- chmod +x "${JIRA_INSTALL}/bin/setenv.sh"
    lxc exec "${CONTAINER_NAME}" -- chown jira:jira "${JIRA_INSTALL}/bin/setenv.sh"
}

create_jira_service() {
    echo "Creating JIRA systemd service..."
    
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee /etc/systemd/system/jira.service
[Unit]
Description=Atlassian JIRA
After=network.target postgresql.service

[Service]
Type=forking
User=jira
Group=jira
Environment=JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ExecStart=/opt/atlassian/jira/bin/startup.sh
ExecStop=/opt/atlassian/jira/bin/shutdown.sh
ExecReload=/bin/kill -HUP $MAINPID
PIDFile=/opt/atlassian/jira/work/catalina.pid
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    lxc exec "${CONTAINER_NAME}" -- systemctl daemon-reload
    lxc exec "${CONTAINER_NAME}" -- systemctl enable jira
}

create_supervisor_config() {
    echo "Creating supervisor configuration..."
    
    cat << 'EOF' | lxc exec "${CONTAINER_NAME}" -- tee /etc/supervisor/conf.d/jira.conf
[program:jira]
command=/opt/atlassian/jira/bin/catalina.sh run
user=jira
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/jira.log
stderr_logfile=/var/log/supervisor/jira_error.log
environment=JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
EOF
    
    lxc exec "${CONTAINER_NAME}" -- systemctl enable supervisor
}

main() {
    echo "Starting JIRA base container creation..."
    
    check_lxd_running
    
    create_jira_base_container
    
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
    
    echo "JIRA base container setup complete!"
    echo "You can now create JIRA instances using jira.sh"
    echo ""
    echo "Database details:"
    echo "  Database: ${POSTGRES_DB}"
    echo "  Username: ${POSTGRES_USER}"
    echo "  Password: ${POSTGRES_PASS}"
    echo "  Host: localhost"
    echo "  Port: 5432"
}

main "$@"
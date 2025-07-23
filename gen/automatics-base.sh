#!/bin/bash

source gen-util.sh

container_name="automatics-base-container"
image_name="centos9"

########################################################################################
# Obtain the image if it does not exist

if ! lxc image list | grep -q $image_name; then
    echo "Obtaining image: centos/9-Stream"
    lxc image copy images:centos/9-Stream local: --alias $image_name
fi

########################################################################################
#
lxc delete ${container_name} -f 2>/dev/null

########################################################################################
#
lxc launch ${image_name} ${container_name}

########################################################################################
#
check_network automatics-base-container

###################################################################################################################################
# alias
lxc exec ${container_name} -- sh -c 'sed -i '\''#alias c=#d'\'' ~/.bashrc && echo '\''alias c="clear && printf \"\033[3J\033[0m\""'\'' >> ~/.bashrc'

###################################################################################################################################
# misc. packages
lxc exec ${container_name} -- dnf install -y tar ncurses dnf which procps-ng findutils git nmap-ncat strace lsof wget tcpdump
lxc exec ${container_name} -- dnf install -y epel-release
lxc exec ${container_name} -- dnf install -y tig

# git config
lxc exec ${container_name} -- git config --global user.name "user"
lxc exec ${container_name} -- git config --global user.email "user@automatics.com"

###################################################################################################################################
# java
lxc exec ${container_name} -- dnf install -y java-17-openjdk java-17-openjdk-devel

###################################################################################################################################
# maven
echo "Installing Apache Maven..."
lxc exec ${container_name} -- bash -c '
    # Try multiple Maven versions and mirrors
    MAVEN_URLS=(
        "https://dlcdn.apache.org/maven/maven-3/3.9.9/binaries/apache-maven-3.9.9-bin.tar.gz"
        "https://dlcdn.apache.org/maven/maven-3/3.9.8/binaries/apache-maven-3.9.8-bin.tar.gz"
        "https://archive.apache.org/dist/maven/maven-3/3.9.9/binaries/apache-maven-3.9.9-bin.tar.gz"
        "https://archive.apache.org/dist/maven/maven-3/3.9.8/binaries/apache-maven-3.9.8-bin.tar.gz"
        "https://downloads.apache.org/maven/maven-3/3.9.9/binaries/apache-maven-3.9.9-bin.tar.gz"
    )
    
    MAVEN_INSTALLED=false
    
    for url in "${MAVEN_URLS[@]}"; do
        echo "Trying to download Maven from: $url"
        filename=$(basename "$url")
        version=$(echo "$filename" | sed -n "s/apache-maven-\(.*\)-bin.tar.gz/\1/p")
        
        if wget -c "$url" -P /root --timeout=30 2>/dev/null; then
            echo "Successfully downloaded $filename"
            
            # Extract and install
            if tar xaf "/root/$filename" -C /opt 2>/dev/null; then
                echo "export PATH=\$PATH:/opt/apache-maven-$version/bin" > /etc/profile.d/maven.sh
                echo "export MAVEN_HOME=/opt/apache-maven-$version" >> /etc/profile.d/maven.sh
                chmod +x /etc/profile.d/maven.sh
                
                # Verify installation
                source /etc/profile.d/maven.sh
                if /opt/apache-maven-$version/bin/mvn --version >/dev/null 2>&1; then
                    echo "Maven $version installed successfully"
                    MAVEN_INSTALLED=true
                    break
                else
                    echo "Maven extraction succeeded but binary test failed"
                    rm -rf "/opt/apache-maven-$version"
                fi
            else
                echo "Failed to extract $filename"
            fi
            rm -f "/root/$filename"
        else
            echo "Failed to download from $url"
        fi
    done
    
    if [ "$MAVEN_INSTALLED" = false ]; then
        echo "ERROR: Failed to install Maven from any source"
        exit 1
    fi
'

###################################################################################################################################
# mariaDB
lxc exec ${container_name} -- dnf install -y mariadb-server mariadb
lxc exec ${container_name} -- systemctl start mariadb
lxc exec ${container_name} -- systemctl enable mariadb

###################################################################################################################################
# tomcat
lxc exec ${container_name} -- bash -c '
tomcat_version="9.0.102"
tomcat_filename="apache-tomcat-${tomcat_version}.tar.gz"
tomcat_url="https://archive.apache.org/dist/tomcat/tomcat-9/v${tomcat_version}/bin/${tomcat_filename}"
wget -c --inet4-only "$tomcat_url" -P /root
mkdir -p /opt/automatics/
tar -xf "/root/$tomcat_filename" -C /opt/automatics/
'

# Run tomcat as a systemd service

lxc exec ${container_name} -- bash -c 'cat <<EOF > /etc/systemd/system/tomcat.service
[Unit]
Description=Apache Tomcat 9
After=network.target

[Service]
Type=forking
User=root
ExecStart=/opt/automatics/apache-tomcat-9.0.102/bin/startup.sh
ExecStop=/opt/automatics/apache-tomcat-9.0.102/bin/shutdown.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

lxc exec ${container_name} -- systemctl daemon-reload
lxc exec ${container_name} -- systemctl enable tomcat
#### lxc exec ${container_name} -- systemctl start tomcat

###################################################################################################################################
# publish the image
lxc stop ${container_name}

lxc image delete automatics-base 2> /dev/null
lxc publish automatics-base-container --alias automatics-base
lxc delete automatics-base-container

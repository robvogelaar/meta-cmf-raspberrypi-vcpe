#!/bin/bash
# Script to run Tomcat and MySQL services for TDK

echo "Starting TDK services..."

# Start MySQL service
echo "Starting MySQL..."
service mysql start
sleep 5

# Verify MySQL is running
if ! pgrep -x "mysqld" > /dev/null; then
    echo "Failed to start MySQL"
    exit 1
fi
echo "MySQL started successfully"

# Start Tomcat service
echo "Starting Tomcat..."
/etc/init.d/tomcat7 start
sleep 10

# Verify Tomcat is running
if ! pgrep -f "tomcat" > /dev/null; then
    echo "Failed to start Tomcat"
    exit 1
fi
echo "Tomcat started successfully"

echo "TDK services are running"
echo "Access TDK Test Manager at: http://localhost:8080/rdk-test-tool"

# Keep the container running
tail -f /opt/apache-tomcat-7.0.96/logs/catalina.out
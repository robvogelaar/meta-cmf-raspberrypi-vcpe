#!/bin/bash

# LXD REST API Test Script with Project Support
# Tests LXD REST API access and lists containers across all projects

set -e

# Configuration
LXD_ENDPOINT="${1:-192.168.2.150:8443}"
CERT_DIR="$HOME/.config/lxc"

echo "====================================="
echo "LXD REST API Advanced Test"
echo "====================================="
echo "Target endpoint: ${LXD_ENDPOINT}"
echo

# Check certificates exist
if [[ ! -f "${CERT_DIR}/client.crt" ]] || [[ ! -f "${CERT_DIR}/client.key" ]]; then
    echo "❌ Client certificates not found!"
    echo "   Please run ./lxd-cert-setup.sh first"
    exit 1
fi

# Helper function for API calls
api_call() {
    local endpoint="$1"
    curl -s -k \
        --cert "${CERT_DIR}/client.crt" \
        --key "${CERT_DIR}/client.key" \
        "https://${LXD_ENDPOINT}${endpoint}" 2>/dev/null
}

# Test basic connectivity
echo "Testing API connectivity..."
RESPONSE=$(api_call "/1.0")
if echo "$RESPONSE" | grep -q '"type":"sync"'; then
    echo "✅ API connection successful"
else
    echo "❌ API connection failed"
    exit 1
fi

# Get server info with jq if available
if command -v jq >/dev/null 2>&1; then
    echo
    echo "Server Information:"
    echo "$RESPONSE" | jq -r '.metadata.environment | "  LXD Version: \(.server_version)
  Kernel: \(.kernel_version)
  Architecture: \(.kernel_architecture)
  Storage: \(.storage)"'
fi

# List all projects
echo
echo "====================================="
echo "Projects:"
echo "====================================="
PROJECTS_RESPONSE=$(api_call "/1.0/projects")

if command -v jq >/dev/null 2>&1; then
    PROJECTS=$(echo "$PROJECTS_RESPONSE" | jq -r '.metadata[]' | sed 's|/1.0/projects/||')

    for project in $PROJECTS; do
        echo
        echo "Project: $project"
        echo "-------------------"

        # Get containers in this project
        CONTAINERS_RESPONSE=$(api_call "/1.0/containers?project=$project")
        CONTAINER_COUNT=$(echo "$CONTAINERS_RESPONSE" | jq '.metadata | length')
        echo "  Containers: $CONTAINER_COUNT"

        if [[ $CONTAINER_COUNT -gt 0 ]]; then
            echo "$CONTAINERS_RESPONSE" | jq -r '.metadata[]' | sed 's|/1.0/containers/||' | while read container; do
                # Get container details
                CONTAINER_INFO=$(api_call "/1.0/containers/$container?project=$project")
                STATE=$(echo "$CONTAINER_INFO" | jq -r '.metadata.status')
                echo "    - $container (Status: $STATE)"

                # Get IP addresses
                if [[ "$STATE" == "Running" ]]; then
                    # Get state info for running containers
                    STATE_INFO=$(api_call "/1.0/containers/$container/state?project=$project")
                    echo "$STATE_INFO" | jq -r '.metadata.network | to_entries[] | select(.key != "lo") | "      \(.key): \(.value.addresses[] | select(.family == "inet") | .address)"' 2>/dev/null || true
                fi
            done
        fi

        # Get VMs in this project
        VMS_RESPONSE=$(api_call "/1.0/virtual-machines?project=$project" 2>/dev/null || echo '{"metadata":[]}')
        VM_COUNT=$(echo "$VMS_RESPONSE" | jq '.metadata | length' 2>/dev/null || echo 0)
        if [[ $VM_COUNT -gt 0 ]]; then
            echo "  Virtual Machines: $VM_COUNT"
            echo "$VMS_RESPONSE" | jq -r '.metadata[]' | sed 's|/1.0/virtual-machines/||' | while read vm; do
                echo "    - $vm"
            done
        fi
    done
else
    # Fallback without jq
    echo "Projects list (install jq for detailed view):"
    echo "$PROJECTS_RESPONSE" | grep -o '"/1.0/projects/[^"]*"' | sed 's/"//g' | sed 's|/1.0/projects/||'
fi

# Test operations
echo
echo "====================================="
echo "API Operations Test:"
echo "====================================="

# List available API extensions
echo
echo "API Extensions available:"
EXTENSIONS=$(api_call "/1.0" | grep -o '"api_extensions":\[[^]]*\]' | grep -o '"[^"]*"' | grep -v "api_extensions" | head -5)
echo "$EXTENSIONS" | sed 's/"//g' | sed 's/^/  - /'
echo "  ... and more"

# Test creating and deleting a test container (optional)
echo
read -p "Test container operations? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    TEST_NAME="api-test-$(date +%s)"
    echo "Creating test container: $TEST_NAME"

    # Create container
    CREATE_RESPONSE=$(curl -s -k \
        --cert "${CERT_DIR}/client.crt" \
        --key "${CERT_DIR}/client.key" \
        -X POST \
        -H "Content-Type: application/json" \
        -d '{
            "name": "'"$TEST_NAME"'",
            "source": {
                "type": "image",
                "protocol": "simplestreams",
                "server": "https://images.linuxcontainers.org",
                "alias": "alpine/3.18"
            }
        }' \
        "https://${LXD_ENDPOINT}/1.0/containers" 2>/dev/null)

    if echo "$CREATE_RESPONSE" | grep -q '"type":"async"'; then
        echo "✅ Container creation initiated"

        # Wait a bit and delete
        sleep 5

        echo "Deleting test container..."
        DELETE_RESPONSE=$(curl -s -k \
            --cert "${CERT_DIR}/client.crt" \
            --key "${CERT_DIR}/client.key" \
            -X DELETE \
            "https://${LXD_ENDPOINT}/1.0/containers/$TEST_NAME" 2>/dev/null)

        if echo "$DELETE_RESPONSE" | grep -q '"type"'; then
            echo "✅ Container deleted"
        fi
    else
        echo "❌ Container creation failed"
    fi
fi

echo
echo "====================================="
echo "Test Complete"
echo "====================================="

#!/bin/bash

# LXD Certificate Setup and REST API Test Script
# This script sets up certificates for LXD REST API access and performs a test

set -e

# Configuration
LXD_ENDPOINT="192.168.2.150:8443"
CERT_DIR="$HOME/.config/lxc"
CERT_VALIDITY_DAYS=3650  # 10 years

echo "====================================="
echo "LXD Certificate Setup Script"
echo "====================================="
echo "Target LXD endpoint: ${LXD_ENDPOINT}"
echo

# Create certificate directory
echo "Creating certificate directory..."
mkdir -p "${CERT_DIR}"

# Generate client certificate and key if they don't exist
if [[ ! -f "${CERT_DIR}/client.crt" ]] || [[ ! -f "${CERT_DIR}/client.key" ]]; then
    echo "Generating new client certificates..."
    openssl req -x509 -newkey rsa:4096 \
        -keyout "${CERT_DIR}/client.key" \
        -out "${CERT_DIR}/client.crt" \
        -days ${CERT_VALIDITY_DAYS} \
        -nodes \
        -subj "/CN=lxd-client/O=LXD/OU=REST-API"
    
    # Set appropriate permissions
    chmod 600 "${CERT_DIR}/client.key"
    chmod 644 "${CERT_DIR}/client.crt"
    
    echo "Client certificates generated successfully"
else
    echo "Client certificates already exist, skipping generation"
fi

# Display certificate information
echo
echo "Certificate information:"
openssl x509 -in "${CERT_DIR}/client.crt" -noout -subject -dates

# Add certificate to LXD trusted certificates
echo
echo "Adding certificate to LXD trusted certificates..."
if lxc config trust add "${CERT_DIR}/client.crt" 2>/dev/null; then
    echo "Certificate added to LXD trust store"
else
    echo "Certificate already trusted or error adding (may already exist)"
fi

# List current trusted certificates
echo
echo "Current trusted certificates:"
lxc config trust list

# Test REST API access
echo
echo "====================================="
echo "Testing LXD REST API Access"
echo "====================================="

# Test 1: Basic connectivity to /1.0
echo
echo "Test 1: Basic API connectivity..."
RESPONSE=$(curl -s -k \
    --cert "${CERT_DIR}/client.crt" \
    --key "${CERT_DIR}/client.key" \
    -w "\nHTTP_CODE:%{http_code}" \
    "https://${LXD_ENDPOINT}/1.0" 2>/dev/null || echo "CURL_FAILED")

if [[ "$RESPONSE" == "CURL_FAILED" ]]; then
    echo "❌ Failed to connect to LXD API at ${LXD_ENDPOINT}"
    echo "   Please check if LXD is running and accessible"
    exit 1
fi

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
API_RESPONSE=$(echo "$RESPONSE" | grep -v "HTTP_CODE:")

if [[ "$HTTP_CODE" == "200" ]]; then
    echo "✅ Successfully connected to LXD API"
    echo "   HTTP Status: $HTTP_CODE"
    
    # Pretty print API version info
    if command -v jq >/dev/null 2>&1; then
        echo "   API Version Info:"
        echo "$API_RESPONSE" | jq -r '.metadata.api_version // "Unknown"' | sed 's/^/   /'
    fi
else
    echo "❌ API connection failed"
    echo "   HTTP Status: $HTTP_CODE"
    echo "   Response: $API_RESPONSE"
fi

# Test 2: List instances (containers and VMs)
echo
echo "Test 2: Listing instances..."
# Try instances endpoint first (newer LXD versions)
INSTANCES_RESPONSE=$(curl -s -k \
    --cert "${CERT_DIR}/client.crt" \
    --key "${CERT_DIR}/client.key" \
    "https://${LXD_ENDPOINT}/1.0/instances" 2>/dev/null)

# Fallback to containers endpoint if instances fails
if ! echo "$INSTANCES_RESPONSE" | grep -q '"type":"sync"'; then
    INSTANCES_RESPONSE=$(curl -s -k \
        --cert "${CERT_DIR}/client.crt" \
        --key "${CERT_DIR}/client.key" \
        "https://${LXD_ENDPOINT}/1.0/containers" 2>/dev/null)
fi

if echo "$INSTANCES_RESPONSE" | grep -q '"type":"sync"'; then
    echo "✅ Successfully retrieved instance list"
    
    # Count and display instances
    if command -v jq >/dev/null 2>&1; then
        INSTANCE_COUNT=$(echo "$INSTANCES_RESPONSE" | jq '.metadata | length')
        echo "   Instance count: $INSTANCE_COUNT"
        
        if [[ $INSTANCE_COUNT -gt 0 ]]; then
            echo "   Instances:"
            echo "$INSTANCES_RESPONSE" | jq -r '.metadata[]' | sed 's/^/   - /' | sed 's|/1.0/instances/||' | sed 's|/1.0/containers/||'
        fi
    else
        # Fallback without jq
        INSTANCE_COUNT=$(echo "$INSTANCES_RESPONSE" | grep -o -E '/1.0/(instances|containers)/' | wc -l)
        echo "   Instance count: $INSTANCE_COUNT"
        
        if [[ $INSTANCE_COUNT -gt 0 ]]; then
            echo "   Instances:"
            echo "$INSTANCES_RESPONSE" | grep -o -E '"/1.0/(instances|containers)/[^"]*"' | sed 's/"//g' | sed 's|/1.0/instances/||' | sed 's|/1.0/containers/||' | sed 's/^/   - /'
        fi
    fi
else
    echo "❌ Failed to retrieve instance list"
fi

# Test 3: Get server info
echo
echo "Test 3: Getting server information..."
SERVER_RESPONSE=$(curl -s -k \
    --cert "${CERT_DIR}/client.crt" \
    --key "${CERT_DIR}/client.key" \
    "https://${LXD_ENDPOINT}/1.0" 2>/dev/null)

if echo "$SERVER_RESPONSE" | grep -q '"type":"sync"'; then
    echo "✅ Successfully retrieved server information"
    
    if command -v jq >/dev/null 2>&1; then
        echo "   Server details:"
        echo "$SERVER_RESPONSE" | jq -r '.metadata | "   - Environment: \(.environment.server_name // "Unknown")"'
        echo "$SERVER_RESPONSE" | jq -r '.metadata | "   - Version: \(.environment.server_version // "Unknown")"'
        echo "$SERVER_RESPONSE" | jq -r '.metadata | "   - Storage: \(.environment.storage // "Unknown")"'
    fi
else
    echo "❌ Failed to retrieve server information"
fi

# Test 4: Test certificate validity
echo
echo "Test 4: Testing with invalid certificate (should fail)..."
INVALID_RESPONSE=$(curl -s -k \
    --cert /dev/null \
    --key /dev/null \
    -w "\nHTTP_CODE:%{http_code}" \
    "https://${LXD_ENDPOINT}/1.0/containers" 2>/dev/null || echo "CURL_FAILED")

INVALID_HTTP_CODE=$(echo "$INVALID_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)

if [[ "$INVALID_HTTP_CODE" == "403" ]] || [[ "$INVALID_RESPONSE" == "CURL_FAILED" ]]; then
    echo "✅ Invalid certificate correctly rejected (HTTP $INVALID_HTTP_CODE)"
else
    echo "⚠️  Unexpected response with invalid certificate (HTTP $INVALID_HTTP_CODE)"
fi

# Summary
echo
echo "====================================="
echo "Certificate Setup Complete"
echo "====================================="
echo "Client certificate: ${CERT_DIR}/client.crt"
echo "Client key: ${CERT_DIR}/client.key"
echo
echo "To use these certificates with curl:"
echo "  curl -k --cert ${CERT_DIR}/client.crt --key ${CERT_DIR}/client.key https://${LXD_ENDPOINT}/1.0"
echo
echo "To use with Python requests:"
echo "  import requests"
echo "  cert = ('${CERT_DIR}/client.crt', '${CERT_DIR}/client.key')"
echo "  response = requests.get('https://${LXD_ENDPOINT}/1.0', cert=cert, verify=False)"
echo
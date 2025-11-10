#!/bin/bash

# do-forkstat.sh - Capture forkstat process tracing from vCPE containers
# Requires: https://github.com/robvogelaar/forkstat

wait() {
    local i=$1
    while [[ $i -ge 0 ]]; do
        printf "\r\033[Kwaiting ($1) $i"
        sleep 1
        ((i--))
    done
    printf "\n"
}

# Check if arguments were provided
if [ "$#" -lt 1 ]; then
    cat << EOF
Usage: $0 <container> [duration] [start-delay]

Capture forkstat process events from a vCPE container.

ARGUMENTS:
  container     Container name (e.g., vcpe, vcpe-001)
  duration      Time to run forkstat in seconds (default: 120)
  start-delay   Delay before starting forkstat in seconds (default: 0)

EXAMPLES:
  $0 vcpe                  # Capture for 120 seconds, start immediately
  $0 vcpe 300              # Capture for 300 seconds
  $0 vcpe 180 10           # Wait 10s, then capture for 180s

OUTPUT:
  forkstat-<container>.log - Process event log file

EOF
    exit 1
fi

CONTAINER=$1
DURATION=${2:-120}
START_DELAY=${3:-0}

# Check for running vcpe containers
running_containers=$(lxc list --format csv -c ns | grep -E "^vcpe" | grep RUNNING)
if [[ ! -z "$running_containers" ]]; then
    echo "Stopping all running vCPE containers..."
    lxc stop -f $(echo "$running_containers" | awk -F "," '{print $1}')
fi

# Determine forkstat flags based on duration
if [ "$DURATION" -le 600 ]; then
    FORKSTAT_FLAGS="-E"  # Short duration: all events
    echo "Using forkstat -E (all events)"
else
    FORKSTAT_FLAGS="-e exec"  # Long duration: exec only
    echo "Using forkstat -e exec (exec events only)"
fi

# Start forkstat
echo "Starting forkstat..."
sudo killall forkstat 2>/dev/null
sudo rm -rf /run/forkstat.log

sudo sh -c "forkstat $FORKSTAT_FLAGS | sudo tee /run/forkstat.log >/dev/null &"

# Optional: wait before starting container
if [ "$START_DELAY" -gt 0 ]; then
    echo "Waiting ${START_DELAY}s before starting container..."
    wait $START_DELAY
fi

# Start container
echo "Starting container ${CONTAINER}..."
lxc start $CONTAINER

# Run for specified duration
echo "Capturing for ${DURATION}s..."
wait $DURATION

# Stop forkstat and save log
echo "Obtaining forkstat log..."
sudo killall forkstat 2>/dev/null
cp /run/forkstat.log forkstat-${CONTAINER}.log
sudo rm -rf /run/forkstat.log

echo "Log saved to: forkstat-${CONTAINER}.log"
echo ""
echo "To process this log:"
echo "  ./forkstat.py forkstat-${CONTAINER}.log"
echo ""
echo "To generate HTML viewer:"
echo "  ./forkstat-catapult.py forkstat-${CONTAINER}.log | \\"
echo "    /path/to/catapult/tracing/bin/trace2html /dev/stdin \\"
echo "    --output forkstat-${CONTAINER}-viewer.html"

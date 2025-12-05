#!/bin/bash

# probes.sh - vCPE log collection and analysis tool

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UTIL_DIR="${SCRIPT_DIR}/util"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $*"
}

show_usage() {
    cat << EOF
Usage: $0 <container-name>

Collect, process, and parse logs from vCPE containers.

EXAMPLES:
    $0 vcpe                    # Collect all logs from 'vcpe' container

Available vCPE containers:
$(lxc list --format csv -c ns | grep -E '^vcpe' | sed 's/^/  - /')

EOF
}

create_next_dir() {
    local container="$1"

    # Create tmp directory if it doesn't exist
    mkdir -p ./tmp

    local base_dir="./tmp/logs-${container}"

    # If base directory doesn't exist, create logs-<container>.1
    if [ ! -d "${base_dir}.1" ]; then
        mkdir -p "${base_dir}.1"
        echo "${base_dir}.1"
        return 0
    fi

    # Find the next available index
    local counter=1
    while [ $counter -le 999 ]; do
        local new_dir="${base_dir}.${counter}"

        if [ ! -d "$new_dir" ]; then
            mkdir "$new_dir"
            echo "$new_dir"
            return 0
        fi

        counter=$((counter + 1))
    done

    log_error "Reached maximum directory number (999)"
    return 1
}

validate_container() {
    local container="$1"

    if ! lxc info "$container" >/dev/null 2>&1; then
        log_error "Container '$container' does not exist"
        return 1
    fi

    if [ "$(lxc list "$container" --format csv | cut -d',' -f2 | head -n1)" != "RUNNING" ]; then
        log_error "Container '$container' is not running"
        return 1
    fi

    return 0
}

collect_misc_logs() {
    local container="$1"
    local output_dir="$2"

    log_step "Collecting miscellaneous logs from $container..."

    # Create logs subdirectory
    mkdir -p "${output_dir}/misc"

    # Collect version info
    if lxc file pull "${container}/version.txt" "${output_dir}/version.txt" 2>/dev/null; then
        log_info "Collected version.txt"
    fi

    # Collect rssfree log
    if lxc file pull "${container}/home/root/rssfree.log" "${output_dir}/misc/rssfree-${container}.log" 2>/dev/null; then
        log_info "Collected rssfree.log"
    fi

    # Collect syscfg, sysevent, rbus logs from /tmp
    if lxc file pull "${container}/tmp/syscfg.log" "${output_dir}/misc/syscfg-${container}.log" 2>/dev/null; then
        log_info "Collected syscfg.log"
    fi

    if lxc file pull "${container}/tmp/sysevent.log" "${output_dir}/misc/sysevent-${container}.log" 2>/dev/null; then
        log_info "Collected sysevent.log"
    fi

    if lxc file pull "${container}/tmp/rtrouted_traffic_monitor" "${output_dir}/misc/rbus-${container}.log" 2>/dev/null; then
        log_info "Collected rbus.log"
    fi
}

collect_rdklogs() {
    local container="$1"
    local output_dir="$2"

    log_step "Collecting RDK logs from $container..."

    export NOW=$(date +%m%d-%H_%M_%S)

    # Create temporary directory in container and copy logs
    lxc exec "${container}" -- mkdir -p "/var/tmp/rdklogs-${NOW}/logs"
    lxc exec "${container}" -- sh -c "cp -a /rdklogs/logs/* /var/tmp/rdklogs-${NOW}/logs/" 2>/dev/null || log_warn "Could not copy /rdklogs/logs"

    # Create tarball in container
    lxc exec "${container}" -- busybox tar czf "/var/tmp/rdklogs-${NOW}.tgz" -C "/var/tmp/rdklogs-${NOW}/logs" .
    lxc exec "${container}" -- rm -rf "/var/tmp/rdklogs-${NOW}/logs"

    # Pull tarball and extract
    mkdir -p "${output_dir}/rdklogs"
    lxc file pull "${container}/var/tmp/rdklogs-${NOW}.tgz" "${output_dir}/rdklogs-${NOW}.tgz"
    lxc exec "${container}" -- rm -rf "/var/tmp/rdklogs-${NOW}.tgz"

    tar xaf "${output_dir}/rdklogs-${NOW}.tgz" -C "${output_dir}/rdklogs"
    rm -rf "${output_dir}/rdklogs-${NOW}.tgz"

    log_info "Collected RDK logs"
}

collect_console_log() {
    local container="$1"
    local output_dir="$2"

    log_step "Collecting console log from $container..."

    if lxc console "${container}" --show-log 2>/dev/null > "${output_dir}/Console.txt"; then
        log_info "Collected console log"
    else
        log_warn "Could not collect console log"
    fi
}

process_rdklogs() {
    local output_dir="$1"

    if [ ! -d "${output_dir}/rdklogs" ]; then
        log_warn "No RDK logs directory found, skipping processing"
        return
    fi

    log_step "Processing RDK logs..."

    # Combine logs
    if [ -x "${UTIL_DIR}/combine-logs.py" ]; then
        log_info "Combining RDK logs..."
        "${UTIL_DIR}/combine-logs.py" "${output_dir}/rdklogs"
    else
        log_warn "combine-logs.py not found or not executable"
    fi

    # Parse combined logs
    if [ -f "${output_dir}/rdklogs/combined_logs.txt.0" ] && [ -x "${UTIL_DIR}/parse-combined-logs.py" ]; then
        log_info "Parsing combined logs..."
        "${UTIL_DIR}/parse-combined-logs.py" "${output_dir}/rdklogs/combined_logs.txt.0"
    else
        log_warn "parse-combined-logs.py not found or combined logs not available"
    fi
}

process_misc_logs() {
    local output_dir="$1"
    local container="$2"

    if [ ! -d "${output_dir}/misc" ]; then
        log_warn "No misc logs directory found, skipping processing"
        return
    fi

    log_step "Processing miscellaneous logs..."

    cd "${output_dir}/misc" || return

    # Parse rssfree log
    if [ -f "rssfree-${container}.log" ] && [ -x "${UTIL_DIR}/parse-rssfree-log.py" ]; then
        log_info "Parsing rssfree log..."
        "${UTIL_DIR}/parse-rssfree-log.py" "rssfree-${container}.log"
    fi

    # Parse syscfg log
    if [ -f "syscfg-${container}.log" ] && [ -x "${UTIL_DIR}/parse-syscfg-log.py" ]; then
        log_info "Parsing syscfg log..."
        "${UTIL_DIR}/parse-syscfg-log.py" "syscfg-${container}.log"
    fi

    # Parse sysevent log
    if [ -f "sysevent-${container}.log" ] && [ -x "${UTIL_DIR}/parse-sysevent-log.py" ]; then
        log_info "Parsing sysevent log..."
        "${UTIL_DIR}/parse-sysevent-log.py" "sysevent-${container}.log"
    fi

    # Parse sysevent map
    if [ -f "sysevent-${container}.log" ] && [ -x "${UTIL_DIR}/parse-sysevent-map.py" ]; then
        log_info "Parsing sysevent map..."
        "${UTIL_DIR}/parse-sysevent-map.py" "sysevent-${container}.log" && rm -rf *.dot 2>/dev/null || rm -rf *.dot 2>/dev/null
    fi

    # Parse rbus log
    if [ -f "rbus-${container}.log" ] && [ -x "${UTIL_DIR}/parse-rbus-log.py" ]; then
        log_info "Parsing rbus log..."
        "${UTIL_DIR}/parse-rbus-log.py" "rbus-${container}.log"
    fi

    cd - > /dev/null
}

display_results() {
    local output_dir="$1"

    echo ""
    log_step "Collection Summary"
    echo "=================================================================================="
    echo "Output directory: ${output_dir}"
    echo ""
    echo "Collected and Processed Files:"
    echo "=================================================================================="

    # Find all files and display with sizes
    find "${output_dir}" -type f -exec sh -c 'echo "  {} ($(stat -c%s "{}" | numfmt --to=iec))"' \; | sort

    echo ""
    echo "=================================================================================="

    # Count files by type
    local total_files=$(find "${output_dir}" -type f | wc -l)
    local log_files=$(find "${output_dir}" -type f -name "*.log" | wc -l)
    local txt_files=$(find "${output_dir}" -type f -name "*.txt" | wc -l)
    local html_files=$(find "${output_dir}" -type f -name "*.html" | wc -l)

    echo "File Statistics:"
    echo "  Total files: ${total_files}"
    echo "  Log files:   ${log_files}"
    echo "  Text files:  ${txt_files}"
    echo "  HTML files:  ${html_files}"
    echo "=================================================================================="
}

main() {
    local container=""

    # Parse arguments
    if [ $# -eq 0 ]; then
        log_error "No container specified"
        echo ""
        show_usage
        exit 1
    fi

    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi

    container="$1"

    # Validate container exists and is running
    if ! validate_container "$container"; then
        exit 1
    fi

    # Create output directory
    output_dir=$(create_next_dir "$container")

    if [ -z "$output_dir" ]; then
        log_error "Failed to create output directory"
        exit 1
    fi

    log_info "Starting log collection for container: ${container}"
    log_info "Output directory: ${output_dir}"
    echo ""

    # Collect logs
    collect_misc_logs "$container" "$output_dir"
    collect_rdklogs "$container" "$output_dir"
    collect_console_log "$container" "$output_dir"

    # Process/parse logs
    echo ""
    process_rdklogs "$output_dir"
    process_misc_logs "$output_dir" "$container"

    # Display results
    echo ""
    display_results "$output_dir"

    log_info "Log collection complete!"
}

# Run main function
main "$@"

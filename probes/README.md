# vCPE Log Collection and Analysis

Collects logs from vCPE containers and generates interactive HTML viewers for analysis.

## Output

Interactive HTML generated for:
- Combined RDK logs
- Per-process memory usage (RSS)
- Syscfg database operations
- Sysevent bus messages
- Utopia service dependency map
- RBUS traffic
- Forkstat process viewer (see forkstat/)

These are created from log files collected from the vCPE container.

## Usage

```bash
./probes.sh vcpe
```

Output directories created under `./tmp` with sequential numbering:
- First run: `./tmp/logs-vcpe.1`
- Second run: `./tmp/logs-vcpe.2`
- Third run: `./tmp/logs-vcpe.3`

## Log File Generation

### syscfg / sysevent / rbus

These logs are **not enabled by default** in RDK-B images. Enable during build by applying patches from `patches/` directory:

```bash
# Patches available as a refeence:
# - 0001-syscfg-custom-logging.patch
# - 0001-sysevent-minimal-debug.patch
# - 0001-print-the-raw-bytes-to-the-traffic-log.patch

# Apply to appropriate recipes in your RDK-B build
```

Once enabled, logs are generated at:
- `/tmp/syscfg.log`
- `/tmp/sysevent.log`
- `/tmp/rtrouted_traffic_monitor`

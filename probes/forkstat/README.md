# forkstat Process Event Tracing

Captures process fork/exec/exit events from vCPE containers for performance analysis and troubleshooting.

## Requirements

Install forkstat from https://github.com/robvogelaar/forkstat

## Usage

### Capturing Events

```bash
./do-forkstat.sh <container> [duration] [start-delay]
```

**Parameters:**
- `container` - LXC container name (required)
- `duration` - Capture duration in seconds (default: 120)
- `start-delay` - Delay before starting capture (default: 0)

**Examples:**
```bash
./do-forkstat.sh vcpe              # Capture 120 seconds
./do-forkstat.sh vcpe 300          # Capture 5 minutes
./do-forkstat.sh vcpe 300 10       # Wait 10s, then capture 5 minutes
```

**Output:** `forkstat-<container>-<timestamp>.log`

### Processing Logs

**Standard HTML:**
```bash
../util/parse-forkstat-log.py forkstat-vcpe-example.log
```
Generates: `forkstat-vcpe-example.html`

**Catapult Trace Viewer:**
```bash
forkstat-catapult.py forkstat-vcpe-example.log | \
  /path/to/catapult/tracing/bin/trace2html /dev/stdin --output forks.html
```

## Google Catapult Setup

Catapult is Chromium's trace viewer for visualizing process events.

### Installation

```bash
git clone https://chromium.googlesource.com/catapult
cd catapult
git checkout 444aba89e1c30edf348c611a9df79e2376178ba8
git am ../meta-cmf-raspberrypi-vcpe/probes/forkstat/catapult/*.patch
```

### Reference

See https://chromium.googlesource.com/catapult/+/HEAD/README.md for Catapult documentation.

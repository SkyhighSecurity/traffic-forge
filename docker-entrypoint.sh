#!/bin/bash
set -e

# Skyhigh Traffic Forge Docker Entrypoint

CONFIG_DIR="${SKYHIGH_CONFIG_DIR:-/etc/skyhigh-traffic-forge}"
OUTPUT_DIR="${SKYHIGH_OUTPUT_DIR:-/var/log/skyhigh-traffic-forge}"

# Ensure output directory exists (for volume mounts)
mkdir -p "$OUTPUT_DIR"

# Get version from Python package
VERSION=$(skyhigh-traffic-forge --version 2>/dev/null | cut -d' ' -f2 || echo "unknown")

# Check if this is the first run (no config exists)
if [ ! -f "$CONFIG_DIR/enterprise.yaml" ]; then
    echo "=========================================="
    echo "Skyhigh Traffic Forge v${VERSION}"
    echo "First Run Setup"
    echo "=========================================="
    echo ""
    echo "No configuration found in $CONFIG_DIR"
    echo ""
    
    # If the first argument is "init", just run it
    if [ "$1" = "init" ]; then
        exec skyhigh-traffic-forge "$@"
    fi
    
    # Otherwise, show help
    echo "To initialize configuration, run:"
    echo "  docker run -v /path/to/config:$CONFIG_DIR skyhigh-traffic-forge init"
    echo ""
    echo "Or to use the default configuration:"
    echo "  docker run -v /path/to/config:$CONFIG_DIR skyhigh-traffic-forge init --force"
    echo ""
    echo "After initialization, edit $CONFIG_DIR/enterprise.yaml"
    echo "to match your organization's settings."
    echo ""
    echo "Then run the traffic generator:"
    echo "  docker run -v /path/to/config:$CONFIG_DIR \\"
    echo "    -v /path/to/logs:$OUTPUT_DIR \\"
    echo "    skyhigh-traffic-forge generate --mode realtime"
    echo ""
    exit 1
fi

# If config exists, run the command with proper directories
# Add output-dir if not already specified
if [[ ! " $@ " =~ " --output-dir " ]]; then
    exec skyhigh-traffic-forge "$@" --output-dir "$OUTPUT_DIR"
else
    exec skyhigh-traffic-forge "$@"
fi
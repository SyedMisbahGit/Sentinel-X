#!/bin/bash
# Shared Configuration & Utils

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

setup_dirs() {
    local TARGET=$1
    # Get the root Sentinel-X directory (one level up from modules/)
    BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    RDIR="$BASE_DIR/reports/$TARGET"
    mkdir -p "$RDIR/patterns"
    mkdir -p "$RDIR/secrets"
    mkdir -p "$RDIR/screenshots"
    LOG_FILE="$RDIR/mission_log.txt"
}

log() {
    echo -e "$1"
    # Strip color codes for log file
    echo -e "$1" | sed 's/\x1b\[[0-9;]*m//g' >> "$LOG_FILE"
}

start_flaresolverr() {
    if ! sudo docker ps | grep -q flaresolverr; then
        sudo docker run -d --name sentinel_flare -p 8191:8191 -e LOG_LEVEL=info flaresolverr/flaresolverr:latest > /dev/null 2>&1
        sleep 5
    fi
}

stop_flaresolverr() {
    sudo docker stop sentinel_flare > /dev/null 2>&1
    sudo docker rm sentinel_flare > /dev/null 2>&1
}

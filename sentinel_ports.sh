#!/bin/bash
TARGET=$1
source ./modules/utils.sh

if [[ -z "$TARGET" ]]; then echo "Usage: ./sentinel_ports.sh <domain>"; exit 1; fi
setup_dirs "$TARGET"

log "${YELLOW}${BOLD}[ PHASE 2.5 ] PORT SCANNING (TURBO)${NC}"

if [[ ! -s "$RDIR/subs_live.txt" ]]; then
    log "${RED}[!] No live subdomains found.${NC}"
    exit 1
fi

log "${GREEN}[+] Engine: Naabu (Top 1000 Ports)...${NC}"
# Optimization:
# -skip-host-discovery: We already know they are live from Phase 2
# -rate 1500: Faster packet rate (default is lower)
# -retries 1: Don't waste time on dropped packets
naabu -list "$RDIR/subs_live.txt" -top-ports 1000 -exclude-ports 80,443 \
      -skip-host-discovery -rate 1500 -retries 1 -silent -o "$RDIR/ports_raw.txt"

COUNT_PORTS=$(wc -l < "$RDIR/ports_raw.txt" 2>/dev/null || echo 0)
log "    -> Open Ports Found: $COUNT_PORTS"

if [[ "$COUNT_PORTS" -gt 0 ]]; then
    log "${GREEN}[+] Probing new ports...${NC}"
    # Optimization: Faster timeout for these specific ports
    httpx -l "$RDIR/ports_raw.txt" -silent -title -tech-detect -status-code \
          -timeout 3 -threads 100 -o "$RDIR/web_ports.txt"
    
    awk '{print $1}' "$RDIR/web_ports.txt" >> "$RDIR/urls_live.txt"
    sort -u "$RDIR/urls_live.txt" -o "$RDIR/urls_live.txt"
fi

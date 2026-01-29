#!/bin/bash
TARGET=$1
source ./modules/utils.sh

if [[ -z "$TARGET" ]]; then echo "Usage: ./sentinel_ports.sh <domain>"; exit 1; fi
setup_dirs "$TARGET"

log "${YELLOW}${BOLD}[ PHASE 2.5 ] PORT SCANNING (BACK DOORS)${NC}"

if [[ ! -s "$RDIR/subs_live.txt" ]]; then
    log "${RED}[!] No live subdomains found. Run Active Recon first.${NC}"
    exit 1
fi

log "${GREEN}[+] Tool: Naabu (Top 1000 Ports)...${NC}"
# -top-ports 1000: Fast scan of most common ports
# -exclude-ports 80,443: We already scanned web ports, looking for weird stuff
naabu -list "$RDIR/subs_live.txt" -top-ports 1000 -exclude-ports 80,443 -silent -o "$RDIR/ports_raw.txt"

COUNT_PORTS=$(wc -l < "$RDIR/ports_raw.txt")
log "    -> Open Ports Found: $COUNT_PORTS"

if [[ "$COUNT_PORTS" -gt 0 ]]; then
    log "${GREEN}[+] Checking for Web Services on new ports...${NC}"
    # If we found port 8080, we want to treat it like a website
    httpx -l "$RDIR/ports_raw.txt" -silent -title -tech-detect -status-code -o "$RDIR/web_ports.txt"
    
    # Merge these new targets into the main list for Phase 3 & 4
    awk '{print $1}' "$RDIR/web_ports.txt" >> "$RDIR/urls_live.txt"
    sort -u "$RDIR/urls_live.txt" -o "$RDIR/urls_live.txt"
    
    log "    -> ${BLUE}Added new web-facing ports to target list.${NC}"
fi

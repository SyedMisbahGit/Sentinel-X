#!/bin/bash
TARGET=$1
source ./modules/utils.sh

if [[ -z "$TARGET" ]]; then echo "Usage: ./sentinel_secrets.sh <domain>"; exit 1; fi
setup_dirs "$TARGET"

log "${YELLOW}${BOLD}[ PHASE 3 ] SECRET MINING${NC}"

if [[ ! -s "$RDIR/urls_live.txt" ]]; then
    log "${RED}[!] No live URLs found. Run Active Recon first.${NC}"
    exit 1
fi

log "${GREEN}[+] Tool: Katana (JS Spidering)...${NC}"
# FIX: Changed "-kf" to "-kf all" so it doesn't break the command
katana -list "$RDIR/urls_live.txt" -jc -kf all -d 3 -em js,json -silent -o "$RDIR/secrets/js_files.txt"

COUNT_JS=$(wc -l < "$RDIR/secrets/js_files.txt" 2>/dev/null || echo 0)
log "    -> Extracted JS Files: $COUNT_JS"

if [[ "$COUNT_JS" -gt 0 ]]; then
    log "${GREEN}[+] Tool: Nuclei (Token Scanning)...${NC}"
    nuclei -l "$RDIR/secrets/js_files.txt" -t http/exposures/ -t http/misconfiguration/ -id exposed-tokens,api-key,google-api-key,aws-access-key -silent -o "$RDIR/secrets/keys_found.txt"
    if [[ -s "$RDIR/secrets/keys_found.txt" ]]; then
        log "    -> ${RED}${BOLD}CRITICAL: SECRETS FOUND!${NC}"
        cat "$RDIR/secrets/keys_found.txt"
    fi
fi

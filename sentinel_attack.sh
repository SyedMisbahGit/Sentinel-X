#!/bin/bash
TARGET=$1
source ./modules/utils.sh

if [[ -z "$TARGET" ]]; then echo "Usage: ./sentinel_attack.sh <domain>"; exit 1; fi
setup_dirs "$TARGET"

log "${RED}${BOLD}[ PHASE 4 ] ACTIVE SCANNING${NC}"

grep -E "admin|api|dev|stage|login" "$RDIR/urls_live.txt" > "$RDIR/urls_attack.txt"
if [[ ! -s "$RDIR/urls_attack.txt" ]]; then head -n 100 "$RDIR/urls_live.txt" > "$RDIR/urls_attack.txt"; fi

log "${GREEN}[+] Tool: Nuclei...${NC}"
nuclei -l "$RDIR/urls_attack.txt" -s medium,high,critical -rl 150 -c 25 -silent -j -o "$RDIR/nuclei.json"

if [[ -s "$RDIR/patterns/xss.txt" ]]; then
    log "${GREEN}[+] Tool: Dalfox (XSS)...${NC}"
    head -n 20 "$RDIR/patterns/xss.txt" | dalfox pipe --silence --skip-mining-all --waf-evasion > "$RDIR/dalfox_verified.txt"
    if [[ -s "$RDIR/dalfox_verified.txt" ]]; then
        log "    -> ${RED}CRITICAL: Verified XSS Found!${NC}"
        cat "$RDIR/dalfox_verified.txt"
    fi
fi

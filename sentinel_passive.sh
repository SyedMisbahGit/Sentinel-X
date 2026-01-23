#!/bin/bash
TARGET=$1
source ./modules/utils.sh

if [[ -z "$TARGET" ]]; then echo "Usage: ./sentinel_passive.sh <domain>"; exit 1; fi
setup_dirs "$TARGET"

log "${YELLOW}${BOLD}[ PHASE 1 ] PASSIVE RECONNAISSANCE${NC}"
log "${GREEN}[+] Tool: Subfinder...${NC}"
subfinder -d "$TARGET" -silent -all > "$RDIR/subs_1.txt"

log "${GREEN}[+] Tool: Assetfinder...${NC}"
assetfinder --subs-only "$TARGET" > "$RDIR/subs_2.txt"

log "${GREEN}[+] Tool: Gau (Archives)...${NC}"
gau --subs "$TARGET" --threads 10 > "$RDIR/urls_history.txt"

cat "$RDIR"/subs_*.txt 2>/dev/null | sort -u > "$RDIR/subs_passive.txt"
log "    -> Unique Subdomains: $(wc -l < "$RDIR/subs_passive.txt")"

grep "=" "$RDIR/urls_history.txt" | gf xss > "$RDIR/patterns/xss.txt"

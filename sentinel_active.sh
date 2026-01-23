#!/bin/bash
TARGET=$1
source ./modules/utils.sh

if [[ -z "$TARGET" ]]; then echo "Usage: ./sentinel_active.sh <domain>"; exit 1; fi
setup_dirs "$TARGET"

log "${YELLOW}${BOLD}[ PHASE 2 ] ACTIVE RECONNAISSANCE${NC}"

# Mutation Logic
COUNT=$(wc -l < "$RDIR/subs_passive.txt")
if [[ "$COUNT" -gt 2000 ]]; then
    log "${YELLOW}[!] Massive Target. Filtering...${NC}"
    grep -E "dev|stage|test|admin|api|vpn|internal" "$RDIR/subs_passive.txt" | head -n 500 > "$RDIR/subs_priority.txt"
    INPUT_MUT="$RDIR/subs_priority.txt"
else
    INPUT_MUT="$RDIR/subs_passive.txt"
fi

log "${GREEN}[+] Tool: Mutation Engine...${NC}"
python3 modules/permutations.py "$INPUT_MUT" > "$RDIR/subs_perm.txt"
cat "$RDIR/subs_passive.txt" "$RDIR/subs_perm.txt" | sort -u > "$RDIR/subs_all.txt"

log "${GREEN}[+] Tool: DNSX...${NC}"
dnsx -l "$RDIR/subs_all.txt" -silent -wd "$TARGET" -o "$RDIR/subs_live.txt"

log "${GREEN}[+] Tool: HTTPX...${NC}"
httpx -l "$RDIR/subs_live.txt" -silent -title -tech-detect -status-code -follow-redirects -threads 100 -o "$RDIR/web_full.txt"
awk '{print $1}' "$RDIR/web_full.txt" > "$RDIR/urls_live.txt"

start_flaresolverr
log "${GREEN}[+] Tool: Favicon Hunter...${NC}"
python3 modules/favicon.py "$TARGET" "$RDIR/urls_live.txt"
stop_flaresolverr

log "${GREEN}[+] Tool: SSL Serial Hunter...${NC}"
python3 modules/ssl_hunt.py "$TARGET"

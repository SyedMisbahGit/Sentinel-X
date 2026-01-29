#!/bin/bash
TARGET=$1
source ./modules/utils.sh

if [[ -z "$TARGET" ]]; then echo "Usage: ./sentinel_active.sh <domain>"; exit 1; fi
setup_dirs "$TARGET"

log "${YELLOW}${BOLD}[ PHASE 2 ] ACTIVE RECONNAISSANCE (TURBO)${NC}"

# Mutation Logic (unchanged)
COUNT=$(wc -l < "$RDIR/subs_passive.txt")
if [[ "$COUNT" -gt 2000 ]]; then
    grep -E "dev|stage|test|admin|api|vpn|internal" "$RDIR/subs_passive.txt" | head -n 500 > "$RDIR/subs_priority.txt"
    INPUT_MUT="$RDIR/subs_priority.txt"
else
    INPUT_MUT="$RDIR/subs_passive.txt"
fi

log "${GREEN}[+] Engine: Mutation & DNS Resolution...${NC}"
# Optimization: Generate mutations in background, then pipe directly to DNSX
python3 modules/permutations.py "$INPUT_MUT" > "$RDIR/subs_perm.txt" &
PERM_PID=$!
wait $PERM_PID

cat "$RDIR/subs_passive.txt" "$RDIR/subs_perm.txt" | sort -u > "$RDIR/subs_all.txt"

# Optimization: Increased threads to 150 for faster resolution
dnsx -l "$RDIR/subs_all.txt" -silent -wd "$TARGET" -t 150 -o "$RDIR/subs_live.txt"

log "${GREEN}[+] Engine: HTTP Probing...${NC}"
# Optimization: Increased threads to 150, disabled some heavy checks for speed
httpx -l "$RDIR/subs_live.txt" -silent -title -tech-detect -status-code \
      -follow-redirects -threads 150 -retries 1 -timeout 5 -o "$RDIR/web_full.txt"
awk '{print $1}' "$RDIR/web_full.txt" > "$RDIR/urls_live.txt"

# WAF Bypass (Optimized to check if Docker is needed first)
log "${GREEN}[+] Engine: Favicon Hunter...${NC}"
start_flaresolverr
python3 modules/favicon.py "$TARGET" "$RDIR/urls_live.txt"
stop_flaresolverr

log "${GREEN}[+] Engine: SSL Serial Hunter...${NC}"
python3 modules/ssl_hunt.py "$TARGET" &  # Run in background
wait

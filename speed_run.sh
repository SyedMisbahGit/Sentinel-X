#!/bin/bash
TARGET=$1
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RDIR="$BASE_DIR/reports/$TARGET"

if [[ ! -d "$RDIR" ]]; then echo "No report found. Run discovery (sentinel_x.sh) first."; exit 1; fi

echo -e "\n\033[1;33m[ INITIATING HYPER-SPEED RUN: $TARGET ]\033[0m"

# 1. FAST NUCLEI (Critical CVEs + Panels Only)
echo -e "\n\033[1;32m[+] Checking for Critical CVEs & Panels...\033[0m"
nuclei -l "$RDIR/urls_live.txt" \
       -t http/cves/ -t http/exposed-panels/ \
       -timeout 3 -retries 0 -rl 300 -c 50 \
       -silent -o "$RDIR/nuclei_fast.txt" &
NUCLEI_PID=$!

# 2. INSTANT XSS (Reflection Check)
echo -e "\n\033[1;32m[+] Checking for Reflected Parameters...\033[0m"
if [[ -s "$RDIR/patterns/xss.txt" ]]; then
    grep "=" "$RDIR/patterns/xss.txt" | head -n 500 | qsreplace 'SENTINEL_XSS' > "$RDIR/xss_fuzz.txt"
    httpx -l "$RDIR/xss_fuzz.txt" -match-string "SENTINEL_XSS" -silent -o "$RDIR/xss_reflected.txt"
fi

wait $NUCLEI_PID

echo -e "\n\033[1;31m=== SPEED RUN RESULTS ===\033[0m"
if [[ -s "$RDIR/nuclei_fast.txt" ]]; then
    echo -e "\033[1;31m[ CRITICAL HITS ]\033[0m"
    cat "$RDIR/nuclei_fast.txt"
else
    echo "No Critical CVEs found."
fi

if [[ -s "$RDIR/xss_reflected.txt" ]]; then
    echo -e "\n\033[1;33m[ POTENTIAL XSS (Reflected) ]\033[0m"
    cat "$RDIR/xss_reflected.txt"
fi

#!/bin/bash
TARGET=$1
source ./modules/utils.sh

if [[ -z "$TARGET" ]]; then echo "Usage: ./sentinel_attack.sh <domain>"; exit 1; fi
setup_dirs "$TARGET"

log "${RED}${BOLD}[ PHASE 4 ] ACTIVE SCANNING (SMART QUEUE)${NC}"

# 1. Target Segmentation
log "${GREEN}[+] Segmenting Targets...${NC}"
grep -E "admin|api|dev|stage|login|dashboard|internal" "$RDIR/urls_live.txt" > "$RDIR/urls_high_value.txt"
grep -v -E "admin|api|dev|stage|login|dashboard|internal" "$RDIR/urls_live.txt" > "$RDIR/urls_low_value.txt"

HV_COUNT=$(wc -l < "$RDIR/urls_high_value.txt")
LV_COUNT=$(wc -l < "$RDIR/urls_low_value.txt")
log "    -> High Value Targets: $HV_COUNT"
log "    -> Low Value Targets:  $LV_COUNT"

# 2. High Value Scan (Deep)
if [[ "$HV_COUNT" -gt 0 ]]; then
    log "${GREEN}[+] Scanning High Value Targets (Deep Scan)...${NC}"
    nuclei -l "$RDIR/urls_high_value.txt" -s medium,high,critical \
           -rl 100 -c 25 -silent -j -o "$RDIR/nuclei_high.json" &
    NUC_PID=$!
fi

# 3. Low Value Scan (Fast/Light) - Run in parallel if possible, or wait
# Optimization: For low value, we only check for Criticals to save time
if [[ "$LV_COUNT" -gt 0 ]]; then
    wait $NUC_PID # Wait for high value to finish to avoid choking bandwidth
    log "${GREEN}[+] Scanning Low Value Targets (Fast Scan)...${NC}"
    nuclei -l "$RDIR/urls_low_value.txt" -s critical \
           -rl 150 -c 50 -silent -j -o "$RDIR/nuclei_low.json"
fi

# Merge Reports
cat "$RDIR"/nuclei_*.json 2>/dev/null > "$RDIR/nuclei.json"

# 4. XSS Verification (unchanged)
if [[ -s "$RDIR/patterns/xss.txt" ]]; then
    log "${GREEN}[+] Engine: Dalfox (XSS)...${NC}"
    head -n 20 "$RDIR/patterns/xss.txt" | dalfox pipe --silence --skip-mining-all --waf-evasion > "$RDIR/dalfox_verified.txt"
    if [[ -s "$RDIR/dalfox_verified.txt" ]]; then
        log "    -> ${RED}CRITICAL: Verified XSS Found!${NC}"
        cat "$RDIR/dalfox_verified.txt"
    fi
fi

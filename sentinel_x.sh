#!/usr/bin/env bash
# SENTINEL-X v20.0: GHOST HUNTER
# Focus: Origin Hiding & WAF Evasion
set -u

TARGET=${1:-}
if [[ -z "$TARGET" ]]; then echo "Usage: ./sentinel_x.sh <domain>"; exit 1; fi

# Setup Directories
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RDIR="$BASE_DIR/reports/$TARGET"
MOD_DIR="$BASE_DIR/modules"
mkdir -p "$RDIR/patterns"
LOG_FILE="$RDIR/mission_log.txt"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log() {
    echo -e "$1"
    echo -e "$1" | sed 's/\x1b\[[0-9;]*m//g' >> "$LOG_FILE"
}

log "${RED}${BOLD}=== SENTINEL-X v20.0: TARGET LOCK [ $TARGET ] ===${NC}"

# ======================================================
# PHASE 1: DISCOVERY (Triangulation)
# ======================================================
run_phase_1() {
    log "\n${YELLOW}${BOLD}[ PHASE 1 ] DISCOVERY${NC}"
    log "${GREEN}[+] Tool 1: Subfinder...${NC}"
    subfinder -d "$TARGET" -silent -all > "$RDIR/subs_1.txt"
    log "${GREEN}[+] Tool 2: Assetfinder...${NC}"
    assetfinder --subs-only "$TARGET" > "$RDIR/subs_2.txt"
    cat "$RDIR"/subs_*.txt | sort -u > "$RDIR/subs_raw.txt"
    log "    -> Total Unique Subdomains: $(wc -l < "$RDIR/subs_raw.txt")"
}

# ======================================================
# PHASE 2: MAPPING (Precision Mode)
# ======================================================
run_phase_2() {
    log "\n${YELLOW}${BOLD}[ PHASE 2 ] MAPPING${NC}"
    COUNT=$(wc -l < "$RDIR/subs_raw.txt")
    
    if [[ "$COUNT" -gt 2000 ]]; then
        log "${YELLOW}[!] Massive Target Detected. Engaging Smart Filter...${NC}"
        grep -E "dev|stage|test|admin|api|vpn" "$RDIR/subs_raw.txt" | head -n 500 > "$RDIR/subs_priority.txt"
        INPUT_FOR_MUTATION="$RDIR/subs_priority.txt"
    else
        INPUT_FOR_MUTATION="$RDIR/subs_raw.txt"
    fi
    
    log "${GREEN}[+] Tool 1: Mutation Engine...${NC}"
    if [[ -s "$INPUT_FOR_MUTATION" ]]; then
        python3 "$MOD_DIR/permutations.py" "$INPUT_FOR_MUTATION" > "$RDIR/subs_perm.txt"
    fi
    cat "$RDIR/subs_raw.txt" "$RDIR/subs_perm.txt" 2>/dev/null | sort -u > "$RDIR/subs_all.txt"
    
    log "${GREEN}[+] Tool 2: DNSX (Wildcard Filter)...${NC}"
    dnsx -l "$RDIR/subs_all.txt" -silent -wd "$TARGET" -o "$RDIR/subs_live.txt"
    
    log "${GREEN}[+] Tool 3: HTTPX (Web Surface)...${NC}"
    httpx -l "$RDIR/subs_live.txt" -silent -title -tech-detect -status-code \
          -follow-redirects -threads 100 -o "$RDIR/web_full.txt"
    awk '{print $1}' "$RDIR/web_full.txt" > "$RDIR/urls_live.txt"
}

# ======================================================
# PHASE 3: GHOST MINING (The Bypass Layer)
# ======================================================
run_phase_3() {
    log "\n${YELLOW}${BOLD}[ PHASE 3 ] GHOST MINING${NC}"
    
    # 1. Favicon Hunter
    log "${GREEN}[+] Tool 1: Favicon Hash Hunter...${NC}"
    if [[ $(wc -l < "$RDIR/urls_live.txt") -gt 1000 ]]; then
        head -n 200 "$RDIR/urls_live.txt" > "$RDIR/urls_sample.txt"
        python3 "$MOD_DIR/favicon.py" "$TARGET" "$RDIR/urls_sample.txt"
    else
        python3 "$MOD_DIR/favicon.py" "$TARGET" "$RDIR/urls_live.txt"
    fi

    # 2. SSL Ghost Hunter
    log "${GREEN}[+] Tool 2: SSL/TLS Serial Hunter...${NC}"
    python3 "$MOD_DIR/ssl_hunt.py" "$TARGET"
    
    # 3. Gau (History)
    log "${GREEN}[+] Tool 3: Gau (Archives)...${NC}"
    gau --subs "$TARGET" --threads 10 > "$RDIR/urls_history.txt"
    
    # 4. GF (Pattern Matcher)
    log "${GREEN}[+] Tool 4: GF (Filtering)...${NC}"
    grep "=" "$RDIR/urls_history.txt" | gf xss > "$RDIR/patterns/xss.txt"
    log "    -> Potential XSS: $(wc -l < "$RDIR/patterns/xss.txt")"
}

# ======================================================
# PHASE 4: WEAPONIZATION
# ======================================================
run_phase_4() {
    log "\n${RED}${BOLD}[ PHASE 4 ] WEAPONIZATION${NC}"
    
    log "${GREEN}[+] Tool 1: Nuclei...${NC}"
    grep -E "admin|api|dev|stage|login" "$RDIR/urls_live.txt" > "$RDIR/urls_attack.txt"
    if [[ ! -s "$RDIR/urls_attack.txt" ]]; then head -n 100 "$RDIR/urls_live.txt" > "$RDIR/urls_attack.txt"; fi
    
    nuclei -l "$RDIR/urls_attack.txt" -s medium,high,critical -rl 150 -c 25 -silent -j -o "$RDIR/nuclei.json"
    
    if [[ -s "$RDIR/patterns/xss.txt" ]]; then
        log "${GREEN}[+] Tool 2: Dalfox (XSS)...${NC}"
        head -n 10 "$RDIR/patterns/xss.txt" | dalfox pipe --silence --skip-mining-all --waf-evasion > "$RDIR/dalfox_verified.txt"
        if [[ -s "$RDIR/dalfox_verified.txt" ]]; then
            log "    -> ${RED}CRITICAL: Verified XSS Found!${NC}"
            cat "$RDIR/dalfox_verified.txt"
        fi
    fi
    
    log "\n${RED}${BOLD}✅ MISSION COMPLETE (v20.0).${NC}"
}

# EXECUTE
run_phase_1
run_phase_2
run_phase_3
run_phase_4

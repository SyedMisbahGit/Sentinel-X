#!/usr/bin/env bash
# ==============================================================================
# SENTINEL-X v20.0: GHOST HUNTER EDITION
# A modular reconnaissance framework for Red Teaming & Bug Bounty.
#
# Author: Syed Misbah Uddin
# Focus: WAF Evasion, Origin Hunting, Adaptive Scanning
# ==============================================================================
set -u

# --- CONFIGURATION ---
TARGET=${1:-}
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RDIR="$BASE_DIR/reports/$TARGET"
MOD_DIR="$BASE_DIR/modules"
LOG_FILE="$RDIR/mission_log.txt"

# --- VISUALS ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# --- VALIDATION ---
if [[ -z "$TARGET" ]]; then
    echo -e "${RED}Usage: ./sentinel_x.sh <domain>${NC}"
    exit 1
fi

if [[ ! -d "$MOD_DIR" ]]; then
    echo -e "${RED}[Error] Modules directory missing. Run install.sh first.${NC}"
    exit 1
fi

mkdir -p "$RDIR/patterns"

# --- LOGGING ---
log() {
    echo -e "$1"
    # Strip color codes for log file
    echo -e "$1" | sed 's/\x1b\[[0-9;]*m//g' >> "$LOG_FILE"
}

log "${BLUE}${BOLD}=== SENTINEL-X MISSION START: $TARGET ===${NC}"

# ======================================================
# PHASE 1: DISCOVERY (Triangulation)
# ======================================================
run_phase_1() {
    log "\n${YELLOW}${BOLD}[ PHASE 1 ] DISCOVERY${NC}"
    
    log "${GREEN}[+] Executing Subfinder (Passive)...${NC}"
    subfinder -d "$TARGET" -silent -all > "$RDIR/subs_1.txt"
    
    log "${GREEN}[+] Executing Assetfinder (Passive)...${NC}"
    assetfinder --subs-only "$TARGET" > "$RDIR/subs_2.txt"
    
    # Merge and Sort
    cat "$RDIR"/subs_*.txt 2>/dev/null | sort -u > "$RDIR/subs_raw.txt"
    COUNT=$(wc -l < "$RDIR/subs_raw.txt")
    log "    -> Total Unique Subdomains: ${BOLD}$COUNT${NC}"
}

# ======================================================
# PHASE 2: MAPPING (Adaptive Logic)
# ======================================================
run_phase_2() {
    log "\n${YELLOW}${BOLD}[ PHASE 2 ] MAPPING${NC}"
    COUNT=$(wc -l < "$RDIR/subs_raw.txt")
    
    # SMART FILTER: Prevents hanging on massive targets
    if [[ "$COUNT" -gt 2000 ]]; then
        log "${YELLOW}[!] Massive Target Detected ($COUNT). Engaging Precision Mode...${NC}"
        grep -E "dev|stage|test|admin|api|vpn|corp|internal" "$RDIR/subs_raw.txt" | head -n 500 > "$RDIR/subs_priority.txt"
        INPUT_FOR_MUTATION="$RDIR/subs_priority.txt"
    else
        INPUT_FOR_MUTATION="$RDIR/subs_raw.txt"
    fi
    
    log "${GREEN}[+] Mutation Engine (Python)...${NC}"
    if [[ -s "$INPUT_FOR_MUTATION" ]]; then
        python3 "$MOD_DIR/permutations.py" "$INPUT_FOR_MUTATION" > "$RDIR/subs_perm.txt"
    fi
    
    # Combine & Resolve
    cat "$RDIR/subs_raw.txt" "$RDIR/subs_perm.txt" 2>/dev/null | sort -u > "$RDIR/subs_all.txt"
    
    log "${GREEN}[+] DNSX (Wildcard Filtering)...${NC}"
    dnsx -l "$RDIR/subs_all.txt" -silent -wd "$TARGET" -o "$RDIR/subs_live.txt"
    
    log "${GREEN}[+] HTTPX (Web Surface Probing)...${NC}"
    httpx -l "$RDIR/subs_live.txt" -silent -title -tech-detect -status-code \
          -follow-redirects -threads 100 -o "$RDIR/web_full.txt"
    
    # Extract Clean URLs
    awk '{print $1}' "$RDIR/web_full.txt" > "$RDIR/urls_live.txt"
    log "    -> Attackable Web Targets: ${BOLD}$(wc -l < "$RDIR/urls_live.txt")${NC}"
}

# ======================================================
# PHASE 3: GHOST MINING (WAF Bypass)
# ======================================================
run_phase_3() {
    log "\n${YELLOW}${BOLD}[ PHASE 3 ] GHOST MINING${NC}"
    
    # 1. Favicon Hunter
    log "${GREEN}[+] Favicon Hash Hunter (WAF Bypass)...${NC}"
    # Sample if list is too large to prevent IP bans
    if [[ $(wc -l < "$RDIR/urls_live.txt") -gt 1000 ]]; then
        head -n 200 "$RDIR/urls_live.txt" > "$RDIR/urls_sample.txt"
        python3 "$MOD_DIR/favicon.py" "$TARGET" "$RDIR/urls_sample.txt"
    else
        python3 "$MOD_DIR/favicon.py" "$TARGET" "$RDIR/urls_live.txt"
    fi

    # 2. SSL Hunter
    log "${GREEN}[+] SSL Serial Hunter (Origin Detection)...${NC}"
    python3 "$MOD_DIR/ssl_hunt.py" "$TARGET"
    
    # 3. Archive Mining
    log "${GREEN}[+] Mining Historical URLs (Gau)...${NC}"
    gau --subs "$TARGET" --threads 10 > "$RDIR/urls_history.txt"
    
    # 4. Pattern Filtering
    log "${GREEN}[+] GF Pattern Matching...${NC}"
    grep "=" "$RDIR/urls_history.txt" | gf xss > "$RDIR/patterns/xss.txt"
    log "    -> Potential XSS Vectors: $(wc -l < "$RDIR/patterns/xss.txt")"
}

# ======================================================
# PHASE 4: WEAPONIZATION
# ======================================================
run_phase_4() {
    log "\n${RED}${BOLD}[ PHASE 4 ] WEAPONIZATION${NC}"
    
    log "${GREEN}[+] Nuclei Vulnerability Scan...${NC}"
    # Prioritize high-value targets for heavy scanning
    grep -E "admin|api|dev|stage|login" "$RDIR/urls_live.txt" > "$RDIR/urls_attack.txt"
    if [[ ! -s "$RDIR/urls_attack.txt" ]]; then 
        head -n 100 "$RDIR/urls_live.txt" > "$RDIR/urls_attack.txt"
    fi
    
    nuclei -l "$RDIR/urls_attack.txt" -s medium,high,critical -rl 150 -c 25 -silent -j -o "$RDIR/nuclei.json"
    
    if [[ -s "$RDIR/patterns/xss.txt" ]]; then
        log "${GREEN}[+] Dalfox XSS Verification...${NC}"
        head -n 15 "$RDIR/patterns/xss.txt" | dalfox pipe --silence --skip-mining-all --waf-evasion > "$RDIR/dalfox_verified.txt"
        
        if [[ -s "$RDIR/dalfox_verified.txt" ]]; then
            log "    -> ${RED}${BOLD}CRITICAL: Verified XSS Found!${NC}"
            cat "$RDIR/dalfox_verified.txt"
        fi
    fi
    
    log "\n${RED}${BOLD}✅ MISSION COMPLETE.${NC}"
}

# EXECUTE CHAIN
run_phase_1
run_phase_2
run_phase_3
run_phase_4

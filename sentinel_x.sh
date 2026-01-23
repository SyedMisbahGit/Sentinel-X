#!/bin/bash
# SENTINEL-X v23.0: MASTER CONTROLLER
# Orchestrates the full modular recon kill chain.

TARGET=$1
if [[ -z "$TARGET" ]]; then echo "Usage: ./sentinel_x.sh <domain>"; exit 1; fi

# Colors
BLUE='\033[1;34m'
GREEN='\033[1;32m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   SENTINEL-X v23.0: TOTAL RECON       ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}[*] TARGET LOCK: $TARGET${NC}"

# Execute Subsidiaries in Order
# 1. Passive OSINT
./sentinel_passive.sh "$TARGET"

# 2. Active Mapping & WAF Evasion
./sentinel_active.sh "$TARGET"

# 3. Secret Mining (JS Analysis)
./sentinel_secrets.sh "$TARGET"

# 4. Weaponization
./sentinel_attack.sh "$TARGET"

echo -e "\n${GREEN}[+] MISSION COMPLETE.${NC}"
echo -e "${GREEN}[+] Report saved to: reports/$TARGET${NC}"

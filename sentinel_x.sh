#!/bin/bash
# SENTINEL-X v24.0: MASTER CONTROLLER
# Orchestrates the full modular recon kill chain with Port Scanning.

TARGET=$1
if [[ -z "$TARGET" ]]; then echo "Usage: ./sentinel_x.sh <domain>"; exit 1; fi

# Colors
BLUE='\033[1;34m'
GREEN='\033[1;32m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   SENTINEL-X v24.0: HYDRA EDITION     ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}[*] TARGET LOCK: $TARGET${NC}"

# Execute Subsidiaries in Order
# 1. Passive OSINT
./sentinel_passive.sh "$TARGET"

# 2. Active Mapping & WAF Evasion
./sentinel_active.sh "$TARGET"

# 3. Port Scanning (New!)
./sentinel_ports.sh "$TARGET"

# 4. Secret Mining (JS Analysis)
./sentinel_secrets.sh "$TARGET"

# 5. Weaponization
./sentinel_attack.sh "$TARGET"

echo -e "\n${GREEN}[+] MISSION COMPLETE.${NC}"
echo -e "${GREEN}[+] Report saved to: reports/$TARGET${NC}"

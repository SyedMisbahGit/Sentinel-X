# Sentinel-X: Automated Reconnaissance Framework

Sentinel-X is a modular, high-speed reconnaissance and vulnerability scanning framework designed for Red Teaming and Bug Bounty hunting. It integrates industry-standard tools into a unified pipeline with smart filtering and WAF evasion capabilities.

## Architecture
- **Phase 1: Discovery** (Subfinder, Assetfinder)
- **Phase 2: Mapping** (DNSX, HTTPX, Smart Permutations)
- **Phase 3: Mining** (Favicon Hashing, SSL Serial Hunting, Archive Mining)
- **Phase 4: Weaponization** (Nuclei, Custom XSS Fuzzing)

## Features
- **WAF Bypass:** Rotates targets and uses Favicon/SSL matching to find Origin IPs.
- **Smart Filtering:** Automatically detects massive targets (>2k subdomains) and switches to "Precision Mode" to prevent hanging.
- **Hyper-Speed Mode:** Includes a `speed_run.sh` module for <2 minute triage.

## Installation
```bash
chmod +x install.sh
./install.sh

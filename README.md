# Sentinel-X: The Fortress Breaker (v22.0)

Sentinel-X is an advanced Red Team framework that includes **FlareSolverr integration** to bypass Cloudflare/WAFs during reconnaissance.

## 🚀 Key Features
- **WAF Bypass:** Automatically spins up a FlareSolverr Docker container to solve JS challenges when 403s are detected.
- **Ghost Hunting:** Uses Favicon Hashes and SSL Serials to find Origin IPs via Shodan.
- **Smart Logic:** Adapts to massive targets to prevent hanging.

## 📦 Setup
1. Ensure Docker is installed.
2. Run `./install.sh`.

## ⚔️ Usage
```bash
./sentinel_x.sh target.com


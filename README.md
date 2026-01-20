# Sentinel-X: Advanced Reconnaissance Framework

**Sentinel-X** is a modular, high-speed reconnaissance and vulnerability scanning framework designed for Red Teaming and Bug Bounty hunting. Unlike standard scanners, it features logic to bypass WAFs, detect origin servers, and handle massive targets without hanging.

## 🚀 Features

### 1. **Ghost Hunter Engine (WAF Bypass)**
   - **Favicon Hash Matching:** Bypasses Cloudflare/Akamai by hunting for the target's favicon hash on alternative IPs (via Shodan).
   - **SSL Serial Hunting:** Extracts the SSL certificate serial number to find "Origin Servers" hiding behind CDNs.
   - **Smart Rotation:** If the main domain blocks requests (403), the tool automatically rotates through live subdomains to find a weak entry point.

### 2. **Adaptive Logic**
   - **Anti-Wildcard:** Automatically detects massive wildcard domains (>2,000 subdomains).
   - **Precision Mode:** If a massive target is detected, it switches to "Smart Filtering," mutating only high-value keywords (`dev`, `api`, `admin`) to prevent scanning from taking days.

### 3. **Hyper-Speed Triage**
   - Includes a dedicated `speed_run.sh` module.
   - Skips deep verification and checks *only* for Critical CVEs and Reflected XSS in under 2 minutes.

---

## 📦 Installation

```bash
# 1. Clone the repository
git clone [https://github.com/SyedMisbahGit/Sentinel-X.git](https://github.com/SyedMisbahGit/Sentinel-X.git)
cd Sentinel-X

# 2. Install Dependencies (Go & Python tools)
chmod +x install.sh
./install.sh

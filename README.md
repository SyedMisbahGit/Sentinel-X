
# Sentinel-X v24.0: Hydra Edition


**Sentinel-X** is an advanced, modular Red Teaming framework. v24.0 introduces **Port Scanning** to identify non-standard entry points (databases, SSH, admin panels) alongside web vulnerabilities.


## 🚀 Key Capabilities


### 🛡️ **WAF & CDN Evasion**

- **FlareSolverr Integration:** Bypasses Cloudflare JS challenges.

- **Origin Hunting:** Finds backend IPs via Favicon/SSL hashing.


### 🚪 **Port Scanning (New)**

- **Naabu Integration:** Blazing fast scanning of top 1000 ports.

- **Service Discovery:** Automatically promotes web services on non-standard ports (e.g., 8080, 8443) to the attack queue.


### 🕵️ **Secret Mining**

- **JavaScript Analysis:** Spiders target JS files for hardcoded API keys using `Katana` and `Nuclei`.


## 📦 Installation


```bash

chmod +x install.sh

./install.sh


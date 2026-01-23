
# Sentinel-X v23.0: Modular Reconnaissance Framework


**Sentinel-X** is an advanced, modular Red Teaming framework designed for high-speed infrastructure mapping, WAF evasion, and secret mining. It breaks the kill chain into distinct, standalone phases that can be run individually or orchestrated together.




## 🚀 Key Capabilities


### 🛡️ **WAF & CDN Evasion**

- **FlareSolverr Integration:** Automatically spins up a Dockerized proxy to solve Cloudflare JavaScript challenges and CAPTCHAs.

- **Origin Hunting:** Uses Favicon Hashing and SSL Serial matching to uncover backend IP addresses hidden behind CDNs.


### 🕵️ **Secret Mining**

- **JavaScript Analysis:** Spiders the target using `Katana` to extract hidden `.js` files.

- **Key Extraction:** Scans extracted assets for hardcoded API keys (AWS, Google, Stripe, etc.) using `Nuclei`.


### ⚡ **Modular Architecture**

Run the full chain or specific phases:

- **`sentinel_passive.sh`**: Non-intrusive OSINT (Subfinder, Gau).

- **`sentinel_active.sh`**: WAF interaction, DNS resolution, and Port probing.

- **`sentinel_secrets.sh`**: JavaScript spidering and token hunting.

- **`sentinel_attack.sh`**: Active vulnerability scanning (Nuclei/Dalfox).


---


## 📦 Installation


```bash

# 1. Clone the repository

git clone [https://github.com/SyedMisbahGit/Sentinel-X.git](https://github.com/SyedMisbahGit/Sentinel-X.git)

cd Sentinel-X


# 2. Install Dependencies (Go, Python, Docker)

chmod +x install.sh

./install.sh


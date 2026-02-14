# MUFTI ⚖️
**The Supreme Security Auditor.**

MUFTI is a next-generation Red Teaming & Reconnaissance framework designed for **Audit, Verdict, and Seizure**. It automates the entire attack lifecycle from Subdomain Enumeration to Subdomain Takeover and Report Generation.

## ⚡ Features

* **Ghost Protocol:** Stealthy port scanning using `Naabu` (Hybrid Mode).
* **The Seizure:** Automated Subdomain Takeover detection via `Nuclei`.
* **Deep Cover:** JavaScript Endpoint Extraction & Secret Mining (`Cortex`).
* **Verdict Engine:** Issues a Security Grade (A-F) based on findings.
* **Shadow IT:** Subdomain Permutation Engine to find hidden dev/stage environments.
* **Chaos Module:** Content Discovery using `FFUF` with auto-calibration.
* **Email Forensics:** Detects Spoofing (DMARC/SPF) and insecure mail ports.

## 🚀 Installation

```bash
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/MUFTI.git](https://github.com/YOUR_USERNAME/MUFTI.git)
cd MUFTI

# Run Setup
chmod +x setup.sh
./setup.sh

# Activate Environment
source venv/bin/activate
⚔️ Usage

MUFTI operates in three modes: Stealth (Quiet), Standard (Balanced), and Loud (Aggressive).
Bash

# Basic Scan
python mufti.py scan tesla.com

# Full Audit (Standard Mode)
python mufti.py scan tesla.com --mode standard

# Resume a previous session
python mufti.py scan tesla.com --resume

📂 Output

MUFTI generates a Verdict Report in output/TARGET/verdict.html.
This report includes:

    Security Grade (A/B/C/F)

    Critical Vulnerabilities

    Hidden API Endpoints

    Email Spoofing Status

📜 Modules
Module	Function	Tools Used
Recon	Passive Subdomain Enumeration	Subfinder, Wayback
Permutations	DNS Mutation Analysis	Pure Python
Ports	Hybrid Port Scanning	Naabu
Probing	Live Host Detection & WAF Evasion	HTTPX
Takeover	Subdomain Seizure Check	Nuclei
Chaos	Content Discovery & Fuzzing	FFUF
Cortex	JS Secrets & Endpoint Mining	Regex
Email	SPF/DMARC/SMTP Analysis	Checkdmarc
⚠️ Disclaimer

This tool is for educational and authorized testing purposes only.

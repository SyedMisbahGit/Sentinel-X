#!/bin/bash

echo "[*] Setting up MUFTI Environment..."

# 1. Update System & Install External Tools
sudo apt update
sudo apt install -y python3-pip python3-venv chromium ffuf jq git

# 2. Install Go Tools (ProjectDiscovery)
echo "[*] Installing Go Tools..."
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install -v github.com/sensepost/gowitness@latest

# Add Go Binaries to Path (Temporary for this session, User should add to .bashrc)
export PATH=$PATH:$(go env GOPATH)/bin

# 3. Python Environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# 4. Install Python Libs
pip install --upgrade pip
pip install -r requirements.txt

# 5. Download Nuclei Templates
nuclei -update-templates

echo "[+] Setup Complete. Activate with: source venv/bin/activate"
echo "[+] Run MUFTI: python mufti.py --help"

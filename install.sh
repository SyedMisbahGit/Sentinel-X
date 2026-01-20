#!/bin/bash
echo -e "\033[1;33m[*] INITIALIZING SENTINEL-X SETUP...\033[0m"

# 1. Update System
sudo apt-get update
sudo apt-get install -y python3 python3-pip unzip jq curl git libpcap-dev

# 2. Install Go (if missing)
if ! command -v go &> /dev/null; then
    echo "[-] Go not found. Installing..."
    wget https://go.dev/dl/go1.21.6.linux-amd64.tar.gz
    sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.21.6.linux-amd64.tar.gz
    export PATH=$PATH:/usr/local/go/bin
fi

# 3. Install Offensive Go Tools
echo "[+] Installing Offensive Engines..."
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/tomnomnom/waybackurls@latest
go install -v github.com/lc/gau/v2/cmd/gau@latest
go install -v github.com/tomnomnom/gf@latest
go install -v github.com/tomnomnom/qsreplace@latest
go install -v github.com/hahwul/dalfox/v2@latest
go install -v github.com/ffuf/ffuf/v2@latest

# 4. Install Python Dependencies
echo "[+] Installing Python Libraries..."
pip3 install mmh3 requests beautifulsoup4 arjun --break-system-packages

# 5. Configure GF Patterns
echo "[+] Configuring GF Patterns..."
mkdir -p ~/.gf
git clone https://github.com/1ndianl33t/Gf-Patterns
mv Gf-Patterns/*.json ~/.gf/
rm -rf Gf-Patterns

# 6. Final Path Setup
echo 'export PATH=$PATH:~/go/bin:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc

echo -e "\033[1;32m[+] SETUP COMPLETE. READY TO HUNT.\033[0m"

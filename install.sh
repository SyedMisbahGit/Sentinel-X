#!/bin/bash
echo "[*] Installing Dependencies..."
sudo apt-get update && sudo apt-get install -y python3 python3-pip git curl
if ! command -v go &> /dev/null; then
    wget https://go.dev/dl/go1.21.6.linux-amd64.tar.gz
    sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.21.6.linux-amd64.tar.gz
    export PATH=$PATH:/usr/local/go/bin
fi
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/lc/gau/v2/cmd/gau@latest
go install -v github.com/tomnomnom/gf@latest
go install -v github.com/hahwul/dalfox/v2@latest
go install -v github.com/tomnomnom/qsreplace@latest
pip3 install mmh3 requests --break-system-packages
mkdir -p ~/.gf
git clone https://github.com/1ndianl33t/Gf-Patterns && mv Gf-Patterns/*.json ~/.gf/ && rm -rf Gf-Patterns
echo "[+] Done."

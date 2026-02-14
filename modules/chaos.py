import subprocess
import logging
import os
import json
from rich.console import Console

console = Console()
log = logging.getLogger("rich")

def run_chaos(session, config):
    """
    Phase 5: Chaos (Content Discovery).
    Uses FFUF to find hidden files.
    """
    console.print("[bold blue]━━ PHASE 5: CHAOS (CONTENT DISCOVERY) ━━[/bold blue]")

    if not session.live_hosts:
        log.warning("No live hosts to fuzz. Skipping.")
        return

    # Setup
    ffuf_path = "ffuf"
    wordlist = "data/wordlists/quickhits.txt"
    target_file = "data/temp_chaos_targets.txt"
    
    # Ensure wordlist exists
    if not os.path.exists(wordlist):
        log.warning("Quickhits wordlist missing. Creating default.")
        os.makedirs("data/wordlists", exist_ok=True)
        with open(wordlist, "w") as f:
            f.write(".env\n.git/HEAD\nwp-config.php\n.DS_Store\n")

    # Generate target list
    with open(target_file, "w") as f:
        for host in session.live_hosts:
            f.write(host['url'] + "/FUZZ\n")
            
    log.info(f"Fuzzing {len(session.live_hosts)} hosts...")

    # Configure FFUF
    cmd = [
        ffuf_path,
        "-w", f"{target_file}:URL",
        "-w", f"{wordlist}:PAYLOAD",
        "-u", "URLPAYLOAD",
        "-mc", "200,301,302,403",
        "-fc", "404",
        "-ac", # Auto-calibrate
        "-s",  # Silent
        "-json"
    ]
    
    # Rate Limiting
    if session.mode == "stealth":
        cmd.extend(["-rate", "5"])
    else:
        cmd.extend(["-rate", "50"])

    try:
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        findings = 0
        for line in process.stdout.splitlines():
            try:
                data = json.loads(line)
                url = data.get("url", "")
                status = data.get("status", 0)
                
                # Filter boring redirects
                if status == 301 and data.get("length") == 0: continue

                color = "green"
                if "env" in url or "git" in url:
                    color = "red"
                    session.vulnerabilities.append({
                        "name": "Hidden File Exposed",
                        "severity": "HIGH",
                        "url": url,
                        "info": f"Status: {status}"
                    })
                
                console.print(f"[{color}]  + Found: {url} (Status: {status})[/{color}]")
                findings += 1
            except: pass
                
        log.info(f"Chaos Module Complete. Found {findings} hidden items.")

    except subprocess.TimeoutExpired:
        log.warning("FFUF timed out.")
    except Exception as e:
        log.error(f"FFUF failed: {e}")
    
    if os.path.exists(target_file): os.remove(target_file)

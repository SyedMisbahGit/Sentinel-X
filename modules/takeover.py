import subprocess
import logging
import os
import json
from rich.console import Console

console = Console()
log = logging.getLogger("rich")

def run_takeover(session, config):
    """
    Phase 1.9: The Seizure (Subdomain Takeover).
    Checks for dangling CNAME records allowing asset seizure.
    """
    console.print("[bold blue]━━ PHASE 1.9: THE SEIZURE (TAKEOVER CHECK) ━━[/bold blue]")

    if not session.live_hosts:
        log.warning("No targets to check for takeover.")
        return

    # 1. Prepare Targets
    target_file = "data/temp_takeover_targets.txt"
    nuclei_path = config['tools']['nuclei']['path']
    
    with open(target_file, "w") as f:
        for host in session.live_hosts:
            f.write(host['url'] + "\n")

    log.info(f"Checking {len(session.live_hosts)} assets for dangling pointers...")

    # 2. Run Nuclei (Takeover Templates Only)
    # This is fast and extremely robust.
    cmd = [
        nuclei_path,
        "-l", target_file,
        "-t", "takeovers", # Only run takeover templates
        "-silent",
        "-json",
        "-retries", "2"
    ]

    try:
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        takeovers = []
        for line in process.stdout.splitlines():
            try:
                data = json.loads(line)
                name = data.get("info", {}).get("name", "Unknown Takeover")
                host = data.get("host", "")
                
                console.print(f"[bold red]>>> CONFIRMED TAKEOVER: {host} ({name})[/bold red]")
                
                takeovers.append({"host": host, "type": name})
                
                # Add to vulnerabilities
                session.vulnerabilities.append({
                    "name": f"Subdomain Takeover ({name})",
                    "severity": "CRITICAL",
                    "url": host,
                    "info": "Dangling CNAME record detected. Asset can be seized."
                })
            except: pass
            
        if takeovers:
            log.info(f"SEIZURE SUCCESSFUL. {len(takeovers)} assets are vulnerable.")
        else:
            log.info("No dangling assets found.")

    except Exception as e:
        log.error(f"Takeover check failed: {e}")
        
    if os.path.exists(target_file): os.remove(target_file)

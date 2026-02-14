import subprocess
import logging
import os
from rich.console import Console

console = Console()
log = logging.getLogger("rich")

def run_ports(session, config):
    """
    Phase 1.5: Port Scanning (Hybrid: Passive + Active).
    """
    console.print("[bold blue]━━ PHASE 1.5: PORT SCANNING ━━[/bold blue]")
    
    naabu_path = config['tools']['naabu']['path']
    port_mode = config['modes'].get(session.mode, {}).get('ports', 'top-100')
    
    # Define Port Strategy
    port_args = []
    if port_mode == "top-100":
        port_args = ["-top-ports", "100"]
    elif port_mode == "top-1000":
        port_args = ["-top-ports", "1000"]
    elif port_mode == "full":
        port_args = ["-p", "-"] 
    else:
        port_args = ["-top-ports", "100"]

    if not session.subdomains:
        log.warning("No subdomains to scan.")
        return

    # Create input file
    input_file = "data/temp_subs_ports.txt"
    os.makedirs("data", exist_ok=True)
    with open(input_file, "w") as f:
        f.write("\n".join(session.subdomains))

    log.info(f"Scanning ports on {len(session.subdomains)} hosts...")

    # OPTIMIZED COMMAND
    cmd = [
        naabu_path,
        "-list", input_file,
        "-silent",
        "-passive",       # <--- CRITICAL: Uses InternetDB/Shodan (Instant)
        "-exclude-cdn",   # <--- CRITICAL: Skips Cloudflare/Akamai IPs (Fast)
    ] + port_args

    # Optimized Rates
    if session.mode == "stealth":
        cmd.extend(["-rate", "300"]) # Bumped from 100 to 300
    elif session.mode == "loud":
        cmd.extend(["-rate", "2000"])
    else:
        cmd.extend(["-rate", "1000"])

    try:
        # 5 Minute Timeout for Port Scan to prevent "Forever" hangs
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        found_targets = process.stdout.splitlines()
        
        # Deduplicate
        unique_targets = list(set(session.subdomains + found_targets))
        
        # Calculate new finds
        new_finds = len(unique_targets) - len(session.subdomains)
        session.subdomains = unique_targets
        
        log.info(f"Port Scan Complete. Found {new_finds} new port mappings.")
        log.info(f"Total Targets for Probing: {len(session.subdomains)}")
        
    except subprocess.TimeoutExpired:
        log.warning("Port scan timed out (Limit: 10m). Proceeding with what we found...")
    except Exception as e:
        log.error(f"Naabu failed: {e}")
        
    if os.path.exists(input_file):
        os.remove(input_file)

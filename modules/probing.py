import subprocess
import json
import logging
import time
import random
import os
from rich.console import Console

console = Console()
log = logging.getLogger("rich")

def run_probing(session, config):
    """
    Phase 2: Active Probing with Smart Global Rate Limiting.
    """
    console.print("[bold blue]━━ PHASE 2: ACTIVE PROBING ━━[/bold blue]")

    if not session.subdomains:
        log.warning("No targets to probe. Skipping.")
        return

    # 1. WAF / Rate Limit Check
    is_blocked = check_waf_block(session.subdomains, config)
    
    extra_flags = []
    if is_blocked:
        log.warning("[red]⚠️  WAF/Rate-Limit Detected! Switching to SAFE MODE.[/red]")
        log.info("Reducing threads and adding delays...")
        # Add httpx flags for slowness
        extra_flags = ["-threads", "2", "-rate-limit", "2"]
        time.sleep(10) # Initial cool-off
    else:
        # Standard optimization
        if session.mode == "stealth":
            extra_flags = ["-threads", "5"]
        elif session.mode == "loud":
            extra_flags = ["-threads", "100"]

    # 2. Main Execution
    httpx_path = config['tools']['httpx']['path']
    input_file = "data/temp_probing.txt"
    os.makedirs("data", exist_ok=True)
    
    # Deduplicate before writing
    unique_targets = list(set(session.subdomains))
    with open(input_file, "w") as f:
        f.write("\n".join(unique_targets))
    
    cmd = [
        httpx_path, 
        "-l", input_file,
        "-silent", "-tech-detect", "-status-code", 
        "-title", "-ip", "-json", "-follow-redirects",
        "-retries", "2",
        "-timeout", "10"
    ] + extra_flags
    
    # Robustness: Random User Agent
    cmd.extend(["-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"])

    log.info(f"Probing {len(unique_targets)} targets...")

    try:
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        live_hosts = []
        for line in process.stdout.splitlines():
            try:
                data = json.loads(line)
                url = data.get("url")
                status = data.get("status_code")
                
                # False Positive Reduction:
                # Filter out 404s and 5xx errors from "Live Hosts" list 
                # We only want actionable targets (200, 301, 302, 401, 403)
                if status in [404, 500, 502, 503]:
                    continue
                
                # Filter Rate Limits
                if status == 429:
                    continue

                host_entry = {
                    "url": url,
                    "ip": data.get("host"),
                    "title": data.get("title"),
                    "status": status,
                    "tech": data.get("tech", [])
                }
                live_hosts.append(host_entry)
            except json.JSONDecodeError:
                continue
        
        session.live_hosts = live_hosts
        log.info(f"Active Live Hosts: {len(live_hosts)}")
        
        if os.path.exists(input_file):
            os.remove(input_file)

    except Exception as e:
        log.error(f"Probing failed: {e}")

def check_waf_block(targets, config):
    """
    Probes 5 random targets to detect WAF/Rate Limiting.
    """
    if not targets: return False
    
    sample = random.sample(targets, min(5, len(targets)))
    httpx_path = config['tools']['httpx']['path']
    
    cmd = [httpx_path, "-silent", "-status-code", "-timeout", "5"]
    try:
        process = subprocess.run(
            cmd, input="\n".join(sample), text=True, capture_output=True
        )
        # Check for 429 or 403 on all requests (Sign of IP ban)
        if "429" in process.stdout:
            return True
        # If we get 403s on ALL requests, it might be a WAF block
        if process.stdout.count("403") == len(sample):
            return True
    except:
        pass
    return False

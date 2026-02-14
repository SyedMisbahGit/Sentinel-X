import subprocess
import requests
import logging
from rich.console import Console

console = Console()
log = logging.getLogger("rich")

def run_recon(session, config):
    """
    Orchestrates the Reconnaissance Phase.
    1. Subfinder (Binary)
    2. Wayback Machine (Native Python)
    """
    console.print("[bold blue]━━ PHASE 1: PASSIVE RECON ━━[/bold blue]")

    # 1. Subfinder Execution
    log.info("Running Subfinder...")
    subs = run_subfinder(session.domain, config)
    
    # 2. Wayback Execution
    log.info("Mining Wayback Machine...")
    wayback_subs = run_wayback(session.domain)

    # 3. deduplicate and Save
    all_subs = list(set(subs + wayback_subs))
    session.subdomains = all_subs
    log.info(f"Total Unique Subdomains Found: {len(session.subdomains)}")

def run_subfinder(domain, config):
    """Runs Subfinder binary and returns a list of subdomains."""
    subfinder_path = config['tools']['subfinder']['path']
    cmd = [
        subfinder_path,
        "-d", domain,
        "-silent",
        "-all"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        subs = result.stdout.splitlines()
        log.info(f"Subfinder found {len(subs)} subdomains")
        return subs
    except FileNotFoundError:
        log.error("Subfinder binary not found! Check config/settings.yaml")
        return []
    except subprocess.CalledProcessError as e:
        log.error(f"Subfinder failed: {e}")
        return []

def run_wayback(domain):
    """
    Native Python implementation of 'gau' for subdomains.
    Queries web.archive.org CDX API.
    """
    url = f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&fl=original&collapse=urlkey"
    
    try:
        # standard timeout 15s
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            # data[0] is header, skip it. data[x][0] is the url.
            urls = [row[0] for row in data[1:]]
            
            # Extract subdomains from URLs
            found_subs = set()
            for u in urls:
                # Basic parsing to extract subdomain
                parts = u.split('/')
                if len(parts) >= 3:
                    host = parts[2]
                    # Remove port if exists
                    host = host.split(':')[0]
                    if host.endswith(domain):
                        found_subs.add(host)
            
            log.info(f"Wayback Machine found {len(found_subs)} subdomains")
            return list(found_subs)
            
    except Exception as e:
        log.warning(f"Wayback Machine failed: {e}")
    
    return []

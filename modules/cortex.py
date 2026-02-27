import re
import math
import requests
import logging
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()
log = logging.getLogger("rich")

PATTERNS = {
    "google_api": r"AIza[0-9A-Za-z-_]{35}",
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "stripe_key": r"sk_live_[0-9a-zA-Z]{24}",
    "slack_token": r"xox[baprs]-([0-9a-zA-Z]{10,48})"
}

ENDPOINT_REGEX = r"(?<=[\"'])(?:/|https?://)[a-zA-Z0-9_./?=&-]+(?=[\"'])"

def shannon_entropy(data):
    """Calculates the cryptographic randomness of a string."""
    if not data: return 0
    entropy = 0
    for x in set(data):
        p_x = float(data.count(x)) / len(data)
        entropy += - p_x * math.log(p_x, 2)
    return entropy

def run_cortex(session, config):
    console.print("[bold blue]━━ PHASE 3: CORTEX (NEURAL JS EXTRACTION) ━━[/bold blue]")
    
    if not session.live_hosts:
        log.warning("No live hosts. Skipping Cortex.")
        return

    js_targets = []
    for host in session.live_hosts[:10]: # Limit to top 10 to save memory
        url = host.get('url', '')
        if url.endswith(".js"): js_targets.append(url)
        else:
            js_targets.append(f"{url}/main.js")
            js_targets.append(f"{url}/app.js")

    js_targets = list(set(js_targets))
    log.info(f"Mining {len(js_targets)} JS bundles with Active Validation...")
    
    found_endpoints = set()

    if js_targets:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(scan_js, url, session) for url in js_targets]
            for f in futures:
                result = f.result()
                if result: found_endpoints.update(result)

    session.endpoints = list(found_endpoints)
    if found_endpoints:
        log.info(f"Extracted and Validated {len(found_endpoints)} active endpoints.")

def scan_js(url, session):
    valid_endpoints = set()
    try:
        r = requests.get(url, timeout=5, verify=False)
        if r.status_code != 200: return set()
        content = r.text
        
        # A. Secret Mining with Entropy Filtering
        for name, pattern in PATTERNS.items():
            matches = re.findall(pattern, content)
            for match in set(matches):
                entropy = shannon_entropy(match)
                if entropy > 3.5: # Threshold for randomness
                    console.print(f"[bold red]>>> CRITICAL: HIGH-ENTROPY {name.upper()} LEAKED: {match}[/bold red]")
                    session.vulnerabilities.append({
                        "name": f"Exposed Credentials ({name})",
                        "severity": "CRITICAL",
                        "url": url,
                        "info": f"Valid cryptographic entropy detected ({entropy:.2f}). Key: {match}"
                    })

        # B. Endpoint Extraction & Active Validation
        base_url = "/".join(url.split("/")[:3]) # Extract scheme://domain
        matches = re.findall(ENDPOINT_REGEX, content)
        
        for m in set(matches):
            if any(x in m for x in ["api", "v1", "admin", "user", "config"]):
                target_url = urljoin(base_url, m)
                try:
                    # The Active Probe: Verify if the hidden route actually responds
                    probe = requests.get(target_url, timeout=3, verify=False)
                    if probe.status_code in [200, 401, 403]: # Exists (even if forbidden)
                        valid_endpoints.add(target_url)
                except: pass
                
    except Exception: pass
    return valid_endpoints

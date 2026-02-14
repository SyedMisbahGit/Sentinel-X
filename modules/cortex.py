import re
import requests
import logging
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console

console = Console()
log = logging.getLogger("rich")

# REGEX FOR SECRETS
PATTERNS = {
    "google_api": r"AIza[0-9A-Za-z-_]{35}",
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "stripe_key": r"sk_live_[0-9a-zA-Z]{24}",
    "slack_token": r"xox[baprs]-([0-9a-zA-Z]{10,48})"
}

# REGEX FOR ENDPOINTS (LinkFinder-lite)
# Captures relative paths starting with / or http/https
ENDPOINT_REGEX = r"(?<=[\"'])(?:/|https?://)[a-zA-Z0-9_./?=&-]+(?=[\"'])"

def run_cortex(session, config):
    """
    Phase 3: Logic, Secret Mining & Endpoint Extraction.
    """
    console.print("[bold blue]━━ PHASE 3: CORTEX (JS & LOGIC) ━━[/bold blue]")
    
    # 1. Technology Sorting
    technologies = {
        "cms": [], "enterprise": [], "cloud": [], "panels": [], "api": []
    }

    if not session.live_hosts:
        log.warning("No live hosts. Skipping Cortex.")
        return

    for host in session.live_hosts:
        url = host.get('url', '')
        tech_str = " ".join(host.get('tech', [])).lower()
        
        if any(x in tech_str for x in ["wordpress", "drupal", "joomla", "wix"]):
            technologies["cms"].append(url)
        elif any(x in tech_str for x in ["jira", "atlassian", "jenkins", "grafana"]):
            technologies["enterprise"].append(url)
        elif any(x in tech_str for x in ["kubernetes", "openshift", "aws", "azure"]):
            technologies["cloud"].append(url)
        elif any(x in tech_str for x in ["swagger", "openapi", "rest", "graphql"]):
            technologies["api"].append(url)
        
        if "login" in url or "admin" in url or "dashboard" in url:
            technologies["panels"].append(url)

    session.technologies = technologies
    log.info(f"Sorted: CMS({len(technologies['cms'])}) Enterprise({len(technologies['enterprise'])}) API({len(technologies['api'])})")

    # 2. Mining JS Files
    # We look for .js files in the live hosts list or construct them
    js_targets = []
    for host in session.live_hosts:
        if host['url'].endswith(".js"):
            js_targets.append(host['url'])
    
    # Also blindly check /main.js or /app.js on top targets if list is empty
    if not js_targets:
        for host in session.live_hosts[:5]: # Check top 5 only to save time
            js_targets.append(f"{host['url']}/main.js")
            js_targets.append(f"{host['url']}/app.js")

    js_targets = list(set(js_targets))
    log.info(f"Mining {len(js_targets)} JS files for secrets & endpoints...")
    
    found_endpoints = set()

    if js_targets:
        active_mode = config['global'].get('active_validation', False)
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(scan_js, url, session, active_mode) for url in js_targets]
            for f in futures:
                result = f.result()
                if result:
                    found_endpoints.update(result)

    # Save endpoints to session (New Field)
    session.endpoints = list(found_endpoints)
    if found_endpoints:
        log.info(f"Extracted {len(found_endpoints)} unique endpoints/paths from JS.")

def scan_js(url, session, active_mode):
    endpoints = set()
    try:
        r = requests.get(url, timeout=5, verify=False)
        if r.status_code != 200: return set()
        
        content = r.text
        
        # A. Secret Scanning
        for name, pattern in PATTERNS.items():
            matches = re.findall(pattern, content)
            for match in matches:
                status = "UNVERIFIED"
                severity = "MEDIUM"
                
                if active_mode:
                    if validate_key(name, match):
                        status = "VERIFIED"
                        severity = "CRITICAL"
                        console.print(f"[bold red]>>> BOOM! VALID {name}: {match}[/bold red]")
                    else:
                        status = "FALSE_POSITIVE"
                
                session.vulnerabilities.append({
                    "name": f"{name} ({status})",
                    "severity": severity,
                    "url": url,
                    "info": f"Key: {match}"
                })

        # B. Endpoint Extraction (LinkFinder)
        # We limit to finding internal API routes
        matches = re.findall(ENDPOINT_REGEX, content)
        for m in matches:
            if any(x in m for x in ["api", "v1", "admin", "user", "account", "config"]):
                endpoints.add(m)
                
    except Exception:
        pass
    
    return endpoints

def validate_key(name, key):
    try:
        if name == "google_api":
            r = requests.get(f"https://maps.googleapis.com/maps/api/staticmap?center=40,10&zoom=1&size=100x100&key={key}", timeout=5)
            if r.status_code == 200: return True
        elif name == "stripe_key":
            r = requests.get("https://api.stripe.com/v1/balance", auth=(key, ""), timeout=5)
            if r.status_code == 200: return True
    except:
        return False
    return False

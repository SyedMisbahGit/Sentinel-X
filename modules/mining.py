import re
import logging
from rich.console import Console

console = Console()
log = logging.getLogger("rich")

def run_mining(session, config):
    """
    Phase 4.5: Parameter Mining.
    Extracts interesting parameters from URLs.
    """
    console.print("[bold blue]━━ PHASE 4.5: PARAMETER MINING ━━[/bold blue]")

    interesting_params = ["id=", "file=", "page=", "dir=", "search=", "url=", "redirect=", "return="]
    count = 0

    log.info(f"Mining parameters from {len(session.live_hosts)} live hosts...")
    
    # Check URLs found in previous steps (Live hosts + Vulnerabilities)
    all_urls = [h['url'] for h in session.live_hosts]
    for v in session.vulnerabilities:
        all_urls.append(v.get('url', ''))
    
    # Simple Pattern Matching
    for url in set(all_urls):
        for param in interesting_params:
            if param in url:
                color = "yellow"
                if "file=" in url or "dir=" in url: color = "red" # LFI Candidate
                
                console.print(f"[{color}]  + Juicy Param: {url}[/{color}]")
                count += 1
                break 
    
    if count == 0:
        log.info("No obvious juicy parameters found in current URL set.")
    else:
        log.info(f"Mined {count} URLs with potential injection points.")

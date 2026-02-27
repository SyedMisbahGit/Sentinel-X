import socket
import requests
import logging
from rich.console import Console
from rich.panel import Panel
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()
log = logging.getLogger("rich")

def run_horizontal(session, config):
    """
    Phase 1.1: Horizontal Recon (ASN/CIDR Mapping)
    Identifies the target's autonomous system and extracts all owned IP ranges.
    """
    console.print("[bold blue]━━ PHASE 1.1: HORIZONTAL RECON (ASN/CIDR MAPPING) ━━[/bold blue]")
    domain = session.domain

    try:
        # 1. Resolve Domain to IP
        ip = socket.gethostbyname(domain)
        console.print(f"INFO     Resolved {domain} to Origin IP: {ip}")
    except Exception as e:
        log.warning(f"Failed to resolve {domain}. Cannot perform ASN mapping.")
        return

    # 2. Query BGPView API for ASN
    asn = None
    org_name = "Unknown"
    try:
        r = requests.get(f"https://api.bgpview.io/ip/{ip}", timeout=10).json()
        if r.get("status") == "ok" and r.get("data", {}).get("prefixes"):
            asn_data = r["data"]["prefixes"][0]["asn"]
            asn = asn_data["asn"]
            org_name = asn_data["name"]
            console.print(f"[cyan]  + Discovered ASN: AS{asn} ({org_name})[/cyan]")
        else:
            log.warning("No ASN data found in global routing tables for this IP.")
            return
    except Exception as e:
        log.error(f"Failed to query BGP API: {e}")
        return

    # 3. The Cloud Shield (Prevent scanning shared infrastructure)
    cloud_providers = ["CLOUDFLARE", "AMAZON", "AKAMAI", "FASTLY", "GOOGLE", "MICROSOFT", "INCAPSULA", "SQUARESPACE", "SHOPIFY"]
    if any(cloud in org_name.upper() for cloud in cloud_providers):
        console.print(f"[yellow]  ! SHIELD ACTIVATED: Target is hosted on shared infrastructure ({org_name}).[/yellow]")
        console.print(f"[yellow]  ! Aborting CIDR extraction to prevent out-of-scope scanning.[/yellow]")
        return

    # 4. Extract IPv4 CIDR Blocks
    cidrs = []
    try:
        r = requests.get(f"https://api.bgpview.io/asn/{asn}/prefixes", timeout=10).json()
        if r.get("status") == "ok":
            prefixes = r.get("data", {}).get("ipv4_prefixes", [])
            cidrs = [p["prefix"] for p in prefixes]
            
            if cidrs:
                session.cidrs = cidrs
                sample = ', '.join(cidrs[:3])
                overflow = f"... [+{len(cidrs)-3} more]" if len(cidrs) > 3 else ""
                
                console.print(Panel(
                    f"[bold green]HORIZONTAL SCOPE EXPANDED[/bold green]\n"
                    f"Organization: {org_name} (AS{asn})\n"
                    f"IPv4 Blocks Discovered: {len(cidrs)}\n"
                    f"Scope: {sample}{overflow}",
                    title="🌐 ASN/CIDR MAPPING SUCCESS", border_style="green"
                ))
            else:
                console.print("[dim]  + No IPv4 prefixes registered to this ASN.[/dim]")
    except Exception as e:
        log.error(f"Failed to fetch CIDR prefixes: {e}")

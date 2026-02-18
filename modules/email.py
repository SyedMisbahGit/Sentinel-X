import checkdmarc
import dns.resolver
import logging
import socket
from rich.console import Console
from rich.panel import Panel

console = Console()
log = logging.getLogger("rich")

def run_email(session, config):
    """
    Phase 2.7: SpoofCheck (Email Security).
    """
    console.print("[bold blue]━━ PHASE 2.7: SPOOFCHECK (CEO FRAUD) ━━[/bold blue]")

    domain = session.domain
    results = {
        "spf": "Missing",
        "dmarc": "Missing",
        "spoofable": False,
        "mx_records": []
    }

    # 1. Get MX Records
    mx_ip = "127.0.0.1"
    try:
        mx_answers = dns.resolver.resolve(domain, 'MX')
        mx_records = sorted([(r.preference, str(r.exchange).rstrip('.')) for r in mx_answers])
        results["mx_records"] = [r[1] for r in mx_records]
        primary_mx = mx_records[0][1]
        
        # Resolve MX to IP for SWAKS
        mx_ip = socket.gethostbyname(primary_mx)
        console.print(f"[cyan]  + Primary MX: {primary_mx} ({mx_ip})[/cyan]")
        
    except Exception:
        log.warning("No MX records found. Email might not be active.")
        primary_mx = f"mx.{domain}"

    # 2. Analyze DMARC
    try:
        dmarc_info = checkdmarc.check_domains([domain], timeout=10)
        data = dmarc_info.get(domain, {})
        
        spf_rec = data.get("spf", {}).get("record", "Missing")
        dmarc_rec = data.get("dmarc", {}).get("record", "Missing")
        p_policy = data.get("dmarc", {}).get("tags", {}).get("p", {}).get("value", "none")
        
        results["spf"] = spf_rec
        results["dmarc"] = dmarc_rec

        if "v=DMARC1" not in str(dmarc_rec) or p_policy == "none":
            results["spoofable"] = True
            console.print(Panel(
                f"[bold red]VULNERABLE: CEO Fraud Possible![/bold red]\n"
                f"Policy: p={p_policy}\n"
                f"Impact: You can send emails as 'admin@{domain}' to anyone.",
                title="❌ SPOOFCHECK FAILED", border_style="red"
            ))
            
            poc_cmd = f"swaks --to user@example.com --from admin@{domain} --server {primary_mx} --header 'Subject: Urgent Transfer'"
            console.print(f"\n[yellow]PoC Command (Authorized Testing Only):[/yellow]")
            console.print(f"[white on black]{poc_cmd}[/white on black]\n")
            
            session.vulnerabilities.append({
                "name": "Email Spoofing (CEO Fraud)",
                "severity": "CRITICAL",
                "url": domain,
                "info": f"DMARC policy is '{p_policy}'. Spoofing is possible."
            })

        elif p_policy == "quarantine":
            console.print(Panel(
                f"[bold orange1]MEDIUM: Spoofing Possible (Spam Folder)[/bold orange1]\n"
                f"Policy: p=quarantine",
                title="⚠️ SPOOFCHECK WARNING", border_style="orange1"
            ))

        elif p_policy == "reject":
            console.print(Panel(
                f"[bold green]SECURE: Spoofing Blocked[/bold green]\n"
                f"Policy: p=reject",
                title="✅ SPOOFCHECK PASSED", border_style="green"
            ))

    except Exception as e:
        log.error(f"DMARC Check failed: {e}")

    session.email_security = results

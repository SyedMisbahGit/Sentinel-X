import checkdmarc
import dns.resolver
import logging
import socket
from rich.console import Console

console = Console()
log = logging.getLogger("rich")

def run_email(session, config):
    """
    Phase 2.7: Email Security & DNS Recon.
    Checks SPF, DMARC, DNSSEC, MX Records, and Spoofability.
    """
    console.print("[bold blue]━━ PHASE 2.7: EMAIL SECURITY RECON ━━[/bold blue]")

    domain = session.domain
    results = {
        "spf": None,
        "dmarc": None,
        "dnssec": False,
        "mx_records": [],
        "spoofable": False,
        "ports": []
    }

    # 1. Check DMARC & SPF (Using checkdmarc library)
    log.info(f"Analyzing Email Security Policies for {domain}...")
    try:
        # checkdmarc performs a full analysis
        dmarc_info = checkdmarc.check_domains([domain])
        data = dmarc_info.get(domain, {})
        
        # Store SPF
        results["spf"] = data.get("spf", {}).get("record", "Missing")
        spf_valid = data.get("spf", {}).get("valid", False)
        
        # Store DMARC
        results["dmarc"] = data.get("dmarc", {}).get("record", "Missing")
        dmarc_valid = data.get("dmarc", {}).get("valid", False)
        
        # 2. Spoofing Logic
        # If DMARC is missing or policy is 'none', spoofing is possible
        p_policy = data.get("dmarc", {}).get("tags", {}).get("p", {}).get("value", "none")
        
        if not dmarc_valid or p_policy == "none":
            results["spoofable"] = True
            console.print(f"[bold red]>>> CRITICAL: Domain {domain} is SPOOFABLE! (DMARC p={p_policy})[/bold red]")
            # Add to vulnerabilities
            session.vulnerabilities.append({
                "name": "Email Spoofing Possible",
                "severity": "HIGH",
                "url": domain,
                "info": f"DMARC policy is '{p_policy}'. Attackers can send emails as {domain}."
            })
        else:
            console.print(f"[green]>>> Email Spoofing Mitigated (DMARC p={p_policy})[/green]")

    except Exception as e:
        log.error(f"DMARC Check failed: {e}")

    # 3. MX Records & Provider Fingerprinting
    try:
        mx_answers = dns.resolver.resolve(domain, 'MX')
        for rdata in mx_answers:
            mx_record = str(rdata.exchange).rstrip('.')
            results["mx_records"].append(mx_record)
            
            # Simple Fingerprinting
            if "google" in mx_record or "googlemail" in mx_record:
                console.print(f"[cyan]  + Provider: Google Workspace (OAuth 2.0 Likely Enforced)[/cyan]")
            elif "outlook" in mx_record or "protection.outlook" in mx_record:
                console.print(f"[cyan]  + Provider: Microsoft 365 (OAuth 2.0 Likely Enforced)[/cyan]")
            elif "pphosted" in mx_record:
                console.print(f"[cyan]  + Security: Proofpoint Detected[/cyan]")
            elif "mimecast" in mx_record:
                console.print(f"[cyan]  + Security: Mimecast Detected[/cyan]")

    except Exception:
        log.warning("No MX records found.")

    # 4. DNSSEC Check
    try:
        # Simple check: query DNSKEY
        dns.resolver.resolve(domain, 'DNSKEY')
        results["dnssec"] = True
        console.print("[green]  + DNSSEC is Enabled[/green]")
    except:
        console.print("[yellow]  - DNSSEC is Disabled[/yellow]")

    # 5. Mail Port Checks (SMTP/IMAP/POP3)
    # We only check the primary MX record to avoid noise
    if results["mx_records"]:
        primary_mx = results["mx_records"][0]
        log.info(f"Checking mail ports on primary MX: {primary_mx}...")
        
        mail_ports = [25, 465, 587, 110, 995, 143, 993]
        open_ports = []
        
        for port in mail_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1) # Fast timeout
            result = sock.connect_ex((primary_mx, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        
        if open_ports:
            log.info(f"Open Mail Ports: {open_ports}")
            results["ports"] = open_ports
            
            # Warn about plaintext ports
            if 110 in open_ports or 143 in open_ports or 25 in open_ports:
                 session.vulnerabilities.append({
                    "name": "Insecure Mail Ports Exposed",
                    "severity": "LOW",
                    "url": primary_mx,
                    "info": f"Plaintext ports {open_ports} exposed. Ensure STARTTLS is enforced."
                })

    # Save results to session for reporting
    session.email_security = results

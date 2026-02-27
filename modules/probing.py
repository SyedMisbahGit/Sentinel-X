import json
import subprocess
import logging
import tempfile
import os
from rich.console import Console

console = Console()
log = logging.getLogger("rich")

def run_probing(session, config):
    console.print("[bold blue]━━ PHASE 2: ACTIVE PROBING & TECH PROFILING ━━[/bold blue]")
    
    targets = list(set(session.subdomains))
    if not targets:
        log.warning("No targets available for active probing.")
        return

    console.print(f"INFO     Probing {len(targets)} targets (WAF-Bypass Enabled)...")
    
    # Use a secure temp directory mapped to RAM
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tf:
        tf.write("\n".join(targets))
        target_file = tf.name

    out_file = f"{target_file}_out.json"

    # Added -random-agent to bypass WAFs blocking default Go agents
    cmd = [
        "httpx",
        "-l", target_file,
        "-sc", "-tech", "-title", "-server", "-td",
        "-t", "50",
        "-random-agent",
        "-json",
        "-o", out_file,
        "-silent"
    ]

    live_hosts = []
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if os.path.exists(out_file):
            with open(out_file, 'r') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        data = json.loads(line)
                        url = data.get("url")
                        status = data.get("status_code", 0)
                        tech = data.get("tech", [])
                        server = data.get("webserver", "Unknown")
                        title = data.get("title", "No Title")
                        
                        live_hosts.append({
                            "url": url, "status": status, "tech": tech,
                            "server": server, "title": title
                        })
                        
                        tech_str = ", ".join(tech[:3]) + ("..." if len(tech) > 3 else "")
                        tech_str = tech_str or "Undetected"
                        status_color = "green" if status in [200, 301, 302] else "yellow" if status in [401, 403] else "red"
                        console.print(f"[{status_color}]  + {url} [/{status_color}][dim] [{status}] | Tech: {tech_str}[/dim]")
                        
                    except json.JSONDecodeError: continue
    except Exception as e:
        log.error(f"HTTPX execution failed: {e}")
    finally:
        if os.path.exists(target_file): os.remove(target_file)
        if os.path.exists(out_file): os.remove(out_file)

    session.live_hosts.extend(live_hosts)
    console.print(f"INFO     Active Live Hosts Profiled: {len(live_hosts)}")

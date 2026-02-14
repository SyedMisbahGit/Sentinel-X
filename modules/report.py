import os
import logging
from rich.console import Console

console = Console()
log = logging.getLogger("rich")

def run_report(session, config):
    console.print("[bold blue]━━ PHASE 6: ISSUING VERDICT ━━[/bold blue]")
    
    output_dir = f"output/{session.domain}"
    os.makedirs(output_dir, exist_ok=True)
    report_file = f"{output_dir}/verdict.html"
    
    # Stats & Grade Logic
    sub_count = len(session.subdomains)
    live_count = len(session.live_hosts)
    vuln_count = len(session.vulnerabilities)
    email_sec = getattr(session, 'email_security', {})
    endpoints = getattr(session, 'endpoints', [])
    
    grade = "A+"
    color = "green"
    
    criticals = len([v for v in session.vulnerabilities if "CRITICAL" in v['severity'].upper() or "HIGH" in v['severity'].upper()])
    mediums = len([v for v in session.vulnerabilities if "MEDIUM" in v['severity'].upper()])
    
    if criticals > 0:
        grade = "F"
        color = "red"
    elif mediums > 2:
        grade = "C"
        color = "orange"
    elif email_sec.get('spoofable'):
        grade = "B-"
        color = "yellow"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MUFTI Verdict: {session.domain}</title>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
        <style>
            body {{ font-family: 'Courier New', monospace; background: #0d1117; color: #c9d1d9; padding: 20px; }}
            h1 {{ color: #ffffff; border-bottom: 2px solid #30363d; text-transform: uppercase; letter-spacing: 2px; }}
            .verdict-box {{ border: 2px solid {color}; padding: 20px; margin: 20px 0; background: #161b22; text-align: center; }}
            .grade {{ font-size: 4em; color: {color}; font-weight: bold; display: block; }}
            .stat {{ font-size: 1.2em; margin: 0 15px; }}
            table.dataTable tbody tr {{ background-color: #0d1117; color: #c9d1d9; font-family: sans-serif; }}
            .critical {{ color: #ff7b72; font-weight: bold; }}
        </style>
    </head>
    <body>
    <h1>MUFTI // SECURITY VERDICT // {session.domain}</h1>
    
    <div class="verdict-box">
        <span class="grade">GRADE: {grade}</span>
        <br>
        <span class="stat">TARGETS: {live_count}</span>
        <span class="stat">CRITICALS: {criticals}</span>
        <span class="stat">SPOOFABLE: { 'YES' if email_sec.get('spoofable') else 'NO' }</span>
    </div>

    <h2>1. The Findings</h2>
    <table id="vulnTable" class="display" style="width:100%">
        <thead><tr><th>Severity</th><th>Name</th><th>URL</th><th>Info</th></tr></thead>
        <tbody>
    """
    
    if session.vulnerabilities:
        for v in session.vulnerabilities:
            sev = v.get('severity', 'LOW').upper()
            cls = "critical" if "CRITICAL" in sev or "HIGH" in sev else "medium"
            html += f"<tr><td class='{cls}'>{sev}</td><td>{v.get('name')}</td><td><a href='{v.get('url')}' style='color:#58a6ff'>{v.get('url')}</a></td><td>{v.get('info')}</td></tr>"
    
    html += """
        </tbody>
    </table>

    <h2>2. Deep Intel (Endpoints & Email)</h2>
    <div style="background:#161b22; padding:15px; border:1px solid #30363d">
        <p><b>SPF Record:</b> <code>{email_sec.get('spf', 'Missing')}</code></p>
        <p><b>DMARC Record:</b> <code>{email_sec.get('dmarc', 'Missing')}</code></p>
        <h3>Extracted Hidden Endpoints:</h3>
        <div style="max-height: 200px; overflow-y: scroll;">
    """
    
    if endpoints:
        for ep in endpoints:
             html += f"<code>{ep}</code><br>"
    else:
        html += "<p>No hidden endpoints found.</p>"

    html += """
        </div>
    </div>
    
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <script>$(document).ready(function() { $('#vulnTable').DataTable({ "order": [[ 0, "asc" ]] }); });</script>
    </body></html>
    """
    
    try:
        with open(report_file, "w") as f:
            f.write(html)
        console.print(f"[bold green][+] Verdict Issued: {report_file}[/bold green]")
    except Exception as e:
        log.error(f"Report generation failed: {e}")

import subprocess
import logging
import os
from rich.console import Console

console = Console()
log = logging.getLogger("rich")

def run_offensive(session, config):
    """
    The Attack Engine.
    Executes Nuclei based on the categories found in Phase 3.
    """
    console.print("[bold blue]━━ PHASE 4: OFFENSIVE STRIKES ━━[/bold blue]")
    
    nuclei_bin = config['tools']['nuclei']['path']
    rate_limit = config['modes'][session.mode]['nuclei_rate']
    
    # 1. SURGICAL STRIKES
    # Check if we have categorized targets
    tech_map = getattr(session, 'technologies', {})
    
    if tech_map.get('cms'):
        run_nuclei(nuclei_bin, tech_map['cms'], "wordpress,drupal,joomla,cve", rate_limit, "CMS_STRIKE")
        
    if tech_map.get('enterprise'):
        run_nuclei(nuclei_bin, tech_map['enterprise'], "jira,jenkins,grafana,cve", rate_limit, "ENTERPRISE_STRIKE")
        
    if tech_map.get('panels'):
        run_nuclei(nuclei_bin, tech_map['panels'], "login,panel,auth-bypass", rate_limit, "PANEL_STRIKE")

    # 2. SMOKE TEST (General scan on everything else)
    # We create a list of all live URLs
    all_live = [h['url'] for h in session.live_hosts]
    
    # Only scan top 50 to save time/bandwidth in stealth mode
    if session.mode == 'stealth':
        all_live = all_live[:50]
        
    run_nuclei(nuclei_bin, all_live, "misconfiguration,exposure,takeover", rate_limit, "GENERAL_SMOKE_TEST")

def run_nuclei(binary, targets, tags, rate, name):
    if not targets:
        return

    log.info(f"Launching {name} against {len(targets)} targets (Tags: {tags})...")
    
    # Create temp target file
    temp_file = f"data/temp_{name}.txt"
    with open(temp_file, "w") as f:
        f.write("\n".join(targets))
        
    cmd = [
        binary,
        "-l", temp_file,
        "-tags", tags,
        "-rl", str(rate),
        "-c", "10",
        "-timeout", "5",
        "-silent",
        "-json"
    ]
    
    try:
        # We process output line by line to show findings in real-time
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
        
        for line in process.stdout:
            # Here you would parse the JSON and add to session.vulnerabilities
            # For now, we just print Criticals
            if "critical" in line or "high" in line:
                console.print(f"[bold red]VULNERABILITY FOUND: {line.strip()}[/bold red]")
                
        os.remove(temp_file)
        
    except Exception as e:
        log.error(f"Nuclei failed: {e}")

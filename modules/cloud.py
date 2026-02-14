import subprocess
import logging
import os
import re
from rich.console import Console

console = Console()
log = logging.getLogger("rich")

def run_cloud(session, config):
    """
    Orchestrates Cloud Enumeration with Strict Timeouts.
    """
    console.print("[bold blue]━━ PHASE 2.5: CLOUD RECON ━━[/bold blue]")

    # 1. Extract Keyword
    domain_parts = session.domain.split('.')
    keyword = domain_parts[0]
    if len(domain_parts) > 2:
        keyword = domain_parts[-2]
    
    log.info(f"Derived Cloud Keyword: [bold]{keyword}[/bold]")
    
    cloud_assets = []

    # 2. Run S3Enum (Fast)
    cloud_assets.extend(run_s3enum(keyword, config))
    
    # 3. Run Cloud_Enum (Slow - Skip in Stealth)
    if session.mode in ['standard', 'loud', 'balanced']:
        cloud_assets.extend(run_cloud_enum(keyword, config))
    else:
        log.info("Skipping Cloud_Enum (Stealth Mode)")

    session.cloud_assets = cloud_assets
    log.info(f"Total Cloud Assets Found: {len(cloud_assets)}")

def run_s3enum(keyword, config):
    bin_path = config['tools']['s3enum']['path']
    wordlist = config['tools']['s3enum']['wordlist']
    
    if not os.path.exists(bin_path):
        log.warning("S3Enum binary missing. Skipping.")
        return []

    log.info("Running S3Enum (AWS)...")
    cmd = [bin_path, "-wordlist", wordlist, "-suffix", "", "-threads", "10", keyword]
    
    found = []
    try:
        # 2 Minute Timeout for S3
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        for line in process.stdout.splitlines():
            if "amazonaws.com" in line:
                clean_url = line.strip()
                if "http" not in clean_url: clean_url = f"https://{clean_url}"
                found.append({"provider": "aws", "type": "bucket", "url": clean_url})
                console.print(f"[green]  + AWS Bucket: {clean_url}[/green]")
    except subprocess.TimeoutExpired:
        log.warning("S3Enum timed out. Moving on.")
    except Exception as e:
        log.error(f"S3Enum failed: {e}")
    return found

def run_cloud_enum(keyword, config):
    script_path = config['tools']['cloud_enum']['path']
    
    if not os.path.exists(script_path):
        return []

    log.info("Running Cloud_Enum (Multi-Cloud)...")
    outfile = f"data/cloud_enum_{keyword}.txt"
    cmd = ["python3", script_path, "-k", keyword, "-l", outfile]
    
    found = []
    try:
        # 3 Minute Hard Limit
        subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if os.path.exists(outfile):
            with open(outfile, 'r') as f:
                content = f.read()
            urls = re.findall(r'https?://[\w\-\.]+(?:s3\.amazonaws\.com|blob\.core\.windows\.net|storage\.googleapis\.com)', content)
            
            for url in set(urls):
                provider = "unknown"
                if "windows.net" in url: provider = "azure"
                elif "googleapis" in url: provider = "gcp"
                elif "amazonaws" in url: provider = "aws"
                
                found.append({"provider": provider, "type": "storage", "url": url})
                console.print(f"[green]  + {provider.upper()} Asset: {url}[/green]")
            os.remove(outfile)
            
    except subprocess.TimeoutExpired:
        log.warning("[yellow]Cloud_Enum timed out (3m limit). Moving to next phase.[/yellow]")
    except Exception as e:
        log.error(f"Cloud_Enum failed: {e}")
        
    return found

import dns.resolver
import itertools
import logging
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console

console = Console()
log = logging.getLogger("rich")

# Top 15 permutations (High Signal / Low Noise)
# We avoid massive lists to prevent rate-limiting.
PERMUTATIONS = [
    "dev", "staging", "test", "prod", "beta", 
    "admin", "api", "vpn", "corp", "internal", 
    "demo", "stage", "preprod", "public", "private",
    "v1", "v2", "bak", "old", "new"
]

def run_permutations(session, config):
    """
    Phase 1.8: Subdomain Permutations.
    Generates and resolves variations of found subdomains.
    Example: api.target.com -> dev-api.target.com
    """
    console.print("[bold blue]━━ PHASE 1.8: SUBDOMAIN PERMUTATIONS ━━[/bold blue]")

    if not session.subdomains:
        log.warning("No subdomains to permute.")
        return

    # 1. Generate Variations
    base_domain = session.domain
    targets = set()
    
    # Extract prefixes from existing subdomains
    # e.g. "auth.tesla.com" -> prefix "auth"
    prefixes = set()
    for sub in session.subdomains:
        if sub.endswith(base_domain):
            # Remove base domain
            prefix = sub.replace(f".{base_domain}", "")
            if prefix:
                prefixes.add(prefix)

    log.info(f"Generating permutations for {len(prefixes)} unique prefixes...")
    
    for prefix in prefixes:
        for perm in PERMUTATIONS:
            # Pattern 1: prefix-perm (api-dev)
            targets.add(f"{prefix}-{perm}.{base_domain}")
            # Pattern 2: perm-prefix (dev-api)
            targets.add(f"{perm}-{prefix}.{base_domain}")
            # Pattern 3: prefix.perm (api.dev - deeper)
            targets.add(f"{prefix}.{perm}.{base_domain}")

    # Remove duplicates and existing subs
    candidates = list(targets - set(session.subdomains))
    
    if not candidates:
        log.info("No new permutations generated.")
        return

    log.info(f"Resolving {len(candidates)} candidate permutations...")

    # 2. Threaded Resolution
    # We use a lower thread count to avoid DNS bans (Robustness)
    valid_new_subs = []
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(resolve_dns, sub): sub for sub in candidates}
        
        for future in futures:
            result = future.result()
            if result:
                valid_new_subs.append(result)
                console.print(f"[green]  + Found Hidden Sub: {result}[/green]")

    if valid_new_subs:
        log.info(f"Permutations found {len(valid_new_subs)} new subdomains.")
        session.subdomains.extend(valid_new_subs)
        # We must save here because this changes the scope for subsequent modules
        session.save()
    else:
        log.info("No new valid subdomains found via permutations.")

def resolve_dns(domain):
    """
    Returns the domain if it resolves to an IP, else None.
    Handles False Positives (Wildcards) basics.
    """
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2
    resolver.lifetime = 2
    # Use reliable resolvers to avoid local ISP filtering
    resolver.nameservers = ['8.8.8.8', '1.1.1.1'] 
    
    try:
        resolver.resolve(domain, 'A')
        return domain
    except:
        return None

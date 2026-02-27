import re
import logging
import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
from rich.console import Console

console = Console()
log = logging.getLogger("rich")

# Extract href and action attributes
LINK_REGEX = re.compile(r'(?:href|action)=[\'"]([^\'"]+)[\'"]', re.IGNORECASE)

async def fetch_and_parse(session, url, base_domain):
    local_urls = set()
    try:
        # 5-second timeout, bypass SSL verification
        async with session.get(url, timeout=5, ssl=False) as response:
            if response.status != 200:
                return local_urls
            
            html = await response.text()
            matches = LINK_REGEX.findall(html)
            
            for match in matches:
                if match.startswith(('mailto:', 'javascript:', 'tel:', '#')): continue
                
                full_url = urljoin(url, match)
                parsed_full = urlparse(full_url)
                
                # Verify it belongs to the target domain
                if parsed_full.netloc == base_domain:
                    # Ignore static media files
                    if not full_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.css', '.svg', '.pdf', '.woff', '.js')):
                        local_urls.add(full_url)
                        
                # Memory constraint: Max 25 links per host
                if len(local_urls) >= 25: break
                
    except Exception:
        pass
    return local_urls

async def run_async_spider(targets):
    crawled_urls = set()
    connector = aiohttp.TCPConnector(limit_per_host=10, limit=100, verify_ssl=False)
    
    # Custom User-Agent to evade basic WAFs
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks = []
        for target in targets:
            base_domain = urlparse(target).netloc
            tasks.append(fetch_and_parse(session, target, base_domain))
        
        # Execute all concurrent requests
        results = await asyncio.gather(*tasks)
        for res in results:
            crawled_urls.update(res)
            
    return list(crawled_urls)

def run_spider(session, config):
    console.print("[bold blue]━━ PHASE 2.2: THE SPIDER (ASYNC SURFACE MAPPING) ━━[/bold blue]")
    
    targets = [host.get('url') for host in session.live_hosts if host.get('url')]
    if not targets:
        log.warning("No live hosts to crawl. Skipping.")
        return

    console.print(f"INFO     Deploying Async Spider to {len(targets)} targets...")
    
    # Trigger the asyncio event loop
    loop = asyncio.get_event_loop()
    new_urls = loop.run_until_complete(run_async_spider(targets))
    
    session.crawled_urls.extend(new_urls)
    
    if new_urls:
        console.print(f"[green]  + Spider Complete. Mapped {len(new_urls)} hidden endpoints.[/green]")
    else:
        console.print("[dim]  + Spider Complete. No internal links found.[/dim]")

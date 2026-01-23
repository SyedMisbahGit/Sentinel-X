#!/usr/bin/env python3
import mmh3, requests, codecs, sys, random, json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Config
FLARESOLVERR_URL = "http://localhost:8191/v1"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}

def get_hash(content): return mmh3.hash(codecs.encode(content, "base64"))

def solve_waf(target_url):
    """Uses FlareSolverr to solve JS Challenge and get cookies"""
    payload = {
        "cmd": "request.get",
        "url": target_url,
        "maxTimeout": 60000
    }
    try:
        r = requests.post(FLARESOLVERR_URL, json=payload, timeout=65)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "ok":
                # Extract cookies for Requests session
                cookies = {c['name']: c['value'] for c in data['solution']['cookies']}
                ua = data['solution']['userAgent']
                return cookies, ua
    except:
        pass
    return None, None

def solve_favicon(domain, subs_file=None):
    print(f"[*] Starting Favicon Hunt for: {domain}", file=sys.stderr)
    targets = [f"https://{domain}", f"https://www.{domain}"]
    if subs_file:
        try:
            with open(subs_file) as f:
                lines = [l.strip() for l in f if l.strip()]
                random.shuffle(lines)
                targets += lines[:30]
        except: pass

    # Google Fallback
    try:
        g_url = f"https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://{domain}&size=64"
        r = requests.get(g_url, headers=HEADERS, timeout=5)
        if r.status_code == 200 and len(r.content) > 0:
            print(f"    -> [Google Cache] Hash: {get_hash(r.content)}")
    except: pass

    # Active Hunt
    for url in targets:
        if not url.startswith("http"): url = "https://" + url
        try:
            # Try Direct Access First
            r = requests.get(f"{url}/favicon.ico", headers=HEADERS, timeout=5, verify=False)
            
            # If Blocked (403/503), engage FlareSolverr
            if r.status_code in [403, 503]:
                print(f"    [!] WAF Detected at {url}. Engaging FlareSolverr...", file=sys.stderr)
                cookies, ua = solve_waf(url) # Solve on homepage first
                if cookies:
                    # Retry with solved cookies
                    h = HEADERS.copy()
                    h['User-Agent'] = ua
                    r = requests.get(f"{url}/favicon.ico", cookies=cookies, headers=h, timeout=10, verify=False)
            
            # Check Result
            if r.status_code == 200 and len(r.content) > 0:
                # Basic check if it's actually an image
                if 'image' in r.headers.get('Content-Type', '').lower() or r.content[:4] in [b'\x00\x00\x01\x00', b'\x89PNG']:
                    h_val = get_hash(r.content)
                    if h_val == 0: continue
                    print(f"\n\033[92m[+] SUCCESS: {url}\033[0m")
                    print(f"\033[92m[+] FAVICON HASH: {h_val}\033[0m")
                    print(f"    -> https://www.shodan.io/search?query=http.favicon.hash:{h_val}")
                    return
        except Exception as e: 
            pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        solve_favicon(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
